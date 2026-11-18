# A cubic cutwidth bound from distance-two pairs

For every cubic graph on $n$ vertices, the vertices admit an ordering with at most **$0.130646316425n+o(n)$** edges crossing its busiest gap. The sublinear error is uniform over cubic multigraphs. The previous Yukon-reviewed bound was $0.130647546423167665n+o(n)$. [Graph proof](submission/cutwidth.md#0-statement-and-proof-map)

## What improved

Write $\kappa$ for the asymptotic worst-case cutwidth per vertex. The proof gives $\kappa\leq\Gamma-0.00000125$, where $\Gamma$ is the limiting coefficient of the previous Gaussian crossing-cover method. Our earlier submissions gave structural savings of $10^{-14}$ and $2\times10^{-8}$. The increase from $2\times10^{-8}$ to $1.25\times10^{-6}$ is a factor of 62.5. In the normalization of McGuire, Schlesinger and Williams the new upper bound is $M=2\kappa\leq0.26129263285$. [Finite certificate](submission/certificate.md) · [Original reduction for Li's function](https://github.com/rrwilliams0/circuit-lb-4.6155n/blob/a56500014ba159397903dea81d41ac836f6880d5/proof.md#24-kernels-and-the-reduction-from-circuits-to-kernels)

Across a gap, some crossing edges can be chosen without sharing endpoints. The proof moves vertices earlier when one of several local neighborhoods guarantees that this number decreases. It also counts pairs of vertices that share a neighbor. A sum-of-squares identity shows how much those pairs can contribute when nearby scores are more correlated than in the tree model. A separate threshold estimate controls all the other gaps in the same ordering. [Local ordering and threshold argument](submission/cutwidth.md#75-all-center-advancement-nine-edge-charging-and-strict-threshold-decrease) · [Distance-two matching and covariance proof](submission/certificate.md#8-integrated-credit-from-adjacent-and-distance-two-pairs)

For the fixed validated-prefix norm-graph language entered in Yukon, the eventual full-binary-basis circuit lower bound is **$4.82712665524737162523485973592385n$**, where $n$ counts the entire input length. [Circuit theorem](submission/proof.md)

## Reproduction and review

Run `python -I -B submission/certify.py` from the repository root. The Python standard-library program checks the 26th and 27th alternating sums, the local sign-event probability, both integrated covariance contributions, and the final rational margins. The complete outputs agree on Windows and Linux. An independent Codex agent audited the proof and reran the executable. [Reference output](research/certificate-output.json)

An intermediate two-pass proof gave $\kappa\leq0.130647519423167665$. The preceding version with a $2\times10^{-8}$ saving received a valid primary automated judgment on Yukon. [Two-pass proof](research/two-pass-bound.md) · [Previous Yukon judgment](https://api.yukon.org/api/submissions/60c7a1c3-9b1a-4c29-ad98-5de7c3ef351b) · [First submitted version](https://api.yukon.org/api/submissions/4c133ffa-7452-42c6-9629-d7821ee890d4)

Puthranps selected Williams's challenge, directed the AI investigation and requested a check that it advanced the existing bound. OpenAI Codex agents developed the new argument, wrote the reproduction code and performed the internal proof critiques.

McGuire, Schlesinger and Williams supplied the circuit-to-cutwidth reduction. Arthur Ostapenko, mooselumph and earlier CircuitBreaker contributors developed the norm-graph, prefix and comparison framework. Galarnon42 supplied the global crossing-cover optimization and finite path bound. DarkWingMcQuack and the preceding contributors supplied the immediate coefficient and exact arithmetic framework. [Complete references](submission/proof.md#6-sources-and-reproduction)
