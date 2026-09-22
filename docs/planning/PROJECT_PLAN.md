# Crag Commune project plan

Chattanooga climbing community and session planner

Version 0.1 • September 22, 2026 • Product and implementation proposal

## 1 Purpose and recommended first release

Crag Commune will help people around Chattanooga find people to climb with and organize a day outside. A member can say where and when they are going, explain the climbs they want to try, and invite others to join. A session planner will suggest a sequence of warmups leading to a chosen project, with a downloadable image showing the approved paths between stops.

The social goal matters as much as the planning tool. Someone who is new to Chattanooga, or simply does not know many other climbers, should be able to find a welcoming outing without already belonging to an established group. Profiles should describe interests and experience without turning climbing ability into a leaderboard. Public pseudonyms are welcome, and real-name or climbing-ability verification is not required.

The recommended first release is a small, mobile-friendly community with a planner covering one selected Stone Fort sector. We can support discussion and meetup posts for other areas before promising automated itineraries there. Build a useful structured planner first, then add optional conversational input. A model outage or spending limit should never prevent people from seeing their plans or arranging a session.

The project will be open source and run on the owner's VPS using Docker Compose. The proposed implementation is a Django application, PostgreSQL database, and the VPS's existing reverse proxy or a small Caddy service. The stack is a recommendation, not an existing implementation. This repository currently contains the planning foundation.

The first decision is whether we can assemble a small, permissioned, field-checked data pack. A forum can be built quickly; an accurate map and climbing catalog require ongoing local care. We should settle that question before investing in a broad conversational interface.

## 2 Product principles and boundaries

1. Make joining an outing approachable. Hosts can say that newcomers are welcome, name the meeting point, and describe the session's pace and expectations.
2. Keep the core useful without AI. Searching climbs, generating a structured itinerary, posting sessions, and downloading a plan should work with no paid model calls.
3. Show the basis of a recommendation. Route details, access notes, and trail directions carry sources, verification dates, and uncertainty.
4. Let people choose their comfort level. Grade preferences are self-reported and separate by climbing discipline. Nobody receives a platform certification of competence.
5. Respect the people who document and maintain climbing areas. Link to local organizations and guidebooks, preserve contributor credit, and do not build the catalog by copying unlicensed material.
6. Keep maintenance realistic for a volunteer owner. Prefer a single application, a small database, and explicit limits over a collection of services.

The launch excludes live GPS tracking, real-time turn-by-turn navigation, an emergency response service, paid guiding, automatic belay matching, native mobile apps, unrestricted AI chat, and a complete Southeastern guidebook. These exclusions keep the first release focused; they do not prevent later expansion.

Use “session plan” or “climbing itinerary” in the interface. “Route” can mean a climb or a walking path, so use “climb,” “trail segment,” and “driving directions” where that distinction matters. Avoid promising an “optimal” day: the application can optimize a stated preference over known data, but cannot know how a climber will feel or whether a boulder will be occupied.

## 3 Existing products and what to learn from them

Mountain Project already combines a route directory, discussion forums, a route finder, and partner search. Its partner finder exposes discipline and climbing-level filters. Crag Commune therefore should not claim that community plus climb discovery is new. Learn from its area hierarchy and searchable partner information, while concentrating our design on a dated, joinable outing with a saved itinerary. [S1, S2]

KAYA provides climbing discovery and beta, and documents saved climb lists and warmup circuits. That supports a familiar interaction: save a sequence of climbs for a future session. Our proposed difference is making the session itself a local invitation, with explicit meeting details and a locally reviewed walking plan. Do not copy its paid guidebook content, topos, photos, or interface assets. [S3]

Gora explicitly describes finding partners, organizing climbing sessions, and group communication. It is a closer social comparison than a route encyclopedia. We still need user interviews to learn whether Chattanooga climbers would prefer a local, open-source alternative; the existence of our desired feature combination does not prove demand. [S4]

OpenBeta is both a potential data source and an open-source project to learn from. Its documentation identifies climbing data as CC0, with photos and software excluded from that statement; its GraphQL repository documents programmatic catalog access. Confirm the exact dataset, field provenance, and local coverage before adoption. Its API code has a separate license, so using data does not mean its application code can be copied under our chosen software license. [S5, S6]

