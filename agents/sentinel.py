# backend/agents/sentinel.py

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import ReviewSession
from mock_data import get_budget




def calculate_proposed_salary(current_salary: int, target_level: str, budget_data: dict) -> int:

    avg  = budget_data["avg_salary"].get(target_level)
    band = budget_data["salary_bands"].get(target_level)

    if avg is None:
        proposed = int(current_salary * 1.20)

    elif current_salary >= avg:
        proposed = int(current_salary * 1.10)
      
        if band and proposed > band["max"]:
            proposed = band["max"]

    else:
        proposed = int((current_salary + avg) / 2)

   
    if band and proposed < band["min"]:
        proposed = band["min"]

    if proposed <= current_salary:
        proposed = current_salary    

    return proposed




def run_sentinel(harvester_output: dict, session: ReviewSession) -> dict:

    department    = harvester_output["department"]
    current_salary= harvester_output["current_salary"]
    target_level  = harvester_output["target_level"]

    # Get budget data
    budget = get_budget(department)

    # Calculate proposed salary
    proposed_salary = calculate_proposed_salary(
        current_salary,
        target_level,
        budget
    )

    salary_increase    = proposed_salary - current_salary
    salary_increase_pct= round((salary_increase / current_salary) * 100, 1)

    # ── Check 1: Salary band ──
    band = budget["salary_bands"].get(target_level)

    if band is None:
        band_check  = False
        band_status = f"No salary band defined for {target_level}"
    elif proposed_salary < band["min"]:
        band_check  = False
        band_status = f"Proposed ₹{proposed_salary:,} is BELOW band minimum ₹{band['min']:,}"
    elif proposed_salary > band["max"]:
        band_check  = False
        band_status = f"Proposed ₹{proposed_salary:,} is ABOVE band maximum ₹{band['max']:,}"
    else:
        band_check  = True
        band_status = f"Within band (₹{band['min']:,} – ₹{band['max']:,})"

    # ── Check 2: Budget ──
    remaining = budget["remaining_budget"]

    if salary_increase > remaining:
        budget_check  = False
        budget_status = f"Increase ₹{salary_increase:,} exceeds remaining budget ₹{remaining:,}"
    else:
        budget_check  = True
        budget_remaining_after = remaining - salary_increase
        budget_status = f"Budget sufficient — ₹{budget_remaining_after:,} remaining after promotion"

    # ── Check 3: Open slots ──
    open_slots = budget["open_slots"].get(target_level, 0)

    if open_slots == 0:
        slots_check  = False
        slots_status = f"No open slots at {target_level}"
    else:
        slots_check  = True
        slots_status = f"{open_slots} open slot(s) at {target_level}"

    # ── Overall feasibility ──
    all_checks_passed = band_check and budget_check and slots_check

    return {
        "feasible":          all_checks_passed,
        "proposed_salary":   proposed_salary,
        "current_salary":    current_salary,
        "salary_increase":   salary_increase,
        "increase_pct":      salary_increase_pct,
        "checks": {
            "band":   {"passed": band_check,   "status": band_status},
            "budget": {"passed": budget_check, "status": budget_status},
            "slots":  {"passed": slots_check,  "status": slots_status}
        }
    }



if __name__ == "__main__":
    from models import ReviewSession
    from agents.harvester import run_harvester

    print("=== Testing Sentinel Agent ===\n")

    # Test with Engineer
    print("── Engineer (E1042) ──")
    session = ReviewSession("E1042")
    harvester_output = run_harvester("E1042", session)
    sentinel_output  = run_sentinel(harvester_output, session)

    print(f"Employee:         {harvester_output['name']}")
    print(f"Current Salary:   ₹{sentinel_output['current_salary']:,}")
    print(f"Proposed Salary:  ₹{sentinel_output['proposed_salary']:,}")
    print(f"Increase:         ₹{sentinel_output['salary_increase']:,} ({sentinel_output['increase_pct']}%)")
    print(f"Feasible:         {sentinel_output['feasible']}")
    print(f"\nChecks:")
    for name, check in sentinel_output["checks"].items():
        print(f"  {name:8} → {check['status']}")

    # Test with Support Lead
    print("\n── Support Lead (E3088) ──")
    session2 = ReviewSession("E3088")
    harvester_output2 = run_harvester("E3088", session2)
    sentinel_output2  = run_sentinel(harvester_output2, session2)

    print(f"Employee:         {harvester_output2['name']}")
    print(f"Current Salary:   ₹{sentinel_output2['current_salary']:,}")
    print(f"Proposed Salary:  ₹{sentinel_output2['proposed_salary']:,}")
    print(f"Increase:         ₹{sentinel_output2['salary_increase']:,} ({sentinel_output2['increase_pct']}%)")
    print(f"Feasible:         {sentinel_output2['feasible']}")
    print(f"\nChecks:")
    for name, check in sentinel_output2["checks"].items():
        print(f"  {name:8} → {check['status']}")

    print("\n── Support Lead (E2055) ──")
    session2 = ReviewSession("E2055")
    harvester_output2 = run_harvester("E2055", session2)
    sentinel_output2  = run_sentinel(harvester_output2, session2)

    print(f"Employee:         {harvester_output2['name']}")
    print(f"Current Salary:   ₹{sentinel_output2['current_salary']:,}")
    print(f"Proposed Salary:  ₹{sentinel_output2['proposed_salary']:,}")
    print(f"Increase:         ₹{sentinel_output2['salary_increase']:,} ({sentinel_output2['increase_pct']}%)")
    print(f"Feasible:         {sentinel_output2['feasible']}")
    print(f"\nChecks:")
    for name, check in sentinel_output2["checks"].items():
        print(f"  {name:8} → {check['status']}")    