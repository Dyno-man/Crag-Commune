# Crag Commune

A homegrown Chattanooga climbing community with shareable session plans: find warmups near your project, organize an outing, and meet people to climb with.

**Status: planning.** There is no running application or deployable Docker image yet.

## Start here

- [Full project plan](docs/planning/PROJECT_PLAN.md)
- [Readable Word companion](docs/planning/Crag_Commune_Project_Plan.docx)
- [GitHub milestones and issue index](docs/planning/GITHUB.md)
- [Roadmap and implementation backlog](docs/planning/ROADMAP.md)
- [Data permissions and source register template](data/README.md)
- [Contributor guide](CONTRIBUTING.md)
- [Coding agent instructions](AGENTS.md)

## Proposed first release

A mobile-friendly community with pseudonymous profiles, dated outings, join requests, discussion, and basic moderation. The first planner covers one locally reviewed Stone Fort sector, with structured preferences, a fixed project, and an original downloadable PNG. Other Chattanooga areas can support community posts before automated planning is available.

Proposed stack: Django, PostgreSQL, and Docker Compose on an existing VPS. Optional model-assisted input and explanations sit around a deterministic planner. Core planning works without model calls.

Data rights, field verification, and current access information are launch dependencies. This repository does not contain Mountain Project exports, copyrighted guidebooks, or real route fixtures.

## Open source

Original repository code and documentation use the [MIT license](LICENSE). See [DATA_POLICY.md](DATA_POLICY.md) for the separate treatment of climbing data, photographs, third-party sources, and member content. Public code does not imply public user records.

The project is independent and is not affiliated with Mountain Project, OpenBeta, SCC, KAYA, or any land manager. The proposed Crag Conditions link awaits confirmation of the intended service.
