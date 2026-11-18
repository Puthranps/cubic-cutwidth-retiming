"""Audit saved finite cubic layouts at every prefix. Usage: python verify_nested_sweep.py directory."""
import argparse
import csv
import hashlib
from pathlib import Path
import sys

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import maximum_bipartite_matching


def all_matchings(g, order):
    """Keep a maximum matching as each vertex moves from the right side to the left side."""
    n = len(g)
    pos = [0] * n
    for i, v in enumerate(order):
        pos[v] = i
    mate = [-1] * n
    seen = [-1] * n
    parent = [-1] * n
    tick = 0

    def augment(root, cutoff):
        nonlocal tick
        tick += 1
        seen[root] = tick
        stack = [root]
        while stack:
            u = stack.pop()
            for r in g[u]:
                if pos[r] <= cutoff:
                    continue
                partner = mate[r]
                if partner == -1:
                    while True:
                        old = mate[u]
                        mate[u], mate[r] = r, u
                        if u == root:
                            return 1
                        r, u = old, parent[u]
                if seen[partner] != tick:
                    seen[partner] = tick
                    parent[partner] = u
                    stack.append(partner)
        return 0

    counts = [0]
    size = 0
    for i, v in enumerate(order):
        old = mate[v]
        if old != -1:
            mate[v] = mate[old] = -1
            size -= 1
            size += augment(old, i)
        size += augment(v, i)
        counts.append(size)
    assert size == 0
    return np.asarray(counts, dtype=np.int64)


def static_size(low, high, k):
    across = (low < k) & (k <= high)
    if not np.any(across):
        return 0
    _, left = np.unique(low[across], return_inverse=True)
    _, right = np.unique(high[across], return_inverse=True)
    mat = csr_matrix((np.ones(len(left), dtype=np.int8), (left, right)),
                     shape=(left.max()+1, right.max()+1))
    return int((maximum_bipartite_matching(mat, perm_type="column") >= 0).sum())


def audit(edges, order):
    n = len(order)
    np.testing.assert_array_equal(np.sort(order), np.arange(n))
    assert edges.shape == (3*n//2, 2) and edges.min() >= 0 and edges.max() < n
    assert np.all(edges[:, 0] < edges[:, 1])
    assert len(np.unique(edges, axis=0)) == len(edges)
    assert np.all(np.bincount(edges.ravel(), minlength=n) == 3)
    adj = [[] for _ in range(n)]
    for a, b in edges.tolist():
        adj[a].append(b)
        adj[b].append(a)
    pos = np.empty(n, dtype=np.int64)
    pos[order] = np.arange(n)
    low, high = np.sort(pos[edges], axis=1).T
    raw = np.cumsum(np.bincount(low+1, minlength=n+1) - np.bincount(high+1, minlength=n+1))
    counts = all_matchings(adj, order.tolist())
    assert np.all((0 <= counts) & (counts <= raw))
    assert np.all(np.abs(np.diff(counts)) <= 1)
    grid = np.rint(np.arange(.30, .70+1e-9, .02)*n).astype(int)
    # Independently rebuild the bipartite graph at the grid, both actual peaks,
    # and 101 uniformly spaced prefixes including the extremes.
    checks = set(grid) | {int(raw.argmax()), int(counts.argmax())}
    checks.update(np.rint(np.linspace(0, n, 101)).astype(int))
    if n <= 256:
        checks.update(range(n+1))
    for k in sorted(checks):
        assert counts[k] == static_size(low, high, k), f"matching disagreement at prefix {k}"
    return (int(counts[grid].max()), int(counts.max()), int(counts.argmax()),
            int(raw.max()), int(raw.argmax()), len(checks))


def self_test():
    import networkx as nx
    for n in (4, 6, 10, 32, 62, 96):
        for seed in range(4):
            g = nx.random_regular_graph(3, n, seed=seed)
            edges = np.sort(np.asarray(g.edges, dtype=np.int32), axis=1)
            order = np.random.default_rng(seed+15).permutation(n)
            audit(edges, order)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("directory", nargs="?", type=Path)
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args()
    if args.self_test:
        self_test()
        print("Small-graph self-test passed on all prefixes of 24 layouts.", file=sys.stderr)
    if args.directory is None:
        return
    out = csv.writer(sys.stdout, lineterminator="\n")
    out.writerow(["n", "seed", "grid_matching", "grid_ratio", "all_matching", "all_ratio",
                  "matching_peak_prefix", "all_edges", "edge_ratio", "edge_peak_prefix",
                  "independent_matching_checks", "edge_sha256", "order_sha256"])
    files = sorted(args.directory.glob("cubic_*_*.npz"),
                   key=lambda f: tuple(map(int, f.stem.split("_")[1:])))
    if not files:
        raise FileNotFoundError(f"No layout files in {args.directory}")
    for f in files:
        n, seed = map(int, f.stem.split("_")[1:])
        with np.load(f, allow_pickle=False) as data:
            edges, order = data["edges"], data["order"]
        assert len(order) == n
        grid, full, fp, raw, rp, checks = audit(edges, order)
        digest = lambda a: hashlib.sha256(np.asarray(a, dtype="<i4").tobytes()).hexdigest()
        out.writerow([n, seed, grid, f"{grid/n:.8f}", full, f"{full/n:.8f}", fp,
                      raw, f"{raw/n:.8f}", rp, checks, digest(edges), digest(order)])
        sys.stdout.flush()


if __name__ == "__main__":
    main()
