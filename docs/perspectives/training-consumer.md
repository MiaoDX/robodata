# Perspective: training consumer

> Status: draft, informative. Scale thresholds below are starting hypotheses to
> be validated with published benchmarks, not normative requirements.

A training consumer turns robotics data into policies or foundation models. At
small scale the priority is flexibility; at large scale it is keeping
accelerators saturated. **The storage format and the training format are
different products.**

## 1. Lesson from large-model training

Language-model pipelines separate storage from training input explicitly:
raw text is cleaned, tokenized, packed into fixed-length sequences, and
written to read-only shards (memory-mapped index/binary pairs, MDS, or
WebDataset tar shards). Training streams those shards sequentially; the GPU
never waits on preprocessing.

Robotics data has heavier bottlenecks than text:

- video decoding dominates data-loading cost;
- streams arrive at different rates and must be aligned;
- training samples windows (action chunks) at random offsets inside long
  episodes.

Rough scale check: one million hours at 30 fps is about 1.08 × 10¹¹ frames.
Decoding those online every epoch makes the data loader, not the model, the
limiting factor.

## 2. Training views are delivery products

A training-optimized dataset is produced by RDX like any other delivery, under
a contract that fixes:

- output rate, image resolution, and camera selection;
- window length, action horizon, and action representation;
- normalization statistics and their computation scope;
- data mixture weights across sources, tasks, and product tiers;
- sharding, shuffling, and determinism requirements.

Because it is a derivation, a training view carries lineage back to source
evidence and can be regenerated when any of these choices change.

## 3. Recommended shapes by scale

| Scale | Typical setting | Recommended shape | Notes |
|---|---|---|---|
| ~100 hours | Fine-tuning, single node | LeRobot v3 read directly | Online decoding is acceptable; flexibility matters most |
| ~1k–10k hours | Multi-node pre-training | Pre-aligned shards (WebDataset, MDS, or equivalent) | Resample to a fixed grid; re-encode video at training resolution; precompute action chunks and normalization; shards of hundreds of MB to a few GB; stream from object storage with a shuffle buffer |
| ~100k–1M+ hours | Foundation-model pre-training | Read-only, memory-mappable arrays of pre-encoded inputs | When the vision encoder is frozen, store latents or embeddings instead of pixels; pack variable-length episodes into fixed windows; encode mixture weights in the manifest; deterministic, resumable sampler |

These thresholds depend on hardware, codec, resolution, and model; they are a
starting point. The project should publish a benchmark method instead of
decreeing numbers:

- cold and warm read throughput;
- time to first batch;
- sustained accelerator utilization;
- object-store request counts;
- decode CPU/GPU cost and memory.

## 4. What a training consumer needs from the substrate

- **Unambiguous action semantics.** Absolute, fixed-anchor relative, or
  stepwise delta; reference frame; joint order; rotation convention. Silent
  convention mismatches are the most expensive training bugs.
- **Epistemic roles.** Whether an action is a measured command, an estimated
  trajectory, or a retargeted target changes how it should be weighted or
  filtered.
- **Typed missingness.** A missing wrist view because the product tier does
  not include it is different from a dropped stream.
- **Stable sample identity.** Sample IDs that survive re-sharding, so
  evaluation failures and data complaints can be traced to exact evidence.
- **Honest hour counts.** Unique source hours, not the sum of formats or
  cameras.

## Open questions

- Should the project maintain reference training-view profiles per scale tier?
- How should latent/embedding training views record the frozen encoder
  version so they are invalidated correctly?
- Which mixture-weight representation is portable across training frameworks?
- What benchmark fixture sizes are representative enough to publish?
