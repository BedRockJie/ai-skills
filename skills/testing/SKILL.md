# Skill: Testing

## Purpose

Help AI agents write effective, maintainable tests that give confidence in
software correctness without becoming a maintenance burden.

## When to use

Use this skill when:

- Writing unit, integration, or end-to-end tests for new code
- Deciding what level of testing to apply to a given component
- Diagnosing a flaky or brittle test suite
- Reviewing test coverage gaps

## Instructions

### 1. Choose the right test level

| Level | What it tests | Speed | Isolation |
|---|---|---|---|
| Unit | A single function or class | Very fast | High |
| Integration | Interaction between components | Moderate | Medium |
| End-to-end | Full user journey through the system | Slow | Low |

Use unit tests as the foundation. Add integration tests for boundaries (DB,
API, filesystem). Reserve E2E tests for critical happy paths.

### 2. Follow the Arrange – Act – Assert pattern

```python
def test_total_price_applies_discount():
    # Arrange
    cart = Cart(items=[Item(price=100)])
    discount = PercentageDiscount(10)

    # Act
    total = cart.calculate_total(discount)

    # Assert
    assert total == 90
```

### 3. Test behaviour, not implementation

- Test *what* the code does, not *how* it does it.
- Avoid asserting on internal state or private methods.
- Tests should survive a refactor that preserves observable behaviour.

### 4. Keep tests independent

- Each test must be runnable in isolation and in any order.
- Use setup/teardown to create fresh state; never share mutable state between tests.
- Avoid relying on external services in unit tests — use mocks or fakes.

### 5. Name tests descriptively

Format: `test_<unit>_<scenario>_<expected_outcome>`

```python
# Good
def test_payment_processor_with_expired_card_raises_error():
    ...

# Bad
def test_payment():
    ...
```

### 6. Treat flaky tests as bugs

A test that sometimes passes and sometimes fails erodes trust.

- Investigate immediately when a test flakes.
- Common causes: time-dependent logic, random data, race conditions, network calls.
- Fix or quarantine (never ignore).

### 7. Aim for meaningful coverage, not 100%

- Target coverage of critical paths and business logic.
- Trivial code (getters, constants) rarely needs its own test.
- Use coverage reports as a *signal*, not a *goal*.

## References

- Inspired by https://github.com/anthropics/skills
- [Test Driven Development: By Example – Kent Beck](https://www.oreilly.com/library/view/test-driven-development/0321146530/)
- [Google Testing Blog](https://testing.googleblog.com/)
