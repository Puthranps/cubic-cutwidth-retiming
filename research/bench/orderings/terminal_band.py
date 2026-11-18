"""Order cubic graphs by a nested sweep of minimum edge cuts between moving terminals."""
import heapq

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import breadth_first_order, connected_components, maximum_flow
from scipy.sparse.linalg import eigsh


def _source_shore(free, neighbors, local, position, rank, start, end, left_limit):
    """Source-minimal minimum cut after contracting all forced vertices."""
    size = len(free)
    around = neighbors[free]
    local[free] = np.arange(size, dtype=np.int32)
    adjacent = local[around]
    local[free] = -1
    inside = adjacent >= 0
    positions = position[around]
    forced_left = (positions < start) | ((positions < end) & (rank[around] < left_limit))
    to_source = np.sum(~inside & forced_left, axis=1, dtype=np.int32)
    to_sink = np.sum(~inside & ~forced_left, axis=1, dtype=np.int32)
    from_source = np.flatnonzero(to_source)
    if not len(from_source):
        return np.zeros(size, dtype=bool)

    row, slot = np.nonzero(inside)
    into_sink = np.flatnonzero(to_sink)
    source, sink = size, size + 1
    tails = np.concatenate((row, np.full(len(from_source), source), into_sink))
    heads = np.concatenate((adjacent[row, slot], from_source, np.full(len(into_sink), sink)))
    capacities = np.concatenate((np.ones(len(row), dtype=np.int32),
                                 to_source[from_source], to_sink[into_sink]))
    graph = csr_matrix((capacities, (tails, heads)), shape=(size+2, size+2))
    flow = maximum_flow(graph, source, sink, method="dinic").flow
    residual = graph - flow
    residual.eliminate_zeros()
    reachable = breadth_first_order(residual, source, directed=True, return_predecessors=False)
    shore = np.zeros(size+2, dtype=bool)
    shore[reachable] = True
    return shore[:size]


def _refine_cohorts(neighbors, levels, rank):
    """Move connected components of a tied group together, with shrinking cuts first."""
    n = len(levels)
    same = levels[neighbors] == levels[:, None]
    row, slot = np.nonzero(same)
    graph = csr_matrix((np.ones(len(row), dtype=np.int8), (row, neighbors[row, slot])),
                       shape=(n,n))
    count, component = connected_components(graph, directed=False)
    left = np.sum(levels[neighbors] < levels[:, None], axis=1, dtype=np.int8)
    right = np.sum(levels[neighbors] > levels[:, None], axis=1, dtype=np.int8)
    delta = np.bincount(component, weights=right-left, minlength=count)
    sizes = np.bincount(component, minlength=count)
    first_rank = np.full(count, n, dtype=np.int64)
    np.minimum.at(first_rank, component, rank)
    level = np.empty(count, dtype=levels.dtype)
    level[component] = levels
    sequence = np.lexsort((first_rank, delta/sizes, level))
    priority = np.empty(count, dtype=np.int32)
    priority[sequence] = np.arange(count, dtype=np.int32)
    ordered = np.lexsort((rank, priority[component]))

    # Within one connected component, adding a vertex changes the edge cut
    # by 3-2*(number of its neighbors already left). Equal gains use seed rank.
    stops = np.cumsum(sizes[sequence])
    placed = np.zeros(n, dtype=bool)
    for index in np.flatnonzero(sizes[sequence] > 1):
        stop = stops[index]
        start = stop-sizes[sequence[index]]
        vertices = ordered[start:stop].copy()
        heap = [(-int(left[v]), int(rank[v]), int(v)) for v in vertices]
        heapq.heapify(heap)
        for at in range(start, stop):
            while True:
                unused_gain, unused_rank, vertex = heapq.heappop(heap)
                if not placed[vertex]:
                    break
            placed[vertex] = True
            ordered[at] = vertex
            for v in neighbors[vertex]:
                if component[v] == component[vertex] and not placed[v]:
                    left[v] += 1
                    heapq.heappush(heap, (-int(left[v]), int(rank[v]), int(v)))
    return ordered


def _sweep(neighbors, initial, half_band):
    n = len(initial)
    rank = np.empty(n, dtype=np.int64)
    rank[initial] = np.arange(n)
    ordered = initial.copy()
    position = rank.copy()
    local = np.full(n, -1, dtype=np.int32)
    levels = np.empty(n, dtype=np.int32)
    bins = min(n, 128)
    work = [(0, n, 0, bins)]
    while work:
        start, end, low, high = work.pop()
        if start == end:
            continue
        if high == low + 1:
            levels[ordered[start:end]] = low
            continue
        middle = (low + high)//2
        target = n*middle//bins
        left_limit, right_limit = target - half_band, target + half_band
        vertices = ordered[start:end].copy()
        ranks = rank[vertices]
        add = ranks < left_limit
        undecided = (ranks >= left_limit) & (ranks < right_limit)
        if np.any(undecided):
            add[undecided] = _source_shore(vertices[undecided], neighbors, local, position,
                                           rank, start, end, left_limit)
        split = start + int(np.count_nonzero(add))
        ordered[start:split], ordered[split:end] = vertices[add], vertices[~add]
        position[ordered[start:end]] = np.arange(start,end)
        # Nestedness of the source-minimal cuts lets the next flows contract
        # the entire previously determined lower and upper shores.
        work.extend(((split,end,middle,high), (start,split,low,middle)))
    return _refine_cohorts(neighbors, levels, rank)


def order_from_ranks(A, initial_order):
    """Use a supplied seed permutation in CSR row coordinates."""
    A = A.tocsr()
    n = A.shape[0]
    if not np.all(np.diff(A.indptr) == 3):
        raise ValueError("terminal_band expects a simple cubic graph")
    neighbors = A.indices.reshape(n,3)
    current = np.asarray(initial_order, dtype=np.int64)
    for fraction in (.16, .12):
        current = _sweep(neighbors, current, max(1, round(fraction*n)))
    return current


def order(G, A, rng):
    """Return vertex IDs left to right. A uses the benchmark's G iteration order."""
    n = A.shape[0]
    values, vectors = eigsh(A, k=2, which="LA", tol=1e-5, v0=rng.standard_normal(n))
    initial = np.argsort(vectors[:,np.argmin(values)], kind="stable")
    node_ids = np.fromiter(G, dtype=np.int64, count=n)
    return node_ids[order_from_ranks(A, initial)]
