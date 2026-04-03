# Report Template

Use this structure exactly.

## When tooling fails

````markdown
# Problem Summary
- blocker: <tool name> failed on <scope>

# Tool Results
## <tool name>
```text
<raw tool output>
```
````

Rules:

- start with `Problem Summary`
- keep the summary short
- include raw tool output
- stop after reporting the tool failure

## When tooling passes

```markdown
# Problem Summary
- major: <short issue summary>
- minor: <short issue summary>

# AI Review Findings
## [major] <file>:<line>
Problem: <direct problem statement>
Suggestion: <direct code-change suggestion>

## [minor] <file>:<line>
Problem: <direct problem statement>
Suggestion: <direct code-change suggestion>
```

## When tooling passes and no issues are found

```markdown
# Problem Summary
- No blocking or major issues found
```

Rules:

- the report must begin with `Problem Summary`
- sort findings by severity
- keep each finding terse
- do not add long background sections
- if there are no findings, say `No blocking or major issues found` and stop there
