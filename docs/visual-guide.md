# Visual guide: the life of robotics data

> Status: informative. These diagrams are discussion aids for every
> perspective. They are written as Mermaid or plain SVG so anyone can propose
> changes through a pull request. Numbers in examples are illustrative.

Colour convention used across diagrams:

- **Green**: measured source evidence
- **Amber**: estimated values (reconstruction, pose estimation, clock mapping)
- **Blue**: exact derivations (frame transforms, resampling, action construction)
- **Purple**: retargeted or simulated values
- **Grey**: packaging and delivery

## 1. Lifecycle

Data is captured once, preserved as evidence, and turned into many products.
Feedback from customers and evaluation flows back into curation or new capture.

```mermaid
flowchart TD
    K["Contract / requirement<br/>what the consumer needs"] -. preflight before capture .-> C
    C["Capture<br/>teleop · UMI · egocentric · sim"] --> I["Ingest<br/>integrity · clocks · consent"]
    I --> E[("Source evidence<br/>immutable")]
    E --> D["Derivations<br/>alignment · trajectories · poses · labels · embeddings"]
    D --> Q["Curation<br/>filter · fraud review · dedup · rebalance"]
    Q --> P["Product tiers<br/>named capability sets"]
    P --> R["Release<br/>preflight · lineage · loss report"]
    K --> R
    R --> DL["Customer delivery<br/>LeRobot · MCAP · Zarr · custom"]
    R --> TV["Training view<br/>aligned shards · latents"]
    DL --> FB{"Feedback"}
    TV --> FB
    FB -- "rejection · eval failure" --> Q
    FB -- "capability gap" --> C
    OV["Operator versions"] -. "new version marks<br/>dependents stale" .-> D

    classDef evidence fill:#d9f2e3,stroke:#2e8b57,color:#1b1b1b
    classDef derived fill:#dbe8fb,stroke:#3b6fb6,color:#1b1b1b
    classDef pkg fill:#e8e8e8,stroke:#777,color:#1b1b1b
    class E evidence
    class D,Q,P derived
    class OV derived
    class R,DL,TV pkg
```

## 2. Who touches which stage

Each perspective enters the lifecycle at different points and cares about
different things. See [perspectives](perspectives/README.md).

![Roles against lifecycle stages](assets/perspectives-map.svg)

## 3. Lineage of one training sample

Every value in a delivered sample should be explainable back to evidence, with
its epistemic role visible. Optional retargeted joints appear only when the
contract allows them.

```mermaid
flowchart TD
    subgraph EV["Source evidence"]
        vf["wrist video<br/>frame #3712"]
        imu["IMU stream"]
        grip["gripper encoder"]
        cal["camera calibration v3"]
    end
    cm["clock mapping sync_v4<br/>residual 0.8 ms"]
    vio["VIO trajectory v2.1"]
    sel["select latest_available<br/>max age 60 ms"]
    rel["relative to<br/>window anchor"]
    ik["IK retarget<br/>to robot model"]
    subgraph S["Delivered sample · t = 12.40 s on 20 Hz grid"]
        oi["observation.image"]
        os["observation.ee_pose"]
        ac["action<br/>anchor-relative chunk"]
        aj["action.joints<br/>optional"]
    end
    vf --> sel
    cm --> sel
    sel --> oi
    vf & imu & cal --> vio
    cm --> vio
    vio --> os
    vio --> rel --> ac
    grip --> ac
    rel -. "only if contract allows" .-> ik -.-> aj

    classDef evidence fill:#d9f2e3,stroke:#2e8b57,color:#1b1b1b
    classDef estimated fill:#fbe9c9,stroke:#c98a1a,color:#1b1b1b
    classDef exact fill:#dbe8fb,stroke:#3b6fb6,color:#1b1b1b
    classDef retarget fill:#eadcf7,stroke:#7d4bb3,color:#1b1b1b
    classDef out fill:#ffffff,stroke:#777,color:#1b1b1b
    class vf,imu,grip,cal evidence
    class cm,vio estimated
    class sel,rel exact
    class ik,aj retarget
    class oi,os,ac out
    style EV fill:none,stroke:#2e8b57,stroke-dasharray:4 3
    style S fill:none,stroke:#777,stroke-dasharray:4 3
```

## 4. Time: native clocks, explicit alignment

Streams keep their own clocks. Alignment is a versioned mapping; the aligned
grid is a view with a declared selection policy and a declared failure mode.

![Multi-clock alignment onto a 20 Hz grid](assets/time-model.svg)

## 5. Action representations

The same trajectory can be encoded in three different ways. A single
`relative: true` flag cannot tell them apart.

![Absolute, anchor-relative, and delta actions](assets/action-representations.svg)

## 6. What is an hour? Metering from capture to delivery

Illustrative numbers. Delivering the same episodes as both LeRobot and MCAP
does not change delivered hours.

```mermaid
sankey-beta
Raw hours,Accepted hours,720
Raw hours,Rejected quality,150
Raw hours,Rejected fraud,30
Raw hours,Rejected duplicate,60
Raw hours,Rejected consent,40
Accepted hours,Delivered hours,650
Accepted hours,Outside product tier,70
```

## 7. Compute or store?

A derivation's materialization policy depends on compute cost, read frequency,
storage cost, and algorithm stability. Unstable algorithms push expensive
results toward `cached` rather than `persisted`.

```mermaid
quadrantChart
    title Materialization policy
    x-axis Cheap to compute --> Expensive to compute
    y-axis Rarely read --> Frequently read
    quadrant-1 persisted
    quadrant-2 on_read
    quadrant-3 on_read
    quadrant-4 cached, or persisted if stable
    Undistortion: [0.15, 0.70]
    Resampling: [0.20, 0.85]
    Frame transforms: [0.10, 0.60]
    VIO trajectory: [0.85, 0.75]
    Hand pose: [0.72, 0.62]
    Embeddings: [0.60, 0.90]
    Preview video: [0.58, 0.30]
    Dense reconstruction: [0.80, 0.15]
```

## 8. Training data shape by scale

Storage format and training format are different products. Thresholds are
hypotheses to be validated with published benchmarks.

```mermaid
flowchart LR
    A["~100 h<br/>fine-tuning<br/><br/>LeRobot v3 read directly<br/>online video decode"] --> B["~1k–10k h<br/>multi-node<br/><br/>pre-aligned shards<br/>training-resolution video<br/>precomputed action chunks"] --> C["~100k–1M+ h<br/>foundation model<br/><br/>read-only mmap arrays<br/>latents instead of pixels<br/>packed windows · mixture manifest"]
    classDef tier fill:#dbe8fb,stroke:#3b6fb6,color:#1b1b1b
    class A,B,C tier
```
