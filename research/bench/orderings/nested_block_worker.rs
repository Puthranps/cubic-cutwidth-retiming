//! Integer split and block optimizers for nested_block_cuts.py.
//! Build with stable Rust, no third-party crates.
use std::{
    collections::BinaryHeap,
    io::{Read, Write},
};

type Graph = Vec<[usize; 3]>;
const UNSET: usize = usize::MAX;

struct Rng(u64);
impl Rng {
    fn next(&mut self) -> u64 {
        self.0 = self.0.wrapping_add(0x9e3779b97f4a7c15);
        let mut x = self.0;
        x = (x ^ (x >> 30)).wrapping_mul(0xbf58476d1ce4e5b9);
        x = (x ^ (x >> 27)).wrapping_mul(0x94d049bb133111eb);
        x ^ (x >> 31)
    }
    fn below(&mut self, bound: usize) -> usize {
        let b = bound as u64;
        let threshold = b.wrapping_neg() % b;
        loop {
            let x = self.next();
            if x >= threshold {
                return (x % b) as usize;
            }
        }
    }
    fn shuffle<T>(&mut self, x: &mut [T]) {
        for j in (1..x.len()).rev() {
            x.swap(j, self.below(j + 1));
        }
    }
}

fn positions(order: &[usize]) -> Vec<usize> {
    let mut pos = vec![UNSET; order.len()];
    for (i, &v) in order.iter().enumerate() {
        assert_eq!(pos[v], UNSET);
        pos[v] = i;
    }
    pos
}

fn cuts(g: &Graph, order: &[usize]) -> Vec<i32> {
    let pos = positions(order);
    let mut width = 0;
    let mut values = vec![0];
    for (i, &v) in order.iter().enumerate() {
        let earlier = g[v].iter().filter(|&&u| pos[u] < i).count() as i32;
        width += 3 - 2 * earlier;
        values.push(width);
    }
    assert_eq!(width, 0);
    values
}

// Resolve equal peaks using the number of cuts at each successively lower level.
fn profile(g: &Graph, order: &[usize]) -> (i32, Vec<usize>) {
    let a = cuts(g, order);
    let peak = *a.iter().max().unwrap();
    let mut hist = vec![0; peak as usize + 1];
    for w in a {
        hist[(peak - w) as usize] += 1;
    }
    (peak, hist)
}

// A global spectral initial order, from lazy adjacency iteration off the constant vector.
fn spectral(g: &Graph, rng: &mut Rng) -> Vec<usize> {
    let n = g.len();
    let mut x: Vec<_> = (0..n)
        .map(|_| (rng.next() >> 11) as f64 / ((1u64 << 53) as f64) - 0.5)
        .collect();
    let mut y = vec![0.; n];
    for _ in 0..384 {
        for (v, nb) in g.iter().enumerate() {
            y[v] = 2. * x[v] + x[nb[0]] + x[nb[1]] + x[nb[2]];
        }
        let mean = y.iter().sum::<f64>() / n as f64;
        let mut sum = 0.;
        for t in &mut y {
            *t -= mean;
            sum += *t * *t;
        }
        let scale = sum.sqrt().recip();
        for t in &mut y {
            *t *= scale;
        }
        std::mem::swap(&mut x, &mut y);
    }
    let mut order: Vec<_> = (0..n).collect();
    order.sort_unstable_by(|&a, &b| x[a].total_cmp(&x[b]).then(a.cmp(&b)));
    order
}

fn find(parent: &mut [usize], mut x: usize) -> usize {
    while parent[x] != x {
        parent[x] = parent[parent[x]];
        x = parent[x];
    }
    x
}

// Remove pins only while every connected free component stays within the cap.
fn free_blocks(g: &Graph, cap: usize, rng: &mut Rng) -> Vec<Vec<usize>> {
    let n = g.len();
    let mut perm: Vec<_> = (0..n).collect();
    rng.shuffle(&mut perm);
    let mut parent = vec![UNSET; n];
    let mut sizes = vec![0; n];
    for v in perm {
        let mut roots = [UNSET; 3];
        let mut count = 0;
        let mut size = 1;
        for &u in &g[v] {
            if parent[u] == UNSET {
                continue;
            }
            let r = find(&mut parent, u);
            if !roots[..count].contains(&r) {
                roots[count] = r;
                count += 1;
                size += sizes[r];
            }
        }
        if size <= cap {
            parent[v] = v;
            sizes[v] = size;
            for &r in &roots[..count] {
                parent[r] = v;
            }
        }
    }
    let mut groups = vec![Vec::new(); n];
    for v in 0..n {
        if parent[v] != UNSET {
            let r = find(&mut parent, v);
            groups[r].push(v);
        }
    }
    groups.into_iter().filter(|b| !b.is_empty()).collect()
}

