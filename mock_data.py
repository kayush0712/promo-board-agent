
EMPLOYEES = {

    "E1042": {
        "name":           "Rahul Sharma",
        "role_title":     "Software Engineer", #how harvestor decide which metrics matter most
        "current_level":  "SDE-2",
        "target_level":   "SDE-3",
        "department":     "Engineering",
        "tenure_years":   2.5,
        "current_salary": 1200000,
        "manager":        "Priya Mehta",
        "last_rating":    "Exceeds Expectations",

        "github": {
            "commits_12m":        847,
            "pr_merge_rate":      94,
            "code_reviews_given": 134,
            "repos_contributed":  6
        },
        "jira": {
            "tickets_closed":        312,
            "story_points":          489,
            "p1_incidents_resolved":  8,
            "avg_resolution_hours":   4.2,
            "team_velocity":          None,
            "on_time_delivery_rate":  None
        },
        "slack": {
            "peer_shoutouts":            14,
            "mentorship_sessions":       47,
            "cross_team_collaborations":  9
        },
        "zendesk": {
            "tickets_closed":       892,
            "avg_resolution_hours":  2.1,
            "csat_score":           4.8
        },
        "hrms": {
            "attrition_rate": None,
            "nps_score":      None
        }
    },

    "E2055": {
        "name":           "Priya Patel",
        "role_title":     "Engineering Manager",
        "current_level":  "EM-1",
        "target_level":   "EM-2",
        "department":     "Engineering",
        "tenure_years":   3.5,
        "current_salary": 2200000,
        "manager":        "CTO",
        "last_rating":    "Exceeds Expectations",

        "github": {
            "commits_12m":        847,
            "pr_merge_rate":      94,
            "code_reviews_given": 134,
            "repos_contributed":  6
        },

        "jira": {
            "tickets_closed":        None,
            "story_points":          None,
            "p1_incidents_resolved":  None,
            "avg_resolution_hours":   None,
            "team_velocity":          87,
            "on_time_delivery_rate":  91
        },
        "slack": {
            "peer_shoutouts":            22,
            "mentorship_sessions":       89,
            "cross_team_collaborations": 31
        },
        "zendesk": {
            "tickets_closed":       892,
            "avg_resolution_hours":  2.1,
            "csat_score":           4.8
        },
        "hrms": {
            "attrition_rate": 4.2,
            "nps_score":      None
        }
    },

    "E3088": {
        "name":           "Neha Joshi",
        "role_title":     "Customer Support Lead",
        "current_level":  "L2",
        "target_level":   "L3",
        "department":     "Customer Success",
        "tenure_years":   1.8,
        "current_salary": 700000,
        "manager":        "Amit Shah",
        "last_rating":    "Exceeds Expectations",

        "github": None,
        "jira": {
            "tickets_closed":        None,
            "story_points":          None,
            "p1_incidents_resolved":  None,
            "avg_resolution_hours":   None,
            "team_velocity":          None,
            "on_time_delivery_rate":  None
        },
        "slack": {
            "peer_shoutouts":            18,
            "mentorship_sessions":       32,
            "cross_team_collaborations":  7
        },
        "zendesk": {
            "tickets_closed":       892,
            "avg_resolution_hours":  2.1,
            "csat_score":           4.8
        },
        "hrms": {
            "attrition_rate": None,
            "nps_score":      72
        }
    },
    # Add these to EMPLOYEES in mock_data.py

    "E4021": {
        "name":           "Arjun Mehta",
        "role_title":     "Data Scientist",
        "current_level":  "DS-2",
        "target_level":   "DS-3",
        "department":     "Analytics",
        "tenure_years":   3.2,
        "current_salary": 1400000,
        "manager":        "Sunita Rao",
        "last_rating":    "Exceeds Expectations",

        # Strong technical data — should get RECOMMEND
        "github": {
            "commits_12m":        423,
            "pr_merge_rate":      89,
            "code_reviews_given": 67,
            "repos_contributed":  4
        },
        "jira": {
            "tickets_closed":        198,
            "story_points":          312,
            "p1_incidents_resolved":  3,
            "avg_resolution_hours":   6.1,
            "team_velocity":          None,
            "on_time_delivery_rate":  None
        },
        "slack": {
            "peer_shoutouts":            19,
            "mentorship_sessions":       38,
            "cross_team_collaborations": 14
        },
        "zendesk": None,
        "hrms": {
            "attrition_rate": None,
            "nps_score":      81
        }
    },

    "E5033": {
        "name":           "Vikram Singh",
        "role_title":     "DevOps Engineer",
        "current_level":  "DE-1",
        "target_level":   "DE-2",
        "department":     "Infrastructure",
        "tenure_years":   0.9,    # ← very short tenure — edge case
        "current_salary": 900000,
        "manager":        "Rahul Khanna",
        "last_rating":    "Meets Expectations",

        # Weak data — should get HOLD
        "github": {
            "commits_12m":        124,
            "pr_merge_rate":      71,    # ← low merge rate
            "code_reviews_given": 12,    # ← very low
            "repos_contributed":  2
        },
        "jira": {
            "tickets_closed":        67,
            "story_points":          98,
            "p1_incidents_resolved":  1,
            "avg_resolution_hours":  11.4,   # ← slow resolution
            "team_velocity":          None,
            "on_time_delivery_rate":  None
        },
        "slack": {
            "peer_shoutouts":             3,   # ← very low
            "mentorship_sessions":        2,
            "cross_team_collaborations":  1
        },
        "zendesk": None,
        "hrms": {
            "attrition_rate": None,
            "nps_score":      None
        }
    },

    "E6044": {
        "name":           "Ananya Krishnan",
        "role_title":     "Product Manager",
        "current_level":  "PM-2",
        "target_level":   "PM-3",
        "department":     "Product",
        "tenure_years":   2.1,
        "current_salary": 1800000,
        "manager":        "CEO",
        "last_rating":    "Exceeds Expectations",

        # No GitHub — PM role — tests role awareness
        "github": None,
        "jira": {
            "tickets_closed":        None,
            "story_points":          None,
            "p1_incidents_resolved":  None,
            "avg_resolution_hours":   None,
            "team_velocity":          92,       # her team's velocity
            "on_time_delivery_rate":  88
        },
        "slack": {
            "peer_shoutouts":            27,
            "mentorship_sessions":       21,
            "cross_team_collaborations": 44    # ← very high — PM talks to everyone
        },
        "zendesk": None,
        "hrms": {
            "attrition_rate": None,
            "nps_score":      74
        }
    },

    "E7001": {
        "name":           "Rohan Verma",
        "role_title":     "Software Engineer",
        "current_level":  "SDE-2",
        "target_level":   "SDE-3",
        "department":     "Engineering",
        "tenure_years":   3.1,
        "current_salary": 1300000,
        "manager":        "Amit Shah",
        "last_rating":    "Outstanding",

        # Very strong numbers across everything
        "github": {
            "commits_12m":        1240,    # very high
            "pr_merge_rate":      97,      # near perfect
            "code_reviews_given": 210,     # mentoring others heavily
            "repos_contributed":  9        # wide impact
        },
        "jira": {
            "tickets_closed":        487,  # very high
            "story_points":          720,  # exceptional delivery
            "p1_incidents_resolved":  14,  # critical problem solver
            "avg_resolution_hours":   2.8, # very fast
            "team_velocity":          None,
            "on_time_delivery_rate":  None
        },
        "slack": {
            "peer_shoutouts":            31,   # widely recognized
            "mentorship_sessions":       89,   # actively mentoring
            "cross_team_collaborations": 22    # broad impact
        },
        "zendesk": None,
        "hrms": {
            "attrition_rate": None,
            "nps_score":      None
        },

        # Rich achievement data — Evaluator won't need to loop
        "achievements": [
            "Led architecture of payments microservice handling 2M transactions/day",
            "Mentored 4 junior engineers — 2 promoted to SDE-2 under his guidance",
            "Reduced API latency by 42% through query optimization initiative",
            "On-call lead for 6 P1 incidents — avg resolution 2.1hrs vs team 5.4hrs",
            "Authored 3 internal design docs — all approved by principal engineer"
        ],
        "system_designs": [
            "Payments microservice architecture — reviewed by CTO",
            "Internal notification system redesign — serving 100k users",
            "GraphQL federation proposal — adopted company-wide"
        ]
    },

    "E7002": {
        "name":           "Sneha Gupta",
        "role_title":     "Software Engineer",
        "current_level":  "SDE-2",
        "target_level":   "SDE-3",
        "department":     "Engineering",
        "tenure_years":   1.1,            # very short — barely 1 year
        "current_salary": 1100000,
        "manager":        "Priya Mehta",
        "last_rating":    "Meets Expectations",   # not exceeding

        # Weak numbers
        "github": {
            "commits_12m":        187,    # low
            "pr_merge_rate":      74,     # below average
            "code_reviews_given": 18,     # very low — not mentoring
            "repos_contributed":  2       # limited scope
        },
        "jira": {
            "tickets_closed":        98,  # low
            "story_points":          142, # below average
            "p1_incidents_resolved":  1,  # minimal critical work
            "avg_resolution_hours":  9.7, # slow
            "team_velocity":          None,
            "on_time_delivery_rate":  None
        },
        "slack": {
            "peer_shoutouts":             4,   # barely recognized
            "mentorship_sessions":        3,   # almost no mentoring
            "cross_team_collaborations":  2    # very limited
        },
        "zendesk": None,
        "hrms": {
            "attrition_rate": None,
            "nps_score":      None
        },

        # Minimal achievements — evaluator will find gaps
        "achievements": [
            "Completed assigned tickets on time",
            "Participated in team code reviews"
        ],
        "system_designs": []    # no architecture work at all
    }
}


