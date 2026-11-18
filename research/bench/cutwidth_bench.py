"""Test bench for vertex orderings of random cubic graphs.

Measures, for a vertex ordering, the worst (over thresholds) crossing edge
count and crossing *maximum matching* size, both divided by n. The matching
size is the quantity the CircuitBreaker cutwidth proofs control; the gate
coefficient obtained from a per-vertex bound kappa is 1 + 1/(2*kappa), so
beating 5 needs kappa < 1/8 = 0.125.

Usage
-----
  python3 cutwidth_bench.py --n 50000 --seeds 1 2 3
  python3 cutwidth_bench.py --n 50000 --smooth 2048
  python3 cutwidth_bench.py --n 50000 --custom my_ordering.py

A custom ordering file must define
    def order(G: networkx.Graph, A: scipy.sparse.csr_array, rng) -> numpy array
returning a permutation of range(n) (vertices listed left to right).

Caveats: random cubic graphs only; finite n; thresholds sampled on a grid.
An empirical number is an upper bound on what is achievable for these graphs,
never a proof about all cubic graphs.
"""
import argparse
import importlib.util
import time

import networkx as nx
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as sla
from scipy.sparse.csgraph import maximum_bipartite_matching


def random_cubic(n, seed):
    G = nx.random_regular_graph(3, n, seed=seed)
    edges = np.array(G.edges(), dtype=np.int64)
    A = nx.to_scipy_sparse_array(G, format="csr", dtype=float)
    return G, edges, A


def measure(order, edges, n, qs):
    """Return list of (q, crossing_edges/n, crossing_matching/n) per threshold."""
    order = np.asarray(order)
    assert len(order) == n and len(np.unique(order)) == n, "order must be a permutation"
    pos = np.empty(n, dtype=np.int64)
    pos[order] = np.arange(n)
    a, b = pos[edges[:, 0]], pos[edges[:, 1]]
    lo, hi = np.minimum(a, b), np.maximum(a, b)
    out = []
    for q in qs:
        t = int(round(q * n))
        m = (lo < t) & (hi >= t)
        e = int(m.sum())
        if e == 0:
            out.append((q, 0.0, 0.0))
            continue
        _, Li = np.unique(lo[m], return_inverse=True)
        _, Ri = np.unique(hi[m], return_inverse=True)
        B = sp.csr_matrix((np.ones(e), (Li, Ri)), shape=(Li.max() + 1, Ri.max() + 1))
        match = maximum_bipartite_matching(B, perm_type="column")
        out.append((q, e / n, int((match >= 0).sum()) / n))
    return out


def fiedler_order(A):
    vals, vecs = sla.eigsh(A, k=2, which="LA")
    return np.argsort(vecs[:, np.argsort(vals)[0]])


def smooth(order, A, iters, seed=0):
    """Rank smoothing: key = (own rank + sum of neighbour ranks)/4, re-rank, repeat."""
    rng = np.random.default_rng(seed)
    n = len(order)
    pos = np.empty(n)
    pos[order] = np.arange(n)
    for _ in range(iters):
        key = (pos + A @ pos) / 4 + 1e-9 * rng.standard_normal(n)
        order = np.argsort(key)
        pos[order] = np.arange(n)
    return order


def load_custom(path):
    spec = importlib.util.spec_from_file_location("custom_order", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.order


def report(name, rows):
    we = max(r[1] for r in rows)
    wm = max(r[2] for r in rows)
    coef = 1 + 1 / (2 * wm) if wm > 0 else float("inf")
    flag = "  <-- below 1/8" if wm < 0.125 else ""
    print(f"  {name:22s} worst edges/n {we:.5f}  worst matching/n {wm:.5f}  "
          f"(coef-equivalent {coef:.4f}){flag}")
    return wm


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=50000)
    ap.add_argument("--seeds", type=int, nargs="+", default=[1])
    ap.add_argument("--smooth", type=int, default=0, help="smoothing iterations after Fiedler")
    ap.add_argument("--custom", help="python file defining order(G, A, rng)")
    ap.add_argument("--qmin", type=float, default=0.30)
    ap.add_argument("--qmax", type=float, default=0.70)
    ap.add_argument("--qstep", type=float, default=0.02)
    args = ap.parse_args()
    qs = np.arange(args.qmin, args.qmax + 1e-9, args.qstep)
    custom = load_custom(args.custom) if args.custom else None

    print("target for coefficient > 5: worst matching/n < 0.125")
    for seed in args.seeds:
        t0 = time.time()
        G, edges, A = random_cubic(args.n, seed)
        print(f"n={args.n} seed={seed}")
        base = fiedler_order(A)
        report("fiedler", measure(base, edges, args.n, qs))
        if args.smooth:
            o = smooth(base, A, args.smooth, seed)
            report(f"fiedler+smooth{args.smooth}", measure(o, edges, args.n, qs))
        if custom:
            o = custom(G, A, np.random.default_rng(seed))
            report("custom", measure(o, edges, args.n, qs))
        print(f"  ({time.time() - t0:.1f}s)")


if __name__ == "__main__":
    main()
