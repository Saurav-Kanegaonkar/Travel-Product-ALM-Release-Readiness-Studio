import csv
import json
import math
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path
from random import Random


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUTS = ROOT / "analysis" / "outputs"
ANALYSIS = ROOT / "analysis"

RAND = Random(42)

CAPABILITIES = [
    ("REL001", "Traveler profile merge rules", "MS Dynamics", "Contact center agent", "Duplicate traveler records cause itinerary preference conflicts.", "Clean preference history before quote or booking edits.", "Reduce duplicate profile touches", "User data quality", "CRM Product"),
    ("REL002", "Advisor quote handoff", "Booking workflow", "Travel advisor", "Quote follow-ups move across email and CRM tasks without a clear owner.", "Create a single handoff state and follow-up SLA.", "Improve quote conversion follow-up", "Workflow automation", "Commercial Product"),
    ("REL003", "Guided tour rooming list changes", "Operations workflow", "Tour operations specialist", "Late rooming updates create manual rework before departure.", "Expose editable change reason and cut-off validation.", "Lower pre-departure operations rework", "Release reliability", "Tour Ops Product"),
    ("REL004", "River cruise cabin inventory exception", "Inventory platform", "Reservations agent", "Cabin inventory exceptions require escalation before a traveler can book.", "Route exceptions with evidence and approval status.", "Protect revenue on exception inventory", "Operational control", "Inventory Product"),
    ("REL005", "Managed solution release packaging", "ALM", "DevOps engineer", "Solution layers are packaged manually and rollback evidence is inconsistent.", "Standardize solution package gates with rollback notes.", "Increase deployment confidence", "ALM governance", "Platform Product"),
    ("REL006", "ServiceNow release incident triage", "ServiceNow", "Support lead", "Release incidents lack product capability linkage.", "Connect incident severity to release capability and acceptance decision.", "Shorten release incident triage", "Release reliability", "Support Product"),
    ("REL007", "Training playbook for itinerary amendments", "Adoption", "Training coordinator", "Agents receive release notes without role-based workflow examples.", "Publish role-based training and readiness checks.", "Improve rollout adoption", "Adoption readiness", "Enablement Product"),
    ("REL008", "Passenger document checklist", "Traveler self-service", "Traveler", "Travelers miss required documents when products span multiple countries.", "Show product-specific document checklist and reminder state.", "Reduce avoidable service contacts", "Customer readiness", "Digital Product"),
    ("REL009", "Supplier schedule change alerts", "Supplier integration", "Operations coordinator", "Schedule changes arrive in several formats and are hard to prioritize.", "Normalize supplier alerts into a ranked exception queue.", "Reduce schedule-change response time", "Partner operations", "Integration Product"),
    ("REL010", "Final payment reminder automation", "Payments", "Traveler services", "Final payment reminder work is manually reconciled across systems.", "Trigger reminder states from balance and due date rules.", "Lower avoidable payment escalations", "Workflow automation", "Payments Product"),
    ("REL011", "Group booking special request intake", "Group travel", "Group coordinator", "Special requests move across spreadsheets and CRM notes.", "Capture special requests with acceptance criteria and owner routing.", "Improve group booking readiness", "User-centric intake", "Groups Product"),
    ("REL012", "Release notes stakeholder digest", "Communications", "Business sponsor", "Stakeholders see release status in scattered updates.", "Generate a digest with scope, trade-offs, gates, and rollout risks.", "Improve sponsor alignment", "Stakeholder transparency", "Portfolio Product"),
    ("REL013", "Loyalty preference migration", "MS Dynamics", "Member services", "Preference migration rules need business acceptance before deployment.", "Map migration exceptions to user stories and sign-off evidence.", "De-risk CRM migration", "Data migration readiness", "CRM Product"),
    ("REL014", "Traveler feedback defect loop", "Voice of customer", "Product owner", "Post-trip feedback does not consistently create backlog items.", "Classify feedback themes and attach them to backlog refinement.", "Close feedback-to-backlog loop", "User-centric design", "Experience Product"),
    ("REL015", "Booking amendment rollback path", "ALM", "Release manager", "Amendment workflow rollback criteria are not documented per release.", "Define rollback triggers, data checkpoints, and owner approval.", "Improve rollback readiness", "ALM governance", "Platform Product"),
    ("REL016", "Destination availability rules", "Product catalog", "Product operations analyst", "Destination availability changes require manual catalog checks.", "Add rule evidence and approval state before catalog publishing.", "Reduce catalog publishing risk", "Process mapping", "Catalog Product"),
    ("REL017", "Pre-departure service case routing", "ServiceNow", "Service desk agent", "Service cases near departure need faster routing and priority rules.", "Prioritize cases by departure window, traveler impact, and product line.", "Protect pre-departure experience", "Service operations", "Support Product"),
    ("REL018", "Agile intake scoring model", "Backlog governance", "Business sponsor", "Enhancement requests arrive without consistent value or readiness signals.", "Score requests by value, dependency, rollout complexity, and evidence.", "Improve backlog prioritization", "Backlog governance", "Portfolio Product"),
]