Discourse is a credible alternative if a full forum becomes the main product. It supplies an established community platform and an official Docker installation path. Integrating a separate planner would introduce additional integration and operational work. For the small session-centered product proposed here, a custom application with a deliberately limited forum is preferable; if moderation and discussion features grow substantially, revisit this choice. [S7]

Facebook groups remain an existing channel named in the original concept, rather than a source of content to import. Members can manually share links to our outings in groups that permit it. Do not scrape posts or import member identities.

The research establishes overlap, not an exhaustive market survey or a claim that nobody else offers this exact experience. Borrow interaction patterns and reuse appropriately licensed software; preserve independent branding, writing, and maps.

## 4 Geography and launch coverage

Community coverage and planner coverage should be different settings. A member can organize a session at an area with only a verified public name and access link. The planner becomes available only when that area has sufficient approved climbs and navigation data.

The proposed first planning area is a single Stone Fort sector chosen with local climbers. A target of 30 to 60 reviewed climbs is a planning estimate, not a statement about available data. The pack must include useful warmups across the pilot group's grade ranges, several project choices, meeting and entry points, and connected approved paths. Expand only after actual sessions show that people can find the stops.

Upper and Lower Leda are candidates for the first rope-climbing expansion. Keep them distinct until local reviewers confirm naming, access, and trail relationships. “St. Elmo” remains a candidate requiring identification of the exact climbing area and permission to publish details; do not convert a neighborhood name into an invented crag or expose an informal access location.

Foster Falls, Rocktown, and Sand Rock are subsequent candidates. Mount Yonah and selected North Carolina and South Carolina destinations belong in a later regional tier until practical driving times, access requirements, and data readiness are checked. Kentucky is north of Tennessee and could be considered eventually, but the launch is not a multistate directory.

Do not label every named destination “within two hours.” Drive time depends on the chosen Chattanooga origin, destination parking, traffic, and road conditions. Area records should store a verified parking link and an optional dated travel estimate with origin. The interface can group areas as local, day trip, or regional without claiming an unverified drive duration.

The Southeastern Climbers Coalition identifies Stone Fort as privately managed by Montlake Golf Course, with check-in, a pass, and waiver requirements. Its Leda page also identifies Montlake check-in and payment requirements. These are examples of access facts the application must preserve and recheck, not permanent guarantees. [S8, S9]

Rocktown illustrates why access information needs dates: the SCC page contains hunting restrictions and older closure dates. Before supporting a planned visit, consult current land-manager information for that date rather than reusing an old seasonal schedule. [S10]

## 5 Who the first release serves

A new local climber needs a low-pressure way to meet people. Their profile can say “mostly V2 to V4, happy to spot, looking for weekend bouldering” without publishing a real name, home address, or exact location. They should find outings by date, area, discipline, and whether new partners are welcome.

A project-focused climber needs a short warmup sequence near a target climb. They should be able to prioritize less walking, fewer stops, familiar movement, or more variety, and reserve time for the project. They can change the plan without rewriting a public post.

A host needs clear attendance and communication. They should set capacity, approve requests if desired, update the meeting time, cancel an outing, and tell participants that plans changed. A request to join is not a booking with a guide or a guarantee of instruction.

A local contributor needs a straightforward correction process. They can submit an original climb description, an alias, a source link, or a trail correction. New factual contributions enter a review queue rather than immediately changing every generated itinerary.

A moderator needs a manageable set of tools: review reports, remove spam or harmful content, suspend accounts, and inspect an audit trail. A visible, named moderation responsibility is more valuable than a large list of unused moderation features.

## 6 Community behavior and member profiles

Profiles include a display name, optional avatar, short biography, approximate home region, preferred disciplines, and self-reported comfortable and project grade ranges. Bouldering, sport leading, top-rope climbing, and trad experience remain separate. Gym and outdoor grades can be distinguished. Avoid a single “average rank,” which hides meaningful differences.

Optional preferences include typical availability, session pace, willingness to welcome newcomers, and equipment someone chooses to bring. Gear availability is not proof of safety or competence. Keep sensitive health details out of required fields, and do not automatically infer them from chat.

Allow public reading without an account. Require a lightweight pseudonymous account for posting, requesting to join, and using quota-limited chat. A proposed low-cost pilot uses a username and password with recovery codes; email can be optional until a dependable delivery service is configured. Store passwords with the framework's supported password hashing, rate-limit authentication, and describe the consequences of losing recovery credentials. Real-name and skill verification remain unnecessary.

