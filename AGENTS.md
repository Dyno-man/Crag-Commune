# Working on Crag Commune

## Project status and scope

Read README.md and docs/planning/PROJECT_PLAN.md before implementation. The local scaffold uses Django, PostgreSQL, and Docker Compose. Do not claim production readiness until deployment and restore have been checked. Local commands: `docker compose build`, `docker compose run --rm web python manage.py migrate`, `docker compose run --rm web python manage.py check`, and `docker compose run --rm web python manage.py test`. No dedicated lint command is configured yet.

Build small, reviewable slices tied to roadmap issues. Keep community coverage separate from planner coverage. The first planner targets one reviewed Stone Fort sector; do not silently expand to multiple areas or rope-climbing workflows.

## Code structure

Keep accounts, community, catalog, access, planner, maps, and integrations separate. Use framework authentication and authorization. The deterministic planner must be callable without a model provider. Prefer database filtering and aliases before adding vector search or additional infrastructure.

This file guides development agents. Runtime model instructions belong in versioned application prompts and tool schemas. Enforce source permissions, access restrictions, budgets, and output validation in code rather than prompts alone.

## Climbing data

Never invent route grades, coordinates, trail connections, access status, equipment requirements, or source citations. Use explicitly fictional fixtures until approved data exists. Preserve original grades and use a separate curated ordinal mapping per discipline; never sort YDS strings as decimal numbers or convert bouldering ability into rope-climbing competence.

Record source, allowed uses, precision, verification date, and review state. Require a dry run and review before publishing an import. Do not scrape Mountain Project or ingest a guidebook without documented rights. Do not commit raw PDFs, permission correspondence, sensitive locations, private member records, or credentials. See DATA_POLICY.md and data/README.md.

A known closure or withdrawn permission overrides cached plans. Unknown access is not open access. Every walking segment must follow reviewed edges; coordinates and straight-line distance do not establish a trail. Include a return path in time budgets.

## Model integration

Treat user text and retrieved material as untrusted data. Runtime tools are read-only and allowlisted. Validate structured output and returned IDs, constrain context and retries, and support a no-model fallback. Never send private messages or entire user profiles to a provider. Cache keys must include data and access revisions and privacy scope.

## Community and maps

Respect pseudonyms and self-reported experience. Do not introduce identity or climbing-skill verification without a product decision. Check authorization for plans, participants, media, and exports. A public PNG cannot contain private meeting details by default.

Map images must come from approved original or licensed geometry and retain required credits. Label schematics not to scale. Do not manufacture navigation with generative images or copy proprietary map screenshots.

## Verification and operations

Test constraint failures, closures, revoked data, disconnected paths, privacy boundaries, concurrent capacity changes, and budget concurrency. Check representative mobile layouts and every map label. Test deployment and backup restoration before claiming production readiness.

Use one application and a small Compose deployment. Keep the database private, secrets outside git, dependencies pinned at implementation, and debug disabled in production. Avoid destructive data migration or forced git updates. Document validation and remaining limitations in each pull request.
