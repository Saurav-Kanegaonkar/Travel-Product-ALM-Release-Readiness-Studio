# Data Dictionary

| File | Grain | Description |
| --- | --- | --- |
| `data/entities.csv` | Product capability | Capability-level release and Product Owner readiness signals. |
| `data/backlog_items.csv` | Azure DevOps-style work item | Epics, features, stories, priorities, acceptance criteria, dependencies, and acceptance decisions. |
| `data/release_gates.csv` | Capability gate | Backlog, build, QA, package, and rollout gate evidence. |
| `data/deployment_packages.csv` | Solution package | Managed and unmanaged solution packaging, deployment risk, and rollback posture. |
| `data/adoption_plan.csv` | Cohort readiness | Training, support handoff, release note, and adoption blocker signals. |
| `data/source_events.csv` | Event | Enhancement requests, QA defects, release incidents, training questions, and ServiceNow-style changes. |
| `analysis/outputs/app_payload.json` | UI payload | Ranked and joined data consumed by the static studio. |
| `analysis/outputs/priority_queue.csv` | Product capability | Scored Product Owner decision queue. |