Start with four discussion categories: find partners, upcoming outings, local questions, and access or stewardship. Use flat replies, a clear edit history for material outing changes, basic search, and reporting. Direct messages, follower graphs, reactions, and complex reputation systems can wait.

The outing is a structured post with an area, date, local time zone, approximate end time, discipline, session goals, capacity, host, join policy, and optional saved plan. Joining has explicit states: requested, accepted, declined, withdrawn, or waitlisted. The host can close or cancel the outing. Prevent duplicate joins and oversubscription with database constraints and transactions.

Default exact meetup instructions and participant lists to accepted participants. Public cards can show area, time window, available spaces, and the host's chosen description. Private or unlisted plans should not become public when attached to a post without an explicit visibility choice. Exported images require the same visibility decision and must not silently include private names or meeting notes.

Use in-app notifications first. Show unread changes prominently, and require hosts to acknowledge material plan changes after people have joined. Email is an optional later convenience. Store instants in UTC and retain an IANA time zone for display, especially as the project crosses state and time-zone boundaries.

Moderation should address spam, harassment, discriminatory conduct, doxxing, unsafe impersonation, and publication of sensitive access information. Users can report a post or account and block unwanted interaction. Self-reported grades must never become “verified partner” badges. An adults-only initial pilot is a proposed operating choice to review before public signup, not an established legal requirement.

## 7 The session planning experience

The planner begins with a selected area and discipline. Users provide a project, comfortable warmup range, available time, meeting or entry point, and optional limits such as maximum walking, fewer stops, or avoiding highballs. They can choose structured controls or explain the same preferences conversationally. A text request must resolve to the same validated planning input.

When someone says “warm up near my project at Stone Fort,” the planner first resolves the project to a database ID. If several climbs share a name or an alias is uncertain, it presents candidates with sector and grade. It asks only for missing information that affects the result. It does not silently choose a different climb because it is famous or nearby.

A result contains a short summary, an ordered set of warmups, the project, optional alternatives, a time budget, source links, and a downloadable map or schematic. Each stop explains why it was selected in terms of the user's preferences. The user can replace or remove a warmup, reorder optional stops, and regenerate the walking sequence. The project remains fixed unless the user changes it.

The itinerary should distinguish estimated walking, climbing, rest, and buffer time. Durations are editable assumptions, not promises. For example, the user might reserve most of a three-hour session for the project; the planner then allocates only the remaining time to approach and warmups. Do not make a training or injury-prevention claim based on a generic grade progression.

A complete session includes the way back to an approved exit or meeting point. A plan that reaches the project but ignores the return can exceed the user's time budget. If there is insufficient time or no connected path, say so and offer a simpler plan.

For early wireframes and tests, use fictional identifiers such as “Warmup A” and “Project C,” clearly labeled as fixtures. Names mentioned during planning, including Back Nine, Mystery Machine, and Fireflake, are leads to resolve against approved data; no grade, coordinate, or direction is assumed from the name alone.

## 8 Reliable planning and the role of the model

The model should interpret preferences and explain a validated plan. The database supplies climb facts; ordinary code enforces constraints and computes trail paths. A retrieval system means supplying the model with relevant approved records at request time. It does not require training a custom model on guidebooks.

The proposed pipeline is:

1. Validate the structured input, or parse conversational input into a constrained schema.
2. Resolve area and climb names, requiring user selection for ambiguity.
3. Load approved records and current access notices for the requested date.
4. Apply hard filters for discipline, permission status, known closures, published visibility, equipment requirements where supported, and connected trail coverage.
5. Select a small candidate set by grade suitability, optional movement preferences, and walking cost.
6. Compute paths on the reviewed trail graph and score feasible itineraries.
7. Validate every climb, segment, time estimate, and source against the selected records.
8. Produce a deterministic explanation or optional model-written explanation, checking any returned references.
9. Save a versioned snapshot and render the export from that same snapshot.

The score should minimize walking and unnecessary backtracking while rewarding the requested warmup range and preserving project time. Use configurable weights and a deterministic tie-breaker. Start with bounded search over a handful of stops and shortest paths between them; a global optimizer is unnecessary. Never optimize across closed or unknown trail edges.