// With fixed pinned bits, minimize actual crossing edges incident to the block.
// Enumerate subsets once per boundary pin. The least minimum cut is monotone.
fn schedule_block(g: &Graph, pos: &[usize], block: &[usize], buckets: &mut [Vec<usize>]) {
    let k = block.len();
    let states = 1usize << k;
    let mut internal = vec![0usize; k];
    let mut boundary = Vec::new();
    for (i, &v) in block.iter().enumerate() {
        for &u in &g[v] {
            if let Some(j) = block.iter().position(|&z| z == u) {
                internal[i] |= 1 << j;
            } else {
                boundary.push((pos[u], i));
            }
        }
    }
    boundary.sort_unstable();
    let mut costs = vec![0i16; states];
    for s in 1..states {
        let i = s.trailing_zeros() as usize;
        let prev = s & (s - 1);
        costs[s] = costs[prev] + 3 - 2 * (internal[i] & prev).count_ones() as i16;
    }
    let mut previous = 0;
    let mut p = 0;
    while p < boundary.len() {
        let anchor = boundary[p].0;
        let mut hits = [0u8; 3];
        let mut e = 0;
        while p < boundary.len() && boundary[p].0 == anchor {
            hits[e] = boundary[p].1 as u8;
            e += 1;
            p += 1;
        }
        let mut lowest = i16::MAX;
        let mut best = 0;
        for (s, cost) in costs.iter_mut().enumerate() {
            // Omit the additive constant e, which is common to all assignments.
            for &i in &hits[..e] {
                *cost -= 2 * ((s >> i) & 1) as i16;
            }
            if *cost < lowest {
                lowest = *cost;
                best = s;
            }
        }
        assert_eq!(best & previous, previous);
        let mut added = best ^ previous;
        while added != 0 {
            let i = added.trailing_zeros() as usize;
            buckets[anchor].push(block[i]);
            added &= added - 1;
        }
        previous = best;
    }
    assert_eq!(previous, states - 1);
}

fn block_pass(g: &Graph, order: &[usize], cap: usize, rng: &mut Rng) -> Vec<usize> {
    let n = g.len();
    let pos = positions(order);
    let blocks = free_blocks(g, cap, rng);
    let mut buckets = vec![Vec::new(); n];
    let mut is_pin = vec![true; n];
    for b in &blocks {
        for &v in b {
            is_pin[v] = false;
        }
        schedule_block(g, &pos, b, &mut buckets);
    }
    for &v in order {
        if is_pin[v] {
            buckets[pos[v]].push(v);
        }
    }
    let mut added = vec![false; n];
    let mut result = Vec::with_capacity(n);
    for mut batch in buckets {
        // Only 1+3*cap vertices can move at a pin. Break ties using the old order.
        while !batch.is_empty() {
            let i = (0..batch.len())
                .min_by_key(|&i| {
                    let v = batch[i];
                    let inside = g[v].iter().filter(|&&u| added[u]).count();
                    (3 - inside, pos[v])
                })
                .unwrap();
            let v = batch.swap_remove(i);
            added[v] = true;
            result.push(v);
        }
    }
    assert_eq!(result.len(), n);
    result
}

