# OES-32 Engine

> **Profile A sidecar.** The normative residual definition is [oes32-residual@b77b612](https://github.com/sparkainlp-x/oes32-residual/tree/b77b61254f15778c6ae221843dceac7a8571158e) (ADR-001). This repo's thresholds and FOLD8/symmetry definitions are Profile A extensions and are not normative.

**Author:** Jean-François Brisson  
**Organization:** Spark AI NLP

A small, deterministic Python reference implementation of symbolic telemetry triage and fault-containment equations for a 32-element state vector. This project is a **software specification and test harness**, not certified hardware-control software and must not be connected directly to safety-critical hardware without independent verification, validation, and engineering review.

## Relation to oes32-residual (ADR-001 · Profile A)

The normative residual aggregate **R** is defined by [`oes32-residual`](https://github.com/sparkainlp-x/oes32-residual) (pin: `b77b61254f15778c6ae221843dceac7a8571158e` until superseded): maximum absolute component residual on length-32 vectors, fail-closed on invalid input.

This engine implements **Profile A sidecars** on top of that residual:

| Check | Role | Default threshold (sidecar) |
|---|---|---|
| Residual coherence R | Normative R (must match oes32-residual) | caller / documented τ |
| Coherence latch | Sidecar | τ_coherence = 0.08 (default in this repo) |
| EVEN/ODD symmetry | Sidecar | τ_sym (see code) |
| FOLD8 ring continuity | Sidecar | τ_fold (see code) |

SAFE/LATCH here is a containment profile decision, **not** a physical qubit gate, QPU status, or certified hardware-control result. See [docs/ADR-001-oes32-tau-unification.md](docs/ADR-001-oes32-tau-unification.md).

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

## Install

Requires Python 3.8+ and only the standard library (no third-party dependencies).

```bash
git clone https://github.com/sparkainlp-x/oes32_engine.git
cd oes32_engine
python3 -m unittest discover -v
```

## Usage

```python
from oes32_engine import evaluate

result = evaluate([0.0] * 32, [0.0] * 32)
assert result.safe
```

Run tests with `python3 -m unittest discover -v`.

## Evidence status

All inputs in the tests are SYNTHETIC. This is research software: not hardware, field, or medical software, and not certified control software.

