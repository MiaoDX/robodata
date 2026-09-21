# ADR-0001: Use RoboData, RDIR, and RDX at different abstraction levels

- Status: Accepted
- Date: 2026-09-21

## Context

The project needs a name that can survive uncertainty about whether its long-term
center of gravity becomes a specification, an SDK, a compiler-like runtime, or a
dataset release system. Three strong candidates emerged: `robodata`, `robodir`,
and `rdx`. Making one term carry every meaning would either constrain the scope
too early or make individual concepts harder to discuss.

## Decision

- **RoboData** is the project, repository, ecosystem, and SDK namespace.
- **RoboData IR (RDIR)** is the canonical semantic intermediate representation.
- **RDX (Robot Data Exchange)** is the typed transformation, validation, and
  delivery runtime and its eventual CLI.

The intended command-line vocabulary is concise and compiler-like, for example:

```console
rdx inspect capture.mcap
rdx validate capture.mcap --against contract.yaml
rdx compile capture.mcap --contract contract.yaml
rdx lineage delivery-release-0042
```

These commands illustrate the naming model; they are not yet implemented.

## Consequences

RoboData retains room to grow without implying that one physical format is the
product. RDIR gives specification work a precise name. RDX communicates movement
between producers and consumers and gives the runtime a short CLI name.

The project must consistently explain the three levels so that RDIR and RDX do
not appear to be separate, competing projects.

## Alternatives considered

- **`robodir` as the repository:** precise for an IR, but too narrow for quality,
  releases, contracts, adapters, and provenance.
- **`rdx` as the repository:** strong product vocabulary, but ambiguous outside
  robotics and biased toward exchange as the whole product.
- **`robot-data-core` or `robot-data-kernel`:** clear internally, but less useful
  as a public project identity.
