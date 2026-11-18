"""Nested balanced cuts and exact placement of connected blocks of up to eight vertices.

The benchmark calls order(G, A, rng). Rust (stable, standard library only)
accelerates the split and block searches; it compiles once per benchmark process.
"""
from functools import lru_cache
from pathlib import Path
import os
import shutil
import subprocess
import tempfile

import numpy as np


@lru_cache(maxsize=1)
def _worker():
    source = Path(__file__).with_name("nested_block_worker.rs")
    compiler = shutil.which("rustc")
    if compiler is None:
        raise RuntimeError("nested_block_cuts requires rustc on PATH")
    build_dir = tempfile.TemporaryDirectory(prefix="nested-block-cuts-")
    binary = Path(build_dir.name) / ("ordering.exe" if os.name == "nt" else "ordering")
    subprocess.run([compiler, "--edition=2021", "-O", str(source), "-o", str(binary)],
                   cwd=build_dir.name, check=True)
    return build_dir, binary


def order(G, A, rng):
    """Return a permutation of integer vertex IDs for a simple cubic input graph."""
    n = len(G)
    if n < 4 or n >= 2**32:
        raise ValueError("expected at least four vertices addressable by 32-bit IDs")
    if not np.array_equal(np.fromiter(G, dtype=np.int64, count=n), np.arange(n)):
        import networkx as nx
        A = nx.to_scipy_sparse_array(G, nodelist=range(n), format="csr")
    adjacency = A.tocsr()
    if not np.all(np.diff(adjacency.indptr) == 3):
        raise ValueError("expected a simple cubic graph")
    rows = np.sort(adjacency.indices.reshape(n, 3), axis=1).astype("<u4", copy=False)
    _, worker = _worker()
    seed = int(rng.bit_generator.random_raw())
    run = subprocess.run([str(worker), str(seed)], input=rows.tobytes(),
                         stdout=subprocess.PIPE, check=True)
    result = np.frombuffer(run.stdout, dtype="<u4").astype(np.int64)
    if result.size != n or not np.array_equal(np.sort(result), np.arange(n)):
        raise RuntimeError("worker returned an invalid permutation")
    return result
