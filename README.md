# Niyantran — Cost, Capacity & SLO-Driven Operations

*Lloyds Financial (training scenario). Modules 6 (Cost, Latency and
Capacity) and 7 (SLOs, Alerting and Incident Response), built on top of
the fully-observable end state of the Anvesh sequence — tracing, metrics,
online evaluation, drift detection, base alerting and human feedback are
all already working here, exactly as Modules 2-5 leave them.*

## What this is

The same fraud/AML transaction-pattern investigation agent (tool loop +
SAR-drafting sub-agent), now with:

**Module 6 — Cost, Latency and Capacity**
- `src/core/cost_attribution.py` — cost rolled up by team, feature, and
  user, not just an aggregate total.
- `src/core/caching.py` — Redis-backed response caching with normalized
  cache keys (falls back to an in-process cache if Redis isn't reachable).
- `src/core/routing.py` — model tiering: simple tool-loop turns go to
  `gpt-4o-mini`, the SAR sub-agent and high-complexity cases go to
  `gpt-4o`. Stands in for a LiteLLM Router config — same decision, fully
  visible logic.
- `src/core/cost_anomaly.py` — baseline-vs-rolling-mean spike detection,
  catching "the runaway loop that only shows up on the invoice."
- Latency decomposition doesn't need a new file — it's already what the
  span hierarchy from Module 2 gives you; see the flow document for how
  to read it.

**Module 7 — SLOs, Alerting and Incident Response**
- `src/core/slo.py` — three SLOs (`answer_quality`, `cost_stability`,
  `narrative_integrity`), each backed by a signal an earlier module
  already measures, with rolling-window error-budget calculation.
- `src/core/incident_response.py` — severity classification (SEV1-3),
  alert-fatigue dedup, and a blameless-postmortem template generator.
- `alert_rules.yml` + `alertmanager.yml` — quality-based Prometheus
  alerting (cost burn rate, cache hit rate, eval score, drift, SLO breach)
  with sustained-duration conditions and tiered repeat intervals, not
  availability-only alerting.
- `docs/runbook.md` — the on-call runbook, one playbook per alert.

## Setup

1. `cp .env.example .env` and fill in `OPENAI_API_KEY`.
2. `python -m venv .venv && source .venv/bin/activate`
3. `pip install -r requirements.txt`
4. Run the deterministic tests (no API key needed):
   `pytest tests/unit -v`
5. **Terminal 1:** `docker compose up` — Jaeger, OTel Collector,
   Prometheus, Alertmanager, Grafana, Redis.
6. **Terminal 2:** `uvicorn app:app --reload --port 8000`
7. **Terminal 3:** `python agent.py` — runs 12 investigations for the same
   customer, then prints cost attribution, SLO status, and any alerts
   fired.
8. Open Jaeger (`:16686`), Prometheus (`:9090`), Alertmanager (`:9093`),
   and Grafana (`:3000`, the "Niyantran — Cost, Capacity & SLOs" dashboard
   is auto-provisioned).

## Where to go next

Open the companion flow document and architecture diagram for how every
M6/M7 module wires into the pipeline, the observation questions document
for a guided tour of the running system, and the unguided assignment
outline for independent practice.

## File map

| Path | Module |
|---|---|
| `src/core/cost_attribution.py`, `caching.py`, `routing.py`, `cost_anomaly.py` | M6 |
| `src/core/slo.py`, `incident_response.py`, `alert_rules.yml`, `alertmanager.yml`, `docs/runbook.md` | M7 |
| `src/core/otel_setup.py`, `metrics.py`, `online_eval.py`, `drift.py`, `alerting.py`, `feedback.py` | Inherited (M2-M5), already working |
| `src/core/llm_provider.py`, `agent_loop.py`, `sub_agent.py` | Pipeline wiring all of the above together |
| `src/tools/investigation_tools.py`, `src/data/mock_store.py` | Domain (unchanged from Anvesh) |
