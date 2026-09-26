# OES-32 Engine

Profile A sidecar to [oes32-residual](https://github.com/sparkainlp-x/oes32-residual): a deterministic Python telemetry-triage harness (residual latch, EVEN/ODD symmetry, FOLD8 continuity) for 32-element vectors.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://github.com/sparkainlp-x/oes32_engine/actions/workflows/ci.yml/badge.svg)](https://github.com/sparkainlp-x/oes32_engine/actions/workflows/ci.yml)
[![Status: research prototype](https://img.shields.io/badge/status-research%20prototype-orange.svg)](#what-it-is-not)
[![ADR-001: Profile A sidecar](https://img.shields.io/badge/ADR--001-Profile%20A%20sidecar-blue.svg)](#relationship-to-adr-001)

**Author:** Jean-François Brisson · **Organization:** Spark AI NLP

## What it is

- A small, standard-library-only Python module, [`oes32_engine.py`](oes32_engine.py), that evaluates a proposed 32-element state vector against a reference and returns a deterministic `SAFE` / `LATCH` containment decision plus all residuals.
- A **software specification and test harness**: [OES32_Technical_Specification.md](OES32_Technical_Specification.md) ([PDF](OES32_Technical_Specification.pdf)) documents the data contracts, equations, threshold semantics, validation rules, and traceability.

## What it is NOT

- **Not** certified control software, and not a certification artifact. It must not be connected directly to safety-critical hardware without independent verification, validation, and engineering review.
- **Not** a qubit gate, QPU status, or quantum-hardware result. `SAFE`/`LATCH` is a containment decision on numbers you supply.
- **Not** hardware, field, or medical software.
- **Not** the normative OES-32 residual. That is [oes32-residual@b77b612](https://github.com/sparkainlp-x/oes32-residual/tree/b77b61254f15778c6ae221843dceac7a8571158e) (ADR-001).

## Symbolic specification

Let \(W=32\), \(i\in\{0,\ldots,31\}\), \(\mu(i)=(i+16)\bmod 32\), and let \(x,x_{ref}\in\mathbb{R}^{32}\).

1. **Residual coherence:**
   \[
   R(x,x_{ref})=\max_{0\le i<W}|x_i-x_{ref,i}|.
   \]

2. **Circuit-breaker latch:** for coherence floor \(\tau=0.08\),
   \[
   L=\mathbf{1}[R>\tau],\qquad A=\mathbf{1}[R\le\tau].
   \]
   Equality at the floor is accepted; only a strict exceedance latches.

3. **EVEN/ODD sector symmetry:** using the explicit reference convention
   \(q_i=+1\) for even \(i\), \(q_i=-1\) for odd \(i\),
   \[
   S_p=\max_{i\equiv p\ (2)}|x_i-q_i x_{\mu(i)}|,
   \qquad C_p=\mathbf{1}[S_p\le\tau_{sym}],\quad p\in\{0,1\}.
   \]
   The sign convention is configurable in code because the original prompt did not specify whether odd sectors should be equal or antisymmetric.

4. **FOLD8 ring continuity:** for ring \(s\in\{0,1,2,3\}\), node \(k\in\{0,\ldots,7\}\), and flattened index \(j=8s+k\),
   \[
   F=\max_{s,k}|x_{8s+k}-x_{8s+(k+1)\bmod 8}|,
   \qquad C_{fold}=\mathbf{1}[F\le\tau_{fold}].
   \]

The aggregate containment decision is
\[
\mathrm{SAFE}=A\land C_0\land C_1\land C_{fold},\qquad
\mathrm{LATCH}=\neg\mathrm{SAFE}.
\]

## Quickstart

Requires Python 3.8+; standard library only.

```bash
git clone https://github.com/sparkainlp-x/oes32_engine.git
cd oes32_engine
python3 -c "from oes32_engine import evaluate; r = evaluate([0.0] * 32, [0.0] * 32); print(r); assert r.safe"
```

Expected output:

```text
Evaluation(residual=0.0, latch=False, even_symmetry_residual=0.0, odd_symmetry_residual=0.0, fold8_residual=0.0, safe=True)
```

In Python:

```python
from oes32_engine import evaluate

result = evaluate([0.0] * 32, [0.0] * 32)          # default tau = 0.08
assert result.safe and not result.latch
```

## Tests

Seven unit tests cover zero-state acceptance, max-absolute residual selection, threshold equality (accepted) vs. strict exceedance (latches), FOLD8 wraparound, the EVEN/ODD symmetry convention, and invalid-width rejection.

```bash
python3 -m unittest discover -v      # standard library only
# or
python3 -m pip install pytest && python3 -m pytest -q
```

CI ([`ci.yml`](.github/workflows/ci.yml)) runs `pytest` on Python 3.11 and 3.12 for every push and pull request to `main`.

## Evidence tags

| Item | Tag |
|---|---|
| Unit-test inputs | **SYNTHETIC** (hand-written vectors) |
| Default thresholds (τ = 0.08; τ_sym, τ_fold default to τ) | Design parameters of this Profile A sidecar; not derived from measured data |
| Timing, hardware, or field behaviour | Not claimed (**UNRUN**) |

Tag definitions: [sparkainlp-x/.github](https://github.com/sparkainlp-x/.github#evidence-tags).

## Relationship to ADR-001

The normative residual aggregate **R** is defined by [`oes32-residual`](https://github.com/sparkainlp-x/oes32-residual) (pin `b77b61254f15778c6ae221843dceac7a8571158e` until superseded): the maximum absolute component residual on length-32 vectors, fail-closed on invalid input. This engine computes the same R and adds **Profile A sidecar** checks. The sidecar thresholds and the FOLD8/symmetry definitions are not normative.

| Check | Role | Default threshold (sidecar) |
|---|---|---|
| Residual coherence R | Normative R (matches oes32-residual) | caller / documented τ |
| Coherence latch | Sidecar | τ_coherence = 0.08, strict `>` latches (same fail rule as the normative contract) |
| EVEN/ODD symmetry | Sidecar | τ_sym (defaults to τ) |
| FOLD8 ring continuity | Sidecar | τ_fold (defaults to τ) |

Cross-repo definition table: [docs/ADR-001-oes32-tau-unification.md](docs/ADR-001-oes32-tau-unification.md). The OES-512 weighted latch (S = 0.45·Peak + 0.35·RMS + 0.20·MeanAbs, τ = 0.50) is a **TARGET** and is not implemented here.

## Citation

Citation metadata is in [CITATION.cff](CITATION.cff); GitHub shows a "Cite this repository" button.

## License

[MIT](LICENSE). Copyright (c) 2026 Jean-François Brisson, Spark AI NLP.
