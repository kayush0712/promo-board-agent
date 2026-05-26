

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.base import call_llm, parse_json
from models import ReviewSession
from agents.base import sanitize_text
from models import ReviewSession
from agents.harvester import run_harvester
from agents.advocate  import run_advocate
from agents.evaluator import run_evaluator
from agents.sentinel  import run_sentinel
    

ORCHESTRATOR_SYSTEM = """
You are the Orchestrator in an AI-powered promotion review board.
You are the final decision agent.

You receive inputs from 3 agents:
1. Advocate   — built the strongest case FOR the employee
2. Evaluator  — critically checked the evidence
3. Sentinel   — checked budget and policy feasibility

Your job is to synthesize all 3 inputs into one
balanced, fair, final promotion recommendation.

Rules:
- If Sentinel says feasible=false → decision MUST be HOLD regardless
- If Evaluator confidence < 65    → decision should be HOLD
- If Evaluator verdict is STRONG and Sentinel feasible=true → RECOMMEND
- If verdict is CONDITIONAL       → use your judgment based on confidence
- Be specific — use numbers from the data
- Be concise — the manager reads this in 60 seconds

You MUST respond in pure JSON only.
No markdown. No explanation. No backticks.

Response format:
{
  "decision":           "RECOMMEND" | "HOLD",
  "confidence":         <integer 50-99>,
  "proposed_salary":    <integer>,
  "salary_increase_pct":<integer>,
  "key_strengths": [
    "specific strength 1 with numbers",
    "specific strength 2 with numbers"
  ],
  "concerns": [
    "concern 1 if any — or empty list if none"
  ],
  "condition": "what needs to happen before promotion if HOLD — or null",
  "executive_summary": "2-3 sentences for the hiring manager summarizing the decision"
}
"""


def run_orchestrator(
    harvester_output:  dict,
    advocate_output:   dict,
    evaluator_output:  dict,
    sentinel_output:   dict,
    session:           ReviewSession
) -> dict:
    """
    Synthesizes all agent outputs into final packet.

    Input:  outputs from all 4 agents
    Output: final promotion recommendation
    """
#basically to get in a particular format of receiving data
    
    strengths_text = ""
    for s in advocate_output.get("strengths", []):
        strengths_text += f"- {s['category']}: {s['evidence']}\n"

    
    evaluator_text = f"""
Verdict:    {evaluator_output.get('verdict')}
Confidence: {evaluator_output.get('confidence')}%
Accepted:   {evaluator_output.get('accepted')}
Challenged: {evaluator_output.get('challenged')}
Gap:        {evaluator_output.get('gap')}
Loops Run:  {evaluator_output.get('loops_run')}
"""

    
    sentinel_text = f"""
Feasible:        {sentinel_output.get('feasible')}
Current Salary:  ₹{sentinel_output.get('current_salary'):,}
Proposed Salary: ₹{sentinel_output.get('proposed_salary'):,}
Increase:        {sentinel_output.get('increase_pct')}%
Band Check:      {sentinel_output['checks']['band']['status']}
Budget Check:    {sentinel_output['checks']['budget']['status']}
Slots Check:     {sentinel_output['checks']['slots']['status']}
"""

    user_prompt = f"""
<employee_data>
Employee:      {sanitize_text(harvester_output['name'])}
Role:          {sanitize_text(harvester_output['role_title'])}
Promotion:     {sanitize_text(harvester_output['current_level'])} → {sanitize_text(harvester_output['target_level'])}
Tenure:        {sanitize_text(harvester_output['tenure_years'])} years
Last Rating:   {sanitize_text(harvester_output['last_rating'])}
</employee_data>

<advocate_report>
{sanitize_text(strengths_text)}
</advocate_report>

<evaluator_report>
{sanitize_text(evaluator_text)}
</evaluator_report>

<sentinel_report>
{sanitize_text(sentinel_text)}
</sentinel_report>

Synthesize all inputs and make the final promotion recommendation.
"""

    
    raw = call_llm(
        system_prompt = ORCHESTRATOR_SYSTEM,
        user_prompt   = user_prompt,
        agent_name    = "orchestrator",
        session       = session,
        model_size    = "medium"
    )

    result = parse_json(raw, "orchestrator")

    if result.get("error"):

        return {
            "decision":           "HOLD",
            "confidence":         50,
            "proposed_salary":    sentinel_output.get("proposed_salary"),
            "salary_increase_pct":sentinel_output.get("increase_pct"),
            "key_strengths":      [],
            "concerns":           ["Orchestrator failed to generate recommendation"],
            "condition":          "Manual review required",
            "executive_summary":  "System error — please review manually."
        }

    return result




if __name__ == "__main__":
    

    print("Testing Full Agent Chain\n")
    test_id = "E4021"

    session = ReviewSession(test_id)

    print("Harvester collecting data")
    harvester_output = run_harvester(test_id, session)
    print(f"Done — {len(harvester_output['metrics'])} metrics | Role: {harvester_output['role_title']}\n")

    
    print("Advocate building case")
    advocate_output = run_advocate(harvester_output, session)
    print(f"Done — {len(advocate_output.get('strengths', []))} strengths built\n")

    #
    print(" Evaluator checking evidence...")
    evaluator_output = run_evaluator(harvester_output, advocate_output, session)
    print(f"Done — Verdict: {evaluator_output.get('verdict')} | Confidence: {evaluator_output.get('confidence')}% | Loops: {evaluator_output.get('loops_run')}\n")

    
    print("Sentinel checking budget...")
    sentinel_output = run_sentinel(harvester_output, session)
    print(f"Done — Feasible: {sentinel_output.get('feasible')} | Proposed: ₹{sentinel_output.get('proposed_salary'):,}\n")

    
    print("Step 5 — Orchestrator synthesizing final packet...")
    final_packet = run_orchestrator(
        harvester_output,
        advocate_output,
        evaluator_output,
        sentinel_output,
        session
    )
    print("Done\n")

    # ── Display final packet ──
    print("=" * 55)
    print("FINAL PROMOTION PACKET")
    print("=" * 55)
    print(f"Employee:    {harvester_output['name']}")
    print(f"Promotion:   {harvester_output['current_level']} → {harvester_output['target_level']}")
    print(f"Decision:    {final_packet.get('decision')}")
    print(f"Confidence:  {final_packet.get('confidence')}%")
    print(f"Salary:      ₹{sentinel_output['current_salary']:,} → ₹{final_packet.get('proposed_salary'):,} (+{final_packet.get('salary_increase_pct')}%)")
    print(f"\nKey Strengths:")
    for s in final_packet.get("key_strengths", []):
        print(f"  {s}")
    print(f"\nConcerns:")
    concerns = final_packet.get("concerns", [])
    if concerns:
        for c in concerns:
            print(f"  {c}")
    else:
        print("  None")
    print(f"\nCondition:   {final_packet.get('condition')}")
    print(f"\nSummary:")
    print(f"  {final_packet.get('executive_summary')}")
    print("=" * 55)

    # ── Token usage ──
    print("\nToken Usage Per Agent")
    print("-" * 55)
    for agent, usage in session.tokens.agent_breakdown().items():
        print(f"  {agent:35} → {usage['total']:5} tokens | ${usage['cost_usd']} | ₹{usage['cost_inr']}")
    print("-" * 55)
    print(f"  {'TOTAL':35} → {session.tokens.total_tokens():5} tokens | ${session.tokens.cost_usd()} ")
    print(f"  {'COST IN INR':35} → ₹{session.tokens.cost_inr()}")