Grade sorting uses a curated ordinal table per discipline and grading system. Do not sort strings lexicographically or treat YDS as a decimal number. Preserve original grades, ranges, and qualifiers. A V grade is not automatically converted into a sport grade. Disputed or unknown grades remain explicit and are excluded from strict grade filters unless the user opts in.

The first bouldering planner can use height and landing tags only when reviewed. Unknown does not mean low risk. Sport planning later needs its own fields and eligibility rules, including rope length and equipment context where documented. Trad and multipitch planning should follow a separate design review rather than extending a bouldering score mechanically.

The model receives only approved, relevant public climb data and the minimum preferences required. Do not send private messages or whole profiles to a model provider. Treat route descriptions, PDFs, and forum posts as untrusted content, never as instructions. Model tools are read-only planning functions; no shell access, arbitrary URL retrieval, database mutation, posting, or access-rule overrides.

Require schema validation, allowlisted record IDs, bounded output size, timeouts, and a deterministic fallback. Unknown routes, disconnected trails, revoked sources, exhausted budgets, and provider outages must produce useful partial results or a clear inability to plan. The model may not fill missing facts from memory.

## 9 Data permissions and acquisition

The data strategy has three lanes: appropriately licensed public datasets, original local contributions, and specific permission from guidebook authors or other rights holders. Every imported item must have a recorded source and a decision about what uses are allowed. A PDF being downloadable, or owned by a member, does not establish redistribution or model-processing permission.

Mountain Project's linked terms limit ordinary access to personal use and restrict reuse of content without permission. Treat it as an external reference link unless a suitable written agreement is obtained. Do not assume that attribution, nonprofit operation, or factual-looking fields authorize bulk extraction. This is an operational recommendation based on the published terms, not a legal determination about every individual fact. [S11]

OpenBeta is the first dataset to evaluate. Its stated CC0 coverage is promising, but inspect current Chattanooga coverage, source provenance, missing coordinates, duplicate names, and freshness before adoption. Start with a sample audit rather than copying a whole country. Verify which photos and ancillary materials have separate rights. API availability and dataset licensing are separate questions. [S5, S6]

TheCrag's published API material requires negotiated access and a legal agreement; its documentation also restricts storage without agreement and says noncommercial API applications are closed. It should not be a dependency for a free launch. Recheck if a partnership becomes relevant. [S12]

For each source, record the source owner, URL, retrieval date, license or permission evidence, covered fields, allowed storage and public display, derivative-map rights, export rights, model-provider processing permission, attribution, expiration, and revocation contact. Track these rights separately: permission to store text does not automatically authorize placing it on a downloadable PNG.

A permission request should explain the community purpose, exact desired fields, public display, local caching, map exports, model retrieval and processing, expected audience, credit, and correction or removal process. Ask whether a small licensed extract is preferable to a whole guidebook. No outreach is sent as part of this planning package.

Provided PDFs enter a private staging area. Inspect ownership and permission first, extract only permitted content, retain page references, and review OCR and table associations manually. Publish normalized records only after review. Never commit raw guidebooks, permission correspondence containing personal details, or restricted scans to the public repository.

Original contributions need an explicit contribution choice. Recommended default: software under MIT; deliberately contributed public factual catalog data under CC0; photographs and descriptive writing under separately recorded terms. Forum posts and private session content do not become an open dataset by accident. Confirm contribution language before collecting data, since public licenses may be irrevocable even if an account is deleted.

## 10 Catalog structure and provenance

Use stable internal IDs independent of provider IDs. The catalog hierarchy is region, area, sector, feature such as a boulder or wall, and climb. Permit missing levels without inventing them. Aliases point to canonical records and include provenance, so “Little Rock City” and a locally used name can be resolved deliberately rather than by fuzzy text alone.

Core records include:

- Area: parent, canonical name, aliases, jurisdiction, time zone, public visibility, approved entry points, access source, coverage status, and review dates.
- Feature: area or sector, kind, reviewed name, position or local map coordinate, coordinate precision, and source.
- Climb: stable ID, feature, name, discipline, original grade, grade order, optional style and height tags, reviewed description, external references, publication state, and per-field evidence.
- Access notice: affected areas or segments, effective interval, status, authority, source, last check, and supersession history.
- Trail node and segment: endpoints, geometry or schematic placement, directionality, length or estimated time, permitted use, review state, source, and closure links.
- Source and permission: evidence and allowed uses; source assertions connect individual fields to their origin and confidence.
- Plan and plan stop: input preferences, ordered climb IDs, selected edges, data revisions, generation time, access-check time, warnings, and visibility.
- Account, profile, outing, participation, post, reply, report, and moderation action: community records with explicit ownership and access control.