COMPETENCY_MATRIX = {
    "SDE-3": {
        "technical":  "Architects medium-scale systems independently. Reviews others' designs.",
        "leadership": "Mentors 2+ junior engineers actively. Runs team rituals.",
        "delivery":   "Delivers complex multi-sprint features with minimal guidance.",
        "impact":     "Work measurably improves team KPIs or product metrics."
    },
    "EM-2": {
        "technical":  "Sets technical direction for the team. Drives architecture decisions.",
        "leadership": "Grows engineers around them. Manages team health and attrition.",
        "delivery":   "Owns team delivery end to end across multiple quarters.",
        "impact":     "Team output drives company-level outcomes."
    },
    "L3": {
        "technical":  "Handles complex customer escalations independently.",
        "leadership": "Mentors junior support staff. Improves team processes.",
        "delivery":   "Maintains high CSAT while handling high ticket volume.",
        "impact":     "Measurably improves customer retention and satisfaction."
    },
    "DS-3": {
    "technical":  "Independently designs and deploys ML models to production. Sets data standards.",
    "leadership": "Mentors junior data scientists. Drives data strategy for product teams.",
    "delivery":   "Delivers end-to-end ML projects with measurable business impact.",
    "impact":     "Models directly improve key product metrics or revenue."
    },

    "DE-2": {
        "technical":  "Manages CI/CD pipelines independently. Handles on-call incidents.",
        "leadership": "Documents infrastructure decisions. Reviews others' deployment configs.",
        "delivery":   "Delivers infrastructure improvements with minimal guidance.",
        "impact":     "Work improves system reliability or deployment speed."
    },

    "PM-3": {
        "technical":  "Defines product roadmap independently. Makes data-driven decisions.",
        "leadership": "Aligns cross-functional teams. Mentors junior PMs.",
        "delivery":   "Ships features on time with clear success metrics.",
        "impact":     "Products directly drive company revenue or retention goals."
    }
}


