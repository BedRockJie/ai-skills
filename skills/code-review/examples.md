# C/C++ Code Review Gate - Examples

## Example 1: Unbounded string copy in user-space code

**Patch under review:**

```c
void process_name(const char *name) {
    char buf[32];
    strcpy(buf, name);
    consume_name(buf);
}
```

**Deterministic finding:**

```
blocker: [src/user.c:3] unbounded or legacy string API - use a bounded alternative
  Expected: bounded copy with explicit termination or length validation
  Actual:   strcpy(buf, name)
```

**Residual review question after the fix:**

```
question: [src/user.c:2] What is the expected maximum input length here?
  Expected: interface contract or validation that matches caller behavior
  Actual:   local truncation risk remains unclear even after replacing strcpy
```

---

## Example 2: Process execution added in a helper path

**Patch under review:**

```c
int reload_helper(const char *unit) {
    char command[256];
    snprintf(command, sizeof(command), "systemctl reload %s", unit);
    return system(command);
}
```

**Deterministic finding:**

```
warning: [src/reload.c:4] process execution requires strict input validation and error handling
  Expected: validated input and a safer spawn/exec strategy where possible
  Actual:   system(command)
```

**Residual review focus:**

```
blocker: [src/reload.c:2] user-controlled input may reach a shell command
  Expected: shell-free execution path or strict allowlist validation
  Actual:   unit is interpolated into a command string
```

---

## Example 3: Public header and ABI risk

**Patch under review:**

```c
typedef struct {
    uint32_t flags;
    uint16_t version;
    uint16_t reserved;
    uint64_t trace_id;
} request_header_t;
```

**Risk summary output:**

```
RISK SUMMARY:
- high: public header or API surface changed: include/request.h
- high: symbol visibility or ABI-related code changed
```

**Residual review focus:**

```
question: [include/request.h:1] Is this struct part of a stable on-disk or on-wire format?
  Expected: explicit compatibility story, packing/alignment review, and versioning plan
  Actual:   layout changed but compatibility intent is not stated
```

---

## Example 4: Concurrency change with clean deterministic gates

**Patch under review:**

```c++
void Worker::stop() {
    stopping_.store(true, std::memory_order_relaxed);
    cv_.notify_all();
    worker_.join();
}
```

**Deterministic outcome:**

```
warning: [src/worker.cpp:2] concurrency primitive changed - verify ordering, lifetime, and shutdown behavior
```

**Residual review question:**

```
question: [src/worker.cpp:1] Can stop() race with a second caller or with a not-yet-started thread?
  Expected: shutdown contract is documented and join() is safe in all call paths
  Actual:   lifetime and call-order assumptions are not obvious from the diff
```
