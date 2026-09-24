# Perspectives

> Status: informative. Perspectives are discussion documents, not normative
> requirements.

RoboData defines one shared semantic substrate (RDIR) and one transformation
model (RDX). Different participants in the robotics data ecosystem use that
substrate for different purposes and care about different trade-offs.

A perspective document answers, for one role:

- what this role must pay attention to when producing or consuming data;
- which RoboData concepts it relies on most;
- which trade-offs it faces and how RoboData lets it make them explicitly;
- which open questions it would like the community to resolve.

Perspectives do not represent any single company. They describe a role that
many organizations share. Every normative feature proposed for `spec/` should
be traceable to a need stated in at least one perspective.

## Current perspectives

| Perspective | Role | Status |
|---|---|---|
| [Data supplier](data-supplier.md) | Collects, processes, stores, and delivers robotics data to multiple customers | Draft |
| [Training consumer](training-consumer.md) | Trains policies or foundation models on robotics data at different scales | Draft |

## Planned perspectives

- Evaluation and benchmarking
- Data platform and tooling (lakehouse, catalog, visualization, annotation)
- Marketplace, licensing, and audit
- Privacy, consent, and data subjects

Contributions of new perspectives are welcome. Keep them role-based,
vendor-neutral, and grounded in concrete workflows.
