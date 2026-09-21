# Deep research synthesis

> Status: informative research note, not a normative specification. This document
> consolidates the research and design discussion that initiated RoboData.

## Executive recommendation

RoboData should be built around three mutually reinforcing ideas:

1. a **componentized, asynchronous, multi-clock semantic IR** as the durable
   internal model;
2. **versioned delivery contracts** as the shared constraint between collection
   and customer delivery;
3. a **typed transformation system** with provenance and loss reporting as the
   core engineering asset.

The project should standardize facts, time, physical semantics, and lineage. A
consumer's sampling frequency, action representation, and file layout are derived
products—not the definition of the source data.

## Research scope and lenses

The investigation considered the problem from several independent perspectives:

- heterogeneous producers: UMI, egocentric devices, physical robots, simulators;
- training consumers: LeRobot, GR00T-style pipelines, and customer-specific readers;
- recording and interchange: MCAP and Project Aria VRS;
- component-oriented data models and coordinate conventions: NVIDIA NCore;
- database evolution and physical/logical separation: Iceberg, Lance, Arrow;
- data compiler design: typed operators, preflight, deterministic releases;
- data-company operations: licensing, customer isolation, quality, billing,
  rejection, and recapture loops.

The goal was not to choose a fashionable container. It was to identify invariants
that prevent silent semantic corruption as data moves between systems.

## The central modeling error to avoid

A synchronized episode table is a useful consumer view, but a poor universal
source model. It tends to make the following assumptions invisible:

- every modality shares one clock and one meaningful sample index;
- one timestamp denotes an instantaneous observation;
- missing data can be represented by zero or an unexplained `NaN`;
- `action` has one meaning across embodiments and controllers;
- coordinate frames and calibrations are fixed and universally known;
- a target-format row is interchangeable with source evidence.

Those assumptions fail for real sensors, reconstructed motion, control loops,
simulation, and customer-specific delivery rules. RoboData should preserve native
asynchrony, then create explicit aligned views.

## Unknown-unknown reduction matrix

The following issues are easy to miss because happy-path conversions can appear
correct even when their meaning is wrong.

| Lens | Hidden failure | Architectural response | Validation question |
|---|---|---|---|
| Time | Host arrival time is mistaken for exposure or device time | Named clock domains, intervals, versioned mappings, residuals | Can every aligned sample explain its source time and selection rule? |
| Geometry | Pose direction, units, scale, or handedness are implicit | Typed frame graph and `SE(3)` convention | Does inverse/composition round-trip on fixtures? |
| Action | Relative-to-current is confused with stepwise delta | Descriptor per action slice and reference instant | Can the exact absolute target be reconstructed? |
| Evidence | Estimated or retargeted values are labeled as measured/executed | Epistemic roles and derivation lineage | What observation or process justifies this field? |
| Missingness | Occlusion, drop, redaction, and inapplicability collapse together | Typed absence reason and validity mask | Can a consumer distinguish retryable quality issues from unavailable capability? |
| Simulation | Ground truth is exported as if observable at deployment | Observability and source-role metadata | Would the real robot possess this signal at inference time? |
| Quality | One global `is_good` determines every product | Raw metrics plus versioned product rules | Good for which product, under which rule and processing version? |
| Identity | Sample IDs encode file offsets or row positions | Stable logical IDs and source mappings | Do IDs survive repacking, transcoding, and resharding? |
| Schema | Same dtype/shape is treated as semantic compatibility | Stable field identity plus semantic versioning | Would a unit, frame, role, or ordering change be detected? |
| Reproducibility | A random seed is considered a complete simulation recipe | Assets, engine, code, config, randomization, and step rates fixed | Can the published asset be regenerated in a clean environment? |
| Security | Access control covers directories but not derivatives or shared shards | Policy propagation through lineage and byte-level release checks | Can unauthorized source material leak through previews, caches, or packaging? |
| Release | A SQL query or metadata snapshot is called a delivery snapshot | Immutable dependency closure with digests | Does the release still work after internal mutable state changes? |
| Operations | “Valid hours” is inferred by adding camera durations | Auditable interval algebra over required modalities and exclusions | Can both parties reproduce the billed duration? |
| Feedback | Customer complaints reference mutable row numbers | Release-scoped stable IDs and intervals | Can a rejection identify the exact bytes, semantics, and processing version? |

## Source families share a base model, not identical capabilities

| Source | Preserve | Never assume |
|---|---|---|
| UMI | Original video, gripper signals, reconstructed poses, calibration, trajectory quality, demonstration semantics | Measured robot joints, executed commands, or measured torques |
| Egocentric capture | First-person media and, when available, hands, body, camera trajectory, tasks, and device perception | Directly executable robot actions |
| Physical robot | Sensors, joint state, controller commands, authority, model and controller configuration | Every state is measured or every predicted action was executed |
| Simulation | Observations, state, action, assets, environment, generation process, and physics/control/render rates | Every ground-truth field is observable on a deployed robot |