GATES = [
    ("Backlog", "User story is refined, estimated, and mapped to acceptance criteria."),
    ("Build", "Feature branch, configuration, and test data are ready for sprint execution."),
    ("QA", "Functional, regression, and role-based test evidence is available."),
    ("Package", "Managed solution package, deployment notes, and dependencies are validated."),
    ("Rollout", "Training, support handoff, release notes, and adoption checks are ready."),
]

PERSONAS = [
    "Traveler",
    "Travel advisor",
    "Reservations agent",
    "Tour operations specialist",
    "Support lead",
    "Business sponsor",
    "Training coordinator",
    "Product owner",
]

STORY_VERBS = [
    "review release impact",
    "capture exception evidence",
    "confirm acceptance criteria",
    "route escalation",
    "publish stakeholder update",
    "validate rollback trigger",
    "prioritize enhancement request",
    "complete training readiness",
]


def clamp(value, low=0, high=100):
    return max(low, min(high, value))


def write_csv(path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def pct(value):
    return round(value, 1)


def money(value):
    return f"${value:,.0f}"


def generate_capabilities():
    rows = []
    for index, item in enumerate(CAPABILITIES, start=1):
        capability_id, name, area, user_group, problem, outcome, goal, theme, owner = item
        release_wave = f"2026.Q{2 + (index % 3)}"
        value_score = clamp(RAND.gauss(78, 10))
        user_need = clamp(RAND.gauss(74, 12))
        process_complexity = clamp(RAND.gauss(58, 18))
        dependency_risk = clamp(RAND.gauss(48, 20))
        qa_open_defects = max(0, round(RAND.gauss(5, 3)))
        story_readiness = clamp(RAND.gauss(72, 15))
        package_readiness = clamp(RAND.gauss(70, 16))
        rollout_readiness = clamp(RAND.gauss(68, 18))
        rollback_confidence = clamp(RAND.gauss(66, 17))
        adoption_risk = clamp(RAND.gauss(44, 18))
        feature_count = max(3, round(RAND.gauss(8, 3)))
        service_items = max(0, round(RAND.gauss(4, 3)))
        status = RAND.choice(["Discovery", "Refinement", "In sprint", "QA", "Release prep"])
        rows.append({
            "capability_id": capability_id,
            "capability_name": name,
            "product_area": area,
            "primary_user": user_group,
            "business_problem": problem,
            "desired_outcome": outcome,
            "product_goal": goal,
            "strategic_theme": theme,
            "product_owner_group": owner,
            "target_release": release_wave,
            "value_score": pct(value_score),
            "user_need_score": pct(user_need),
            "process_complexity_score": pct(process_complexity),
            "dependency_risk_score": pct(dependency_risk),
            "qa_open_defects": qa_open_defects,
            "story_readiness_pct": pct(story_readiness),
            "solution_package_readiness_pct": pct(package_readiness),
            "rollout_readiness_pct": pct(rollout_readiness),
            "rollback_confidence_pct": pct(rollback_confidence),
            "adoption_risk_score": pct(adoption_risk),
            "azure_devops_feature_count": feature_count,
            "servicenow_open_items": service_items,
            "current_status": status,
        })
    return rows


def generate_daily_metrics(capabilities):
    rows = []
    start = date(2026, 3, 2)
    for capability in capabilities:
        base_readiness = float(capability["story_readiness_pct"])
        base_risk = float(capability["dependency_risk_score"])
        base_adoption = 100 - float(capability["adoption_risk_score"])
        for day in range(70):
            current = start + timedelta(days=day)
            trend = day / 70
            readiness = clamp(base_readiness + trend * RAND.uniform(4, 12) + RAND.gauss(0, 4))
            risk = clamp(base_risk - trend * RAND.uniform(2, 8) + RAND.gauss(0, 5))
            adoption = clamp(base_adoption + trend * RAND.uniform(3, 9) + RAND.gauss(0, 4))
            rows.append({
                "date": current.isoformat(),
                "capability_id": capability["capability_id"],
                "story_readiness_pct": pct(readiness),
                "release_risk_score": pct(risk),
                "qa_pass_rate_pct": pct(clamp(86 - risk * 0.12 + RAND.gauss(0, 3))),
                "adoption_readiness_pct": pct(adoption),
                "stakeholder_alignment_pct": pct(clamp(76 + readiness * 0.08 - risk * 0.1 + RAND.gauss(0, 4))),
                "open_decisions": max(0, round(float(capability["dependency_risk_score"]) / 22 + RAND.gauss(0, 1))),
            })
    return rows


def generate_backlog(capabilities):
    rows = []
    story_counter = 1
    for capability in capabilities:
        story_count = max(3, int(capability["azure_devops_feature_count"]) + RAND.choice([-2, -1, 0, 1]))
        for index in range(story_count):
            persona = RAND.choice(PERSONAS)
            verb = RAND.choice(STORY_VERBS)
            priority = RAND.choice(["P0", "P1", "P1", "P2", "P2"])
            readiness = clamp(float(capability["story_readiness_pct"]) + RAND.gauss(0, 12))
            acceptance_count = max(2, round(RAND.gauss(5, 2)))
            effort = RAND.choice([2, 3, 5, 8, 13])
            state = RAND.choice(["New", "Refining", "Ready", "Committed", "In QA", "Accepted"])
            qa_status = RAND.choice(["Not started", "In progress", "Passed", "Needs rework"])
            decision = "Accept" if state == "Accepted" and qa_status == "Passed" else RAND.choice(["Clarify", "Defer", "Ready for sprint", "Needs dependency"])
            rows.append({
                "story_id": f"ADO-{story_counter:04d}",
                "capability_id": capability["capability_id"],
                "story_type": RAND.choice(["Epic", "Feature", "User Story", "User Story", "Enabler"]),
                "summary": f"As a {persona.lower()}, I need to {verb} for {capability['capability_name'].lower()}.",
                "persona": persona,
                "agile_state": state,
                "priority": priority,
                "value_score": pct(clamp(float(capability["value_score"]) + RAND.gauss(0, 8))),
                "story_readiness_pct": pct(readiness),
                "acceptance_criteria_count": acceptance_count,
                "dependency": RAND.choice(["Dynamics config", "ServiceNow mapping", "Training owner", "QA data", "Business sign-off", "None"]),
                "target_sprint": f"Sprint {12 + (story_counter % 6)}",
                "effort_points": effort,
                "qa_status": qa_status,
                "acceptance_decision": decision,
            })
            story_counter += 1
    return rows


def generate_release_gates(capabilities):
    rows = []
    base = date(2026, 5, 18)
    for capability in capabilities:
        risk = float(capability["dependency_risk_score"])
        for offset, (gate, evidence) in enumerate(GATES):
            readiness = float(capability["story_readiness_pct"])
            gate_bias = offset * 4
            score = readiness - risk * 0.25 - gate_bias + RAND.gauss(0, 9)
            status = "Pass" if score >= 68 else "Watch" if score >= 52 else "Block"
            risk_level = "High" if status == "Block" else "Medium" if status == "Watch" else "Low"
            blocker = "None" if status == "Pass" else RAND.choice([
                "Missing acceptance evidence",
                "Dependency owner not confirmed",
                "Rollback note incomplete",
                "Training sign-off pending",
                "Open ServiceNow release item",
            ])
            rows.append({
                "gate_id": f"{capability['capability_id']}-{gate.upper()}",
                "capability_id": capability["capability_id"],
                "gate_name": gate,
                "gate_status": status,
                "risk_level": risk_level,
                "owner": RAND.choice(["Product Owner", "QA Lead", "DevOps", "Training", "Support"]),
                "due_date": (base + timedelta(days=offset * 5 + RAND.randint(0, 10))).isoformat(),
                "evidence_required": evidence,
                "blocker": blocker,
            })
    return rows


def generate_deployment_packages(capabilities):
    rows = []
    for capability in capabilities:
        package_readiness = float(capability["solution_package_readiness_pct"])
        rollback = float(capability["rollback_confidence_pct"])
        deployment_risk = clamp((100 - package_readiness) * 0.45 + (100 - rollback) * 0.4 + float(capability["dependency_risk_score"]) * 0.25)
        rows.append({
            "package_id": f"PKG-{capability['capability_id']}",
            "capability_id": capability["capability_id"],
            "solution_type": RAND.choice(["Managed solution", "Managed solution", "Unmanaged configuration", "Workflow package"]),
            "environment": RAND.choice(["UAT", "Pre-prod", "Production pilot"]),
            "solution_package_readiness_pct": pct(package_readiness),
            "rollback_confidence_pct": pct(rollback),
            "deployment_risk_score": pct(deployment_risk),
            "release_window": RAND.choice(["Week 22", "Week 23", "Week 24", "Week 25"]),
            "rollback_plan": RAND.choice(["Documented", "Needs data checkpoint", "Needs owner approval", "Documented"]),
        })
    return rows


def generate_adoption(capabilities):
    rows = []
    cohorts = ["Contact center", "Travel advisors", "Operations", "Support", "Product sponsors", "Training leads"]
    for capability in capabilities:
        for cohort in RAND.sample(cohorts, 3):
            training = clamp(float(capability["rollout_readiness_pct"]) + RAND.gauss(0, 13))
            adoption = clamp(100 - float(capability["adoption_risk_score"]) + RAND.gauss(0, 12))
            rows.append({
                "adoption_id": f"ADOPT-{capability['capability_id']}-{cohort.replace(' ', '').upper()}",
                "capability_id": capability["capability_id"],
                "cohort": cohort,
                "training_readiness_pct": pct(training),
                "expected_adoption_pct": pct(adoption),
                "support_handoff_status": RAND.choice(["Ready", "Ready", "Watch", "Blocked"]),
                "release_note_status": RAND.choice(["Published", "Draft", "Needs PO review"]),
                "primary_adoption_blocker": RAND.choice(["None", "Role-based training gap", "Sponsor decision pending", "Support script missing", "Workflow change not mapped"]),
            })
    return rows


def generate_events(capabilities):
    rows = []
    for event_id in range(1, 541):
        capability = RAND.choice(capabilities)
        event_type = RAND.choice(["Enhancement request", "QA defect", "Release incident", "Training question", "Sponsor decision", "ServiceNow change"])
        severity = RAND.choice(["Low", "Medium", "Medium", "High", "Critical"])
        impact = {
            "Low": RAND.randint(1200, 5200),
            "Medium": RAND.randint(5200, 17000),
            "High": RAND.randint(17000, 42000),
            "Critical": RAND.randint(42000, 90000),
        }[severity]
        rows.append({
            "event_id": f"EVT-{event_id:04d}",
            "capability_id": capability["capability_id"],
            "event_type": event_type,
            "severity": severity,
            "estimated_impact": impact,
            "source_system": RAND.choice(["Azure DevOps", "MS Dynamics", "ServiceNow", "Training LMS", "Stakeholder intake"]),
            "current_state": RAND.choice(["Open", "Open", "In review", "Resolved", "Deferred"]),
        })
    return rows


def score_capabilities(capabilities, gates, packages, adoption, events):
    gate_groups = defaultdict(list)
    for gate in gates:
        gate_groups[gate["capability_id"]].append(gate)

    adoption_groups = defaultdict(list)
    for row in adoption:
        adoption_groups[row["capability_id"]].append(row)

    event_groups = defaultdict(list)
    for row in events:
        event_groups[row["capability_id"]].append(row)

    package_by_capability = {row["capability_id"]: row for row in packages}
    ranked = []
    for capability in capabilities:
        capability_id = capability["capability_id"]
        gate_rows = gate_groups[capability_id]
        blocked_gates = sum(1 for row in gate_rows if row["gate_status"] == "Block")
        watch_gates = sum(1 for row in gate_rows if row["gate_status"] == "Watch")
        event_impact = sum(int(row["estimated_impact"]) for row in event_groups[capability_id] if row["current_state"] != "Resolved")
        adoption_rows = adoption_groups[capability_id]
        avg_training = sum(float(row["training_readiness_pct"]) for row in adoption_rows) / len(adoption_rows)
        package = package_by_capability[capability_id]
        release_risk = (
            float(capability["dependency_risk_score"]) * 0.25
            + (100 - float(capability["story_readiness_pct"])) * 0.2
            + (100 - float(package["solution_package_readiness_pct"])) * 0.18
            + (100 - float(capability["rollback_confidence_pct"])) * 0.13
            + blocked_gates * 9
            + watch_gates * 3
            + int(capability["qa_open_defects"]) * 1.4
            + int(capability["servicenow_open_items"]) * 1.1
            + (100 - avg_training) * 0.11
        )
        delivery_value = (
            float(capability["value_score"]) * 0.33
            + float(capability["user_need_score"]) * 0.22
            + float(capability["story_readiness_pct"]) * 0.12
            + float(package["solution_package_readiness_pct"]) * 0.1
            + float(capability["rollout_readiness_pct"]) * 0.1
            + float(capability["rollback_confidence_pct"]) * 0.08
            - release_risk * 0.18
        )
        priority_score = delivery_value + release_risk * 0.55 + math.log(max(event_impact, 1), 10)
        if blocked_gates >= 2:
            decision = "Hold release until gates clear"
        elif release_risk >= 60:
            decision = "PO trade-off required"
        elif float(capability["story_readiness_pct"]) < 65:
            decision = "Refine stories before sprint"
        elif float(package["deployment_risk_score"]) > 55:
            decision = "Validate package and rollback"
        else:
            decision = "Ready for sprint review"

        ranked.append({
            **capability,
            "priority_score": pct(priority_score),
            "release_risk_score": pct(release_risk),
            "delivery_value_score": pct(delivery_value),
            "blocked_gate_count": blocked_gates,
            "watch_gate_count": watch_gates,
            "open_event_impact": event_impact,
            "avg_training_readiness_pct": pct(avg_training),
            "decision_needed": decision,
        })
    return sorted(ranked, key=lambda row: float(row["priority_score"]), reverse=True)


def build_recommended_actions(ranked):
    actions = []
    for index, row in enumerate(ranked[:12], start=1):
        if row["decision_needed"] == "Hold release until gates clear":
            action = "Block production release, assign gate owners, and reopen sprint scope only after evidence is complete."
        elif row["decision_needed"] == "PO trade-off required":
            action = "Run a sponsor trade-off review on scope, timing, and rollback posture before sprint commitment."
        elif row["decision_needed"] == "Refine stories before sprint":
            action = "Rewrite user stories with explicit acceptance criteria, test data, and business sign-off."
        elif row["decision_needed"] == "Validate package and rollback":
            action = "Complete managed solution package validation and document rollback checkpoints."
        else:
            action = "Move into sprint review with acceptance evidence and rollout owner confirmed."
        actions.append({
            "rank": index,
            "capability_id": row["capability_id"],
            "capability_name": row["capability_name"],
            "decision_needed": row["decision_needed"],
            "recommended_action": action,
            "owner": row["product_owner_group"],
            "target_release": row["target_release"],
        })
    return actions


def build_outputs():
    capabilities = generate_capabilities()
    daily = generate_daily_metrics(capabilities)
    backlog = generate_backlog(capabilities)
    gates = generate_release_gates(capabilities)
    packages = generate_deployment_packages(capabilities)
    adoption = generate_adoption(capabilities)
    events = generate_events(capabilities)
    ranked = score_capabilities(capabilities, gates, packages, adoption, events)
    actions = build_recommended_actions(ranked)

    write_csv(DATA / "entities.csv", capabilities, list(capabilities[0].keys()))
    write_csv(DATA / "daily_metrics.csv", daily, list(daily[0].keys()))
    write_csv(DATA / "backlog_items.csv", backlog, list(backlog[0].keys()))
    write_csv(DATA / "release_gates.csv", gates, list(gates[0].keys()))
    write_csv(DATA / "deployment_packages.csv", packages, list(packages[0].keys()))
    write_csv(DATA / "adoption_plan.csv", adoption, list(adoption[0].keys()))
    write_csv(DATA / "source_events.csv", events, list(events[0].keys()))
    write_csv(DATA / "recommended_actions.csv", actions, list(actions[0].keys()))

    OUTPUTS.mkdir(parents=True, exist_ok=True)
    write_csv(OUTPUTS / "priority_queue.csv", ranked, list(ranked[0].keys()))
    high_risk_gates = [row for row in gates if row["gate_status"] != "Pass"]
    write_csv(OUTPUTS / "release_gate_queue.csv", high_risk_gates, list(gates[0].keys()))
    write_csv(OUTPUTS / "backlog_readiness_queue.csv", sorted(backlog, key=lambda row: float(row["story_readiness_pct"]))[:30], list(backlog[0].keys()))
    write_csv(OUTPUTS / "adoption_readiness_queue.csv", sorted(adoption, key=lambda row: float(row["training_readiness_pct"]))[:30], list(adoption[0].keys()))

    summary = {
        "capability_count": len(capabilities),
        "backlog_item_count": len(backlog),
        "blocked_gate_count": sum(1 for row in gates if row["gate_status"] == "Block"),
        "watch_gate_count": sum(1 for row in gates if row["gate_status"] == "Watch"),
        "avg_story_readiness": pct(sum(float(row["story_readiness_pct"]) for row in capabilities) / len(capabilities)),
        "avg_package_readiness": pct(sum(float(row["solution_package_readiness_pct"]) for row in packages) / len(packages)),
        "avg_rollout_readiness": pct(sum(float(row["rollout_readiness_pct"]) for row in capabilities) / len(capabilities)),
        "total_open_event_impact": sum(row["open_event_impact"] for row in ranked),
        "top_capability": ranked[0]["capability_name"],
        "top_decision": ranked[0]["decision_needed"],
    }
    payload = {
        "summary": summary,
        "capabilities": ranked,
        "backlog": backlog,
        "gates": gates,
        "packages": packages,
        "adoption": adoption,
        "actions": actions,
    }
    (OUTPUTS / "app_payload.json").write_text(json.dumps(payload, indent=2))
    (OUTPUTS / "summary.json").write_text(json.dumps(summary, indent=2))

    write_supporting_docs(summary, ranked)
    print(f"Top capability: {summary['top_capability']}")
    print(f"Decision needed: {summary['top_decision']}")
    print(f"Backlog items: {summary['backlog_item_count']}")
    print(f"Blocked gates: {summary['blocked_gate_count']}")


def write_supporting_docs(summary, ranked):
    ANALYSIS.mkdir(exist_ok=True)
    (ANALYSIS / "analysis_plan.md").write_text(
        "# Analysis Plan\n\n"
        "1. Model the travel product release portfolio at the capability level.\n"
        "2. Score each capability across user value, story readiness, ALM package readiness, rollout readiness, rollback confidence, QA defects, and ServiceNow release signals.\n"
        "3. Convert the score into a Product Owner decision queue with explicit trade-offs.\n"
        "4. Break the queue into backlog readiness, release gates, deployment packaging, and adoption actions.\n"
        "5. Use the static studio to explain which stories are sprint-ready, which releases need a hold, and which rollout actions need owner follow-up.\n"
    )
    (ANALYSIS / "methodology.md").write_text(
        "# Methodology\n\n"
        "The project uses synthetic data because real Azure DevOps, MS Dynamics, ServiceNow, deployment, and training records for a travel platform are internal business data. "
        "The generated fields mirror common Agile and ALM structures: epics, features, user stories, acceptance criteria, release gates, managed solution packages, rollback notes, defects, support changes, and training readiness.\n\n"
        "Capability priority combines delivery value and release risk. Delivery value is based on user need, business value, story readiness, package readiness, rollout readiness, and rollback confidence. "
        "Release risk increases when dependencies, blocked gates, QA defects, ServiceNow items, incomplete training, or weak rollback evidence appear. The score is not a claim about any real company performance. "
        "It is a defensible portfolio simulation for Product Owner decision practice.\n"
    )
    top = ranked[0]
    (ANALYSIS / "executive_findings.md").write_text(
        "# Executive Findings\n\n"
        "## What I analyzed\n\n"
        f"I modeled {summary['capability_count']} travel product capabilities, {summary['backlog_item_count']} Azure DevOps-style backlog items, release gates, solution package readiness, adoption plans, and support events.\n\n"
        "## Findings\n\n"
        f"- The highest-priority capability is **{top['capability_name']}** with a priority score of **{top['priority_score']}**.\n"
        f"- The portfolio has **{summary['blocked_gate_count']}** blocked release gates and **{summary['watch_gate_count']}** gates on watch.\n"
        f"- Average story readiness is **{summary['avg_story_readiness']}%**, while average package readiness is **{summary['avg_package_readiness']}%**.\n"
        f"- Open or in-review events represent **{money(summary['total_open_event_impact'])}** of modeled operational impact.\n\n"
        "## Recommendation\n\n"
        "Use the Product Owner decision queue to force clear sponsor conversations on scope, readiness, rollback, and adoption before release commitment.\n"
    )
    (ANALYSIS / "sql_checks.sql").write_text(
        "-- Portfolio SQL checks for a travel product ALM and release readiness studio.\n\n"
        "-- 1. Capabilities with blocked release gates.\n"
        "SELECT capability_id, gate_name, blocker\n"
        "FROM release_gates\n"
        "WHERE gate_status = 'Block'\n"
        "ORDER BY due_date;\n\n"
        "-- 2. Stories that should not enter sprint commitment.\n"
        "SELECT story_id, capability_id, summary, story_readiness_pct, dependency\n"
        "FROM backlog_items\n"
        "WHERE story_readiness_pct < 65 OR acceptance_decision IN ('Clarify', 'Needs dependency')\n"
        "ORDER BY story_readiness_pct ASC;\n\n"
        "-- 3. Release packages that need rollback review.\n"
        "SELECT package_id, capability_id, deployment_risk_score, rollback_plan\n"
        "FROM deployment_packages\n"
        "WHERE deployment_risk_score > 55 OR rollback_plan <> 'Documented'\n"
        "ORDER BY deployment_risk_score DESC;\n\n"
        "-- 4. Adoption cohorts with training risk.\n"
        "SELECT adoption_id, capability_id, cohort, training_readiness_pct, primary_adoption_blocker\n"
        "FROM adoption_plan\n"
        "WHERE training_readiness_pct < 70\n"
        "ORDER BY training_readiness_pct ASC;\n"
    )
    (ROOT / "data_dictionary.md").write_text(
        "# Data Dictionary\n\n"
        "| File | Grain | Description |\n"
        "| --- | --- | --- |\n"
        "| `data/entities.csv` | Product capability | Capability-level release and Product Owner readiness signals. |\n"
        "| `data/backlog_items.csv` | Azure DevOps-style work item | Epics, features, stories, priorities, acceptance criteria, dependencies, and acceptance decisions. |\n"
        "| `data/release_gates.csv` | Capability gate | Backlog, build, QA, package, and rollout gate evidence. |\n"
        "| `data/deployment_packages.csv` | Solution package | Managed and unmanaged solution packaging, deployment risk, and rollback posture. |\n"
        "| `data/adoption_plan.csv` | Cohort readiness | Training, support handoff, release note, and adoption blocker signals. |\n"
        "| `data/source_events.csv` | Event | Enhancement requests, QA defects, release incidents, training questions, and ServiceNow-style changes. |\n"
        "| `analysis/outputs/app_payload.json` | UI payload | Ranked and joined data consumed by the static studio. |\n"
        "| `analysis/outputs/priority_queue.csv` | Product capability | Scored Product Owner decision queue. |\n"
    )
    (DATA / "README.md").write_text(
        "# Synthetic Data Notes\n\n"
        "The data in this folder is synthetic. It is modeled on common Agile product ownership and ALM records that a travel platform team would use: Azure DevOps work items, MS Dynamics configuration releases, ServiceNow change and incident records, managed solution packages, training plans, and stakeholder enhancement requests.\n\n"
        "The generator uses a fixed random seed so the project is reproducible. Capability records receive business value, user need, process complexity, dependency risk, QA defects, story readiness, package readiness, rollout readiness, rollback confidence, and adoption risk. Backlog items are assigned personas, priorities, acceptance criteria counts, dependencies, sprints, QA states, and Product Owner decisions. Release gates and adoption rows are then derived from those readiness signals.\n\n"
        "These records do not represent any real company performance or private system extract.\n"
    )
    (ROOT / "STATUS.md").write_text(
        "# Status\n\n"
        "- Project: Travel Product ALM Release Readiness Studio\n"
        "- Status: upgraded through the Portfolio Artifact Upgrade Workflow.\n"
        "- Surfaces: Release Command Center, Backlog and Acceptance Lab, Deployment and Adoption Board.\n"
    )


if __name__ == "__main__":
    build_outputs()
