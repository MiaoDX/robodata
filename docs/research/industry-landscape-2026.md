# Industry landscape: robotics data platforms and autonomous-driving lessons

> Status: informative research note, not a normative specification.
> Snapshot as of 2026-09-24. Figures marked *(company-reported)* come from
> press releases, marketing pages, or executive statements and have not been
> independently verified. Nothing here endorses any vendor.

## Summary

Robotics data companies converge on the same business shape: a collection
network, a processing and annotation engine, and delivery metered in accepted
hours. Public materials show strong convergence on delivery formats (LeRobot
v3 plus MCAP), metering, hierarchical task taxonomies, curation pipelines, and
consent/de-identification. No public material describes a machine-readable
semantic intermediate representation, typed action descriptors, or loss
reports. That gap is where RoboData's RDIR/RDX is positioned.

## 1. Robotics data companies

### Maniformer (觅蜂科技)

- Incubated by AgiBot; founded February 2026. Positions itself as a one-stop
  physical-AI data service spanning teleoperation, embodiment-free capture, and
  simulation.
- **MEgo hardware** (gripper and head-mounted rig), claimed sub-millisecond
  synchronization; designed to be isomorphic with the AgiBot G2 Air robot so
  UMI-style data maps directly to that embodiment.
- **MEgo Engine**, as publicly described: multi-source time alignment and
  filtering, 6-DoF trajectory and spatial reconstruction, multi-embodiment
  replay and scoring for quality checks, automated annotation.
- **"Maniformer Pai" (觅蜂派), launched 2026-09-23**: a crowdsourcing service,
  not a data format. Participants take tasks in an app, capture with MEgo
  devices, and are paid by reviewed effective duration. Workflow: accept task,
  capture, acceptance review, settlement. Supported by a "scene network"
  (venues supplying real environments) and a "people network" (contributors).
  Quality is described through five headline criteria (compliant, authentic,
  standard, not mixed, multi-site); detailed rules are not public.
  Scale during a one-month beta *(company-reported)*: about 20,000 registered
  users, 13,000 submitted tasks, 22 scene categories, 5,000+ tasks, 50,000+
  environments, 120+ standard atomic actions.
- Launched the "Hive data co-creation initiative" with national standards
  bodies; no standard text has been published.
- **Not public:** delivery format, schema, per-hour pricing, quality scoring
  algorithms, marketplace mechanics.

AgiBot World (the related open dataset) separates `state` (sensor feedback)
from `action` (commands to the hardware abstraction layer) in per-episode HDF5
files with per-task JSON action segments, and provides a LeRobot converter.
Its documentation notes that definitions may change across hardware and
software versions, illustrating the need for versioned semantic descriptors.

### Lightwheel (光轮智能)

- Simulation-first, expanded to egocentric human data. Product loop:
  EgoSuite (capture) → SimReady Foundry (reconstruction and expansion) →
  RoboFinals (evaluation) → deployment feedback.
- **EgoSuite-Open100K** with Hugging Face (announced 2026-08): 100,000 hours
  planned, first ~10,000 released. Organized as layered SKUs by viewpoint
  (head vs. head+wrist) and supervision (hand pose vs. hand+body pose).
- Dataset cards state that LeRobot and MCAP files are alternative
  representations of the same episodes and must not be counted as additional
  hours; temporal semantic annotations are a complimentary add-on.
- Data is distributed through mutable buckets where the current file listing
  and manifests are declared the source of truth.
- Public MCAP devkit (Apache-2.0) documents topics for session metadata, body
  and hand pose, semantic segments, and per-frame bad-frame flags with problem
  types, using Foxglove schemas for video and calibration.
- Declares automated de-identification with human verification and
  participant consent covering collection, annotation, controlled release, and
  licensed uses.

### Maxinsights

- Egocentric data vendor *(company-reported)*: 2M accumulated hours, up to
  450k hours/month capacity, 50,000 scenes.
- Hierarchy: Environment → Task → Subtask → Instruction; three complexity
  levels (single-step, multi-step, long-horizon with contact and recovery).
- Nine enrichment signals derived from video and sensors: video understanding,
  depth, object tracking, hand pose, upper-body pose, tactile force,
  localization, segmentation, point cloud.
- Emphasizes curation, search, and mixture assembly per model as the
  advantage at scale. No public format details.

### Figure Index

- Buyer-side, vertically integrated. Figure states that purchased data did not
  meet its throughput, diversity, or quality requirements, so it built a
  crowdsourced app.
- Five-stage pipeline: automated quality filtering → fraud review →
  embedding-based deduplication → quota and cluster rebalancing → hierarchical
  captions.
- Diversity expressed per 1,000 retained hours *(company-reported)*: 373
  unique tasks, 1,146 manipulated objects, 116 environments.
- Public figures are uploads, not accepted training hours: a reminder that
  metering must distinguish raw from accepted data.

### Others

