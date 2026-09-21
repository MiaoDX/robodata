# Architecture

This document describes the intended boundaries of RoboData. It is a design
baseline, not yet a stable specification.

## System model

RoboData separates evidence, meaning, computation, and packaging:

| Layer | Responsibility | Must not do |
|---|---|---|
| Source evidence | Preserve native records, clocks, identifiers, and capture metadata | Pretend missing capabilities were captured |
| RDIR | Give streams stable logical identity and explicit semantics | Require one file layout or synchronized table |
| RDX | Type-check and execute transformations with lineage and loss reporting | Hide interpolation, estimation, or retargeting |
| Delivery contract | Define a consumer-specific, testable product | Become the internal source of truth |
| Physical views | Optimize storage, browsing, training, and export workloads | Redefine sample identity or semantic meaning |

The architecture supports references to immutable source objects as well as
materialized components. Ingestion does not require immediate duplication into a
new monolithic canonical file.

## RDIR primitives

The semantic IR is component-oriented. Components may evolve and be regenerated
independently while retaining common asset identity and lineage.

| Primitive | Purpose |
|---|---|
| Asset | Durable identity for a captured or generated body of evidence |
| Component | Independently versioned logical data such as video, joint state, pose, calibration, or annotation |
| Stream | Ordered observations or events in a declared clock domain |
| Interval | Start/end validity, exposure, execution, or availability range |
| Entity | Robot, human, device, object, articulation, or named part |
| Frame | Named coordinate system connected by known static or dynamic transforms |
| Descriptor | Type, shape, units, axes, reference frame, role, and representation |
| Capability | Machine-checkable statement of what an asset can support |
| Derivation | Inputs, operator, configuration, software/model version, and outputs |
| Release | Immutable closure of data objects, schemas, dependencies, and checks |

Stable logical IDs must not encode a shard path, byte offset, or row number.

## Time is native, not reconstructed from row position

Every record retains a source timestamp and clock domain. When available, it may
also carry device sequence numbers, capture intervals, and host arrival times.
Cross-clock alignment is a versioned mapping with method, parameters, residuals,
valid range, and quality—not an overwritten timestamp column.

Aligned training tables are views. Their contract must state the output grid,
selection policy, interpolation policy, maximum age, tolerance, and behavior when
a required stream is missing.

Clock resets, wraparound, drift, out-of-order arrival, duplicated frames, and
partial uploads are expected conditions and require explicit representation.

## Geometry and embodiment

Frames form a named graph of static and dynamic `SE(3)` relationships. Every
pose descriptor declares transform direction, parent and child frames, units,
axis conventions, and rotation representation.

The entity model must accommodate robot kinematic chains, human skeletons, and
handheld devices without fabricating a robot URDF for every source. Unknown scale
or an unknown transform remains unknown. Calibration has an identity, version,
validity range, and provenance.

## State, observation, command, and action are different roles

An array becomes meaningful only with a descriptor. At minimum, action-like data
declares:

- controlled entity and part;
- joint, end-effector, task, or other control space;
- physical quantity and control mode;
- absolute, fixed-anchor-relative, or stepwise-delta representation;
- reference frame and reference instant;
- axes, joint ordering, units, and rotation convention;
- horizon, time offsets, and validity interval;
- source role and execution status.

For poses `T_k = T_(W<-E_k)`, fixed-anchor relative motion and stepwise deltas are
different operations:

```text
R_k     = inverse(T_0)     * T_k
Delta_k = inverse(T_(k-1)) * T_k
```

RDIR permits mixed representations in one logical action—for example, a relative
arm trajectory and absolute gripper width—so a single coarse `relative: true`
flag is insufficient.

The following distinctions are invariant:

```text
measured != estimated != commanded != executed
demonstrated != retargeted != simulated ground truth
```

Retargeting a UMI trajectory into a robot's joint space may create a legitimate
derived training target. It does not prove that those joints executed that
trajectory during capture.

## Capability profiles

Assets advertise granular capabilities rather than conforming to one maximal
schema. Examples include:

```text
ego.rgb
ego.hand_pose.estimated
umi.ee_motion.metric
robot.joint_command.recorded
sim.contact.ground_truth
```

Missingness is also typed: not collected, dropped, occluded, estimation failed,
redacted, not applicable, or unknown. RDX checks a delivery contract against
capabilities before scheduling work.

## RDX transformation graph

RDX behaves like a typed compiler pipeline:

```text
contract -> capability check -> plan -> validate -> execute -> verify -> release
```

Operators may include clock mapping, interval selection, quality filtering,
resampling, coordinate transformation, action construction, modality mapping,
encoding, and sharding.

Every operator declares:

- input and output semantic types;
- preconditions and external dependencies;
- deterministic configuration and implementation version;
- whether it is exact, estimated, retargeted, or lossy;
- new derivation and source-sample mappings;
- validation properties and failure behavior.

A preflight report classifies contract requirements as directly satisfiable,
derivable, lossy-but-allowed, estimation or retargeting required, or impossible
without recapture. A delivery report records discarded intervals, interpolation,
frame reuse, calibration, estimates, and content hashes.

## Storage and physical views

RoboData specifies semantics and interfaces before byte layout. Mature encodings
should be reused where they fit:

- preserve source-native capture objects;
- use schema-aware containers such as MCAP for appropriate recorded streams;
- use standard media codecs with explicit timestamp mappings;
- use columnar numeric layouts for states, actions, trajectories, and indexes;
- keep descriptors, calibration, lineage, and manifests independently versioned;
- generate customer and workload-specific layouts from the same logical asset.

Chunking considers both co-read patterns and authorization boundaries. Preview
images, embeddings, annotations, caches, and training shards inherit access and
retention constraints through their derivations.

## Release invariant

A delivery release is an immutable, auditable closure. It is published only when:

1. every required object, schema, calibration, descriptor, and derived component
   is fixed by version or content digest;
2. authorization has been evaluated over the actual packaged bytes and all
   dependencies;
3. the target reader validates keys, types, shapes, time windows, and action
   interpretation;
4. provenance and loss reports are complete;
5. the release can still be interpreted after internal mutable systems change.

## Explicit non-goals for the first release

- Inventing a universal binary container.
- Supporting every robotics format or modality.
- Replacing object storage, catalogs, workflow engines, or media codecs.
- Claiming transparent conversion between source capabilities that are not
  semantically equivalent.
- Selecting a universal shard size or sample frequency without workload data.
