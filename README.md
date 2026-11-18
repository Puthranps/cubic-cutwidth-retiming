# Cubic cutwidth by retiming a Gaussian vertex ordering

For every cubic graph on $n$ vertices, the vertices admit an ordering with at most $0.130647519423167665n+o(n)$ edges crossing its busiest gap. The sublinear remainder is uniform over all such graphs. The proof also covers cubic multigraphs. The previous version gave $0.130647546423167665n+o(n)$. [Short proof of the improvement](research/two-pass-bound.md) · [Full graph theorem](submission/cutwidth.md#0-statement-and-proof-map)

## Bound and circuit consequence

Write $\kappa$ for the asymptotic worst-case cutwidth per vertex and $\Gamma$ for the limiting coefficient from the earlier Gaussian crossing-cover method. We prove $\kappa\leq\Gamma-4.7\times10^{-8}$. In the McGuire–Schlesinger–Williams normalization, $M=2\kappa\leq0.261295038846335330$. Their kernel-to-circuit theorem applies this universal graph bound to Li's function. For the separate validated-prefix norm-graph language entered in CircuitBreaker, the eventual full-binary-basis circuit lower bound is **$4.82709141518790465583497877634923n$**. [Original transfer theorem](https://github.com/rrwilliams0/circuit-lb-4.6155n/blob/a56500014ba159397903dea81d41ac836f6880d5/proof.md#24-kernels-and-the-reduction-from-circuits-to-kernels) · [CircuitBreaker proof](submission/proof.md)

## Why two passes help

In the first pass some vertices move earlier. In the second, eligible vertices move later using the updated order. Every successful move at a threshold decreases the maximum number of disjoint crossing edges there by one. Splitting the two directions into successive passes lets more vertices participate. Counting only the nine edges that the local probability estimate uses also strengthens the guarantee for graphs with few eligible vertices. [Two-pass argument](submission/cutwidth.md#76-two-passes-on-nine-edge-patches)

## Reproduction

Run `python -I -B submission/certify.py` from the repository root. The program uses the Python standard library. It encloses 47 Gaussian probabilities and checks the exact rational constants used by the proof. [Certificate derivation](submission/certificate.md) · [Reference output](research/certificate-output.json)

## Versions and review

Yukon's primary hosted reviewer marked the $2\times10^{-8}$ revision valid. Its container reproduced every finite-certificate output in 14.5 seconds. A separate automated audit timed out during final adjudication. The public entry is in review with no human verdict recorded. [Yukon judgment](https://api.yukon.org/api/submissions/60c7a1c3-9b1a-4c29-ad98-5de7c3ef351b) · [Hosted evaluation](https://github.com/Layr-Labs/circuitbreaker-llm-verifier/actions/runs/44235424767)

The first version established a $10^{-14}$ saving. Its separate hosted evaluation also marked it valid. [First proof](https://github.com/Puthranps/cubic-cutwidth-retiming/tree/7b0d2587b3da62877fea4fae2d4fa9a370f3919f) · [First official judgment](https://api.yukon.org/api/submissions/4c133ffa-7452-42c6-9629-d7821ee890d4)

Puthranps selected Williams's challenge, directed the AI investigation and requested a check that it advanced the existing bound. OpenAI Codex agents developed the new argument, wrote the reproduction code and performed the internal proof critiques.

McGuire, Schlesinger and Williams supplied the circuit-to-cutwidth reduction. Arthur Ostapenko, mooselumph and earlier CircuitBreaker contributors developed the norm-graph, prefix and comparison framework. Galarnon42 supplied the global crossing-cover optimization and finite path bound. DarkWingMcQuack and the preceding contributors supplied the immediate coefficient and exact arithmetic framework. [Complete references](submission/proof.md#6-sources-and-reproduction)