Use a controlled set of review states: proposed, reviewed, published, disputed, withdrawn. A factual correction produces a revision, keeping the old value and reviewer decision. Imported updates must not silently overwrite locally reviewed fields. Prefer field-level provenance over assigning one license to an entire mixed record.

A database coordinate can identify an entire sector rather than the base of a climb. Store precision and the represented object; do not display six decimal places as a substitute for accuracy. Nearby climbing starts can also be separated by cliffs, fences, vegetation, or access restrictions, so geographic proximity cannot create a walking edge.

Deduplicate using source IDs and contextual candidates such as name plus parent feature. Human review resolves collisions. Keep import batches idempotent, with dry-run counts and a rollback path. Removing a source must disable dependent records and invalidate affected cached plans and exports while preserving an appropriate audit record.

Community observations are timestamped reports, not canonical facts. A comment that a hold broke or a path is blocked can trigger review or a temporary conservative restriction; a comment that an area is “open again” cannot override a land-manager closure. Do not scrape other communities' comments or treat popular opinion as an access authority.

## 11 Maps and downloadable PNGs

Separate travel to the parking area from movement inside the crag. An external Google Maps directions link can open the verified entry point without an embedded paid map. Google's Maps URLs documentation says these links do not require an API key. It does not establish permission to copy Google map imagery into our exports. [S13]

For the pilot, create an original map from reviewed local data. It can be a simple SVG with trails, boulders, meeting points, numbered stops, and a legend, rasterized to PNG by the application. Where only a schematic is supported, label it “not to scale” and omit invented distances, compass orientation, and geographic coordinates. Provide matching text directions.

A geographic version requires approved geometry, a coordinate reference system, and a checked map extent. Draw the actual reviewed path between stops. Do not draw straight lines between coordinates and imply that they are walkable trails. Do not trace a proprietary topo without permission.

Every export includes the area and sector, ordered stops, entry and exit, plan revision, generation date, data review date, relevant access note, source credits, and a short URL or QR code to check the current plan. Text must remain readable on a phone. Keep private participant data out of a public export and provide accessible HTML text equivalent to the image.

Exports are snapshots. A downloaded file cannot be recalled after a closure or correction, so the image must identify its age and point to the current page. Regenerate hosted versions when relevant data changes, show a stale warning on affected saved plans, and notify accepted participants of material changes through the available notification channel.

An OpenStreetMap-derived basemap is a later option. OSM data licensing and hosted tile usage are different obligations. The public tile policy prohibits bulk prefetching and offline download features. Do not build an export pipeline by sweeping its public tile servers; choose a permitted provider or render a small licensed extract ourselves, preserving required attribution and applicable database obligations. [S14, S15]

The pilot needs no continuous location permission, paid routing API, image-generation model, or large map server. Its quality depends on local map review, not rendering sophistication.

## 12 Conditions and access integration

Crag Conditions should initially be an ordinary external link configured per area. The supplied candidate address is https://cragconditions.com/. The retrieved page describes UK crags; confirm with the owner that this is the intended service before branding a link as the friend's project. Retrieval does not establish live uptime or ownership. [S16]

The community and planner must work if that site is unavailable. Do not proxy, scrape, embed, or cache its forecasts without an agreed interface and permission. If a future API is offered, define allowed use, update cadence, attribution, request limits, and stale-data behavior with its owner.

Separate forecasts, observed conditions, and official access notices in the interface. A weather forecast cannot certify that a climb is dry or open. Show observation time, source, and uncertainty. Do not calculate a “safe to climb” score from a generic rain threshold.

Local stewardship should be visible: link to SCC and relevant land managers, encourage guidebook purchases where appropriate, and make access corrections easy to report. Closures must be able to disable a sector or trail edge promptly without taking down the community.

## 13 Architecture and implementation choices

Recommended design: one Django application with server-rendered pages and small JavaScript enhancements; PostgreSQL for relational data and search; a local SVG-to-PNG renderer; and a replaceable model-provider adapter. Django's built-in data models and administration interface are useful for the large amount of catalog review this project needs. Use a currently supported framework release and lock exact dependencies when implementation starts. [S17]

