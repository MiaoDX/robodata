# Perspective: data supplier

> Status: draft, informative. Intended for open discussion.

A data supplier collects robotics data (teleoperation on physical robots,
embodiment-free capture such as UMI grippers and egocentric rigs, and
simulation), processes it, stores it long-term, and delivers derived products
to many downstream customers with different format and semantic requirements.

The supplier's core tension: **keep one trustworthy source of truth at a
controlled cost, while serving many consumers who each want a different view
of it.**

## 1. Three layers: evidence, derivations, deliveries

| Layer | Contents | Mutability | Cost profile |
|---|---|---|---|
| Source evidence | Native capture: video, IMU, gripper signals, joint logs, clocks, calibration inputs | Immutable | Dominant storage cost; kept long-term |
| Derivations | Anything computable from evidence: trajectories, poses, annotations, embeddings, previews, aligned views | Versioned; regenerable | Compute cost, optionally traded for storage |
| Deliveries | Customer- or workload-specific packages (LeRobot, MCAP, Zarr, custom) | Immutable per release; regenerable from lineage | Transient; ideally a cache |

This follows the architecture's separation of evidence, RDIR, and delivery
contracts. The supplier-specific point is operational: **only the evidence
layer is irreplaceable.** Every other byte is, in principle, a cache with
lineage.

## 2. Compute or store: explicit materialization policy

A strictly non-redundant store (never persist what can be recomputed) minimizes
storage but can be ruinous in compute when a derivation is expensive and read
often. The supplier needs an explicit, per-derivation decision.

Proposed concept: every derived component declares a **materialization policy**.

| Policy | Meaning |
|---|---|
| `on_read` | Computed on access; never persisted |
| `cached` | Persisted for performance; may be evicted at any time and rebuilt |
| `persisted` | Retained as a durable derived component; still carries full lineage |

The decision weighs four quantities:

- compute cost of one derivation run;
- expected number of reads over the retention period;
- storage cost for the same period and storage tier;
- **algorithm stability**: how likely the operator version is to change.

Illustrative defaults:

| Derivation | Suggested policy | Reason |
|---|---|---|
| Undistortion, frame transforms, resampling | `on_read` | Cheap; parameters differ per consumer |
| VIO/SLAM 6-DoF trajectory | `persisted` | Expensive; algorithm relatively stable |
| Hand/body pose estimation | `persisted`, versioned | Expensive; models improve, so re-runs per version must be possible |
| Embeddings, deduplication fingerprints | `persisted` | Reused constantly for search and curation |
| Low-resolution preview video | `cached` | Cheap to rebuild; suitable for cold tier or eviction |

A `persisted` component is still semantically a derivation. When an operator
version changes, lineage identifies which components are stale and which
releases depend on them; the supplier then decides whether to recompute,
without silently rewriting historical deliveries.

## 3. Delivery formats: recommended defaults, others on request

| Format | Recommended use |
|---|---|
| LeRobot (v3) | Default training delivery; largest open ecosystem |
| MCAP | Lossless exchange, pipeline hand-off, visualization; best preserves multi-clock, multi-topic structure |
| Zarr | Array-heavy workloads needing chunked random access (common in UMI / diffusion-policy style pipelines) |

Any other target is produced by RDX under a delivery contract. Every
conversion ships a **loss report**: for example, "multi-clock timing collapsed
to one timeline", "raw calibration omitted", "estimated pose delivered in a
field conventionally read as measured".

Two market conventions are worth adopting explicitly:

- **Multiple representations of the same episodes are not additional data.**
  Delivering LeRobot and MCAP copies of one capture does not double its hours.
- **Add-on annotations do not add hours.** They add capabilities.

## 4. Metering: what is an hour?

Suppliers, crowdsourced collectors, and customers all price and plan in hours,
but they often mean different things. The substrate should support at least
three distinct, auditable quantities:

| Quantity | Definition |
|---|---|
| `raw_hours` | Captured or uploaded duration |
| `accepted_hours` | Duration surviving quality review, fraud review, and deduplication |
| `delivered_hours` | Duration of unique source evidence contained in a release, per contract rules |

Each should be computed by interval algebra over required modalities, with
rejection reasons recorded as a distribution. Multiple cameras do not multiply
hours; resampling does not create evidence.

## 5. Products: modality-layered SKUs

Public releases in the market already organize data as layered products: the
same capture base offered with different viewpoint sets (head, wrist,
third-person) and supervision depths (hand pose, full-body pose, semantic
segments, force). In RoboData terms, a product tier is a **named set of
required capabilities** over shared evidence, not a separate dataset.

## 6. Curation metadata consumers increasingly expect

- Taxonomy: environment/scene, task, subtask, atomic action, instruction;
  versioned vocabularies.
- Diversity statistics per 1,000 hours: unique tasks, objects, environments.
- Concentration: hours per collector and per site.
- Near-duplicate rate and rebalancing weights.
- Per-frame or per-segment quality flags with problem types.

## 7. Consent, privacy, and residency

- Consent scope as an enumerated, machine-readable field (collection,
  annotation, controlled release, commercial training, resale) with
  revocation state.
- De-identification state (pending, processed, human-verified) and method.
- Presence of third parties or minors in frame.
- Data residency and cross-border transfer status, propagated through lineage
  into previews, embeddings, caches, and training shards.

## Open questions

- Should materialization policy live in RDIR, or only in an implementation
  profile?
- What is the minimum metering rule set that both supplier and customer can
  reproduce independently?
- How are consent revocations propagated to already-delivered immutable
  releases?
- Which taxonomy vocabularies can be shared across suppliers without
  exposing proprietary task design?