This motivates capability profiles. An exporter asks whether required capabilities
exist and whether derivations are allowed. It does not wait until serialization to
discover absent columns.

Project Aria's VRS organization is useful evidence for keeping sensor records and
device-computed perception in explicit streams. MCAP demonstrates a mature,
schema-aware recorded-message container. Neither alone supplies RoboData's full
semantic, derivation, or delivery-contract model.

## Time model

Robotics pipelines routinely contain sensor clocks, device monotonic clocks, host
clocks, simulation time, control ticks, and media presentation time. A mapping
between two clocks is itself a derived artifact. It can change when synchronization
is recalibrated.

The IR should retain:

- source timestamp and source clock identity;
- sequence number where provided;
- start and end time for non-instantaneous acquisition or validity;
- optional arrival/ingestion timestamps, clearly labeled;
- mapping identity, algorithm, parameters, residual/error statistics, and valid range;
- discontinuities such as reset, wraparound, or epoch changes.

An aligned view additionally fixes the output grid and policies for nearest/latest
selection, interpolation, maximum age, tie-breaking, and missing streams. Repeated
use of a video frame is legitimate when declared; it is corruption when hidden.

## Geometry and action semantics

NCore provides a useful model of named frames joined by static and dynamic
`SE(3)` transforms. RoboData needs the same explicitness while supporting robots,
humans, and handheld devices in one entity model.

Action descriptors require more than a vector shape:

| Dimension | Examples |
|---|---|
| Entity and part | left arm, right arm, base, gripper |
| Space | joint, end-effector, task |
| Quantity/mode | position, velocity, torque, impedance target |
| Representation | absolute, fixed-anchor relative, stepwise delta |
| Reference | world, base, tool, prediction-start state |
| Axes and units | named joints and order; radians, metres, newtons |
| Rotation | quaternion order, matrix convention, or Lie algebra convention |
| Time structure | single command, horizon, per-point offsets, validity/execution interval |
| Role | demonstration, command, prediction, executed command, retargeted target |

LeRobot's action documentation confirms that fixed-anchor relative chunks and
sequential delta chunks are different representations, and that gripper values may
remain absolute while arm values are relative. Joint/end-effector conversion also
requires an embodiment-specific kinematic model.

The critical boundary is epistemic: inverse kinematics can derive a joint target
from an end-effector trajectory, but cannot establish that the target was the
historical command or measured joint state.

## Logical model versus physical storage

The first release should not invent a new low-level binary format. The durable
project-owned surface is the schema, semantics, manifests, clock and action
models, conversion rules, and identity/index conventions.

A pragmatic layout strategy is:

| Content | Initial physical strategy |
|---|---|
| Source capture | Preserve native format; consider MCAP plus explicit schemas for owned recorders |
| Video/audio | Preserve original encodings or quality-constrained transcodes with separate time mapping |
| State/action/trajectory/indexes | Columnar numeric organization behind one logical interface |
| Descriptors/calibration/lineage | Independently versioned components and manifests |
| Customer delivery | Generated from a contract into LeRobot, MCAP, or customer layouts |
| Training acceleration | Derived workload-specific copies, never the only source of truth |

Database systems offer three transferable ideas:

1. Iceberg-style stable field identity enables renaming and reordering without
   relying on position; RoboData must additionally version physical meaning.
2. Component/column-oriented updates let derived pose or annotation be replaced
   without transcoding all media.
3. Query, review, playback, training, and delivery can use different physical
   views while sharing identity and lineage.

Chunking must optimize both co-reading and co-authorization. Time windows, media
decode boundaries, object size, modality groups, customer rights, and retention
all matter. Shard and GOP sizes should follow measured workloads, not doctrine.

## RDX as a typed compiler

The most defensible long-term engineering asset is not a collection of customer
scripts. It is a planner and executor with a flow like:

```text
read contract
  -> check source capabilities
  -> construct typed transformation graph
  -> validate preconditions
  -> execute deterministically
  -> test with the target reader
  -> publish release and loss report
```

Transformations fall into distinct risk classes:

| Request | Classification |
|---|---|
| Rename/reorder fields or reorder quaternion components | Representation change; convention validation required |
| Convert units or frames | Mathematical transform; units/calibration required |
| Resample, crop, transcode | Potentially lossy; quality and source mapping required |
| Robot joints plus model to end-effector pose | Kinematic derivation |
| UMI motion to a robot's joint targets | Retargeting/planning product, not simple format conversion |
| EGO video to measured robot torque | Impossible as source fact; any estimate must be labeled derived |

