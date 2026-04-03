# Issue Library

增量 `PixelCore` Review 的常见问题库，用于识别重复出现的问题并保持审查用语一致。

## 问题速查表

| # | Level | Issue | Risk |
|---|-------|-------|------|
| 1 | `blocker` | Release path adds NVTX / NV Event | hot path latency regression |
| 2 | `blocker` | Hidden sync on hot path | tail latency ↑, stream serialize, breaks `ZeroDelayPipeline` |
| 3 | `major` | Redundant full-frame copy / conversion | latency ↑, bandwidth ↑, harder to profile |
| 4 | `major` | Pipeline semantics become implicit | stream ownership / submit order unreadable |
| 5 | `minor` | Coding standard drift | maintainability ↓, future defect risk ↑ |

---

## 详细说明

### 1. `blocker` — Release path adds NVTX / NV Event

**Signal：** `NVTX_*`、`nvtxRange*`、hot path 新增 event marker / instrumentation macro

**Review：** Release build 引入 NVTX / NV Event instrumentation，违反 hot path 禁令。Remove 或 gate behind non-Release build flag。

### 2. `blocker` — Hidden sync on hot path

**Signal：** `cudaDeviceSynchronize()`、unconditional `cudaStreamSynchronize()`、producer-consumer stream 间新增 wait

**Review：** Hot path 引入 blocking sync。Replace with explicit stream dependency 或 justify why blocking is required。

### 3. `major` — Redundant full-frame copy / conversion

**Signal：** 新增 `cudaMemcpy*`、D2H/H2D round-trip、多余 intermediate buffer、不必要的 pixel format conversion

**Review：** Processing path 增加 copy / conversion overhead。Reuse existing buffer 或 preserve prior in-place path。

### 4. `major` — Pipeline semantics become implicit

**Signal：** Helper abstraction 隐藏 stream 选择、launch order 不可读、delay semantics 从 explicit design 退化为 implicit side-effect

**Review：** Pipeline timing semantics 变 implicit。Keep stream ownership、queue behavior、submit boundary visible in code。

### 5. `minor` — Coding standard drift

**Signal：** Raw pointer where RAII expected、vague log message、generic `catch` where `parse_error` / `type_error` expected、non-fixed-width int in protocol code

**Review：** Code drifts from repo coding standard。Fix to keep behavior and diagnostics predictable。
