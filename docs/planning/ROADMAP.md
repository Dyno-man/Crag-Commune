# Roadmap and implementation backlog

This is a proposed sequence. Items are not implemented. Data permission and local review determine planner readiness; community development can proceed independently. See the full project plan for rationale.

## Milestones

| Milestone | Outcome | Exit condition |
| --- | --- | --- |
| M0 Data feasibility | A viable first area | Scope, permitted catalog, and review ownership confirmed |
| M1 Community foundation | A small usable local community | Profiles, outings, discussion, privacy, moderation, and recovery work |
| M2 Reviewed session planner | Form-based itinerary and original PNG | Approved data, tested constraints, and field-checked trails |
| M3 Conversational pilot | Bounded chat and evidence from real use | Model controls work and pilot results support launch or revision |

## Initial epics

| ID | Epic | Priority | Dependencies |
| --- | --- | --- | --- |
| E01 | [Confirm the pilot sector and local community needs](../issues/E01.md) | P0 | None |
| E02 | [Audit data rights and assemble a reviewed pilot catalog](../issues/E02.md) | P0 | E01 |
| E03 | [Scaffold the application and prove Docker deployment and restoration](../issues/E03.md) | P0 | None |
| E04 | [Build pseudonymous profiles and joinable climbing outings](../issues/E04.md) | P0 | E03 |
| E05 | [Add discussion moderation and member privacy controls](../issues/E05.md) | P0 | E03, E04 |
| E06 | [Build and field-check the deterministic planner and map exports](../issues/E06.md) | P0 | E02, E03 |
| E07 | [Add constrained conversational planning and hard spending limits](../issues/E07.md) | P1 | E06 |
| E08 | [Run the local pilot and decide whether to expand](../issues/E08.md) | P1 | E04, E05, E06, E07 |

Split each epic into focused implementation issues as it becomes ready. Checklists in docs/issues provide concrete work and acceptance criteria. issue-seed.json contains the initial issue bodies. Track ongoing status on GitHub rather than rewriting the original research document on every task completion.

## Deferred work

- Additional Stone Fort sectors, followed by areas with reviewed data and maintainers.
- Rope-climbing planning with separate equipment and eligibility requirements.
- Deeper conditions integration, subject to owner agreement.
- Direct messages, notification email, and richer member controls based on pilot feedback.
- Live GPS, native mobile apps, offline basemaps, and regional coverage only after demonstrated demand.

## Estimate

For one experienced part-time developer, allow roughly 6 to 11 development weeks across the first four stages, plus the four-week pilot. These are planning estimates, not deadlines; licensing responses and local field review may take longer.
