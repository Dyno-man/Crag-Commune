# Crag Commune

A homegrown Chattanooga climbing community with shareable session plans: find warmups near your project, organize an outing, and meet people to climb with.

**Status: local prototype.** Django has pseudonymous accounts and member-hosted Stone Fort outings with join requests and private meetup details. The reviewed climbing planner and production deployment do not exist yet.

## Local development

1. Copy `.env.example` to `.env` and replace both placeholder secrets. Keep `.env` out of git.
2. Start Docker Desktop, then run `docker compose build`.
3. Run `docker compose run --rm web python manage.py migrate`.
4. Run `docker compose up -d` and open `http://127.0.0.1:8000/health/`.

Use `docker compose run --rm web python manage.py check` for Django checks and `docker compose run --rm web python manage.py test` for tests. After model changes, create migrations with `docker compose run --rm web python manage.py makemigrations` and apply them with the migration command above. Stop services with `docker compose down`; the named PostgreSQL volume remains. This Compose setup is for local development only. VPS deployment, TLS, backups, and an isolated restore are tracked in [issue #3](https://github.com/Dyno-man/Crag-Commune/issues/3).

The account scaffold uses a custom user model. Start it with a fresh local database volume; a volume created by the earlier health-only scaffold has Django's original user migration history and is not migrated by this slice. Keep any existing volume until its contents have been reviewed. Signup and login use shared PostgreSQL limits; see [abuse limits and email transition](docs/planning/ACCOUNT_ABUSE.md). Password recovery and public deployment remain open work.

The local outing board is at `/outings/`. Hosts can post a dated outing, accept or decline requests, and keep meetup details visible to accepted members. Outings do not provide reviewed route, trail, or access guidance. Cancellation, material-change notifications, abuse limits, and a production-ready moderation flow remain open work.

## Start here

- [Full project plan](docs/planning/PROJECT_PLAN.md)
- [Stone Fort pilot scope and evidence log](docs/planning/PILOT_SCOPE.md)
- [Readable Word companion](docs/planning/Crag_Commune_Project_Plan.docx)
- [GitHub milestones and issue index](docs/planning/GITHUB.md)
- [Roadmap and implementation backlog](docs/planning/ROADMAP.md)
- [Data permissions and source register template](data/README.md)
- [Contributor guide](CONTRIBUTING.md)
- [Coding agent instructions](AGENTS.md)

## Proposed first release

A mobile-friendly community with pseudonymous profiles, dated outings, join requests, discussion, and basic moderation. The owner wants all of Stone Fort as the pilot area. The planner opens only for connected sections with reviewed data and paths, with structured preferences, a fixed project, and an original downloadable PNG. Other Chattanooga areas can support community posts before automated planning is available.

Proposed stack: Django, PostgreSQL, and Docker Compose on an existing VPS. Optional model-assisted input and explanations sit around a deterministic planner. Core planning works without model calls.

Data rights, field verification, and current access information are launch dependencies. This repository does not contain Mountain Project exports, copyrighted guidebooks, or real route fixtures.

## Open source

Original repository code and documentation use the [MIT license](LICENSE). See [DATA_POLICY.md](DATA_POLICY.md) for the separate treatment of climbing data, photographs, third-party sources, and member content. Public code does not imply public user records.

The project is independent and is not affiliated with Mountain Project, OpenBeta, SCC, KAYA, or any land manager. The proposed Crag Conditions link awaits confirmation of the intended service.