Keep code in clear modules: accounts, community, catalog, access, planner, maps, and integrations. The planner is an ordinary service module with typed inputs and outputs, independent of the conversational interface. Use server-side authorization for every private plan, participant list, attachment, and export.

For a small catalog, relational filtering, aliases, and full-text search are sufficient. Add vector search only if an evaluation demonstrates that it improves retrieval. Do not begin with a separate vector database, microservices, Kubernetes, a locally hosted large model, or a Redis cluster.

A deployment contains a web service and database, plus a proxy only if the VPS does not already provide TLS and routing. A small worker using the same application image can handle exports and imports once needed. A database-backed job table is enough initially if workers implement atomic claims, retries, and idempotency. Use an external queue only when measurement justifies it.

Public requests follow this path: browser to reverse proxy to application to database. A planning request calls the deterministic planner; an optional model adapter performs interpretation or explanation. Exports are generated from saved plan records and stored in a persistent volume with visibility-aware access. Restricted source files live outside public media storage.

The alternative is a TypeScript full-stack application if maintainers strongly prefer that ecosystem. The data contracts and planner separation remain the same. Choose one implementation stack before scaffolding; do not build both. The recommended Django choice reduces the amount of administrative tooling we need to write.

AGENTS.md documents how coding agents work in the repository. It is not the runtime model's instruction store or a replacement for database rules. Version runtime prompts and tool schemas with the application; test them against stored scenarios. Important restrictions, such as closure filtering and permission checks, must be enforced in code.

## 14 VPS and Docker Compose operations

Use Docker Compose with pinned release images or reproducible application builds, health checks, restart policies, and named persistent volumes. PostgreSQL stays on an internal network without a public host port. Expose only the proxy publicly; if an existing VPS proxy is present, integrate with it rather than competing for ports 80 and 443.

Configuration includes the domain, allowed hosts, database credentials, application secret, optional model credentials, spending cap, and optional external conditions URL. Commit an example configuration with placeholders, never live secrets. Production disables debug output, uses secure cookies and CSRF protection, and limits uploads and request bodies.

A starting sizing hypothesis is 2 virtual CPUs and 2 to 4 GB of RAM for a small pilot, excluding a local model and depending on other VPS workloads. This is a load-test target, not a measured requirement. Check actual available RAM, storage, architecture, Docker support, and reverse-proxy setup before deployment.

The first release runbook must cover clean install, database migration, administrator creation, seed import, health verification, update, rollback, backup, and restore. Run migrations once as a controlled release step. Back up before schema changes and avoid assuming that reverting a container image reverses a database migration.

Back up the database, uploaded originals that may be retained, reviewed map sources, and configuration recovery information. Store encrypted backups away from the VPS and test restoration to an isolated environment. Proposed pilot objectives are no more than 24 hours of data loss and restoration within one working day; verify them with a drill before promising them.

Monitor uptime, error rate, available disk, job failures, backup age, planning latency, and model spend. Log operational identifiers and timing, avoiding full private prompts and messages by default. Define retention explicitly: proposed defaults are 14 days for routine request logs and 30 days for rotating operational backups, with restricted moderation records reviewed separately. Apply account deletion to active stores and disclose backup aging behavior.

No VPS deployment occurs during this planning phase. The implementation milestone will add a working Dockerfile and compose.yaml together with an application that can actually start; a nonfunctional Compose stub would make the repository misleading.

## 15 Keeping operation inexpensive

“Free for members” is achievable as a product policy; “zero operating cost” depends on existing infrastructure and donated maintenance. The VPS, domain, backups, email if enabled, and optional model calls still have costs. This plan uses spending allowances rather than unverified vendor price quotes.

Core mode has no model calls. A form produces deterministic itineraries and templated explanations, and existing plans remain readable without a provider. The owner can enable chat with a hard monthly budget, for example a proposed $5 to $10 pilot allowance, without making that expenditure necessary to use the community.

For budgeting, monthly model cost equals total input tokens divided by one million times the current input price, plus output tokens divided by one million times the current output price. As an illustrative workload, 1,000 generations using 2,500 input and 700 output tokens each consume 2.5 million input and 0.7 million output tokens before retries. These are assumptions for estimating demand, not observed usage or a provider quote.