Preflight should return a structured explanation rather than a boolean: direct,
derived, lossy, estimated/retargeted, or requires recapture. The same contract
mechanism should run before collection so capability gaps are found before data is
captured.

## Data-company operational requirements

These concerns deserve first-class design because they are easy to postpone and
expensive to retrofit.

### Product-specific quality

Store raw quality signals. Apply versioned policies per product, calibration, and
processing release. A trajectory can be acceptable for semantic pretraining and
unacceptable for precision imitation learning.

### Auditable quantity

“Valid hours” should be interval-based and contract-defined: required modalities
simultaneously valid, with explicit treatment of setup, idle, reset, failed tasks,
and human review. Multiple cameras do not multiply task hours, and resampling does
not create new evidence.

### Customer isolation

Rights and retention follow the asset and derivation graph into previews,
annotations, embeddings, caches, and training shards. Final packages must be
inspected for actual unauthorized bytes, especially after clipping or shared
sharding.

### Versioned interpretation

Source, calibration, processing, semantics, physical layout, and contract have
separate versions. A new calibration creates new derived results; it does not
silently rewrite historical deliveries.

### Black-box feedback

A useful loop does not require customer model access. Track technical acceptance,
semantic defects, quality rejection, coverage gaps, and recapture requests against
the exact release and stable source interval.

## Recommended V1

V1 should prove one end-to-end slice across UMI, EGO, physical robot, and
simulation, exporting to LeRobot, schema-aware MCAP, and one actual customer
format. Its core should include:

- domain schema and registry;
- native time and clock mappings;
- calibration and explicit action descriptors;
- capability profiles and typed missingness;
- a small set of typed RDX operators;
- machine-readable delivery contracts;
- immutable release manifests and target-reader tests.

Object storage, metadata databases, and orchestration can use mature systems.
Avoid introducing multiple lakehouse stacks, vector databases, or custom
containers before the workload demonstrates a need.

The SDK should expose three visibly different operations: read native streams,
construct an aligned view, and export under a contract. A generic `load_episode()`
must not silently resample, transform coordinates, or construct actions.

## Performance evaluation

Benchmark at least four workloads independently:

- interactive random access to short intervals;
- sparse frame access during training;
- continuous long-form media playback;
- batch delivery compilation.

For each, record cold and warm throughput, time to first result, object requests,
decode cost, CPU/GPU use, and memory. Use the results to select grouping, chunking,
indexes, caching, and materialization.

## Open questions to resolve with fixtures

- What is the smallest descriptor vocabulary that covers the four source families
  without creating generic escape hatches?
- Which IDs are content-derived, assigned, or namespaced, and how are partial
  re-uploads reconciled?
- Which clock mapping families and error models are needed in practice?
- How should semantic compatibility be versioned independently from serialization?
- What is the minimum release manifest needed for offline verification?
- How are authorization policies evaluated on mixed-source derived components?
- Which operator boundaries produce useful caching without fragmenting lineage?
- Which metrics predict customer acceptance for each product category?

These questions should be answered through representative fixtures and adversarial
tests before freezing a public specification.

## References

Primary sources reviewed during the research:

- [Universal Manipulation Interface](https://github.com/real-stanford/universal_manipulation_interface) — capture, SLAM/trajectory processing, and relative trajectory motivation.
- [LeRobot action representations](https://huggingface.co/docs/lerobot/action_representations) — joint versus end-effector space and absolute, relative, and delta semantics.
- [NVIDIA NCore specification](https://nvidia.github.io/ncore/data/conventions.html) — named coordinate systems, static/dynamic `SE(3)` transforms, and acquisition intervals.
- [MCAP specification](https://mcap.dev/spec) — schema-aware channels, messages, attachments, metadata, and chunked records.
- [Project Aria VRS data format](https://facebookresearch.github.io/projectaria_tools/gen2/technical-specs/vrs/data-format) — multimodal sensor and on-device perception streams.
- [Isaac Lab manager-based environment tutorial](https://isaac-sim.github.io/IsaacLab/main/source/tutorials/03_envs/create_manager_rl_env.html) — distinct simulation step, control decimation, and render interval.
- [Apache Iceberg schema evolution](https://iceberg.apache.org/docs/latest/evolution/) — stable field identity and safe schema evolution.
- [Lance format](https://lance.org/format/) — independently evolvable columnar fragments and workload-oriented storage.
- [Apache Arrow IPC](https://arrow.apache.org/docs/python/ipc.html) — stream/file formats and memory-mapped access boundaries.

These systems are precedents, not dependencies or endorsements. RoboData combines
their useful ideas around a robotics-specific semantic and delivery boundary.
