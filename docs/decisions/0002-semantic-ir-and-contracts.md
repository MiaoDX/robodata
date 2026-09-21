# ADR-0002: Separate semantic facts from delivery products

- Status: Accepted
- Date: 2026-09-21

## Context

Robot data arrives from sources with incompatible capabilities: handheld UMI
devices, egocentric cameras, physical robots, and simulators. Consumers then ask
for fixed-rate episodes, different action spaces, or customer-specific layouts.
Treating one consumer layout as the canonical source either discards information
or silently invents semantics the source never possessed.

## Decision

RoboData will use three explicit layers:

1. **Source evidence** preserves native records, identifiers, clocks, and metadata.
2. **RDIR** describes logical components with typed time, geometry, action,
   provenance, quality, and access semantics.
3. **Delivery products** are produced under versioned, machine-readable contracts
   by RDX transformations.

Physical encodings are replaceable backends. A value's role—measured,
commanded, estimated, demonstrated, retargeted, simulated, or ground truth—is
part of its type and provenance, not inferred from a field name.

RDX operators must declare input and output types, preconditions, dependencies,
version, information loss, and derived lineage. A release is publishable only
after all required objects and dependencies are fixed and validated by the target
reader.

## Consequences

- The same source may produce multiple valid aligned views without rewriting the
  source streams.
- Capability checks can reject impossible requests instead of filling missing
  values with zeros.
- Retargeted or estimated actions cannot be mislabeled as executed commands.
- Implementations carry more metadata and validation logic than a flat episode
  table.
- Storage optimization must be measured against workloads and cannot redefine
  logical identity.

## Alternatives considered

- **One canonical episode table:** familiar to training pipelines, but erases
  asynchronous timing and encourages implicit semantics.
- **One universal binary container:** duplicates mature storage technology and
  couples logical evolution to byte layout.
- **Per-customer conversion scripts:** quick initially, but cannot provide shared
  type checking, loss reporting, or reproducible lineage.
