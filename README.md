# Travel Product ALM Release Readiness Studio

I built this because travel product ownership, ALM release readiness, rollout adoption, and Agile backlog governance needs more than a dashboard: it needs a decision artifact that connects source data, analysis, and next actions.

![Travel Product ALM Release Readiness Studio](docs/images/dashboard.png)

## What this project is

This project is a ops for travel product ownership, ALM release readiness, rollout adoption, and Agile backlog governance. It uses synthetic but workflow-shaped data to rank release capability-level risks and convert the output into stakeholder-ready recommendations.

## Data sources

- `entities.csv` - 36 release capability records
- `daily_metrics.csv` - 5,040 daily operating rows
- `source_events.csv` - 760 event, exception, QA, and stakeholder-request records
- `recommended_actions.csv` - 220 action candidates

## Analysis outputs

- `analysis/executive_findings.md`
- `analysis/analysis_plan.md`
- `analysis/sql_checks.sql`
- `analysis/outputs/priority_queue.csv`

## Recommendation

Use the priority queue to focus stakeholder attention on the release capability segments where performance upside, measurement risk, and operational readiness overlap.

## Run locally

```bash
python3 -m http.server 4173
```