// A Kernighan--Lin / Fiduccia--Mattheyses refinement of a fixed-rank split.
// Vertices preceding and following the interval stay on their respective sides.
// Pair opposite moves, keep the best prefix, and preserve both child sizes.
fn refine_split(
    g: &Graph,
    order: &mut [usize],
    pos: &mut [usize],
    lo: usize,
    hi: usize,
    mid: usize,
    rng: &mut Rng,
) {
    let size = hi - lo;
    let left = mid - lo;
    let mut nb = vec![[0; 3]; size];
    for (i, &v) in order[lo..hi].iter().enumerate() {
        for (j, &u) in g[v].iter().enumerate() {
            let p = pos[u];
            nb[i][j] = if p < lo {
                size
            } else if p >= hi {
                size + 1
            } else {
                p - lo
            };
        }
    }
    let mut chosen: Vec<_> = (0..size).map(|i| usize::from(i >= left)).collect();
    for pass in 0..6 {
        let mut side = chosen.clone();
        side.extend([0, 1]);
        let mut heaps = [BinaryHeap::new(), BinaryHeap::new()];
        let mut gain = vec![0i8; size];
        let mut locked = vec![false; size];
        let priority: Vec<_> = (0..size).map(|_| rng.next()).collect();
        for i in 0..size {
            gain[i] = 2 * nb[i].iter().filter(|&&u| side[u] != side[i]).count() as i8 - 3;
            heaps[side[i]].push((gain[i], priority[i], i));
        }
        let mut moves = Vec::with_capacity(size);
        let mut total = 0i32;
        let mut best = 0;
        let mut keep = 0;
        for _ in 0..left.min(size - left) {
            for half in 0..2 {
                let s = (pass + half) % 2;
                let (d, i) = loop {
                    let (d, _, i) = heaps[s].pop().unwrap();
                    if !locked[i] && d == gain[i] {
                        break (d, i);
                    }
                };
                locked[i] = true;
                moves.push(i);
                total += d as i32;
                side[i] = 1 - s;
                for &u in &nb[i] {
                    if u >= size || locked[u] {
                        continue;
                    }
                    gain[u] += if side[u] == s { 2 } else { -2 };
                    heaps[side[u]].push((gain[u], priority[u], u));
                }
            }
            if total > best {
                best = total;
                keep = moves.len();
            }
        }
        if keep == 0 {
            break;
        }
        for &i in &moves[..keep] {
            chosen[i] ^= 1;
        }
    }
    let mut ordered = Vec::with_capacity(size);
    for s in 0..2 {
        for i in 0..size {
            if chosen[i] == s {
                ordered.push(order[lo + i]);
            }
        }
    }
    assert_eq!(chosen.iter().filter(|&&x| x == 0).count(), left);
    for (i, &v) in ordered.iter().enumerate() {
        pos[v] = lo + i;
        order[lo + i] = v;
    }
}

fn hierarchical(g: &Graph, source: &[usize], rng: &mut Rng) -> Vec<usize> {
    let mut order = source.to_vec();
    let mut pos = positions(source);
    let mut intervals = vec![(0, source.len())];
    while let Some((lo, hi)) = intervals.pop() {
        if hi - lo < 40 {
            continue;
        }
        let mid = (lo + hi) / 2;
        refine_split(g, &mut order, &mut pos, lo, hi, mid, rng);
        intervals.push((lo, mid));
        intervals.push((mid, hi));
    }
    order
}

fn improve_blocks(g: &Graph, start: &[usize], passes: usize, rng: &mut Rng) -> Vec<usize> {
    let mut best = start.to_vec();
    let mut best_profile = profile(g, &best);
    for j in 0..passes {
        let cap = [2, 4, 6, 8, 3, 5][j % 6];
        let mut source = best.clone();
        if j % 2 == 1 {
            source.reverse();
        }
        let mut trial = block_pass(g, &source, cap, rng);
        if j % 2 == 1 {
            trial.reverse();
        }
        let score = profile(g, &trial);
        if score < best_profile {
            best = trial;
            best_profile = score;
        }
    }
    best
}

fn main() {
    // Little-endian CSR neighbor triples in numeric vertex order.
    let seed: u64 = std::env::args().nth(1).expect("seed").parse().unwrap();
    let mut input = Vec::new();
    std::io::stdin().read_to_end(&mut input).unwrap();
    assert!(input.len() % 12 == 0);
    let g: Graph = input
        .chunks_exact(12)
        .map(|row| {
            std::array::from_fn(|i| {
                u32::from_le_bytes(row[4 * i..4 * i + 4].try_into().unwrap()) as usize
            })
        })
        .collect();
    let mut rng = Rng(seed);
    let initial = spectral(&g, &mut rng);
    let passes = 320;
    let direct = improve_blocks(&g, &initial, passes, &mut rng);
    let mut split_rng = Rng(seed ^ 0x8cb92baa3f3d8dd7);
    let nested = hierarchical(&g, &initial, &mut split_rng);
    let refined = improve_blocks(&g, &nested, passes, &mut split_rng);
    let chosen = if profile(&g, &direct) < profile(&g, &refined) {
        direct
    } else {
        refined
    };
    let mut output = Vec::with_capacity(4 * chosen.len());
    for v in chosen {
        output.extend_from_slice(&(v as u32).to_le_bytes());
    }
    std::io::stdout().write_all(&output).unwrap();
}
