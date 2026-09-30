# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (c) 2026 Jean-François Brisson, Spark AI NLP

"""Deterministic OES-32 symbolic telemetry triage reference implementation."""
from __future__ import annotations
from dataclasses import dataclass
from math import isfinite
from typing import Sequence

WIDTH = 32
MU_OFFSET = 16
DEFAULT_TAU = 0.08

@dataclass(frozen=True)
class Evaluation:
    residual: float
    latch: bool
    even_symmetry_residual: float
    odd_symmetry_residual: float
    fold8_residual: float
    safe: bool


def _validate_vector(v: Sequence[float], name: str) -> tuple[float, ...]:
    if len(v) != WIDTH:
        raise ValueError(f"{name} must contain exactly {WIDTH} elements")
    values = tuple(float(a) for a in v)
    if not all(isfinite(a) for a in values):
        raise ValueError(f"{name} must contain only finite numeric values")
    return values


def residual(x: Sequence[float], x_ref: Sequence[float]) -> float:
    x, x_ref = _validate_vector(x, "x"), _validate_vector(x_ref, "x_ref")
    return max(abs(a - b) for a, b in zip(x, x_ref))


def symmetry_residual(x: Sequence[float], parity: int, *, antisymmetric_odd: bool = True) -> float:
    x = _validate_vector(x, "x")
    if parity not in (0, 1):
        raise ValueError("parity must be 0 (EVEN) or 1 (ODD)")
    values = []
    for i in range(parity, WIDTH, 2):
        sign = -1.0 if parity == 1 and antisymmetric_odd else 1.0
        j = (i + MU_OFFSET) % WIDTH
        values.append(abs(x[i] - sign * x[j]))
    return max(values)


def fold8_residual(x: Sequence[float]) -> float:
    x = _validate_vector(x, "x")
    return max(abs(x[8*s+k] - x[8*s+(k+1) % 8]) for s in range(4) for k in range(8))


def evaluate(x: Sequence[float], x_ref: Sequence[float], *, tau: float = DEFAULT_TAU,
             tau_sym: float | None = None, tau_fold: float | None = None,
             antisymmetric_odd: bool = True) -> Evaluation:
    if tau < 0 or (tau_sym is not None and tau_sym < 0) or (tau_fold is not None and tau_fold < 0):
        raise ValueError("thresholds must be non-negative")
    tau_sym = tau if tau_sym is None else tau_sym
    tau_fold = tau if tau_fold is None else tau_fold
    r = residual(x, x_ref)
    even = symmetry_residual(x, 0, antisymmetric_odd=antisymmetric_odd)
    odd = symmetry_residual(x, 1, antisymmetric_odd=antisymmetric_odd)
    fold = fold8_residual(x)
    safe = r <= tau and even <= tau_sym and odd <= tau_sym and fold <= tau_fold
    return Evaluation(r, not safe, even, odd, fold, safe)
