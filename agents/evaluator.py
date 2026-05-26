

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from agents.base import call_llm, parse_json
from models import ReviewSession



EVALUATOR_SYSTEM = """
You are the Objective Evaluator in an AI-powered promotion review board.
You are strict, evidence-based, and skeptical of vague claims.

Your job is to cross-check the Advocate's brief against the
official competency matrix for the target level.

Rules:
- Challenge every claim that lacks specific, verifiable data
- Accept claims that have concrete numbers as evidence
- Check if evidence actually proves the competency — not just sounds good
- Numeric evidence (commits, tickets, scores, hours) is sufficient proof
- Be fair but tough — your job is to protect promotion standards

Reflection Loop Rules (CRITICAL):
- Set needs_more_data=true ONLY IF confidence is below 70
- If confidence is 70 or above → needs_more_data MUST be false
- If loop_number >= 1 → needs_more_data MUST be false — you must conclude
- Only request data that realistically exists in HR/engineering systems
- Do NOT repeat a data request you already made in a previous loop

You MUST respond in pure JSON only.
No markdown. No explanation. No backticks.

Response format:
{
  "verdict":         "STRONG" | "CONDITIONAL" | "INSUFFICIENT",
  "accepted":        ["strength categories you accept as proven"],
  "challenged":      ["strength categories that need more evidence"],
  "gap":             "the single most important missing evidence",
  "needs_more_data": true | false,
  "data_request":    "specific data needed (or null if none)",
  "confidence":      <integer 50-95>,
  "reasoning":       "one sentence explaining your verdict"
}

Verdict guide:
- STRONG:       3+ strengths accepted, confidence 80+
- CONDITIONAL:  1-2 strengths accepted, confidence 60-79
- INSUFFICIENT: 0 strengths accepted, confidence below 60
"""




FETCHER_SYSTEM = """
You are a Data Fetcher agent inside an HR promotion review system.

The Evaluator found a gap in the promotion evidence.
Your job is to search the available raw employee data and
find the most relevant information to fill that gap.

Rules:
- Read the gap request carefully
- Search through ALL available data sources provided
- Extract ONLY data relevant to the specific gap
- Be specific — use exact numbers and facts from the data
- If the data genuinely does not exist — clearly say "Data not available: <reason>"
- Do NOT invent or assume data that is not explicitly provided
- Keep response under 100 words — focused and specific

Return plain text only. No JSON. No headers. Just the finding.
"""




def run_agentic_fetcher(
    data_request:  str,
    raw_employee:  dict,
    session:       ReviewSession
) -> str:


    searchable_data = {
        "github": raw_employee.get("github"),
        "jira":   raw_employee.get("jira"),
        "slack":  raw_employee.get("slack"),
        "zendesk":raw_employee.get("zendesk"),
        "hrms": {
            "tenure_years":  raw_employee.get("tenure_years"),
            "last_rating":   raw_employee.get("last_rating"),
            "attrition_rate":raw_employee.get("hrms", {}).get("attrition_rate") if raw_employee.get("hrms") else None,
            "nps_score":     raw_employee.get("hrms", {}).get("nps_score") if raw_employee.get("hrms") else None,
        },
        "achievements": raw_employee.get("achievements", []),
        "system_designs":raw_employee.get("system_designs", [])
    }

    user_prompt = f"""
Gap identified by Evaluator:
"{data_request}"

All available employee data to search through:
{json.dumps(searchable_data, indent=2)}

Find and return the most relevant data for this specific gap.
Use exact numbers and facts. Be concise.
"""

    response = call_llm(
        system_prompt = FETCHER_SYSTEM,
        user_prompt   = user_prompt,
        agent_name    = f"agentic_fetcher",
        session       = session,
        model_size    = "small",   
        max_tokens    = 300,        
        temperature   = 0.1        
    )

    return response.strip()