BUDGET = {
    "Engineering": {
        "remaining_budget": 800000,
        "salary_bands": {
            "SDE-3": {"min": 1300000, "max": 1900000},
            "EM-2":  {"min": 2800000, "max": 4000000}
        },
        "avg_salary": {
            "SDE-3": 1520000,
            "EM-2":  3200000
        },
        "open_slots": {
            "SDE-3": 4,
            "EM-2":  1
        }
    },
    "Customer Success": {
        "remaining_budget": 300000,
        "salary_bands": {
            "L3": {"min": 900000, "max": 1400000}
        },
        "avg_salary": {
            "L3": 1050000
        },
        "open_slots": {
            "L3": 1
        }
    },
    "Analytics": {
    "remaining_budget": 600000,
    "salary_bands": {
        "DS-3": {"min": 1600000, "max": 2400000}
    },
    "avg_salary": {
        "DS-3": 1900000
    },
    "open_slots": {
        "DS-3": 1
    }
    },

    "Infrastructure": {
        "remaining_budget": 200000,   # ← tight budget — edge case
        "salary_bands": {
            "DE-2": {"min": 1100000, "max": 1600000}
        },
        "avg_salary": {
            "DE-2": 1250000
        },
        "open_slots": {
            "DE-2": 1
        }
    },

    "Product": {
        "remaining_budget": 1200000,
        "salary_bands": {
            "PM-3": {"min": 2000000, "max": 3200000}
        },
        "avg_salary": {
            "PM-3": 2500000
        },
        "open_slots": {
            "PM-3": 2
        }
    }

}


def get_employee(employee_id: str) -> dict:
    if employee_id not in EMPLOYEES:
        raise ValueError(f"Employee {employee_id} not found")
    return EMPLOYEES[employee_id]


def get_competency(level: str) -> dict:
    if level not in COMPETENCY_MATRIX:
        raise ValueError(f"Level {level} not in competency matrix")
    return COMPETENCY_MATRIX[level]


def get_budget(department: str) -> dict:
    if department not in BUDGET:
        raise ValueError(f"Department {department} not found")
    return BUDGET[department]


if __name__ == "__main__":

    print("Test 1: Software Engineer")
    emp = get_employee("E1042")
    print(f"Name: {emp['name']} | Role: {emp['role_title']}")
    print(f"Level: {emp['current_level']} → {emp['target_level']}")

    print("\nTest 2: Engineering Manager")
    emp = get_employee("E2055")
    print(f"Name: {emp['name']} | Role: {emp['role_title']}")
    print(f"Level: {emp['current_level']} → {emp['target_level']}")

    print("\nTest 3: Support Lead")
    emp = get_employee("E3088")
    print(f"Name: {emp['name']} | Role: {emp['role_title']}")
    print(f"Level: {emp['current_level']} → {emp['target_level']}")

    print("\nTest 4: Competency Matrix")
    comp = get_competency("SDE-3")
    print(f"SDE-3 Leadership bar: {comp['leadership']}")

    print("\nTest 5: Budget")
    budget = get_budget("Engineering")
    band = budget["salary_bands"]["SDE-3"]
    print(f"SDE-3 band: ₹{band['min']:,} → ₹{band['max']:,}")
    print(f"Remaining budget: ₹{budget['remaining_budget']:,}")

    print("\nTest 6: Invalid Employee")
    try:
        get_employee("E9999")
    except ValueError as e:
        print(f"Error caught correctly: {e}")