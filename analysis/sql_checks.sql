-- Portfolio SQL checks for a travel product ALM and release readiness studio.

-- 1. Capabilities with blocked release gates.
SELECT capability_id, gate_name, blocker
FROM release_gates
WHERE gate_status = 'Block'
ORDER BY due_date;

-- 2. Stories that should not enter sprint commitment.
SELECT story_id, capability_id, summary, story_readiness_pct, dependency
FROM backlog_items
WHERE story_readiness_pct < 65 OR acceptance_decision IN ('Clarify', 'Needs dependency')
ORDER BY story_readiness_pct ASC;

-- 3. Release packages that need rollback review.
SELECT package_id, capability_id, deployment_risk_score, rollback_plan
FROM deployment_packages
WHERE deployment_risk_score > 55 OR rollback_plan <> 'Documented'
ORDER BY deployment_risk_score DESC;

-- 4. Adoption cohorts with training risk.
SELECT adoption_id, capability_id, cohort, training_readiness_pct, primary_adoption_blocker
FROM adoption_plan
WHERE training_readiness_pct < 70
ORDER BY training_readiness_pct ASC;