def run_evaluator(
    harvester_output: dict,
    advocate_output:  dict,
    session:          ReviewSession,
    raw_employee:     dict = None,    
    stream_callback   = None          
) -> dict:
    """
    Evaluates the Advocate's brief against the competency matrix.

    What makes this agentic:
    1. Reflection loop — Evaluator decides IF it needs more data
    2. Agentic fetcher  — LLM decides WHAT data is relevant
    3. Loop-aware prompt — LLM knows when to conclude
    4. Self-reasoning   — returns explicit reasoning for its verdict

    Flow:
    Loop 0: Base evaluation
            → If gap found and confidence < 70 → trigger fetcher
    Loop 1: Re-evaluation with extra data
            → Must conclude regardless (loop >= 1 rule)
    """

    from mock_data import get_competency, get_employee

    MAX_LOOPS  = 2
    loop_count = 0

  
    current_metrics = dict(harvester_output.get("metrics", {}))

   
    previous_requests = []

    
    if raw_employee is None:
        try:
            raw_employee = get_employee(harvester_output.get("employee_id", ""))
        except Exception:
            raw_employee = {}

    while loop_count < MAX_LOOPS:

        
        competency = get_competency(harvester_output["target_level"])

        
        strengths_text = ""
        for i, s in enumerate(advocate_output.get("strengths", []), 1):
            strengths_text += f"{i}. {s['category']}\n"
            strengths_text += f"   Evidence:  {s['evidence']}\n"
            strengths_text += f"   Relevance: {s['relevance']}\n\n"

        if not strengths_text:
            strengths_text = "No strengths provided by Advocate."

        
        metrics_text = ""
        for key, data in current_metrics.items():
            if isinstance(data, dict) and data.get("value") is not None:
                metrics_text += f"- {key}: {data['value']}\n"
            elif isinstance(data, str):
                # Extra data added by fetcher in previous loop
                metrics_text += f"- {key}: {data}\n"

        # ── Loop-aware instructions ──
        # Tell LLM which loop it's on so it knows when to conclude
        if loop_count == 0:
            loop_instruction = (
                "This is your FIRST evaluation. "
                "If you find a critical gap and confidence < 70, "
                "you may request more data."
            )
        else:
            loop_instruction = (
                f"This is loop {loop_count} — your FINAL evaluation. "
                "You MUST set needs_more_data=false and give your final verdict. "
                "Do not request more data."
            )

        # ── Include previous requests to avoid repetition ──
        prev_req_text = ""
        if previous_requests:
            prev_req_text = f"\nAlready requested in previous loops: {previous_requests}\nDo NOT repeat these requests."

        # ── Build user prompt ──
        user_prompt = f"""
Employee:     {harvester_output.get('name', 'the employee')}
Role:         {harvester_output.get('role_title', 'Unknown')}
Promotion:    {harvester_output.get('current_level')} → {harvester_output.get('target_level')}
Tenure:       {harvester_output.get('tenure_years')} years
Last Rating:  {harvester_output.get('last_rating')}

Loop Status: {loop_instruction}
{prev_req_text}

── Advocate's Brief ──
{strengths_text}

── Raw Performance Data ──
{metrics_text if metrics_text else "No metrics available."}

── Target Level Competency ({harvester_output.get('target_level')}) ──
Technical:  {competency.get('technical')}
Leadership: {competency.get('leadership')}
Delivery:   {competency.get('delivery')}
Impact:     {competency.get('impact')}

Evaluate strictly. Is the evidence strong enough for promotion?
"""

        # ── Call LLM ──
        raw = call_llm(
            system_prompt = EVALUATOR_SYSTEM,
            user_prompt   = user_prompt,
            agent_name    = f"evaluator_loop_{loop_count}",
            session       = session,
            model_size    = "large",    # needs best reasoning model
            max_tokens    = 1000,
            temperature   = 0.1         # very consistent decisions
        )

        result = parse_json(raw, "evaluator")

        # ── Handle parse failure ──
        if result.get("error"):
            print(f"⚠️  Evaluator parse failed on loop {loop_count}")
            return {
                "verdict":    "CONDITIONAL",
                "confidence": 60,
                "accepted":   [],
                "challenged": [],
                "gap":        "Evaluator failed to parse response",
                "reasoning":  "Parse error — defaulting to CONDITIONAL",
                "loops_run":  loop_count,
                "total_calls":loop_count + 1
            }

        needs_more   = result.get("needs_more_data", False)
        data_request = result.get("data_request")
        confidence   = result.get("confidence", 0)

        # ── Decide whether to loop ──
        should_loop = (
            needs_more                           # LLM says it needs more
            and data_request                     # LLM specified what it needs
            and confidence < 70                  # confidence actually low
            and loop_count < MAX_LOOPS - 1       # haven't hit ceiling
            and data_request not in previous_requests  # not a repeat request
        )

        if should_loop:
            msg = f"Gap found → {data_request}"
            print(f"🔄 Evaluator loop {loop_count + 1}: {msg}")

            if stream_callback:
                stream_callback("evaluator", "loop", msg)

            
            previous_requests.append(data_request)

            #
            print(f"   🔍 Fetcher searching for: {data_request}")
            extra_data = run_agentic_fetcher(data_request, raw_employee, session)
            print(f"   📦 Fetcher found: {extra_data[:100]}...")

            
            current_metrics[f"extra_evidence_{loop_count}"] = {
                "value":  extra_data,
                "weight": 0.0,
                "reason": f"Additional evidence for: {data_request}"
            }

            loop_count += 1
            

        else:
            
            reason = ""
            if not needs_more:
                reason = "Evaluator satisfied with evidence"
            elif confidence >= 70:
                reason = f"Confidence {confidence}% sufficient — no loop needed"
            elif loop_count >= MAX_LOOPS - 1:
                reason = "Maximum loops reached — concluding"
            elif data_request in previous_requests:
                reason = "Repeated data request — concluding"

            if reason:
                print(f"✅ Evaluator concluding: {reason}")

            result["loops_run"]    = loop_count
            result["total_calls"]  = loop_count + 1
            result["conclusion_reason"] = reason
            return result

    
    
    result["loops_run"]   = loop_count
    result["total_calls"] = loop_count + 1
    return result