Limit context to relevant records, cap output length and model calls per request, and cache only where permissions allow. Cache keys include normalized preferences, catalog and access revisions, prompt and model versions, and visibility scope. Never reuse private content across users. An access update invalidates related plans even when a cache has time remaining.

Enforce quotas per account and IP with a site-wide budget ledger. Reserve a conservative maximum request cost atomically before making a call so concurrent requests cannot overspend the cap; settle actual usage afterward. Set provider-level limits where available, rate-limit retries, and disable calls when pricing configuration is missing or stale. The interface falls back to structured planning with a clear explanation.

Do not rely on a temporary free API tier for production or assume a consumer chat subscription supplies server API usage. Hosting a model on a small CPU VPS could increase hardware demands and response times; evaluate it only if suitable hardware is already available and measured performance warrants it.

The principal noncash cost is stewardship: corrections, community moderation, access checks, and field verification. Before expanding areas, confirm someone can maintain each data pack. A small, current catalog is more useful than a large abandoned import.

## 16 Verification and launch criteria

Automated planner tests should cover exact grade ordering, aliases and ambiguity, closed areas, date-specific access, missing coordinates, disconnected graphs, return paths, time budgets, mixed disciplines, revoked sources, and unsupported model IDs. Property-style checks should ensure every selected stop is allowed and every walking leg follows approved edges.

Community tests must cover anonymous reading, account authorization, private plan isolation, participant visibility, concurrent joins at capacity, cancellation, reporting, blocking, and moderator audit trails. Test malicious HTML, oversized uploads, and prompt injection in imported descriptions. An exported URL must not bypass access control.

Model evaluation uses a small versioned set of realistic requests, including missing information and deliberate attempts to override restrictions. Every published result must resolve to approved records; zero fabricated IDs and zero known-closure violations are release gates. Measure helpfulness and preference fit separately with pilot users rather than using a model's own confidence score.

Field validation is required before advertising a navigable sector. At least two local reviewers should independently walk the published paths, check ambiguous junctions, locate the named stops, and report disagreement. Do not claim accessibility, trail difficulty, or safety certification from a casual walk-through. Record what was checked and when.

Proposed performance targets are a useful form-based result within two seconds for the pilot dataset, conversational response within fifteen seconds before falling back, and readable exports on a typical phone. Validate on the actual VPS and throttle expensive concurrent work. These are acceptance targets, not current benchmarks.

The initial pilot should include roughly 10 to 20 invited climbers, several hosted outings, and a range of grades. Suggested success signals after four weeks are repeated use by at least five members, several real outings involving someone the host did not previously know, and no unresolved wrong-location or access incidents. Treat these as experiments, not guaranteed outcomes or quotas for volunteers.

Track plans created and saved, invitations posted, join requests accepted, self-reported outings completed, return visits, correction rates, and moderator workload. Avoid public attendance tracking and exact-location analytics. Ask whether the application helped someone climb with a new person; raw signup counts alone do not measure the goal.

## 17 Roadmap and decision gates

Milestone 0 establishes feasibility: confirm the pilot sector and maintainers, interview five to eight local climbers, audit a small dataset sample, document permissions, and sketch the first reviewed trail graph. Exit only when there is a viable permitted data pack and someone responsible for corrections. If permissions fail, build with original contributions and reduce coverage.

Milestone 1 delivers the local community: accounts, profiles, area pages, structured outings, join states, discussion, reporting, and moderation. Deploy a private pilot through Compose and prove backup restoration. This can proceed while map work continues, but must not advertise a planner that does not exist.

Milestone 2 delivers the deterministic planner: reviewed climb records, aliases and grade sorting, project selection, time and walking constraints, approved paths, versioned plans, and original PNG exports. Exit after field review and automated failure-case coverage.

Milestone 3 adds conversational planning and opens the pilot: constrained model parsing, explanations, spend controls, provider-failure fallback, participant notifications, and a four-week evaluation. Launch publicly only if moderation ownership, privacy behavior, access maintenance, and the planner checks are operating reliably.

Milestone 4 expands coverage: add another Stone Fort sector, then choose a second area according to demand, permission, and local maintenance. Rope climbing has a separate readiness checklist. Native apps, live GPS, offline map packages, equipment matching, and deeper conditions integration stay in the later backlog.

