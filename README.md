# Cubic cutwidth by retiming a Gaussian vertex ordering

A cubic graph layout lists its vertices from left to right. Its width is the largest number of edges crossing any gap in the list. This research fork gives an AI-assisted proof that changing a Gaussian ordering locally can reduce the worst-case asymptotic width below the limit of the previous crossing-cover argument. [New argument, Section 7](submission/cutwidth.md#7-a-uniform-improvement-of-10-14-by-retiming-vertex-keys)

## Result

Let $\kappa$ be the limsup, over even $n$, of the largest ratio of cutwidth to $n$ among cubic multigraphs on $n$ vertices. Let $\Gamma$ be the limiting alternating-path coefficient of the previous Gaussian crossing-cover argument. The manuscript proves

$$\kappa\leq\Gamma-10^{-14},\qquad \kappa\leq 0.130647566423157664341749378137356.$$

The first inequality quantifies the effect of changing the ordering. The second uses an upward rounding of $\Gamma$. In the normalization of McGuire, Schlesinger and Williams, $M=2\kappa$, giving the rational bound $M\leq 0.261295132846315328683498756274712$. Their kernel-to-circuit reduction then yields a liminf of at least $1+1/(2\kappa_0)$ for Li's function, where $\kappa_0$ is the displayed rational upper bound. [Original Theorem K2C, Section 2.4](https://github.com/rrwilliams0/circuit-lb-4.6155n/blob/a56500014ba159397903dea81d41ac836f6880d5/proof.md#24-kernels-and-the-reduction-from-circuits-to-kernels)

The accompanying CircuitBreaker submission uses the earlier validated-prefix norm-graph language, counts every input bit, and proves an eventual full-binary-basis lower bound of $4.8270900384055950810649810365841\,n$. The preceding Yukon submission gave $4.827090038405301192\ldots\,n$. The increase is approximately $2.93889\times 10^{-13}n$. Earlier contributors account for the improvement from the original paper to that predecessor. [Circuit proof](submission/proof.md) · [Preceding submission](https://api.yukon.org/api/submissions/3f2be7ea-aa22-4f7e-98e9-23b40557dbcf)

## How the ordering changes

At a threshold, the crossing graph contains exactly the edges with one endpoint on either side. Its maximum matching size equals its minimum vertex-cover size. The proof identifies seven nearby vertices whose positions certify that moving a center across this cut decreases the matching size by one. Compatible centers can be moved simultaneously. The difficult case is a graph whose short cycles change the local Gaussian correlations. There the proof extracts an explicit saving from an interpolation between a high-girth cover and the original graph. [Matching argument and interpolation](submission/cutwidth.md#7-a-uniform-improvement-of-10-14-by-retiming-vertex-keys)

## Reproduce the finite checks

From the repository root run these commands with Python 3.12 or later. Both scripts use the standard library.

    python -I -B submission/certify.py
    python -I -B research/check_constants.py

The first program checks the 82nd and 83rd alternating sums with directed enclosures and a separate exact rational bound for the key matching event. It outputs one JSON record with all 83 probability intervals. The second verifies the elementary inequalities in the two graph cases. The analytic passage from these finite inequalities to cutwidth appears in the manuscript. [Certificate derivation](submission/certificate.md) · [Reference output](research/certificate-output.json)

## Review and credits

Developed with OpenAI Codex and independent AI proof critiques. The finite certificate passed on Windows and Linux. The pinned Linux verifier accepted the eight-file submission structure and froze its intake. The graph theorem and its application are research claims open to mathematical review. [CircuitBreaker](https://www.yukon.org/circuitbreaker)

McGuire, Schlesinger and Williams supplied the circuit-to-cutwidth reduction. Arthur Ostapenko, mooselumph and earlier CircuitBreaker contributors developed the norm-graph, prefix and comparison framework. Galarnon42 supplied the global crossing-cover optimization and finite path bound. DarkWingMcQuack and preceding submissions supplied the immediate certified coefficient and exact arithmetic framework. This fork retains their arguments with provenance in the manuscript. [Complete references](submission/proof.md#6-sources-and-reproduction)
