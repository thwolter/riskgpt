# Audience Output Matrix

The following tables describe how `prepare_presentation_output` adapts the generated content for different target audiences.

## Summary Table

| Audience  | Main Focus                                | Key Output Elements                        |
|-----------|-------------------------------------------|--------------------------------------------|
| executive | Decision making, overview                | Short summary, top risks, action options, concise chart |
| workshop  | Discussion and challenge                 | Detailed risks, scenarios, open questions  |

## Audience Output Matrix

| Audience        | Purpose/Focus                       | Output Characteristics       | Example Section                 | Required/Optional         |
|-----------------|-------------------------------------|------------------------------|---------------------------------|---------------------------|
| executive       | Decision, overview                  | Summary, key KPIs, action items | Executive summary, traffic lights | Required |
| workshop        | Discussion, challenge               | Detailed, scenarios, open questions | Risk register, open questions    | Required |
| risk_internal   | Modelling, validation               | Parameters, assumptions, model logic | Sensitivity analysis, validation | Required |
| audit           | Traceability, control               | Audit trail, controls, data lineage | Data lineage, checkpoints        | Required |
| regulator       | Compliance, method                  | Regulatory mapping, method explanation | Compliance section, framework map | Optional |
| project_owner   | Execution, schedule/cost impact     | Project-specific impact, deadlines  | Milestone table, risk actions    | Optional |
| investor        | Value, risk-return                  | Financial impact, scenario results  | Value-at-risk, scenario table    | Optional |
| operations      | Controls, implementation            | KRIs, actionable alerts, trends     | Incident log, KRI dashboard      | Optional |

Developers can extend this matrix by adding a new enum value to `AudienceEnum` and updating the helper function that formats the output.

## How-to Extend

1. Add a new value to `AudienceEnum` in `riskgpt.models.schemas`.
2. Adjust `apply_audience_formatting` in `riskgpt.workflows.prepare_presentation_output` to handle the new audience.
3. Document the expected output in this file and create a corresponding test.
