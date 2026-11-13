

\# M2 Week 4 – AI Triage Handoff



\## 1. Purpose and Ownership



This document describes the M2 AI security triage output and its handoff contract for the project dashboard.



M2 is responsible for AI-assisted SAST finding triage, evaluation, and providing structured triage events. The dashboard, shared logging infrastructure, and overall end-to-end integration remain under M4 ownership.



\## 2. AI Triage Workflow



The implemented flow is:



1\. Semgrep scans application code and produces a JSON report.

2\. The Semgrep adapter converts scanner results into the normalized finding format expected by the triage agent.

3\. The agent sends finding context to the Groq-hosted language model.

4\. The agent validates the model response and writes structured triage results.

5\. The triage event exporter matches each result to its original finding and creates JSONL events using the project's common event logger.

6\. The CI workflow uploads the Semgrep report, triage results, and event JSONL as build artifacts.



The configured model in the current workflow is `openai/gpt-oss-120b`. The API key is supplied through the GitHub Actions secret `GROQ\_API\_KEY`. The key itself must never be committed.



\## 3. Triage Output Contract



Each AI triage result contains:



| Field | Description |

|---|---|

| `finding\_id` | Identifier matching the source finding |

| `classification` | `TRUE\_POSITIVE`, `FALSE\_POSITIVE`, or `INSUFFICIENT\_EVIDENCE` |

| `risk\_level` | AI-assessed risk: `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, or `INFO` |

| `confidence` | Integer confidence score from 0 to 100 |

| `evidence` | List of evidence strings supporting the assessment |

| `explanation` | Short explanation of the classification |

| `remediation` | Suggested remediation |



The agent validates the response structure and allowed classification and risk values. Invalid or failed model responses are represented as insufficient evidence with error details rather than being treated as confirmed vulnerabilities.



\## 4. Event Handoff Contract



The exporter writes one JSON object per line to:



`logs/ai-triage-events.jsonl`



It uses the common event logger and preserves the project's shared event fields:



\- `timestamp`

\- `project`

\- `pipeline\_run\_id`

\- `stage`

\- `tool`

\- `event\_type`

\- `severity`

\- `rule\_id`

\- `file`

\- `message`

\- `status`



The AI-specific fields added by M2 are:



\- `finding\_id`

\- `classification`

\- `confidence`

\- `evidence`

\- `remediation`

\- `triage\_error` when applicable



\### Field Mapping



| AI triage/source value | Event field |

|---|---|

| AI `risk\_level` | `severity` |

| Original finding `rule\_id` | `rule\_id` |

| Original finding `file` | `file` |

| AI `explanation` | `message` |

| Pipeline run identifier | `pipeline\_run\_id` |

| Constant `sast-triage` | `stage` |

| Constant `ai-triage` | `tool` |

| Constant `finding` | `event\_type` |



\### Status Mapping



| AI classification | Event status | Handling |

|---|---|---|

| `TRUE\_POSITIVE` | `OPEN` | Surface as an open finding |

| `FALSE\_POSITIVE` | `REVIEWED` | Retain for review; do not automatically suppress |

| `INSUFFICIENT\_EVIDENCE` | `REVIEWED` | Requires human review |



The exporter deliberately does not automatically close or suppress findings classified as false positives or insufficient evidence. This avoids treating an AI assessment as a replacement for human security review.



\## 5. CI Workflow and Artifacts



The triage workflow:



\- Installs Python dependencies and Semgrep.

\- Runs the M2 test suite.

\- Runs Semgrep against the application.

\- Runs AI triage using the configured Groq model.

\- Validates the triage output.

\- Exports the AI triage events to JSONL.

\- Uploads the Semgrep report, triage results, and event log as GitHub Actions artifacts.



The event artifact is named using the workflow commit SHA and is retained for 14 days.



The CI artifact provides a handoff output for downstream integration. It does not, by itself, demonstrate that the dashboard is ingesting or displaying these events.



\## 6. Prompt and Response Safeguards



The triage agent is instructed to assess the supplied finding context conservatively and distinguish confirmed issues from false positives and cases where evidence is insufficient.



The response is constrained to a structured schema. The implementation validates required fields, classification, risk level, confidence range, evidence type, and explanation/remediation fields.



A model response that cannot be validated is not treated as a confirmed vulnerability. It is represented as an insufficient-evidence result with error information.



\## 7. Limitations and Follow-up



\- The model's decision is based on the finding context supplied by the scanner and repository. Missing code context can reduce assessment quality.

\- Confidence is a model-provided score, not a statistically calibrated probability.

\- The current evaluation uses small, curated datasets and does not establish production performance.

\- The actual false-positive reduction rate has not yet been measured against a separately recorded baseline.

\- Human review remains necessary, especially for insufficient-evidence results and high-impact findings.

\- The CI workflow uploads the JSONL event artifact. Dashboard ingestion and display must be confirmed by M4 as part of the dashboard integration.



\## 8. M2 Handoff Checklist



\- \[x] AI triage result schema implemented and validated.

\- \[x] Semgrep findings adapted for the triage agent.

\- \[x] Event exporter implemented using the common event logger.

\- \[x] Event fields and status mapping documented.

\- \[x] Exporter tests added.

\- \[x] JSONL event output generated and checked locally.

\- \[x] CI workflow updated to run triage and export events.

\- \[ ] Confirm downstream dashboard ingestion and display with M4.

\- \[ ] Evaluate on larger, independently labelled real-world findings.

\- \[ ] Measure false-positive reduction against a baseline.
