# PixelCore Review Rules

These are repository-specific review rules for `PixelCore`.

Read `AGENTS.md`, `.agents/IDENTITY.md`, and `tool/C++编码规范.md` alongside this document.

## Core priorities

Review in this order:

1. correctness and pipeline semantics
2. latency and determinism
3. observability and diagnosability
4. throughput and utilization
5. maintainability without hiding cost

## Pipeline invariants

Preserve these terms and their intended semantics:

- `ZeroDelayPipeline`
- `OneFrameDelayPipeline`
- explicit submit behavior
- explicit queueing behavior
- explicit CUDA stream ownership
- explicit synchronization boundaries
- diagnosable frame boundaries

Flag changes that:

- add hidden queueing or delay
- blur stream ownership
- hide launch order or execution cost
- make `ZeroDelayPipeline` less credible
- turn `OneFrameDelayPipeline` delay into an accidental side effect

## CUDA and hot-path review

Escalate findings when changed code introduces:

- `cudaDeviceSynchronize` in hot paths
- extra `cudaStreamSynchronize` or cross-stream waits without a clear boundary need
- blocking host round-trips
- extra full-frame copies
- unnecessary temporary buffers
- extra format conversion or host-device-host bouncing

Also inspect:

- submit order
- cross-stream dependencies
- memory ownership and lifetime
- pitch, stride, bit depth, color space, and channel-order assumptions

## Release constraints

Treat these as hard review rules unless the user explicitly states otherwise:

- do not add new `NVTX`
- do not add new `NV Event`
- do not add other tracing or instrumentation that can increase Release-path business latency

If the repository later distinguishes debug-only instrumentation with a safe build guard, review that separately and explicitly.

## C++ and reliability rules

Check that changed code remains aligned with project standards:

- fixed-width integer use in protocol and buffer code
- `enum class` for scoped semantic enums
- `nullptr` instead of `NULL`
- RAII and explicit ownership
- early validation and actionable logging
- JSON parsing catches specific errors before generic catches

## Validation expectations

Flag missing validation when change risk is meaningful, especially for:

- parser and processor edits
- pipeline and hot-path changes
- color, HDR, CSC, LUT, tone mapping, or bit-depth behavior
- synchronization changes

Recommended validation references:

- targeted gtest where available
- full unit tests for wider pipeline changes
- `format-check`
- trace or timing evidence for performance claims
