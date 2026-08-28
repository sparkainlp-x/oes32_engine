# OES-32 Engine

A small, deterministic Python reference implementation of symbolic telemetry triage and fault-containment equations for a 32-element state vector. This project is a **software specification and test harness**, not certified hardware-control software and must not be connected directly to safety-critical hardware without independent verification, validation, and engineering review.

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

## Usage

```python
from oes32_engine import evaluate

result = evaluate([0.0] * 32, [0.0] * 32)
assert result.safe
```

Run tests with `python3 -m unittest discover -v`.
