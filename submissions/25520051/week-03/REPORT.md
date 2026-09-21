# Week 03 — Contract Net with LLM Contractors

## 1. Setup

- **Provider / model / temperature:** `TODO` — fill in once a real run has been made
  (this repo defaults to the OpenRouter free model documented in the week-03 README:
  `nvidia/nemotron-3.5-lightning:free`, temperature `0.7`, set via `AGENT_MODEL` /
  `AGENT_TEMPERATURE`). Anthropic is used instead if `ANTHROPIC_API_KEY` is set.
- **Contractors:** three fixed identities, `coder`, `writer`, `analyst`, defined in
  [`contract_net.py`](./contract_net.py). Their system prompts change per condition;
  their names and the `gold` labels in [`tasks.json`](./tasks.json) never do.
- **Conditions:**
  - `baseline` — each contractor's system prompt matches one distinct skill.
  - `homogeneous` — all three contractors get the same generalist system prompt.
  - `overconfident` — baseline, but the `writer` contractor's prompt is appended with
    an instruction to always bid `true` with confidence ≥ 0.9, regardless of fit.
- **Protocol:** the manager sends one announcement (one LLM call) per contractor per
  task, asking for a JSON bid `{"bid": bool, "confidence": float, "reason": str}`. An
  unparseable reply is treated as a non-bid, per the README's guidance on free models
  that answer with reasoning instead of JSON. The manager awards each task to the
  highest-confidence `bid=true` contractor; a task with no `bid=true` contractor is
  left unassigned.
- **How to run:**
  ```bash
  export OPENAI_BASE_URL=https://openrouter.ai/api/v1
  export OPENAI_API_KEY=<your openrouter key>
  export AGENT_MODEL=nvidia/nemotron-3.5-lightning:free
  cd submissions/25520051/week-03
  python run_experiment.py --runs 3
  python ../../../scripts/check_week03.py ..
  ```
  (`check_week03.py` is invoked with the parent `week-03` directory as its argument;
  adjust the relative path to `scripts/` for wherever you run it from.)

## 2. Results

`TODO` — paste the table from `results.csv` here after a real run. No run has been
made in this environment yet because no API key (`OPENAI_API_KEY` / `ANTHROPIC_API_KEY`)
is present; see the note at the bottom of this report.

| run | condition | tasks | correct | messages | unassigned | misawards | note |
|---|---|---|---|---|---|---|---|
| — | — | — | — | — | — | — | pending a real run |

## 3. Smith (1980) vs. this reproduction

| Dimension | Smith 1980 (distributed sensing) | This reproduction |
|---|---|---|
| Nodes | Fixed-function sensor/processing nodes on a network, each with hard-coded capabilities | Three LLM contractors (`coder`, `writer`, `analyst`), capability defined only by a system prompt |
| How a bid is produced | A deterministic rule evaluates the node's local workload and known capability against the task's requirements | The contractor LLM reads the task description and free-form judges fit, emitting a JSON confidence score |
| What guarantees bid honesty | The bidding rule is fixed code the node cannot deviate from; dishonesty is not representable | Nothing — the system prompt is the only constraint, and a prompt (accidentally or deliberately) telling a contractor to always bid high produces dishonest bids with no protocol-level defense |
| What allocation quality means | The manager awards to the node whose rule-computed capability best matches the task; correctness follows from the rule being correct | Allocation quality is measured against a task's known `gold` contractor; correctness now depends on whether the LLM's self-assessment happens to track the gold label |
| What negotiation costs | Fixed message count: one announcement, one bid, one award per contractor per task — cheap, synchronous | Same message shape, but each message is an LLM call: costs tokens and wall-clock time, and a call can fail to parse, which the original protocol has no analogue for |
| Failure modes | Node overload, message loss, stale bids | Overconfident/dishonest bidding sweeping awards away from the gold contractor; unparseable replies counted as silent non-bids; homogeneous contractors making allocation quality collapse toward chance |

## 4. Interpretation

`TODO` — one paragraph once real runs exist, citing specific `logs/*.txt` lines as
evidence for which condition moved which metric and why (e.g., which contractor's
bids swept awards in `overconfident`, or how often replies were unparseable).

---

**Status note (2026-09-21):** the contract net, the task set, and the experiment
runner are implemented and were validated with a mocked model call (bid parsing,
message counting, award logic, and per-condition metrics all behave as expected: in
a mocked baseline every task went to its gold contractor; in a mocked homogeneous run
no contractor matched confidently; in a mocked overconfident run the `writer`
contractor won several non-gold tasks). No `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` is
set in this environment, so no real run has been made yet, and `results.csv` and
`logs/` are not yet populated. Set one of those keys (see "How to run" above) and run
`python run_experiment.py --runs 3`, then fill in sections 2 and 4 above from the
real output before submitting.
