"""Example custom ordering for cutwidth_bench.py --custom.

Fiedler vector followed by 256 rounds of rank smoothing. Replace the body
with the ordering rule a proof claims to analyze, then check the measured
worst matching/n is at least as good as the bound the proof states.
"""
import numpy as np
import scipy.sparse.linalg as sla


def order(G, A, rng):
    vals, vecs = sla.eigsh(A, k=2, which="LA")
    o = np.argsort(vecs[:, np.argsort(vals)[0]])
    n = len(o)
    pos = np.empty(n)
    pos[o] = np.arange(n)
    for _ in range(256):
        key = (pos + A @ pos) / 4 + 1e-9 * rng.standard_normal(n)
        o = np.argsort(key)
        pos[o] = np.arange(n)
    return o
