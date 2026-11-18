# Cubic vertex ordering experiment log

## Nested balanced cuts with movable vertex blocks

**Verdict.** The same ordering rule met the strict matching threshold on all six requested graphs. The largest matching fraction across every prefix was 0.123140, attained on 50,000 vertices, seed 2, with 6,157 matched edges. This left 93 edges of margin below one eighth. The largest raw crossing-edge fraction among the six layouts was 0.123180. Phase 1 reached its empirical stopping condition. A uniform bound on cubic multigraphs remains open.

| Vertices | Seed | Fiedler, grid | Smooth 1024, grid | Candidate, grid | Candidate, all prefixes | Raw edges, all prefixes |
|---:|---:|---:|---:|---:|---:|---:|
| 50,000 | 1 | 0.13164 | 0.12556 | 0.122000 | 0.122060 | 0.122100 |
| 50,000 | 2 | 0.13118 | 0.12542 | 0.123060 | 0.123140 | 0.123180 |
| 50,000 | 3 | 0.13088 | 0.12546 | 0.121920 | 0.121980 | 0.122020 |
| 200,000 | 1 | 0.13001 | 0.12566 | 0.121860 | 0.121930 | 0.121940 |
| 200,000 | 2 | 0.13093 | 0.12562 | 0.122240 | 0.122290 | 0.122305 |
| 200,000 | 3 | 0.13065 | 0.12537 | 0.122400 | 0.122440 | 0.122455 |

Each matching column reports the largest maximum matching divided by graph size. The supplied grid has 21 thresholds from the 30th to the 70th percentile. Baseline values retain the precision printed by the supplied script. Candidate values come from integer matching counts. The last column counts crossing edges directly.

### Ordering rule

The initial order comes from 384 rounds of lazy adjacency iteration on random vertex scores, with the constant part removed. One branch recursively bisects the order. Paired moves exchange vertices on opposite sides of a split and retain the best prefix of moves. Each split accounts for edges to the vertices already assigned to the left or right of its interval. Recursion stops on intervals smaller than 40 vertices.

Both that branch and a branch starting from the initial order go through 320 passes of block placement. Each pass holds some vertices in a fixed relative order. The remaining vertices form disconnected blocks of at most eight. At every neighboring anchor event, the algorithm enumerates the subsets of each affected block to find the least minimum edge cut. It assembles the full order and scores its actual prefix cuts. Both branches use the same fixed rule. The algorithm returns the branch with the smaller maximum raw cut, breaking ties by counts at successively lower cut sizes. The matching score used for evaluation is computed separately.

**Analyzability.** Before sorting, the initial scores depend on finite-radius neighborhoods up to a common shift and scale. Individual block problems are exact and bounded in size once their anchors are fixed. Balanced exchanges over a whole interval and the decision to retain a full ordering depend on the entire graph. Extending the complete ordering to the infinite cubic tree, or controlling it uniformly on finite cubic graphs, remains open.

### Reproduce

Run from the repository root with Python, NumPy, SciPy, NetworkX and a stable Rust compiler on the path. The Python candidate compiles its standard-library Rust helper into a temporary directory. These runs used Python 3.14.7, NumPy 2.5.5, SciPy 1.18.1, NetworkX 3.6.1 and rustc 1.99.1 on Windows. OpenBLAS and OpenMP each used one thread.

```text
python research/bench/cutwidth_bench.py --n 50000 --seeds 1 2 3 --smooth 1024
python research/bench/cutwidth_bench.py --n 50000 --seeds 1 2 3 --custom research/bench/orderings/nested_block_cuts.py
python research/bench/cutwidth_bench.py --n 200000 --seeds 1 2 3 --smooth 1024 --custom research/bench/orderings/nested_block_cuts.py
```

The measured candidate runs used `research/bench/capture_witnesses.py`, a wrapper around the supplied benchmark that also saved the exact edge lists and vertex permutations. The six saved instances can be audited immediately with `python research/bench/verify_nested_sweep.py --self-test research/bench/results/witnesses`. [Saved graphs and permutations](results/witnesses) · [Exact results and hashes](results/nested_block_cuts.csv)

To regenerate the instances into a local `witnesses` directory and audit that output, run

```text
python research/bench/capture_witnesses.py . witnesses --n 50000 --seeds 1 2 3 --custom research/bench/orderings/nested_block_cuts.py
python research/bench/capture_witnesses.py . witnesses --n 200000 --seeds 1 2 3 --custom research/bench/orderings/nested_block_cuts.py
python research/bench/verify_nested_sweep.py --self-test witnesses
```

The audit checked all 750,006 prefixes, including empty and full prefixes. It recomputed maximum matchings from scratch with SciPy at 617 selected prefixes, including both observed peaks on each graph. A separate test checked the sweep against SciPy at every prefix of 24 smaller layouts. The raw crossing counts also used an independent edge-interval calculation. The CSV records the integer maxima, their attaining prefixes, and hashes of the saved graphs and orders. The three supplied benchmark files are byte-identical to the downloads.

A second verification regenerated each graph from the supplied NetworkX seed and compared its complete sorted edge list with the saved instance. It counted all raw cuts independently by adding $3-2d$ as each vertex entered the prefix, where $d$ is its number of neighbors already placed. All six edge maxima, their first attaining prefixes and the six permutation hashes matched the CSV. Every matching is a subset of the crossing edges, so these raw counts independently certify the strict threshold for each saved ordering.

## Terminal-band minimum-cut pilot

A second rule sweeps source-minimal cuts between moving sets of fixed terminals. It starts in spectral rank order, makes two sweeps with rank half-widths of 16% and 12% of the graph size, then places connected groups of tied vertices together. The min-cut steps and tie resolution depend on the global graph, which makes an infinite-tree analysis harder. [Python implementation](orderings/terminal_band.py)

```text
python research/bench/cutwidth_bench.py --n 1600 --seeds 1 2 3 --custom research/bench/orderings/terminal_band.py
```

At 1,600 vertices the maximum matching fractions on the benchmark grid were 0.13000, 0.12812 and 0.12250 for seeds 1, 2 and 3. The corresponding Fiedler values were 0.13750, 0.13375 and 0.12875. Only seed 3 cleared 0.125. This pilot ended when the nested-block rule satisfied the full six-instance stopping condition.
