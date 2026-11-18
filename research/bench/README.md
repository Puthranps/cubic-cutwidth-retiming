# Cutwidth test bench

Empirical checks for vertex orderings of random cubic graphs. Use it before and after any proof attempt on the CircuitBreaker cutwidth route.

## Background

- The gate coefficient from a per-vertex bound κ is **1 + 1/(2κ)**. Beating 5 needs **κ < 1/8 = 0.125**.
- The proofs bound the **maximum matching across a cut**, not the raw edge count. The bench measures both, taking the worst value over a grid of thresholds.
- Hard floor: some cubic graphs have bisection width at least n/9.9, so κ ≥ about 0.101 and this route tops out near 5.95.

## Baseline numbers

These are worst matching/n on random cubic graphs (the exact digits vary with seed and n):

| Ordering | n = 50k | n = 200k |
|---|---|---|
| Fiedler (top non-trivial eigenvector) | 0.1309–0.1312 | 0.1300 |
| + 128 smoothing rounds | 0.1265 | 0.1263 |
| + 1024–2048 smoothing rounds | 0.1254–0.1257 | not run |

The Fiedler value matches the proven Γ ≈ 0.13065. Smoothing plateaus just above 0.125.

## Commands

    pip install networkx scipy numpy
    python3 cutwidth_bench.py --n 50000 --seeds 1 2 3
    python3 cutwidth_bench.py --n 50000 --smooth 1024
    python3 cutwidth_bench.py --n 50000 --custom example_ordering.py

A custom file defines `order(G, A, rng)`, which returns a permutation listing the vertices left to right.

## Rules for using it with a proof attempt

1. **Find it before proving it.** Look first for an ordering that reaches worst matching/n < 0.125 across several seeds and at least two sizes. If none exists, don't ask for a proof of κ < 1/8.
2. **Check every claimed proof.** Every proof here comes with an ordering rule. Implement that rule and measure it. If the measured value is *worse* than the bound the proof claims, the proof is wrong.
3. **Random graphs are only a sanity check.** A proof has to cover every cubic graph, and passing the bench is necessary for that, not sufficient.
4. **Don't spend effort polishing constants.** Local retiming has proved savings of order 10⁻⁸. The gap to 0.125 is about 0.0056, so the missing gain has to come from global structure.