- **Scale AI**: Physical AI Data Engine; with Universal Robots, capture of
  synchronized motion, force, and vision on production cobots.
- **Build AI**: Egocentric-10K and Egocentric-100K on Hugging Face,
  WebDataset shards organized by factory and worker, Apache-2.0; publishes
  per-worker hour concentration.
- **Service vendors** (e.g. Claru) publish clip-level schemas with privacy
  state machines (pending, blurred, reviewed).

## 2. Chinese standards relevant to data quality

- YD/T 6770-2026, embodied-intelligence benchmark test methods (effective
  2026-06-01).
- YD/T 6771-2026, embodied-intelligence dataset quality requirements and
  evaluation (effective 2026-11-01), with eight quality dimensions.
- GB/Z 218.1-2026, embodied-intelligence data quality, part 1: real data.

RoboData quality metadata should be mappable to these dimensions.

## 3. Autonomous-driving lessons

| Source | Transferable idea |
|---|---|
| NVIDIA NCore | Component-oriented storage (independent Zarr stores), named frame graph with static and dynamic SE(3) edges, microsecond timestamps, raw measurements first, fully non-redundant storage (derive on demand), labels as components with explicit reference frames, multiple component instances coexisting |
| Waymo Open Dataset v2 | Parquet component tables sharing key columns; download only needed components |
| Tesla data engine | Triggers as queries for mining rare cases; offline heavy-model auto-labeling; iterative loops |
| Lakehouse practice in industry | Unified store for structured tags, JSON metadata, and vector search; hot/cold tiering over Iceberg/Lance |
| MCAP / Foxglove | De facto log container and visualization schemas, already reused by robotics vendors |

What does **not** transfer directly:

- Driving has one embodiment and a narrow action space; robotics needs action
  representation descriptors, multi-embodiment support, and retargeting
  semantics.
- Shadow mode depends on a large production fleet; robotics substitutes are
  deployment rollouts fed back into data.
- Human demonstrations are the data itself, not a ground-truth comparison, so
  epistemic roles (demonstrated, estimated, retargeted) must be explicit.
- Privacy moves from public roads to homes and workplaces, making consent
  models more complex.

## 4. Implications for RoboData

Validated by the market; candidates for the public specification:

1. Product-tier (SKU) descriptors as named capability sets.
2. Metering with `raw`, `accepted`, and `delivered` hours, the no-double-count
   rule for alternative representations, and rejection-reason distributions.
3. Versioned hierarchical taxonomy down to atomic actions.
4. Curation statistics: diversity per 1,000 hours, collector and site
   concentration, near-duplicate rate, mixture weights.
5. Per-frame quality flags and mapping to published quality dimensions.
6. Consent scope, de-identification state, and residency metadata.

Differentiators not found in public materials:

- epistemic roles for every value;
- action representation descriptors;
- native multi-clock time with alignment residuals;
- capability profiles with typed missingness;
- machine-readable delivery contracts with loss reports;
- immutable, content-addressed releases with lineage.

## 5. Gaps in this research

- Company scale figures are largely self-reported.
- First-hand technical talks from Chinese automakers on data loops were not
  located in citable form.
- Several vendors publish too little for meaningful comparison.

## References

- Maniformer Pai launch coverage: https://news.pedaily.cn/202609/569576.shtml, https://www.163.com/dy/article/L7HQ45AC055284JB.html
- Maniformer platform launch (2026-04): https://www.cnr.cn/shanghai/tt/20260416/t20260416_527587735.shtml
- AgiBot World: https://github.com/OpenDriveLab/AgiBot-World, https://huggingface.co/datasets/agibot-world/AgiBotWorld-Beta
- Lightwheel EgoSuite-Open100K: https://huggingface.co/blog/LightwheelAI/egosuite-open100k
- Lightwheel EgoStandard card: https://huggingface.co/datasets/LightwheelAI/EgoStandard
- Lightwheel EgoPro card: https://huggingface.co/datasets/LightwheelAI/EgoPro
- LW-Egosuite-DevKit: https://github.com/LightwheelAI/LW-Egosuite-DevKit
- Maxinsights: https://www.maxinsights.ai/
- Figure Index: https://www.figure.ai/news/introducing-index
- Scale AI physical AI: https://scale.com/blog/physical-ai
- Universal Robots and Scale AI: https://www.universal-robots.com/news-and-media/news-center/universal-robots-scale-ai-launch-imitation-learning-system-accelerate-ai-training-lab-to-factory/
- Build AI Egocentric-10K: https://huggingface.co/datasets/builddotai/Egocentric-10K
- NVIDIA NCore formats: https://nvidia.github.io/ncore/data/formats.html
- Waymo Open Dataset: https://github.com/waymo-research/waymo-open-dataset
- LeRobotDataset v3: https://huggingface.co/blog/lerobot-datasets-v3
- Embodied dataset quality standard coverage: https://m.21jingji.com/article/20260805/herald/63ebde09e0dcbb872922d986f91bd5a4.html