For one experienced developer working part time with timely access to data and reviewers, a rough planning range is 1 to 2 weeks for feasibility, 2 to 3 for the community, 2 to 4 for the planner and maps, and 1 to 2 for conversational features, followed by the four-week pilot. These are estimates; permission responses and fieldwork are external dependencies and may dominate the schedule.

## 18 Open source and project governance

Use the existing public repository Dyno-man/Crag-Commune. Keep the project plan in Markdown as the editable source of truth and publish a readable Word companion. The initial repository should contain a README, roadmap and actionable issue backlog, AGENTS.md, contribution guidance, software license, data-rights policy, and issue templates.

Use milestones for feasibility, community, planner, and pilot. Create a small number of initial epic issues with checklists and acceptance criteria; split them into implementation issues when the work is ready. Reference dependencies and evidence rather than filing dozens of vague “add AI” tickets. Avoid artificial due dates before data feasibility is known.

Suggested workflow: triage, ready, in progress, review, done. Maintainers accept scope changes through issues or small design decisions. Keep pull requests focused, describe user-visible behavior and validation, and do not merge unreviewed source imports. A release should record data-pack revisions separately from application versions.

MIT is the proposed license for original code and project documentation. Third-party datasets retain their own terms; approved original factual contributions can use CC0. The code license must explicitly exclude community content, private records, photos, and licensed source material. Do not present the whole production database as MIT-licensed.

No one is represented as a partner, sponsor, instructor, or official access authority without agreement. A guidebook author, SCC representative, or the Crag Conditions owner may be invited to participate later; the planning document does not commit them to work.

## 19 Decisions still needed

The project name and public repository are established as Crag Commune and Dyno-man/Crag-Commune. The proposed stack, launch sector, and license split are working defaults that can be revised through the initial issues.

Before implementation, confirm the VPS operating system, available resources, existing proxy, domain, and backup destination. Select the pilot Stone Fort sector and local reviewers. Identify the exact area meant by St. Elmo. Confirm the friend's conditions URL and whether the intended arrangement is just a link. Decide whether chat begins with a small paid allowance or remains disabled during the first pilot.

Before collecting public contributions, finalize the contribution terms, privacy notice, age policy, recovery method, and moderator responsibilities. Before adding each new area, confirm data rights, access sources, field coverage, and a named maintenance role. These decisions can be tracked independently; they should not prevent work on the documentation, data schema, or community prototype.

## 20 Source register

Sources were consulted on September 22, 2026. Provider policies and access information must be checked again at implementation and before publication. Links establish the cited finding, not endorsement or permission beyond their stated terms.

- S1 Mountain Project home and route finder: https://www.mountainproject.com/
- S2 Mountain Project partner finder: https://www.mountainproject.com/partner-finder
- S3 KAYA product and lists: https://kayaclimb.com/ and https://kayaclimb.com/blog/climb-lists
- S4 Gora climbing partner and session product: https://goraclimb.com/
- S5 OpenBeta licensing FAQ and dataset: https://github.com/OpenBeta/docs.openbeta.io/blob/develop/docs/faq.mdx and https://github.com/OpenBeta/climbing-data
- S6 OpenBeta GraphQL API documentation and code license: https://github.com/OpenBeta/openbeta-graphql
- S7 Discourse installation documentation: https://github.com/discourse/discourse/blob/main/docs/INSTALL.md
- S8 SCC Stone Fort access information: https://www.seclimbers.org/project/stone-fort/
- S9 SCC Leda access information: https://www.seclimbers.org/project/leda/
- S10 SCC Rocktown access information: https://www.seclimbers.org/project/rocktown/
- S11 Terms linked by Mountain Project, revised August 4, 2023: https://www.adventureprojects.net/ap-terms
- S12 TheCrag integration and API policies: https://www.thecrag.com/en/article/extend and https://www-internal.thecrag.com/en/article/api
- S13 Google Maps URLs documentation: https://developers.google.com/maps/documentation/urls/get-started
- S14 OpenStreetMap hosted tile policy: https://operations.osmfoundation.org/policies/tiles/
- S15 OpenStreetMap copyright and license: https://www.openstreetmap.org/copyright
- S16 Candidate Crag Conditions site: https://cragconditions.com/
- S17 Django framework overview: https://docs.djangoproject.com/en/5.2/intro/overview/
