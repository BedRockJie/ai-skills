# Skill: Software Architecture

## Purpose

Help AI agents reason about and communicate software architecture decisions —
including component decomposition, data flow design, and technology selection.

## When to use

Use this skill when:

- Designing a new system or service from scratch
- Evaluating whether an existing design meets scalability or maintainability goals
- Choosing between architectural patterns (monolith vs. microservices, MVC vs.
  hexagonal, etc.)
- Writing Architecture Decision Records (ADRs)

## Instructions

### 1. Clarify requirements first

Before proposing any design, gather:

- **Functional requirements** – what the system must do
- **Non-functional requirements** – latency, throughput, availability, security
- **Constraints** – team size, existing stack, budget, deadline

### 2. Identify components and boundaries

- Break the system into cohesive modules with clear responsibilities.
- Prefer high cohesion within a component and loose coupling between components.
- Name components by what they *do*, not what they *are* (e.g., `OrderProcessor`
  not `OrderService`).

### 3. Define data flow

- Draw (or describe) the path data takes from input to output.
- Identify synchronous vs. asynchronous boundaries.
- Note where data is persisted and by whom.

### 4. Choose patterns deliberately

| Concern | Candidate patterns |
|---|---|
| Request handling | REST, gRPC, GraphQL |
| Data persistence | Repository, Active Record |
| Async work | Queue, Event bus, CQRS |
| Cross-cutting concerns | Middleware, Decorator, AOP |

### 5. Write an ADR for significant decisions

```markdown
# ADR-001: Use PostgreSQL as primary datastore

## Status
Accepted

## Context
We need a relational store with strong ACID guarantees for financial records.

## Decision
Use PostgreSQL 16.

## Consequences
+ Battle-tested, strong ecosystem
- Requires schema migrations; less flexible than NoSQL for unstructured data
```

### 6. Review for common pitfalls

- **Premature optimization** – design for today's load, add scaling later
- **Distributed monolith** – microservices that are tightly coupled defeat the purpose
- **God objects** – split any component that grows beyond a single responsibility

## References

- Inspired by https://github.com/anthropics/skills
- [The Architecture of Open Source Applications](https://aosabook.org/)
- [Designing Data-Intensive Applications – Kleppmann](https://dataintensive.net/)