if __name__ == "__main__":
    from models import ReviewSession
    from agents.harvester import run_harvester
    from agents.advocate  import run_advocate
    from mock_data import get_employee

    print("=== Testing Agentic Evaluator ===\n")

    employee_id  = "E1042"
    session      = ReviewSession(employee_id)
    raw_employee = get_employee(employee_id)

    print("🔄 Step 1 — Harvester...")
    harvester_output = run_harvester(employee_id, session)
    print(f"✅ {len(harvester_output['metrics'])} metrics collected\n")

    print("🔄 Step 2 — Advocate...")
    advocate_output = run_advocate(harvester_output, session)
    print(f"✅ {len(advocate_output.get('strengths', []))} strengths built\n")

    print("🔄 Step 3 — Evaluator (agentic)...")
    evaluator_output = run_evaluator(
        harvester_output,
        advocate_output,
        session,
        raw_employee = raw_employee
    )

    print(f"\n✅ Evaluator Result:")
    print(f"  Verdict:    {evaluator_output.get('verdict')}")
    print(f"  Confidence: {evaluator_output.get('confidence')}%")
    print(f"  Accepted:   {evaluator_output.get('accepted')}")
    print(f"  Challenged: {evaluator_output.get('challenged')}")
    print(f"  Gap:        {evaluator_output.get('gap')}")
    print(f"  Reasoning:  {evaluator_output.get('reasoning')}")
    print(f"  Loops Run:  {evaluator_output.get('loops_run')}")
    print(f"  Total Calls:{evaluator_output.get('total_calls')}")
    print(f"  Concluded:  {evaluator_output.get('conclusion_reason')}")

    print("\n=== Token Usage ===")
    for agent, usage in session.tokens.agent_breakdown().items():
        print(f"  {agent:40} → {usage['total']:5} tokens | ${usage['cost_usd']}")
    print(f"  {'TOTAL':40} → {session.tokens.total_tokens():5} tokens | ${session.tokens.cost_usd()}")
