
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import asyncio 
from models import ReviewSession
from agents.harvester          import run_harvester
from agents.advocate           import run_advocate
from agents.evaluator          import run_evaluator
from agents.sentinel           import run_sentinel
from agents.orchestrator_agent import run_orchestrator
from database                  import save_review_start, save_agent_output, save_final_packet



async def run_full_review(
    employee_id:     str,
    session:         ReviewSession,
    stream_callback  
) -> dict:
    try:
        async with asyncio.timeout(300):

            # ── Step 1: Harvester ──
            await stream_callback("harvester", "running", "Collecting data...")
            harvester_output = run_harvester(employee_id, session)

            await save_review_start(employee_id, harvester_output["name"])
            await save_agent_output(employee_id, "harvester", harvester_output)

            await stream_callback("harvester", "done", f"Collected {len(harvester_output['metrics'])} metrics")

            # ── Step 2: Advocate ──
            await stream_callback("advocate", "running", "Building promotion case...")
            advocate_output = run_advocate(harvester_output, session)

            # ✅ Save advocate output
            await save_agent_output(employee_id, "advocate", advocate_output)

            await stream_callback("advocate", "done", f"Built {len(advocate_output.get('strengths', []))} strengths")

            # ── Step 3: Evaluator ──
            await stream_callback("evaluator", "running", "Cross-checking evidence...")

            evaluator_messages = []
            def evaluator_sync_callback(agent, status, message):
                evaluator_messages.append((agent, status, message))

            evaluator_output = run_evaluator(
                harvester_output, advocate_output, session,
                stream_callback = evaluator_sync_callback
            )

            for agent, status, message in evaluator_messages:
                await stream_callback(agent, status, message)

            
            await save_agent_output(employee_id, "evaluator", evaluator_output)

            await stream_callback("evaluator", "done", f"Verdict: {evaluator_output.get('verdict')}")

            # ── Step 4: Sentinel ──
            await stream_callback("sentinel", "running", "Checking budget...")
            sentinel_output = run_sentinel(harvester_output, session)

            
            await save_agent_output(employee_id, "sentinel", sentinel_output)

            await stream_callback("sentinel", "done", f"Feasible: {sentinel_output.get('feasible')}")

            # ── Step 5: Orchestrator ──
            await stream_callback("orchestrator", "running", "Synthesizing recommendation...")
            final_packet = run_orchestrator(
                harvester_output, advocate_output,
                evaluator_output, sentinel_output, session
            )
            session.final_packet = final_packet

            
            await save_final_packet(
                employee_id,
                final_packet,
                session.tokens.summary()
            )

            await stream_callback("orchestrator", "done", f"Decision: {final_packet.get('decision')}", final_packet)

            # ── Step 6: Human waiting ──
            await stream_callback("human", "waiting", "Waiting for manager decision...", {
                "employee_name":       harvester_output["name"],
                "current_level":       harvester_output["current_level"],
                "target_level":        harvester_output["target_level"],
                "decision":            final_packet.get("decision"),
                "confidence":          final_packet.get("confidence"),
                "proposed_salary":     final_packet.get("proposed_salary"),
                "key_strengths":       final_packet.get("key_strengths"),
                "concerns":            final_packet.get("concerns"),
                "condition":           final_packet.get("condition"),           # ← added
                "summary":             final_packet.get("executive_summary"),   # ← added
                "current_salary":      sentinel_output.get("current_salary"),
                "salary_increase_pct": sentinel_output.get("increase_pct"),
                "token_usage":         session.tokens.summary()
            })

            return final_packet

    except asyncio.TimeoutError:
        await stream_callback("system", "error", "Review timed out after 5 minutes")
        raise
    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}") 
        await stream_callback("system", "error", "An internal system error occurred. Review aborted.") 
        raise

def apply_human_decision(
    session:  ReviewSession,
    decision: str,           
    comment:  str = ""
) -> dict:
    if decision == "approved":
        session.approve(comment)
    elif decision == "rejected":
        session.reject(comment)
    else:
        raise ValueError(f"Invalid decision: {decision}. Must be 'approved' or 'rejected'")

    return {
        "employee_id":    session.employee_id,
        "human_decision": session.human_decision,
        "human_comment":  session.human_comment,
        "ai_decision":    session.final_packet.get("decision") if session.final_packet else None,
        "token_usage":    session.tokens.summary(),
        "complete":       session.is_complete()
    }