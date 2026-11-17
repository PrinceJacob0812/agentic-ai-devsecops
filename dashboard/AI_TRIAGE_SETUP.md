# SecureFlow AI Triage Integration

The dashboard reads AI triage events from:

`dashboard/public/data/ai-triage-events.jsonl`

The file is generated from the team's existing Groq triage module and the shared JSONL event exporter. It is intentionally not populated with invented findings.

## 1. Configure the Groq key

From the repository root, create a local `.env` file:

```env
GROQ_API_KEY=your_groq_api_key
```

Do not commit this file or paste the key into source code. Confirm that `.env` is ignored by Git before committing anything.

## 2. Generate dashboard triage data

From the repository root, run:

```bash
python scripts/run_dashboard_triage.py
```

To use a Semgrep JSON report instead:

```bash
python scripts/run_dashboard_triage.py --input path/to/semgrep.json --format semgrep
```

The script calls the existing AI triage implementation, converts its results through `src/triage_events.py`, and writes the dashboard feed. Previous output is replaced on each run to avoid duplicate rows.

## 3. Start or refresh the dashboard

```bash
cd dashboard
npm install
npm run dev
```

Open the local Vite URL and select **AI Triage**. The page loads the JSONL feed and displays classification, risk level, confidence, evidence, explanation, remediation, and review status. Use **Refresh** after generating new results.

If the feed does not exist yet, the page shows a setup message instead of a misleading “integration pending” status.

## Data note

The dashboard reads a local static JSONL file. This makes the AI triage view functional for local demonstrations, but it does not automatically fetch GitHub Actions artifacts or provide a hosted live API. Automated artifact publishing is a separate deployment/integration step.
