# Debugging Skill – Examples

## Example 1: Diagnosing a Python KeyError

**Symptom:** `KeyError: 'user_id'` in production logs.

**Steps:**

1. Reproduce locally with the same payload that triggers the error.
2. Add a debug print before the failing line:

```python
print(f"[DEBUG] data keys: {list(data.keys())}")
user_id = data["user_id"]
```

3. Discover that the key is `"userId"` (camelCase) in the incoming JSON.
4. Fix: normalise the key on ingestion.

```python
user_id = data.get("user_id") or data.get("userId")
if user_id is None:
    raise ValueError("Missing user identifier in payload")
```

5. Remove the debug print and add a regression test.

---

## Example 2: Flaky test investigation

**Symptom:** `test_send_email` fails ~30% of the time.

**Steps:**

1. Run the test 10 times in a row: `for i in {1..10}; do pytest tests/test_email.py; done`
2. Notice it fails when the clock rolls over a minute boundary.
3. Hypothesis: the test builds an expected timestamp string using `datetime.now()`,
   but the code under test also calls `datetime.now()` slightly later.
4. Fix: mock `datetime.now` to return a fixed value in both the test setup and
   the code path.

```python
from unittest.mock import patch
import datetime

FIXED_TIME = datetime.datetime(2026, 1, 1, 12, 0, 0)

@patch("myapp.email.datetime")
def test_send_email(mock_dt):
    mock_dt.now.return_value = FIXED_TIME
    ...
```

---

## Example 3: Performance regression via binary search

**Symptom:** API response time doubled after a deploy.

**Steps:**

1. `git bisect start`
2. Mark current bad commit: `git bisect bad`
3. Mark last known good release: `git bisect good v1.4.0`
4. For each commit Git checks out, run the benchmark and mark good/bad.
5. Git identifies the commit that introduced an N+1 query in the ORM layer.
6. Fix by adding `.select_related("author")` to the queryset.
