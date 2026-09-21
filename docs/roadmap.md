# Initial roadmap

The roadmap prioritizes falsifying the architecture with real data over growing a
large abstract schema.

## Phase 0 — Fixtures and semantic spike

- Acquire small, redistributable fixtures representing UMI, egocentric capture,
  physical robot logs, and simulation.
- Inventory native clocks, frames, metadata, missingness, and epistemic roles.
- Define the smallest RDIR descriptors required to describe those fixtures
  without semantic promotion.
- Write executable tests for time mapping and pose/action conventions.

**Exit criterion:** all four fixture families can be inspected through one
logical interface without forcing them into one synchronized episode table.

## Phase 1 — Thin vertical slice

- Implement component identity, descriptors, capability profiles, lineage, and
  release manifests.
- Implement a small RDX planner with typed operators for selection, resampling,
  coordinate conversion, and action representation.
- Build source adapters for one sample from each source family.
- Export LeRobot, schema-aware MCAP, and one real customer contract.
- Validate each export with the consumer's actual reader.

**Exit criterion:** a release can explain exactly how every output sample maps to
source evidence and why an unsupported contract cannot be produced.

## Phase 2 — Operational hardening

- Add clock resets, drift, drops, out-of-order records, and incomplete uploads to
  adversarial tests.
- Add versioned calibration revisions and delivery diffs.
- Enforce authorization and retention over derived artifacts and caches.
- Add resumable execution, content-addressed caching, and deterministic builds.
- Benchmark cold and warm behavior for browsing, sparse training reads,
  continuous playback, and batch export.

**Exit criterion:** failures are explicit, releases are reproducible, and storage
choices are backed by workload measurements.

## Phase 3 — Extensibility

- Stabilize the public descriptor and adapter APIs.
- Add schema migration and semantic compatibility tooling.
- Add new modalities through components rather than changes to a universal row.
- Publish a conformance suite and reference fixtures.

## Cross-phase acceptance tests

| Scenario | Required behavior |
|---|---|
| Export the same asynchronous capture at 20 Hz and 50 Hz | Source streams stay unchanged; both sampling policies and mappings are inspectable |
| Request measured robot joints from EGO video | Preflight rejects the capability gap; no zero-filled substitute |
| Revise calibration or action representation | New derivations are created; old release dependencies remain resolvable |
| Swap joint order or quaternion convention | Semantic compatibility tests fail |
| Reset a clock or drop/duplicate frames | No silent cross-stream mismatch or fabricated continuity |
| Deliver a licensed subset | Packaged bytes and derived dependencies contain no unauthorized data |
| Add tactile or human-pose data | New components and adapters suffice; existing schemas are not rewritten wholesale |
| Load with the target reader | Keys, types, shapes, time windows, and action meaning pass consumer-side tests |
