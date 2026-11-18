# Cubic cutwidth by retiming a Gaussian vertex ordering

In a cubic graph layout, list the vertices from left to right and count the edges crossing each gap. The largest count is the width of the layout. This research fork gives an AI-assisted proof of an improvement of **at least $2\times10^{-8}$ in the asymptotic cutwidth per vertex** over the limiting value of the previous Gaussian crossing-cover method. [Graph theorem](submission/cutwidth.md#0-statement-and-proof-map)

## Bound and circuit consequence

Let $\kappa$ be the limsup, over even $n$, of the largest cutwidth divided by $n$ among cubic multigraphs on $n$ vertices. Write $\Gamma$ for the earlier method's limiting alternating-path coefficient. The proof gives

$$\kappa\leq\Gamma-2\times10^{-8},\qquad \kappa\leq 0.130647546423167665.$$

The first bound measures what changes in the ordering. The second uses a rational upper bound on $\Gamma$. In the normalization of McGuire, Schlesinger and Williams this gives $M=2\kappa\leq 0.261295092846335330$. Their kernel-to-circuit theorem applies this graph bound to Li's function. [Original Theorem K2C](https://github.com/rrwilliams0/circuit-lb-4.6155n/blob/a56500014ba159397903dea81d41ac836f6880d5/proof.md#24-kernels-and-the-reduction-from-circuits-to-kernels)

The CircuitBreaker entry uses the earlier validated-prefix norm-graph language. The eventual full-binary-basis circuit bound is **$4.82709062427011829815939834410753\,n$**, counting the entire input length. The preceding public entry by DarkWingMcQuack gave $4.827090038405301192\ldots\,n$. The difference in the two circuit coefficients is about $5.86\times10^{-7}$. Prior work accounts for the improvement from Williams's original $4.6155$ to the preceding $4.82709$. [Circuit proof](submission/proof.md) · [Preceding entry](https://api.yukon.org/api/submissions/3f2be7ea-aa22-4f7e-98e9-23b40557dbcf)

## Where the gain comes from

At a threshold of a vertex ordering, the edges with one endpoint on either side form a bipartite graph. A pattern of seven nearby vertices certifies that moving a center across the threshold saves exactly one unit of maximum matching size. A compatible set of centers can move simultaneously. Where the local Gaussian law is close enough to the cubic-tree wave, a three-dimensional integral bounds the frequency of that pattern. Where it deviates, the excess in adjacent correlations yields a separate decrease in the original matching-size bound. The two savings add on the same graph. [Local ordering rule](submission/cutwidth.md#71-a-local-change-in-a-vertex-ordering) · [Good-center calculation](submission/certificate.md#8-a-quantitative-probability-bound-at-good-centers) · [Covariance interpolation](submission/certificate.md#9-integrated-covariance-gain-at-a-heavy-edge)

## Reproduction

Run the following from the repository root with Python 3.12 or later. The complete finite certificate uses the Python standard library.

    python -I -B submission/certify.py

The program checks the two alternating path-sum enclosures, the preparatory matching event, the good-center lower sum, and the integrated edge credit. It emits one JSON record with all 47 probability intervals and the key integer floors. The paper supplies the graph and circuit arguments that connect those finite checks to the asymptotic claims. [Certificate derivation](submission/certificate.md) · [Reference output](research/certificate-output.json)

## Versions and review

Yukon's primary hosted reviewer marked the $2\times10^{-8}$ revision valid. Its container reproduced every finite-certificate output in 14.5 seconds. A separate automated audit timed out during final adjudication. The public entry is in review with no human verdict recorded. [Yukon judgment](https://api.yukon.org/api/submissions/60c7a1c3-9b1a-4c29-ad98-5de7c3ef351b) · [Hosted evaluation](https://github.com/Layr-Labs/circuitbreaker-llm-verifier/actions/runs/44235424767)

The first version established a $10^{-14}$ saving. Its separate hosted evaluation also marked it valid. [First proof](https://github.com/Puthranps/cubic-cutwidth-retiming/tree/7b0d2587b3da62877fea4fae2d4fa9a370f3919f) · [First official judgment](https://api.yukon.org/api/submissions/4c133ffa-7452-42c6-9629-d7821ee890d4)

Puthranps selected Williams's challenge, directed the AI investigation and requested a check that it advanced the existing bound. OpenAI Codex agents developed the new argument, wrote the reproduction code and performed the internal proof critiques.

McGuire, Schlesinger and Williams supplied the circuit-to-cutwidth reduction. Arthur Ostapenko, mooselumph and earlier CircuitBreaker contributors developed the norm-graph, prefix and comparison framework. Galarnon42 supplied the global crossing-cover optimization and finite path bound. DarkWingMcQuack and the preceding contributors supplied the immediate coefficient and exact arithmetic framework. [Complete references](submission/proof.md#6-sources-and-reproduction)
