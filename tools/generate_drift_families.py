"""
Generate three new scenario families for the MVI benchmark:
  - preference_drift           (pd001–pd035)
  - external_dependency_change (ed001–ed035)
  - stakeholder_conflict       (stk001–stk035)

Run from the repo root or the tools/ directory:
    python tools/generate_drift_families.py
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = ROOT / "scenarios"
SCHEMA_VERSION = "mvi-scenario-v1"


def write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def mem(mid: str, tier: str, content: str, validity: str, bucket: str, notes: str | None = None) -> dict:
    d: dict = {"id": mid, "tier": tier, "content": content, "validity": validity, "bucket": bucket}
    if notes:
        d["notes"] = notes
    return d


def std_scenario(
    family: str,
    sid: str,
    task: str,
    budget: int,
    s1: str, p1: str, p2: str, l1: str,
    x1: str, x1_notes: str, x2: str,
    x1_validity: str = "stale",
    x1_tier: str = "project",
    x1_bucket: str = "supporting",
    split: str = "public",
) -> dict:
    mems = [
        mem(f"{sid}-s1", "session",   s1, "valid",     "critical"),
        mem(f"{sid}-p1", "project",   p1, "valid",     "critical"),
        mem(f"{sid}-p2", "project",   p2, "valid",     "supporting"),
        mem(f"{sid}-l1", "long_term", l1, "valid",     "supporting"),
        mem(f"{sid}-x1", x1_tier,     x1, x1_validity, x1_bucket, notes=x1_notes),
        mem(f"{sid}-x2", "project",   x2, "stale",     "supporting"),
    ]
    return {
        "schema_version": SCHEMA_VERSION,
        "scenario_id": sid,
        "family": family,
        "split": split,
        "task": task,
        "repo_state_fingerprint": f"{sid}-repo-v1",
        "token_budget": budget,
        "candidate_memories": mems,
        "gold_valid_ids": [f"{sid}-s1", f"{sid}-p1", f"{sid}-p2", f"{sid}-l1"],
        "gold_invalid_ids": [f"{sid}-x1", f"{sid}-x2"],
        "preferred_order_buckets": [
            {"name": "session_critical", "memory_ids": [f"{sid}-s1"]},
            {"name": "project_critical", "memory_ids": [f"{sid}-p1"]},
            {"name": "supporting",       "memory_ids": [f"{sid}-p2", f"{sid}-l1"]},
        ],
        "task_outcome_baselines": {"no_memory": 0.12, "ideal": 1.0},
    }


# ─── PREFERENCE DRIFT ────────────────────────────────────────────────────────
# The user changed a stated preference mid-project.  x1 is the OLD preference
# (stale) that was superseded.  The system must surface the newer preference
# and demote or invalidate x1.

_PD_HOLDOUTS = {f"pd{n:03d}" for n in range(24, 36)}

_PD_DEFS = [
    # (sid, task, budget, s1, p1, p2, l1, x1, x1_notes, x2)
    ("pd001", "Implement new API response formatting using the updated preference for camelCase keys.", 190,
     "User explicitly stated in session 24: switch all API response keys from snake_case to camelCase.",
     "Current project style guide (updated session 24) mandates camelCase for all HTTP response payloads.",
     "API response envelope fields (data, error, meta) must also use camelCase after the migration.",
     "When a style preference is explicitly changed mid-project, demote all prior style memories immediately.",
     "Project style guide (session 3): all API response keys must use snake_case for consistency with the DB schema.",
     "preference_drift: old snake_case preference superseded by explicit camelCase instruction in session 24",
     "Old integration note says client scripts were written to expect snake_case response keys."),

    ("pd002", "Write new test utilities using the updated preference for integration tests over unit tests.", 195,
     "User stated in session 31: stop writing isolated unit tests for service logic; use integration tests only.",
     "Current test policy (updated session 31) requires integration tests against real dependencies, not mocks.",
     "New test utilities must provision real database connections, not in-memory fakes.",
     "When testing preference changes, update all test scaffolding to match the new policy before writing tests.",
     "Test policy (session 5): all service logic must be covered by isolated unit tests with mocked dependencies.",
     "preference_drift: old unit-test-first policy superseded by explicit integration-test preference in session 31",
     "Old coverage note says unit test coverage was required at 80% before integration tests were considered."),

    ("pd003", "Implement logging with the updated preference for structured JSON logs, not plain text.", 185,
     "User directed in session 18: switch all logging from plain text to structured JSON immediately.",
     "Logging standard (updated session 18) requires all log statements to emit structured JSON with level, msg, and trace fields.",
     "Existing plain-text log calls must be migrated as part of any file touched during this task.",
     "When a logging format preference changes, treat all plain-text log calls in touched files as technical debt.",
     "Logging standard (session 2): use plain human-readable text log lines for clarity during development.",
     "preference_drift: old plain-text logging preference superseded by structured JSON mandate in session 18",
     "Old debug note says plain-text logs are easier to read in the terminal during local development."),

    ("pd004", "Implement the new async/await version of the task runner per the updated coding preference.", 200,
     "User stated in session 40: stop using callback-style async; all new async code must use async/await.",
     "Code style guide (updated session 40): async/await is the mandatory pattern for all asynchronous operations.",
     "Callback-based code in files touched during this task should be migrated to async/await.",
     "When async style preference changes explicitly, apply it to all new code and refactor touched files.",
     "Code style guide (session 12): use callback-style async for all async operations to avoid Promise chain issues.",
     "preference_drift: old callback preference superseded by explicit async/await mandate in session 40",
     "Old compatibility note says callback style was chosen to support older Node.js runtimes in the project."),

    ("pd005", "Apply the updated error handling preference: return Result types instead of throwing exceptions.", 190,
     "User directed in session 27: stop throwing exceptions for expected errors; return Result/Either types instead.",
     "Error handling policy (updated session 27): all expected errors must be expressed as Result return values.",
     "Unhandled exception paths in files touched during this task should be migrated to Result returns.",
     "When error handling preference changes, treat exception-throwing for expected errors as a pattern violation.",
     "Error handling policy (session 8): throw typed exceptions for all error conditions to simplify call sites.",
     "preference_drift: old exception-throwing preference superseded by Result type mandate in session 27",
     "Old error note says typed exceptions were chosen because the team found Result types verbose in early review."),

    ("pd006", "Implement the new database access pattern using the updated preference for raw SQL over ORM.", 195,
     "User stated in session 33: switch all new database queries from the ORM to raw SQL with parameterized queries.",
     "Database access policy (updated session 33): raw SQL with named parameters is now the required approach.",
     "ORM-based queries in files touched during this task should be migrated to raw SQL.",
     "When a database access preference changes, flag all ORM calls in touched files for migration.",
     "Database access policy (session 7): use the ORM exclusively for all database interactions for safety and portability.",
     "preference_drift: old ORM mandate superseded by explicit raw SQL preference in session 33",
     "Old data note says ORM was chosen to prevent SQL injection and enable multi-database support."),

    ("pd007", "Implement state management using the updated preference for server-side state over client state.", 185,
     "User directed in session 29: move all session state from client-side local storage to server-side sessions.",
     "State management policy (updated session 29): no sensitive state may persist in client-side storage.",
     "All new session flows must use server-side session tokens and clear client-side storage on logout.",
     "When state management preference changes, treat client-side storage of session data as a policy violation.",
     "State management policy (session 6): use client-side local storage for session state to reduce server load.",
     "preference_drift: old client-state preference superseded by server-side session mandate in session 29",
     "Old performance note says client-side state was chosen to avoid server memory overhead at scale."),

    ("pd008", "Implement the API pagination using the updated preference for cursor-based over offset-based.", 200,
     "User stated in session 22: switch all API pagination from offset/limit to cursor-based pagination.",
     "API pagination standard (updated session 22): all list endpoints must use opaque cursor tokens.",
     "Offset/limit pagination parameters in existing endpoints must be deprecated and cursor params added.",
     "When pagination preference changes, add cursor support before deprecating offset params in touched endpoints.",
     "API pagination standard (session 4): use offset/limit pagination for all list endpoints for simplicity.",
     "preference_drift: old offset pagination preference superseded by cursor-based mandate in session 22",
     "Old API note says offset pagination was chosen because it is easier to implement and test."),

    ("pd009", "Use the updated import style: named exports preferred over default exports.", 190,
     "User directed in session 35: stop using default exports; all new modules must use named exports only.",
     "Module style guide (updated session 35): named exports are mandatory for all new and refactored modules.",
     "Default export patterns in files touched during this task should be migrated to named exports.",
     "When module export style preference changes, apply the new style consistently to all touched modules.",
     "Module style guide (session 9): use default exports to keep import statements simple for consumers.",
     "preference_drift: old default-export preference superseded by named-export mandate in session 35",
     "Old module note says default exports were chosen to align with the existing team coding conventions."),

    ("pd010", "Apply the updated configuration approach: environment variables only, no config files.", 195,
     "User stated in session 38: remove all config file reading; all configuration must come from environment variables.",
     "Configuration policy (updated session 38): environment variables are the single source of truth for all config.",
     "Config file readers in files touched during this task should be replaced with env var reads.",
     "When configuration source preference changes, treat config file reads in touched files as policy violations.",
     "Configuration policy (session 11): use TOML config files for all configuration; environment variables are overrides only.",
     "preference_drift: old config-file preference superseded by env-var-only mandate in session 38",
     "Old config note says TOML config files were chosen for explicitness and the ability to version control defaults."),

    ("pd011", "Implement new data validation using the updated preference for schema-first validation.", 185,
     "User directed in session 26: switch all input validation from imperative checks to schema-first validation.",
     "Validation policy (updated session 26): JSON Schema or equivalent is required for all API input validation.",
     "Imperative validation logic in files touched during this task should be migrated to schema definitions.",
     "When validation preference changes, generate schemas from existing imperative checks before removing them.",
     "Validation policy (session 5): write imperative validation functions for clear and debuggable validation logic.",
     "preference_drift: old imperative validation preference superseded by schema-first mandate in session 26",
     "Old validation note says imperative checks were chosen because schema validation had poor error messages."),

    ("pd012", "Write the new API endpoints using the updated preference for REST over GraphQL.", 200,
     "User stated in session 44: stop adding new GraphQL resolvers; all new API surfaces must be RESTful.",
     "API design policy (updated session 44): REST is the required approach for all new endpoints.",
     "GraphQL resolver additions to existing schemas are no longer permitted for new features.",
     "When API design preference changes, document REST endpoint design before implementing any resolver.",
     "API design policy (session 14): all new API surfaces must be implemented as GraphQL resolvers for flexibility.",
     "preference_drift: old GraphQL preference superseded by REST-only mandate in session 44",
     "Old API note says GraphQL was chosen to allow frontend teams to fetch exactly the data they need."),

    ("pd013", "Implement the new feature flag system using the updated preference for static config over dynamic.", 190,
     "User directed in session 32: stop adding runtime feature flag checks; use build-time static config instead.",
     "Feature flag policy (updated session 32): feature availability must be determined at build time, not runtime.",
     "Runtime feature flag library calls in new code are no longer permitted under the updated policy.",
     "When feature flag strategy changes, replace runtime checks with build-time constants in touched files.",
     "Feature flag policy (session 8): use a runtime feature flag service for all new feature gates for flexibility.",
     "preference_drift: old runtime feature flag preference superseded by static build-time mandate in session 32",
     "Old product note says runtime flags were chosen so features could be toggled without a redeploy."),

    ("pd014", "Implement caching using the updated preference for Redis over in-process memory cache.", 195,
     "User stated in session 37: stop using in-process memory caches; switch all caching to Redis for consistency.",
     "Caching policy (updated session 37): Redis is the required cache backend for all new caching needs.",
     "In-process cache implementations in files touched during this task should be migrated to Redis client calls.",
     "When cache backend preference changes, add Redis client configuration before migrating in-process caches.",
     "Caching policy (session 10): use in-process memory caches to avoid network overhead for frequently read data.",
     "preference_drift: old in-process cache preference superseded by Redis mandate in session 37",
     "Old performance note says in-process caches were chosen to avoid Redis dependency for simpler deployments."),

    ("pd015", "Apply the updated code organization preference: one class per file, no grouped modules.", 185,
     "User directed in session 28: split all grouped module files so each type or class lives in its own file.",
     "Code organization policy (updated session 28): one exported class or type per file is now mandatory.",
     "Multi-class files in directories touched during this task should be split as part of routine work.",
     "When file organization preference changes, split files as you touch them rather than in a separate pass.",
     "Code organization policy (session 6): group related types in a single file for navigational convenience.",
     "preference_drift: old grouped-module preference superseded by one-class-per-file mandate in session 28",
     "Old structure note says grouped modules were chosen to reduce the number of files in the project."),

    ("pd016", "Implement the new service communication using the updated preference for gRPC over REST.", 200,
     "User stated in session 41: switch all new internal service calls from REST to gRPC for typed contracts.",
     "Internal service communication policy (updated session 41): gRPC is required for all new internal calls.",
     "REST-based internal service clients in files touched during this task should be marked for migration.",
     "When internal communication preference changes, generate proto files before implementing gRPC clients.",
     "Internal communication policy (session 13): use REST for all internal service communication for simplicity.",
     "preference_drift: old internal REST preference superseded by gRPC mandate in session 41",
     "Old service note says REST was chosen for internal calls to allow easy testing with curl."),

    ("pd017", "Implement new date handling using the updated preference for UTC-only timestamps.", 190,
     "User directed in session 36: stop storing local timezone timestamps; all timestamps must be UTC-only.",
     "Timestamp policy (updated session 36): all stored and transmitted timestamps must be in UTC ISO 8601 format.",
     "Timezone-aware timestamp handling in files touched during this task should be migrated to UTC.",
     "When timestamp policy changes, audit all date fields in touched models before writing new code.",
     "Timestamp policy (session 9): store timestamps in local timezone to avoid conversion overhead at query time.",
     "preference_drift: old local-timezone preference superseded by UTC-only mandate in session 36",
     "Old data note says local timezone timestamps were chosen to simplify display in the user's region."),

    ("pd018", "Write the new API client using the updated preference for generated clients over hand-written.", 185,
     "User stated in session 43: stop hand-writing API clients; generate all clients from the OpenAPI spec.",
     "Client generation policy (updated session 43): generated clients from the OpenAPI spec are mandatory.",
     "Hand-written API client code in files touched during this task should be replaced with generated clients.",
     "When client generation preference changes, update the OpenAPI spec before running the code generator.",
     "Client generation policy (session 12): write API clients by hand to keep tight control over behavior.",
     "preference_drift: old hand-written client preference superseded by generated client mandate in session 43",
     "Old API note says hand-written clients were chosen because the generator produced verbose boilerplate."),

    ("pd019", "Apply the updated deployment preference: containers only, no bare-metal VM deployments.", 200,
     "User directed in session 39: stop deploying to VMs; all new deployments must use container images.",
     "Deployment policy (updated session 39): container-based deployments are required for all new services.",
     "VM-based deployment scripts in files touched during this task should be flagged as deprecated.",
     "When deployment infrastructure preference changes, write Dockerfiles before modifying deployment scripts.",
     "Deployment policy (session 11): deploy to bare-metal VMs for lowest latency and simplest runtime.",
     "preference_drift: old bare-metal VM preference superseded by containers-only mandate in session 39",
     "Old infra note says VM deployments were chosen to avoid the overhead of container orchestration."),

    ("pd020", "Implement new authentication using the updated preference for JWTs over session cookies.", 190,
     "User stated in session 25: switch all authentication from session cookies to signed JWTs immediately.",
     "Authentication policy (updated session 25): JWTs are required for all new authentication flows.",
     "Session cookie-based auth in files touched during this task should be migrated to JWT issuance.",
     "When auth mechanism preference changes, update the token verification middleware before changing issue logic.",
     "Authentication policy (session 7): use session cookies for authentication to leverage browser security defaults.",
     "preference_drift: old session cookie preference superseded by JWT mandate in session 25",
     "Old security note says session cookies were chosen to avoid JWT key management complexity."),

    ("pd021", "Write new code comments using the updated preference for doc comments over inline comments.", 185,
     "User directed in session 30: remove all inline comments and use doc comments on public symbols only.",
     "Comment policy (updated session 30): doc comments on exported functions are required; inline comments are banned.",
     "Inline comments in files touched during this task should be removed and replaced with doc comment blocks.",
     "When comment style preference changes, apply it to all newly written and touched code.",
     "Comment policy (session 4): use inline comments freely to explain complex logic for future readers.",
     "preference_drift: old inline comment preference superseded by doc-comment-only mandate in session 30",
     "Old style note says inline comments were chosen because the team found doc comments overly formal."),

    ("pd022", "Implement the new data serialization using the updated preference for Protocol Buffers over JSON.", 200,
     "User stated in session 42: switch all internal data serialization from JSON to Protocol Buffers.",
     "Serialization policy (updated session 42): Protocol Buffers are required for all internal data exchange.",
     "JSON serialization for internal data exchange in files touched during this task should be flagged.",
     "When serialization preference changes, define proto schemas before migrating JSON serialization code.",
     "Serialization policy (session 13): use JSON for all data serialization for human readability and flexibility.",
     "preference_drift: old JSON serialization preference superseded by Protocol Buffers mandate in session 42",
     "Old data note says JSON was chosen because Protocol Buffers require a compile step that slowed iteration."),

    ("pd023", "Apply the updated branching strategy: trunk-based development over feature branches.", 195,
     "User directed in session 45: stop creating long-lived feature branches; commit directly to trunk with feature flags.",
     "Branching policy (updated session 45): trunk-based development with feature flags is now mandatory.",
     "Long-lived feature branches in the active repository should be flagged for integration into trunk.",
     "When branching strategy changes, add feature flag scaffolding before merging any in-progress branches.",
     "Branching policy (session 15): all work must happen on named feature branches; direct trunk commits are prohibited.",
     "preference_drift: old feature-branch mandate superseded by trunk-based development policy in session 45",
     "Old workflow note says feature branches were chosen to enable code review before any changes reached trunk."),

    # HOLDOUTS (pd024–pd035)

    ("pd024", "Implement error reporting using the updated preference for centralized error tracking over local logs.", 195,
     "User stated in session 46: send all errors to the centralized error tracking service, not to local log files.",
     "Error reporting policy (updated session 46): centralized error tracking is required for all production errors.",
     "Local log-based error reporting in files touched during this task should be migrated to error tracking calls.",
     "When error reporting preference changes, add error tracking SDK calls before removing local log handlers.",
     "Error reporting policy (session 16): write all errors to local log files for simplicity and portability.",
     "preference_drift: old local-log error reporting superseded by centralized tracking mandate in session 46",
     "Old ops note says local logs were chosen because they do not require an external service dependency."),

    ("pd025", "Write the new API using the updated preference for versioned endpoints over version headers.", 185,
     "User directed in session 47: stop using version headers; all API versioning must use URL path versioning.",
     "API versioning policy (updated session 47): URL path versioning (/v1/, /v2/) is now required.",
     "Header-based versioning in existing endpoints must be deprecated in favor of path versioning.",
     "When API versioning preference changes, add path-versioned routes before deprecating header-based ones.",
     "API versioning policy (session 17): use version headers (API-Version: 2) to keep URLs clean.",
     "preference_drift: old header versioning preference superseded by URL path versioning mandate in session 47",
     "Old API note says version headers were chosen because URL versioning creates breaking changes in bookmarks."),

    ("pd026", "Apply the updated database transaction policy: explicit transactions for all multi-step writes.", 200,
     "User stated in session 48: wrap all multi-step database writes in explicit transactions, no auto-commit.",
     "Transaction policy (updated session 48): explicit transactions are required for any write that spans two or more steps.",
     "Auto-committed multi-step writes in files touched during this task should be migrated to explicit transactions.",
     "When transaction policy changes, add transaction scaffolding before modifying write logic in touched files.",
     "Transaction policy (session 18): rely on auto-commit for individual writes; only use transactions for long workflows.",
     "preference_drift: old auto-commit preference superseded by explicit transaction mandate in session 48",
     "Old data note says auto-commit was chosen to simplify code for writes that rarely span multiple steps."),

    ("pd027", "Implement event handling using the updated preference for event sourcing over direct DB writes.", 190,
     "User stated in session 49: move all state mutations to event sourcing; no direct DB writes for domain changes.",
     "State mutation policy (updated session 49): all domain state changes must be recorded as events first.",
     "Direct DB write patterns for domain changes in files touched during this task should be flagged for migration.",
     "When state mutation preference changes, implement the event store schema before migrating write code.",
     "State mutation policy (session 19): write domain changes directly to the database for simplicity.",
     "preference_drift: old direct-write preference superseded by event sourcing mandate in session 49",
     "Old architecture note says direct DB writes were chosen because event sourcing adds implementation complexity."),

    ("pd028", "Write new documentation using the updated preference for Markdown over Confluence pages.", 195,
     "User directed in session 50: stop writing documentation in Confluence; all docs must be Markdown in the repo.",
     "Documentation policy (updated session 50): Markdown files in the repository are the required documentation format.",
     "Confluence-based documentation for features touched during this task should be migrated to Markdown.",
     "When documentation format preference changes, create the Markdown structure before removing Confluence pages.",
     "Documentation policy (session 20): write all technical documentation in Confluence for centralized access.",
     "preference_drift: old Confluence preference superseded by repo-Markdown mandate in session 50",
     "Old doc note says Confluence was chosen because it allows non-engineers to contribute without Git knowledge."),

    ("pd029", "Implement rate limiting using the updated preference for token bucket over fixed window.", 185,
     "User stated in session 51: replace all fixed-window rate limiting with token bucket rate limiting.",
     "Rate limiting policy (updated session 51): token bucket algorithm is required for all rate limiting.",
     "Fixed-window rate limit implementations in files touched during this task should be migrated to token bucket.",
     "When rate limiting algorithm preference changes, verify token bucket parameters with the team before migrating.",
     "Rate limiting policy (session 21): use fixed-window rate limiting for simplicity and predictable behavior.",
     "preference_drift: old fixed-window preference superseded by token bucket mandate in session 51",
     "Old API note says fixed-window limiting was chosen because token bucket state is harder to distribute."),

    ("pd030", "Apply the updated observability preference: distributed tracing over per-service metrics only.", 200,
     "User directed in session 52: implement distributed tracing across all services, not just per-service metrics.",
     "Observability policy (updated session 52): OpenTelemetry distributed tracing is required for all services.",
     "Per-service-only metric instrumentation in files touched during this task should be supplemented with trace spans.",
     "When observability preference changes, add trace context propagation before adding new metric instrumentation.",
     "Observability policy (session 22): instrument each service with local Prometheus metrics only.",
     "preference_drift: old per-service metrics preference superseded by distributed tracing mandate in session 52",
     "Old ops note says per-service metrics were chosen because distributed tracing adds per-request overhead."),

    ("pd031", "Implement new configuration validation using the updated preference for startup validation.", 195,
     "User stated in session 53: validate all configuration at startup and fail fast; do not validate lazily at use time.",
     "Config validation policy (updated session 53): all configuration must be validated before the service accepts requests.",
     "Lazy configuration validation in files touched during this task should be migrated to startup validation.",
     "When config validation preference changes, add a startup validation pass before removing lazy checks.",
     "Config validation policy (session 23): validate configuration lazily at the point of use to simplify startup.",
     "preference_drift: old lazy validation preference superseded by startup fail-fast mandate in session 53",
     "Old startup note says lazy validation was chosen to speed up service startup during local development."),

    ("pd032", "Write the new background worker using the updated preference for pull-based over push-based.", 185,
     "User stated in session 54: switch background workers from push-based triggers to pull-based polling.",
     "Background worker policy (updated session 54): workers must poll for work, not receive pushed triggers.",
     "Push-triggered worker patterns in files touched during this task should be migrated to poll loops.",
     "When background worker trigger preference changes, implement the poll interval config before migrating triggers.",
     "Background worker policy (session 24): use push-based triggers from the message queue for low-latency worker starts.",
     "preference_drift: old push-based trigger preference superseded by pull-based polling mandate in session 54",
     "Old worker note says push triggers were chosen because polling introduces latency for time-sensitive tasks."),

    ("pd033", "Apply the updated code review preference: required architectural review for all data model changes.", 200,
     "User directed in session 55: all data model changes must get architect sign-off before merging.",
     "Review policy (updated session 55): architect review is mandatory for any change to data models or schemas.",
     "Data model changes without architect review in the current branch should be flagged before proceeding.",
     "When review policy changes, add the architectural review step to the PR template before submitting.",
     "Review policy (session 25): peer code review by any senior engineer is sufficient for data model changes.",
     "preference_drift: old peer-review-only preference superseded by architect sign-off mandate in session 55",
     "Old process note says peer review was chosen to avoid bottlenecks on architect availability."),

    ("pd034", "Implement the new health check endpoint using the updated preference for deep health over shallow.", 190,
     "User stated in session 56: replace shallow ping health checks with deep health checks that verify dependencies.",
     "Health check policy (updated session 56): all services must implement a deep health endpoint that checks downstream deps.",
     "Shallow ping-only health endpoints in files touched during this task should be enhanced with dependency checks.",
     "When health check depth preference changes, add dependency check stubs before wiring real health calls.",
     "Health check policy (session 26): use shallow ping health checks to avoid cascading health failures.",
     "preference_drift: old shallow health check preference superseded by deep dependency check mandate in session 56",
     "Old ops note says shallow checks were chosen to prevent downstream failures from marking healthy services as unhealthy."),

    ("pd035", "Apply the updated testing data preference: generated test data over hardcoded fixtures.", 195,
     "User directed in session 57: stop using hardcoded fixture files; generate all test data programmatically.",
     "Test data policy (updated session 57): programmatically generated test data is required for all new tests.",
     "Hardcoded fixture files touched during this task should be replaced with generator functions.",
     "When test data preference changes, write data generator utilities before migrating existing fixtures.",
     "Test data policy (session 27): use hardcoded fixture files for reproducibility and simplicity in test setup.",
     "preference_drift: old hardcoded fixture preference superseded by programmatic generation mandate in session 57",
     "Old test note says hardcoded fixtures were chosen because generated data can produce non-deterministic test failures."),
]


def gen_preference_drift() -> None:
    for row in _PD_DEFS:
        sid = row[0]
        split = "holdout" if sid in _PD_HOLDOUTS else "public"
        sc = std_scenario(
            "preference_drift", sid, *row[1:],
            x1_validity="stale", x1_tier="project", x1_bucket="supporting",
            split=split,
        )
        write(SCENARIOS / "preference_drift" / f"{sid}.json", sc)
    print(f"preference_drift: {len(_PD_DEFS)} scenarios written.")


# ─── EXTERNAL DEPENDENCY CHANGE ──────────────────────────────────────────────
# An external library or API changed externally.  The stored memory about the
# old endpoint/type/contract is now false.  x1 is the stale memory that
# references the deprecated behavior.

_ED_HOLDOUTS = {f"ed{n:03d}" for n in range(24, 36)}

_ED_DEFS = [
    # (sid, task, budget, s1, p1, p2, l1, x1, x1_notes, x2)
    ("ed001", "Fix Stripe API integration after the payment provider deprecated the v1 charge endpoint.", 195,
     "Integration logs show 410 Gone responses; Stripe removed the /v1/charges endpoint in API version 2024-01.",
     "Current Stripe integration must use /v1/payment_intents per the provider's migration guide.",
     "Stripe's 2024-01 version also changed the idempotency key header name from Idempotency-Key to Stripe-Idempotency-Key.",
     "When a payment provider deprecates an endpoint, update the client before changing any application logic.",
     "Stripe integration note (session 8): use /v1/charges with the source parameter for one-time card payments.",
     "external_dependency_change: /v1/charges endpoint deprecated and removed in Stripe API 2024-01",
     "Old compatibility note says /v1/charges works for legacy integrations that have not migrated."),

    ("ed002", "Fix the AWS S3 client after AWS deprecated the path-style URL addressing for new buckets.", 200,
     "S3 client is receiving 400 errors for new buckets created after December 2023; virtual-hosted addressing is required.",
     "AWS S3 buckets created after December 2023 must use virtual-hosted addressing (bucket.s3.amazonaws.com).",
     "The S3 client config must set force_path_style to false for all new bucket operations.",
     "When AWS deprecates a URL style, audit all S3 client configurations before adding new bucket operations.",
     "S3 client note (session 5): always set force_path_style=true for compatibility with older S3-compatible endpoints.",
     "external_dependency_change: S3 path-style URL addressing deprecated for buckets created after December 2023",
     "Old S3 note says path-style addressing was required for compatibility with non-AWS S3 endpoints in the stack."),

    ("ed003", "Fix the SendGrid email client after the provider removed the legacy v2 send API.", 190,
     "Email delivery failures show 404 responses; SendGrid removed the v2 /mail/send endpoint in January 2024.",
     "Current email integration must use the SendGrid v3 API endpoint at /v3/mail/send.",
     "SendGrid v3 requires a personalizations array in the request body; the v2 to/from format is not accepted.",
     "When an email provider removes an API version, update the client payload structure as well as the endpoint.",
     "SendGrid integration note (session 6): use the v2 API at /mail/send with to, from, subject, and text fields.",
     "external_dependency_change: SendGrid v2 /mail/send endpoint removed; v3 /v3/mail/send is required",
     "Old email note says the v2 API is simpler to use and is still documented in internal wikis."),

    ("ed004", "Fix the Google OAuth integration after Google deprecated the deprecated token info endpoint.", 185,
     "Token validation is failing with 404; Google removed the /oauth2/v2/tokeninfo endpoint in March 2024.",
     "Google OAuth token validation must now use the /oauth2/v3/userinfo endpoint or the token introspection endpoint.",
     "The v3 userinfo endpoint returns a sub field for user ID instead of the user_id field from v2.",
     "When an identity provider removes a token validation endpoint, update both the URL and the response field mapping.",
     "Google OAuth note (session 9): validate tokens using /oauth2/v2/tokeninfo and extract the user_id field.",
     "external_dependency_change: /oauth2/v2/tokeninfo removed; token validation must use v3 endpoints",
     "Old auth note says tokeninfo v2 was the recommended approach for server-side token verification."),

    ("ed005", "Fix the Twilio SMS client after the provider changed the message status webhook payload.", 195,
     "Webhook handler is throwing null pointer errors; Twilio changed the status field from MessageStatus to SmsStatus.",
     "Current Twilio webhook handler must read the SmsStatus field instead of the removed MessageStatus field.",
     "Twilio also renamed the SmsSid field to MessageSid in the same webhook payload change.",
     "When a messaging provider changes webhook payload field names, update all field references atomically.",
     "Twilio webhook note (session 7): parse the MessageStatus and SmsSid fields from the Twilio status webhook payload.",
     "external_dependency_change: Twilio renamed MessageStatus to SmsStatus and SmsSid to MessageSid in webhooks",
     "Old SMS note says Twilio webhook fields are stable and do not change between API versions."),

    ("ed006", "Fix the Elasticsearch client after the provider removed the deprecated _type field support.", 200,
     "Index operations are returning 400 errors; Elasticsearch 8.x removed support for the _type field in all APIs.",
     "All Elasticsearch document operations must omit the _type field; it is no longer accepted.",
     "Index mappings must be recreated without _type to use Elasticsearch 8.x without compatibility mode.",
     "When Elasticsearch removes a major legacy feature, audit all document and index operations for _type usage.",
     "Elasticsearch note (session 10): include _type in document index calls for compatibility with multi-type indices.",
     "external_dependency_change: _type field removed from all Elasticsearch 8.x APIs; indices must omit it",
     "Old search note says _type was useful for organizing multiple document kinds in a single index."),

    ("ed007", "Fix the Kubernetes client after the provider removed the deprecated apps/v1beta1 API group.", 190,
     "Deployment manifests are failing validation; Kubernetes removed the apps/v1beta1 API group in version 1.26.",
     "All Deployment and StatefulSet manifests must use the apps/v1 API group.",
     "The apps/v1 API requires a selector.matchLabels field that was optional in apps/v1beta1.",
     "When Kubernetes removes a deprecated API group, update all affected manifests and add required fields.",
     "Kubernetes manifest note (session 4): use apps/v1beta1 for Deployment manifests for backward compatibility.",
     "external_dependency_change: apps/v1beta1 API group removed in Kubernetes 1.26; apps/v1 is required",
     "Old k8s note says v1beta1 was kept for backward compatibility and would not be removed without notice."),

    ("ed008", "Fix the npm package after the axios library changed its error response format in v1.0.", 185,
     "Error handling is broken after upgrading axios; the error.response.data structure changed in axios v1.0.",
     "Axios v1.0 moved error details from error.response.data to error.response.data.error for structured errors.",
     "Axios v1.0 also removed the error.request shorthand; use error.config.url for request metadata instead.",
     "When a major dependency changes its error format, update all error handling code before upgrading.",
     "Axios integration note (session 11): read HTTP error details from error.response.data for API error messages.",
     "external_dependency_change: axios v1.0 restructured error response format; error.response.data.error is now standard",
     "Old HTTP note says axios error.response.data reliably contains the API error payload in all versions."),

    ("ed009", "Fix the GitHub API integration after GitHub removed the deprecated v3 search rate limit header.", 200,
     "Rate limit tracking is broken; GitHub removed the X-RateLimit-Search-Remaining header in February 2024.",
     "GitHub API search rate limits must now be read from the x-ratelimit-remaining header in the resource-specific context.",
     "The GitHub API also deprecated the link header pagination in favor of cursor-based pagination tokens.",
     "When a VCS provider removes a rate limit header, update rate limit tracking before making more API calls.",
     "GitHub API note (session 8): read remaining search rate limit from the X-RateLimit-Search-Remaining response header.",
     "external_dependency_change: X-RateLimit-Search-Remaining header removed from GitHub API responses",
     "Old GitHub note says search rate limit headers are stable across GitHub API versions."),

    ("ed010", "Fix the PostgreSQL client after the database server deprecated MD5 password authentication.", 190,
     "Database connections fail with authentication error; the Postgres server disabled MD5 auth in favor of SCRAM-SHA-256.",
     "PostgreSQL connection strings must specify sslmode=require and the client library must support SCRAM-SHA-256.",
     "The pg_hba.conf on the server now enforces SCRAM-SHA-256 for all client connections.",
     "When a database server removes an authentication method, update the client library and connection config together.",
     "PostgreSQL connection note (session 6): use MD5 password authentication with pg_hba.conf set to md5.",
     "external_dependency_change: PostgreSQL server disabled MD5 auth; SCRAM-SHA-256 is now required",
     "Old database note says MD5 auth was used for backward compatibility with older PostgreSQL client libraries."),

    ("ed011", "Fix the Firebase integration after Google deprecated the legacy FCM send API.", 195,
     "Push notification delivery fails; Google deprecated the FCM legacy send endpoint at /fcm/send in January 2024.",
     "Firebase push notifications must now use the FCM HTTP v1 API at /v1/projects/{project_id}/messages:send.",
     "The FCM v1 API uses OAuth 2.0 tokens instead of the legacy server key for authentication.",
     "When a push notification provider deprecates a send endpoint, update both the URL and the auth mechanism.",
     "Firebase integration note (session 9): send push notifications via the legacy FCM endpoint /fcm/send using a server key.",
     "external_dependency_change: FCM legacy /fcm/send endpoint deprecated; FCM HTTP v1 API is required",
     "Old notification note says the legacy FCM endpoint is still functional and easier to use than v1."),

    ("ed012", "Fix the Slack API client after Slack removed the legacy incoming webhook payload format.", 185,
     "Slack messages fail to post; Slack removed the text-only payload format for incoming webhooks in March 2024.",
     "Slack incoming webhooks now require a blocks array with at least one section block for message delivery.",
     "The old text top-level field is still accepted but ignored if a blocks array is present.",
     "When a messaging platform changes its webhook payload format, update message composition before changing URLs.",
     "Slack integration note (session 7): post messages via the incoming webhook URL with a JSON body containing text.",
     "external_dependency_change: Slack no longer accepts text-only payloads; blocks array is required",
     "Old Slack note says the text field in the webhook payload is the simplest way to send formatted messages."),

    ("ed013", "Fix the Docker registry client after DockerHub changed the image manifest schema.", 200,
     "Image pull operations fail with 404; DockerHub switched to the OCI image manifest format in November 2023.",
     "Docker registry client must send Accept: application/vnd.oci.image.manifest.v1+json headers.",
     "OCI manifests require a mediaType field in every layer descriptor; Docker manifest v2 did not require it.",
     "When a registry changes its manifest schema, update the Accept header and layer parsing before pulling images.",
     "Docker registry note (session 5): use the Docker manifest v2 schema with Accept: application/vnd.docker.distribution.manifest.v2+json.",
     "external_dependency_change: DockerHub migrated to OCI image manifest format; v2 manifest schema is deprecated",
     "Old container note says the Docker manifest v2 format is universally supported across all registries."),

    ("ed014", "Fix the Redis client after the cloud provider deprecated the CLUSTER INFO command format.", 190,
     "Cluster health checks fail; the managed Redis provider changed the CLUSTER INFO response format in version 7.0.",
     "CLUSTER INFO responses in Redis 7.0 use a different field separator and added new required status fields.",
     "The cluster_state field now returns active instead of ok when the cluster is healthy.",
     "When a managed cache provider changes a command response format, update all response parsers before adding health checks.",
     "Redis cluster note (session 8): parse the CLUSTER INFO response and check for cluster_state:ok to confirm health.",
     "external_dependency_change: Redis 7.0 changed CLUSTER INFO response; cluster_state now returns 'active' not 'ok'",
     "Old Redis note says CLUSTER INFO response format is stable and has not changed across Redis versions."),

    ("ed015", "Fix the Datadog metrics client after Datadog deprecated the v1 metrics submission endpoint.", 195,
     "Metric submission failures show 410 Gone; Datadog sunset the v1 /api/v1/series endpoint for custom metrics.",
     "Custom metrics must now be submitted to the /api/v2/series endpoint with the updated payload schema.",
     "The v2 payload uses a resources array instead of the host field for metric tagging.",
     "When a monitoring provider removes a metric submission endpoint, update both the URL and payload schema.",
     "Datadog integration note (session 6): submit custom metrics to /api/v1/series with a host field and tags array.",
     "external_dependency_change: Datadog v1 /api/v1/series endpoint sunsetted; v2 /api/v2/series is required",
     "Old monitoring note says the Datadog v1 API is reliable and used by most legacy integrations."),

    ("ed016", "Fix the Auth0 integration after Auth0 deprecated the legacy /oauth/ro endpoint.", 185,
     "Authentication flows fail with 410; Auth0 removed the legacy /oauth/ro endpoint for resource owner password grant.",
     "Auth0 resource owner password grant must now use the /oauth/token endpoint with grant_type=password.",
     "The new endpoint requires a client_secret in the request body when client authentication is required.",
     "When an identity provider removes an auth endpoint, update the grant type request before changing token parsing.",
     "Auth0 integration note (session 10): authenticate users via the /oauth/ro endpoint with username and password.",
     "external_dependency_change: Auth0 /oauth/ro endpoint removed; /oauth/token with grant_type=password is required",
     "Old auth note says /oauth/ro was the standard approach for resource owner password grant in Auth0."),

    ("ed017", "Fix the npm package after the lodash library removed the _.pluck method in v4.", 200,
     "Code fails at runtime with TypeError; lodash v4 removed the _.pluck method from the library.",
     "Array projection must now use _.map with a property name string instead of _.pluck.",
     "Lodash v4 also changed _.flatten to shallow-flatten only; deep flatten requires _.flattenDeep.",
     "When a utility library removes methods in a major version, audit all usages before upgrading.",
     "Lodash integration note (session 4): use _.pluck(array, 'propertyName') to extract a named property from each object.",
     "external_dependency_change: _.pluck removed in lodash v4; use _.map(array, 'propertyName') instead",
     "Old utility note says _.pluck is the clearest way to project a property from an array of objects."),

    ("ed018", "Fix the Python client after the requests library changed its SSL default behavior in v2.28.", 190,
     "Outbound HTTPS calls fail certificate verification; requests v2.28 changed the default CA bundle source.",
     "The requests library v2.28 now uses the system trust store by default; custom CA bundles must be explicit.",
     "The verify parameter now accepts a directory path for custom CA stores, not just individual cert files.",
     "When an HTTP client library changes SSL defaults, audit all verify parameter usages before upgrading.",
     "requests library note (session 7): set verify=True in all HTTPS requests to enable certificate validation.",
     "external_dependency_change: requests v2.28 changed default CA bundle; system trust store is now used by default",
     "Old HTTP note says requests v2.28 is backward compatible and does not require changes for existing integrations."),

    ("ed019", "Fix the Java client after Spring Boot deprecated the spring.datasource.url format for cloud databases.", 195,
     "Database connection fails on startup; Spring Boot 3.1 deprecated the JDBC URL format for managed cloud databases.",
     "Spring Boot 3.1 with cloud databases requires spring.datasource.r2dbc.url for reactive connections.",
     "The legacy JDBC URL format still works for traditional blocking datasources but not reactive datasources.",
     "When a framework changes its datasource URL format, confirm the connection type before updating config.",
     "Spring Boot note (session 11): set spring.datasource.url with a JDBC connection string for database connectivity.",
     "external_dependency_change: Spring Boot 3.1 deprecated JDBC URL for reactive cloud database connections",
     "Old Spring note says spring.datasource.url works for all supported databases in Spring Boot."),

    ("ed020", "Fix the Go module after the AWS SDK v2 removed the deprecated session.NewSession function.", 185,
     "AWS SDK calls fail to compile; AWS SDK for Go v2 removed the session.NewSession function from the SDK.",
     "AWS clients must now be created using aws.NewConfig and config.LoadDefaultConfig instead of session.NewSession.",
     "AWS SDK v2 also moved credential provider types to the credentials package with different initialization.",
     "When an AWS SDK major version removes session management, update all client creation patterns atomically.",
     "AWS SDK Go note (session 8): create AWS clients using session.NewSession and then passing the session to the service client.",
     "external_dependency_change: AWS SDK Go v2 removed session.NewSession; use config.LoadDefaultConfig instead",
     "Old AWS note says AWS SDK v1 session handling is still maintained and can coexist with SDK v2 clients."),

    ("ed021", "Fix the Ruby client after the Twilio gem removed the deprecated Account SID auth format.", 200,
     "Twilio API calls return 401; the Twilio Ruby gem v6 removed support for passing Account SID in the URL.",
     "Twilio authentication must now use HTTP Basic auth with Account SID as username and Auth Token as password.",
     "The Twilio Ruby gem v6 also removed the deprecated send_message method in favor of messages.create.",
     "When a client gem removes an auth format, update both authentication and API call patterns together.",
     "Twilio Ruby gem note (session 6): initialize the client with account_sid in the URL and auth_token as a parameter.",
     "external_dependency_change: Twilio Ruby gem v6 removed URL-based Account SID auth; HTTP Basic auth is required",
     "Old Ruby note says the Twilio gem's URL-based auth was the standard approach in gem versions 4 and 5."),

    ("ed022", "Fix the iOS SDK after Apple deprecated the UIWebView class in iOS 17.", 190,
     "App submission fails App Store Review; Apple deprecated UIWebView and requires WKWebView in iOS 17.",
     "All web content rendering must use WKWebView; UIWebView calls are rejected during App Store submission.",
     "WKWebView requires a delegate pattern instead of UIWebViewDelegate for navigation events.",
     "When Apple deprecates a UI class, migrate all usages before the next App Store submission.",
     "iOS development note (session 9): use UIWebView for rendering web content within the app for simplicity.",
     "external_dependency_change: Apple deprecated UIWebView in iOS 17; WKWebView is required for App Store submission",
     "Old iOS note says UIWebView is still functional on older iOS versions and migration can wait."),

    ("ed023", "Fix the Python ORM after SQLAlchemy 2.0 removed the execute() shorthand on session objects.", 195,
     "SQLAlchemy calls fail with AttributeError; SQLAlchemy 2.0 removed the execute() method from Session objects.",
     "Raw SQL execution must now use session.execute(text('SELECT ...')) with the text() construct explicitly.",
     "SQLAlchemy 2.0 also removed the Query.filter_by returning a list; queries must call .all() explicitly.",
     "When an ORM removes session execution shortcuts, audit all session.execute usages before upgrading.",
     "SQLAlchemy integration note (session 7): call session.execute('SELECT ...') to run raw SQL via the ORM session.",
     "external_dependency_change: SQLAlchemy 2.0 removed Session.execute shorthand; text() construct is required",
     "Old ORM note says SQLAlchemy execute() on session is a long-standing stable interface that rarely changes."),

    # HOLDOUTS (ed024–ed035)

    ("ed024", "Fix the Node.js server after the express library deprecated the res.json() null body behavior.", 195,
     "API clients receive unexpected 200 with null body; express 5 changed res.json(null) to return a 204 response.",
     "Explicit empty responses must use res.status(204).end() instead of res.json(null) in express 5.",
     "Express 5 also removed the res.send(body) shorthand for objects; res.json(body) must be used explicitly.",
     "When an HTTP framework changes response defaults, audit all empty response handlers before upgrading.",
     "Express note (session 8): return null as the JSON response body for endpoints that succeed with no payload.",
     "external_dependency_change: express 5 changed res.json(null) behavior to emit 204; explicit end() is required",
     "Old HTTP note says res.json(null) is a safe way to send an empty successful response in express."),

    ("ed025", "Fix the GraphQL client after the apollo-client library removed the deprecated ApolloClient constructor.", 185,
     "Apollo client initialization fails; apollo-client v3 removed the deprecated ApolloClient({client}) constructor.",
     "ApolloClient must now be constructed with ApolloClient({link, cache}) using the InMemoryCache.",
     "Apollo v3 also removed the deprecated apollo-link-http package in favor of @apollo/client/link/http.",
     "When a GraphQL client removes a constructor overload, update both initialization and link imports together.",
     "Apollo client note (session 10): initialize ApolloClient with the client option pointing to an HttpLink instance.",
     "external_dependency_change: apollo-client v3 removed deprecated constructor; link and cache are required",
     "Old GraphQL note says the Apollo client constructor accepts flexible options and rarely has breaking changes."),

    ("ed026", "Fix the Python ML client after scikit-learn deprecated the fit_transform return type.", 200,
     "Model training fails with type error; scikit-learn 1.2 changed fit_transform to return a dense array by default.",
     "Sparse matrix outputs from fit_transform must now be requested explicitly with set_output(transform='pandas').",
     "Scikit-learn 1.2 also deprecated the n_iter_ attribute in LinearSVC; use n_iter_no_change_ instead.",
     "When a machine learning library changes transformer output types, update all downstream array operations.",
     "scikit-learn note (session 6): fit_transform returns a sparse matrix that can be directly used in downstream models.",
     "external_dependency_change: scikit-learn 1.2 changed fit_transform to return dense by default; sparse must be explicit",
     "Old ML note says scikit-learn transformer output types are consistent across versions."),

    ("ed027", "Fix the Terraform provider after HashiCorp deprecated the aws_iam_role inline policy attribute.", 190,
     "Terraform plan fails with deprecation error; AWS Terraform provider 5.0 removed the inline_policy attribute.",
     "IAM role policies must now be managed with separate aws_iam_role_policy resources instead of inline_policy.",
     "The aws_iam_role_policies_exclusive resource replaces the managed_policy_arns attribute for policy management.",
     "When a Terraform provider removes an inline attribute, create separate resources before removing the old attribute.",
     "Terraform AWS provider note (session 9): use the inline_policy block within aws_iam_role to attach IAM policies.",
     "external_dependency_change: AWS Terraform provider 5.0 removed inline_policy; aws_iam_role_policy resources required",
     "Old Terraform note says inline_policy is the simplest way to attach policies directly within the role resource."),

    ("ed028", "Fix the Android SDK after Google deprecated the AsyncTask class in API level 30.", 195,
     "Android build generates deprecation warnings on AsyncTask; Google deprecated AsyncTask in Android API 30.",
     "Background work must now use Kotlin coroutines with Dispatchers.IO or WorkManager for deferred work.",
     "AsyncTask also leaked memory in configuration change scenarios that coroutines handle correctly.",
     "When Google deprecates a threading class, migrate to coroutines before targeting API level 31 or higher.",
     "Android development note (session 7): use AsyncTask for background network calls to keep UI thread responsive.",
     "external_dependency_change: AsyncTask deprecated in Android API 30; coroutines or WorkManager are required",
     "Old Android note says AsyncTask is simple to use and is still supported on older API levels."),

    ("ed029", "Fix the Ruby gem after the Faraday HTTP library changed its error class hierarchy in v2.", 185,
     "Error rescue blocks are not catching network failures; Faraday v2 reorganized its error class hierarchy.",
     "Network errors must now be rescued with Faraday::Error instead of the removed Faraday::ClientError class.",
     "Faraday v2 also changed connection timeout errors to raise Faraday::TimeoutError directly.",
     "When an HTTP client library reorganizes error classes, update all rescue blocks before upgrading.",
     "Faraday gem note (session 8): rescue Faraday::ClientError to handle all Faraday HTTP client errors.",
     "external_dependency_change: Faraday v2 replaced Faraday::ClientError with Faraday::Error as the base class",
     "Old Ruby note says Faraday error class hierarchy is stable across minor versions of the gem."),

    ("ed030", "Fix the .NET client after Microsoft deprecated the HttpWebRequest class in .NET 6.", 200,
     "Build warnings indicate HttpWebRequest is marked obsolete; Microsoft deprecated it in .NET 6.",
     "HTTP requests must now use HttpClient with HttpRequestMessage for all outbound HTTP calls.",
     "HttpClient supports HTTP/2 and HTTP/3 by default in .NET 6; HttpWebRequest did not.",
     "When Microsoft deprecates an HTTP class, migrate to HttpClient before targeting .NET 7 or higher.",
     ".NET HTTP note (session 5): use HttpWebRequest.Create() to make HTTP requests for maximum control.",
     "external_dependency_change: HttpWebRequest deprecated in .NET 6; HttpClient is the required replacement",
     "Old .NET note says HttpWebRequest is still functional in .NET 6 despite the deprecation warning."),

    ("ed031", "Fix the PHP client after Guzzle removed the deprecated http_errors option in version 7.", 190,
     "Guzzle throws exceptions for 4xx responses unexpectedly; Guzzle 7 removed the http_errors=false option.",
     "HTTP error response handling must now use try/catch around Guzzle\\Exception\\RequestException.",
     "Guzzle 7 also removed the GuzzleHttp\\json_decode function; use json_decode() directly.",
     "When a PHP HTTP client removes response error options, update all error handling to use exceptions.",
     "Guzzle integration note (session 7): set http_errors=>false to prevent Guzzle from throwing on 4xx responses.",
     "external_dependency_change: Guzzle 7 removed http_errors option; RequestException handling is required",
     "Old PHP note says the http_errors option is a clean way to handle error responses without try/catch."),

    ("ed032", "Fix the Swift client after Apple deprecated the completion handler pattern in URLSession.", 195,
     "Xcode shows deprecation warnings; Apple deprecated URLSession completion handler methods in iOS 15.",
     "Network requests must now use Swift async/await with URLSession.data(from:) for new code.",
     "The async URLSession APIs also improve cancellation handling through structured concurrency task groups.",
     "When Apple deprecates completion handler APIs, migrate to async/await before targeting iOS 16 minimum.",
     "Swift networking note (session 8): use URLSession.dataTask(with:completionHandler:) for asynchronous network requests.",
     "external_dependency_change: Apple deprecated URLSession completion handlers in iOS 15; async/await is required",
     "Old Swift note says completion handler pattern is still supported and well-understood across the codebase."),

    ("ed033", "Fix the Kubernetes operator after the operator-framework deprecated the legacy reconciler interface.", 185,
     "Operator build fails; operator-framework v0.15 deprecated the Reconciler interface in favor of TypedReconciler.",
     "Operators must now implement the TypedReconciler interface with explicit request type parameters.",
     "The TypedReconciler interface requires a generics-aware Go version (1.18 or higher).",
     "When the operator framework deprecates an interface, update the Go version requirement before migrating.",
     "Operator framework note (session 9): implement the Reconciler interface with Reconcile(ctx, Request) Result method.",
     "external_dependency_change: operator-framework v0.15 deprecated Reconciler; TypedReconciler is required",
     "Old k8s note says the Reconciler interface is the stable operator contract and rarely changes."),

    ("ed034", "Fix the React client after React 18 deprecated the ReactDOM.render API.", 200,
     "React 18 prints deprecation warnings; ReactDOM.render was deprecated and will be removed in React 19.",
     "React apps must now use createRoot(container).render(<App/>) for rendering in React 18.",
     "ReactDOM.createRoot also enables concurrent features like Suspense and startTransition.",
     "When React deprecates a render API, update the root rendering code before enabling concurrent features.",
     "React integration note (session 6): call ReactDOM.render(<App />, document.getElementById('root')) to mount the app.",
     "external_dependency_change: ReactDOM.render deprecated in React 18; createRoot().render() is required",
     "Old React note says ReactDOM.render still works in React 18 and migration to createRoot can wait."),

    ("ed035", "Fix the Go module after the gorilla/mux library was archived and removed from active maintenance.", 195,
     "Security audit flagged gorilla/mux as archived; the library received no security updates since November 2023.",
     "HTTP routing must be migrated from gorilla/mux to an actively maintained router such as chi or stdlib ServeMux.",
     "gorilla/mux handler function signatures are compatible with stdlib net/http; migration is mostly URL pattern syntax.",
     "When a critical dependency is archived, plan the migration before the dependency has an unpatched vulnerability.",
     "HTTP routing note (session 7): use gorilla/mux for flexible URL pattern matching and middleware chaining.",
     "external_dependency_change: gorilla/mux archived and no longer receives security updates; migration required",
     "Old routing note says gorilla/mux is the most popular Go router and is safe to use in production."),
]


def gen_external_dependency_change() -> None:
    for row in _ED_DEFS:
        sid = row[0]
        split = "holdout" if sid in _ED_HOLDOUTS else "public"
        sc = std_scenario(
            "external_dependency_change", sid, *row[1:],
            x1_validity="stale", x1_tier="project", x1_bucket="critical",
            split=split,
        )
        write(SCENARIOS / "external_dependency_change" / f"{sid}.json", sc)
    print(f"external_dependency_change: {len(_ED_DEFS)} scenarios written.")


# ─── STAKEHOLDER CONFLICT ─────────────────────────────────────────────────────
# Two stakeholders (e.g., PM and tech lead) issued conflicting instructions
# stored at different tiers.  x1 is the lower-priority stakeholder instruction
# that the system must demote.  The priority rule favors the tech lead / architect
# for technical decisions and the PM / product owner for scope decisions.

_STK_HOLDOUTS = {f"stk{n:03d}" for n in range(24, 36)}

_STK_DEFS = [
    # (sid, task, budget, s1, p1, p2, l1, x1, x1_notes, x2)
    ("stk001", "Implement the authentication change per the tech lead decision, not the PM scope request.", 200,
     "Tech lead issued a binding decision in session 18: disable password-based auth and require SSO for all users.",
     "Tech lead decisions on authentication architecture have priority over PM scope requests by team policy.",
     "The auth migration roadmap (approved by tech lead) requires SSO enforcement before the Q3 release.",
     "When a tech lead and PM conflict on technical architecture, apply the tech lead decision and document the PM scope note.",
     "PM instruction (session 19): keep password-based auth available alongside SSO to reduce churn from power users.",
     "stakeholder_conflict: PM scope instruction conflicts with binding tech lead authentication architecture decision",
     "Old compromise note says a hybrid auth approach was discussed but not formally approved by the tech lead."),

    ("stk002", "Apply the database schema decision from the architect, not the PM's field addition request.", 195,
     "Architect issued a binding schema freeze decision in session 22: no new columns until migration debt is resolved.",
     "Schema changes require architect approval; the freeze decision blocks all new column additions until migration clears.",
     "The migration debt backlog has 6 unresolved items; the architect's freeze is in effect until all 6 are resolved.",
     "When an architect freezes a schema and a PM requests additions, enforce the freeze and document the PM request.",
     "PM instruction (session 23): add a user_preferences JSON column to the accounts table this sprint for the new feature.",
     "stakeholder_conflict: PM column addition request conflicts with architect's binding schema freeze decision",
     "Old workaround note says JSON columns can be added outside the normal schema review process."),

    ("stk003", "Implement the API versioning strategy chosen by the tech lead, not the PM's shortcut proposal.", 190,
     "Tech lead decided in session 15: all breaking API changes require a new major version path prefix.",
     "Tech lead API versioning decisions are binding; they protect downstream integrators from silent breakage.",
     "The versioning policy requires a migration guide and deprecation notice before any breaking change ships.",
     "When tech lead and PM conflict on API versioning, apply the versioning policy and log the PM's shortcut request.",
     "PM instruction (session 16): make the breaking change in-place on the current endpoint to ship faster this week.",
     "stakeholder_conflict: PM in-place change request conflicts with tech lead's binding API versioning policy",
     "Old delivery note says minor breaking changes can sometimes be absorbed without a version bump."),

    ("stk004", "Apply the security policy from the CISO, not the PM's feature scope expansion.", 185,
     "CISO issued a binding security requirement in session 20: all user data exports must be encrypted at rest.",
     "CISO security requirements have the highest organizational priority and override PM feature scope requests.",
     "Export encryption must use AES-256 with keys managed in the approved key management service.",
     "When a CISO security requirement conflicts with a PM feature request, apply the security requirement first.",
     "PM instruction (session 21): allow unencrypted data exports for enterprise customers to reduce download friction.",
     "stakeholder_conflict: PM export friction request conflicts with binding CISO encryption requirement",
     "Old enterprise note says some customers were granted exceptions to encryption requirements in the past."),

    ("stk005", "Use the performance budget set by the tech lead, not the PM's feature completeness goal.", 200,
     "Tech lead set a binding performance constraint in session 25: API response times must stay under 200ms at p99.",
     "Performance constraints set by the tech lead have engineering authority over product feature completeness goals.",
     "The 200ms p99 budget includes all database queries, cache lookups, and response serialization time.",
     "When a feature's performance cost violates the tech lead's budget, cut scope rather than exceeding the budget.",
     "PM instruction (session 26): add three additional enrichment queries to the API response to complete the feature.",
     "stakeholder_conflict: PM enrichment request would push p99 beyond the tech lead's binding 200ms performance budget",
     "Old feature note says enrichment queries were accepted in the prototype because performance was not yet measured."),

    ("stk006", "Implement the error handling policy from the architect, not the PM's simplified error model.", 190,
     "Architect issued a binding error handling policy in session 17: all API errors must use RFC 7807 problem+json format.",
     "Architect error handling policies are binding on all API implementations in the project.",
     "RFC 7807 requires type, title, status, and detail fields in all error responses.",
     "When architect error policy conflicts with a PM's simpler model request, implement the RFC 7807 format.",
     "PM instruction (session 18): return a simple error string in a message field for easier client parsing.",
     "stakeholder_conflict: PM simplified error request conflicts with architect's binding RFC 7807 error policy",
     "Old API note says a simple error message field was used in early endpoints before the RFC 7807 policy was set."),

    ("stk007", "Apply the deployment freeze from ops, not the PM's urgent release request.", 195,
     "Ops issued a deployment freeze in session 30: no deployments to production between Dec 23 and Jan 3.",
     "Ops deployment freezes override PM release urgency during the defined freeze window.",
     "The freeze was approved by leadership to protect the revenue-critical holiday period from deployment risk.",
     "When a PM requests deployment during an ops freeze, document the request and hold deployment until the freeze lifts.",
     "PM instruction (session 31): deploy the new checkout feature to production today to capture holiday traffic.",
     "stakeholder_conflict: PM urgent deployment conflicts with ops leadership-approved holiday deployment freeze",
     "Old release note says critical features have been deployed during freezes with executive approval in the past."),

    ("stk008", "Use the data retention policy from legal, not the PM's analytics data extension request.", 185,
     "Legal issued a binding data retention limit in session 12: user behavioral data must be deleted after 90 days.",
     "Legal data retention policies override PM analytics retention requests in all jurisdictions we operate.",
     "The 90-day limit was set to comply with GDPR Article 5(1)(e) storage limitation principle.",
     "When legal retention policy conflicts with a PM's extended analytics request, enforce the legal limit.",
     "PM instruction (session 13): extend behavioral data retention to 18 months for better cohort analysis.",
     "stakeholder_conflict: PM retention extension conflicts with binding legal GDPR 90-day storage limitation",
     "Old analytics note says 18-month retention was approved for anonymized cohort data in a prior legal review."),

    ("stk009", "Apply the accessibility standard from the design lead, not the PM's visual simplicity request.", 200,
     "Design lead issued a binding accessibility requirement in session 19: all interactive elements must meet WCAG 2.1 AA.",
     "Design lead accessibility decisions are binding on all UI implementations and take precedence over visual simplicity requests.",
     "WCAG 2.1 AA requires a minimum 4.5:1 color contrast ratio for normal text and 3:1 for large text.",
     "When accessibility requirements conflict with PM visual simplicity requests, apply the WCAG standard.",
     "PM instruction (session 20): use lighter gray text on white backgrounds for a cleaner, more minimal look.",
     "stakeholder_conflict: PM visual simplicity request conflicts with design lead's binding WCAG 2.1 AA contrast standard",
     "Old design note says some low-contrast text was accepted in earlier screens without flagging WCAG compliance."),

    ("stk010", "Implement the testing requirement from QA lead, not the PM's speed-to-delivery request.", 190,
     "QA lead issued a binding gate in session 28: all new features must pass a full regression suite before release.",
     "QA lead release gates have engineering authority; they block releases regardless of PM delivery timelines.",
     "The regression suite covers 847 test cases and runs for 45 minutes on the CI cluster.",
     "When a QA gate conflicts with a PM's delivery urgency, hold the release and fix regressions first.",
     "PM instruction (session 29): release the feature today with a deferred regression run to meet the stakeholder demo.",
     "stakeholder_conflict: PM deferred testing request conflicts with QA lead's binding regression gate",
     "Old release note says regression runs were sometimes waived for low-risk features with PM sign-off."),

    ("stk011", "Use the infrastructure choice from the tech lead, not the PM's cost reduction vendor switch.", 195,
     "Tech lead issued a binding infrastructure decision in session 33: use GCP Pub/Sub for all event streaming.",
     "Tech lead infrastructure decisions are binding; they reflect a strategic vendor relationship and engineering capability.",
     "The GCP Pub/Sub decision was made after a 3-month evaluation and is not subject to per-feature override.",
     "When a PM requests a vendor switch for cost reasons, document the request and escalate rather than switching.",
     "PM instruction (session 34): switch event streaming to AWS SQS this quarter because it is 30% cheaper.",
     "stakeholder_conflict: PM vendor cost request conflicts with tech lead's binding GCP Pub/Sub infrastructure decision",
     "Old cost note says AWS SQS was used in a previous project and is familiar to part of the team."),

    ("stk012", "Apply the rate limit policy from the API team lead, not the PM's partner exception request.", 185,
     "API team lead issued a binding rate limit policy in session 24: all external clients are limited to 1000 req/min.",
     "API rate limit policies are set by the API team lead and may not be overridden for individual partners without review.",
     "The 1000 req/min limit protects shared infrastructure; exceptions require a capacity review before approval.",
     "When a PM requests a partner rate limit exception, hold the exception and initiate a capacity review.",
     "PM instruction (session 25): grant the enterprise partner an unlimited rate limit to support their batch workload.",
     "stakeholder_conflict: PM unlimited exception conflicts with API team lead's binding per-partner rate limit policy",
     "Old partner note says a previous enterprise partner was given an informal unlimited rate limit before the policy existed."),

    ("stk013", "Implement the data model per the architect's normalized design, not the PM's denormalized shortcut.", 200,
     "Architect issued a binding data model decision in session 16: use normalized relational tables for user preferences.",
     "Architect data model decisions are binding and protect long-term query performance and schema maintainability.",
     "The normalized preferences model uses a user_preference_entries table with key/value rows per user.",
     "When a PM requests a denormalized shortcut to an architect's data model decision, apply the normalized design.",
     "PM instruction (session 17): store all user preferences in a single JSON blob column for simpler application code.",
     "stakeholder_conflict: PM JSON blob preference conflicts with architect's binding normalized data model decision",
     "Old data note says JSON columns were used for preferences in the prototype to move quickly."),

    ("stk014", "Apply the monitoring policy from the platform team, not the PM's silent failure request.", 190,
     "Platform team issued a binding monitoring requirement in session 27: all background jobs must emit failure alerts.",
     "Platform team monitoring requirements are binding; they protect SLA reporting and incident response.",
     "Failure alerts must include job name, error message, and retry count to enable rapid incident triage.",
     "When a PM requests silent failure handling to hide noise, apply the monitoring requirement and adjust alert thresholds.",
     "PM instruction (session 28): make the email notification job fail silently to avoid alert fatigue from retry noise.",
     "stakeholder_conflict: PM silent failure request conflicts with platform team's binding failure alert requirement",
     "Old ops note says some low-priority jobs were configured to fail silently before the monitoring policy was set."),

    ("stk015", "Implement the caching strategy from the tech lead, not the PM's direct DB request.", 185,
     "Tech lead issued a binding caching requirement in session 21: all product catalog reads must go through the cache.",
     "Tech lead caching decisions protect database load targets; bypassing the cache is not permitted for catalog reads.",
     "The cache-first strategy uses a 5-minute TTL with write-through invalidation on catalog updates.",
     "When a PM requests direct DB reads to bypass cache inconsistency, enforce the cache strategy and fix invalidation.",
     "PM instruction (session 22): read catalog data directly from the database to avoid stale cache issues for customers.",
     "stakeholder_conflict: PM direct DB request conflicts with tech lead's binding cache-first catalog read strategy",
     "Old catalog note says direct DB reads were used before the cache layer was added during the last performance sprint."),

    ("stk016", "Apply the auth scope decision from the security lead, not the PM's broad access request.", 200,
     "Security lead issued a binding decision in session 26: API tokens must be scoped to the minimum required permissions.",
     "Security lead scope decisions enforce least-privilege; broad access tokens are rejected regardless of PM requests.",
     "The scope review process must document the specific permissions needed before any token scope is granted.",
     "When a PM requests a broad-scope token to simplify integration, enforce least-privilege and run a scope review.",
     "PM instruction (session 27): issue integration partner tokens with full read/write scope to simplify their integration.",
     "stakeholder_conflict: PM broad scope request conflicts with security lead's binding least-privilege token policy",
     "Old integration note says full-scope tokens were used for developer testing before the scope policy was enforced."),

    ("stk017", "Use the incident severity definition from the SRE team, not the PM's priority override.", 190,
     "SRE team issued binding severity definitions in session 14: SEV1 requires all-hands response and is triggered by SLO breach.",
     "SRE severity definitions are binding for incident response; PMs may not reclassify incidents during response.",
     "SEV1 incidents override all planned work; team members must join the incident call within 5 minutes.",
     "When a PM requests to downgrade a SEV1 to reduce business visibility, enforce the SRE severity definition.",
     "PM instruction (session 15): reclassify this as a SEV3 to avoid triggering the executive escalation process.",
     "stakeholder_conflict: PM reclassification request conflicts with SRE team's binding SEV1 severity definition",
     "Old incident note says PMs have previously reclassified incidents to manage executive communication."),

    ("stk018", "Implement the feature flag rollout strategy from the tech lead, not the PM's full release request.", 185,
     "Tech lead issued a binding rollout strategy in session 29: new payments flow must use a 1%-5%-25%-100% staged rollout.",
     "Tech lead rollout strategies are binding; they protect revenue-critical flows from wide-surface bugs.",
     "The staged rollout gates on error rate; if error rate exceeds 0.5% at any stage, the rollout halts.",
     "When a PM requests a full immediate release, apply the staged rollout and document the PM's urgency.",
     "PM instruction (session 30): release the new payments flow to 100% of users immediately for the earnings call.",
     "stakeholder_conflict: PM immediate release request conflicts with tech lead's binding staged rollout strategy",
     "Old release note says some features have been released to 100% immediately when the PM accepted the risk."),

    ("stk019", "Apply the code review policy from the engineering manager, not the PM's self-merge request.", 200,
     "Engineering manager issued a binding code review policy in session 11: no self-merges; all PRs require 2 approvals.",
     "Engineering manager code review policies are binding; they protect code quality and incident prevention.",
     "Critical path code (payment, auth, data export) requires 3 approvals including at least one from a senior engineer.",
     "When a PM requests a self-merge to ship faster, enforce the approval policy and expedite the review process.",
     "PM instruction (session 12): allow the engineer to self-merge this PR to make the Friday release cutoff.",
     "stakeholder_conflict: PM self-merge request conflicts with engineering manager's binding 2-approval code review policy",
     "Old delivery note says self-merges were allowed for hotfixes with PM sign-off before the policy was formal."),

    ("stk020", "Use the API contract from the platform team, not the PM's response field addition.", 195,
     "Platform team issued a binding API contract freeze in session 35: the /v2/orders response shape is frozen until Q4.",
     "API contract freezes protect downstream consumer integrations; additive changes require a deprecation notice period.",
     "The freeze includes both required and optional fields; no new fields may be added during the freeze.",
     "When a PM requests a response field addition during a contract freeze, hold the change until the freeze lifts.",
     "PM instruction (session 36): add an estimated_delivery_date field to the /v2/orders response this sprint.",
     "stakeholder_conflict: PM field addition request conflicts with platform team's binding API contract freeze",
     "Old API note says additive changes are backward compatible and should not require a freeze exemption."),

    ("stk021", "Apply the localization requirement from the compliance lead, not the PM's English-only scope.", 185,
     "Compliance lead issued a binding localization requirement in session 32: all user-facing strings must support French and German.",
     "Compliance lead localization requirements are binding in regulated EU markets; English-only scoping is not permitted.",
     "The localization requirement applies to all error messages, labels, and notification content.",
     "When a PM requests English-only scope for speed, apply the localization requirement and add i18n scaffolding.",
     "PM instruction (session 33): ship the feature in English only to hit the deadline; localize next quarter.",
     "stakeholder_conflict: PM English-only scope conflicts with compliance lead's binding EU localization requirement",
     "Old release note says previous features shipped English-only to EU markets with a localization follow-up."),

    ("stk022", "Implement the logging format from the data engineering team, not the PM's custom log request.", 200,
     "Data engineering team issued a binding log format requirement in session 38: all events must use structured JSON logs.",
     "Data engineering log format requirements are binding; they ensure downstream pipelines can parse and aggregate logs.",
     "The structured log format must include event_type, timestamp, user_id, and correlation_id at minimum.",
     "When a PM requests a custom log format for readability, apply the structured format and add human-readable metadata.",
     "PM instruction (session 39): use human-readable plain text logs so the support team can read them without tooling.",
     "stakeholder_conflict: PM plain text log request conflicts with data engineering team's binding structured log format",
     "Old logging note says plain text was the default log format before the data engineering team standardized the schema."),

    ("stk023", "Apply the dependency upgrade policy from the security team, not the PM's freeze request.", 190,
     "Security team issued a binding dependency upgrade requirement in session 42: CVE-critical dependencies must be patched within 7 days.",
     "Security team patching requirements override PM feature freeze requests when CVE severity is critical.",
     "The current lodash vulnerability is rated CVSS 9.8 and requires an upgrade to lodash 4.17.21 immediately.",
     "When a security team CVE patch requirement conflicts with a PM feature freeze, apply the patch first.",
     "PM instruction (session 43): freeze all dependency changes this sprint to stabilize the release candidate.",
     "stakeholder_conflict: PM dependency freeze conflicts with security team's binding 7-day CVE patch requirement",
     "Old release note says dependency updates were deferred during release stabilization periods in previous cycles."),

    # HOLDOUTS (stk024–stk035)

    ("stk024", "Use the privacy policy from legal, not the PM's analytics expansion request.", 195,
     "Legal issued a binding privacy policy in session 44: behavioral analytics must require explicit user consent.",
     "Legal privacy policies are binding and override PM analytics expansion requests in all user-facing flows.",
     "The consent requirement must be implemented as an opt-in gate before any behavioral data is collected.",
     "When a PM requests analytics expansion without a consent gate, implement the consent mechanism first.",
     "PM instruction (session 45): enable full behavioral analytics for all users without a consent prompt to improve data.",
     "stakeholder_conflict: PM no-consent analytics request conflicts with legal's binding explicit consent requirement",
     "Old analytics note says behavioral data was collected without consent before the privacy policy was updated."),

    ("stk025", "Apply the capacity allocation from the infra team, not the PM's burst capacity request.", 185,
     "Infra team issued a binding capacity allocation in session 46: the analytics service is capped at 200 CPU cores.",
     "Infra team capacity allocations are binding; they protect shared cluster resources from overcommitment.",
     "The 200-core cap was set based on the cluster utilization budget approved in the quarterly planning process.",
     "When a PM requests burst capacity beyond the allocation, escalate to infra for reallocation rather than overriding.",
     "PM instruction (session 47): spin up 500 additional CPU cores for the analytics service to handle the product launch.",
     "stakeholder_conflict: PM 500-core burst request conflicts with infra team's binding 200-core capacity allocation",
     "Old launch note says the infra team provided burst capacity for previous product launches without formal allocation."),

    ("stk026", "Implement the SLA from the customer success team, not the PM's deferred response timeline.", 200,
     "Customer success team issued a binding SLA commitment in session 48: enterprise support tickets must be acknowledged within 1 hour.",
     "Customer success SLA commitments are binding contractual obligations; PM deferred timelines violate customer contracts.",
     "The 1-hour acknowledgment SLA applies 24/7 and requires an on-call rotation to be staffed.",
     "When a PM defers SLA response timelines for feature work, enforce the SLA and escalate staffing gaps.",
     "PM instruction (session 49): defer enterprise support acknowledgment to next-business-day to focus the team on features.",
     "stakeholder_conflict: PM deferred response conflicts with customer success team's binding 1-hour enterprise SLA",
     "Old support note says next-business-day response was used for enterprise tickets before the SLA was formalized."),

    ("stk027", "Use the release naming convention from the brand team, not the PM's version shorthand.", 190,
     "Brand team issued a binding release naming policy in session 50: releases must use the codename system, not version numbers.",
     "Brand team naming policies are binding on all external-facing release communications and documentation.",
     "The codename system uses city names in alphabetical order; the next release is codenamed Amsterdam.",
     "When a PM uses version numbers in release communications, apply the codename and document the version mapping.",
     "PM instruction (session 51): name the release 'v4.2' in all customer communications for clarity.",
     "stakeholder_conflict: PM version number naming conflicts with brand team's binding codename release policy",
     "Old release note says version numbers were used in customer communications before the codename policy was introduced."),

    ("stk028", "Apply the API deprecation timeline from the platform team, not the PM's early removal request.", 195,
     "Platform team issued a binding deprecation policy in session 52: deprecated APIs must remain available for 12 months.",
     "Platform team deprecation timelines are binding contractual commitments to API consumers.",
     "The 12-month notice was communicated to all registered API consumers in the deprecation announcement.",
     "When a PM requests early removal of a deprecated API, enforce the 12-month timeline and document the request.",
     "PM instruction (session 53): remove the deprecated /v1/users endpoint this sprint to reduce maintenance burden.",
     "stakeholder_conflict: PM early removal request conflicts with platform team's binding 12-month deprecation timeline",
     "Old API note says deprecated endpoints have been removed early when usage dropped to near-zero."),

    ("stk029", "Implement the observability requirement from the SRE team, not the PM's instrumentation scope cut.", 185,
     "SRE team issued a binding observability requirement in session 54: all new services must have p50/p95/p99 latency metrics.",
     "SRE observability requirements are binding for production readiness gating; metrics are checked before deployment approval.",
     "p50/p95/p99 latency histograms must be emitted for all request-handling paths, not just the main endpoint.",
     "When a PM cuts instrumentation scope for delivery speed, enforce the SRE readiness requirement before deploying.",
     "PM instruction (session 55): skip the latency histogram instrumentation to ship the service faster this sprint.",
     "stakeholder_conflict: PM instrumentation cut conflicts with SRE team's binding p50/p95/p99 observability requirement",
     "Old service note says some services shipped without full histogram instrumentation during early-stage launches."),

    ("stk030", "Apply the API authentication requirement from the security team, not the PM's public access request.", 200,
     "Security team issued a binding authentication requirement in session 56: all API endpoints must require authentication.",
     "Security team authentication requirements are binding; unauthenticated endpoints violate the security baseline.",
     "The authentication requirement applies to all routes including read-only and status endpoints.",
     "When a PM requests a public unauthenticated endpoint for convenience, enforce authentication and add a scoped read-only token.",
     "PM instruction (session 57): make the /v1/status and /v1/version endpoints publicly accessible without a token.",
     "stakeholder_conflict: PM public access request conflicts with security team's binding all-endpoints authentication requirement",
     "Old API note says status and version endpoints were sometimes made public for easier health check configuration."),

    ("stk031", "Use the testing standard from QA lead, not the PM's manual testing substitution.", 190,
     "QA lead issued a binding testing standard in session 58: all new features must have automated end-to-end tests.",
     "QA lead automated testing requirements are binding for release gating; manual testing does not satisfy them.",
     "End-to-end tests must cover the critical user journey for the feature with at least 5 distinct test cases.",
     "When a PM proposes manual testing as a substitute for automation, enforce the e2e requirement and schedule the tests.",
     "PM instruction (session 59): use manual QA testing for this feature instead of automated tests to ship sooner.",
     "stakeholder_conflict: PM manual testing proposal conflicts with QA lead's binding automated e2e test requirement",
     "Old QA note says manual testing was accepted for low-risk features before the automated testing policy was formalized."),

    ("stk032", "Apply the change management process from the ops team, not the PM's emergency change request.", 195,
     "Ops team issued a binding change management policy in session 60: production changes require 48-hour advance notice.",
     "Ops change management policies are binding; emergency exceptions require approval from the ops manager.",
     "The 48-hour window allows stakeholder notification, rollback planning, and off-hours scheduling.",
     "When a PM requests an unplanned production change, initiate the emergency exception process rather than bypassing.",
     "PM instruction (session 61): make the config change in production today without going through change management.",
     "stakeholder_conflict: PM unplanned change conflicts with ops team's binding 48-hour advance notice policy",
     "Old ops note says urgent config changes were sometimes made without 48-hour notice during customer incidents."),

    ("stk033", "Implement the backup frequency from the DBA team, not the PM's cost reduction request.", 185,
     "DBA team issued a binding backup frequency in session 62: production databases must be backed up hourly.",
     "DBA backup frequency requirements are binding for RPO compliance; reducing frequency violates the data recovery SLA.",
     "The hourly backup requirement corresponds to a 1-hour RPO commitment documented in the DR plan.",
     "When a PM requests reduced backup frequency to cut cloud storage costs, enforce the DBA RPO requirement.",
     "PM instruction (session 63): reduce database backups to daily to cut cloud storage costs by 70%.",
     "stakeholder_conflict: PM daily backup request conflicts with DBA team's binding 1-hour RPO backup frequency",
     "Old cost note says daily backups were used before the DBA team formalized the RPO commitment."),

    ("stk034", "Use the UI design standard from the design system team, not the PM's custom component request.", 200,
     "Design system team issued a binding standard in session 64: all UI components must use the approved design system.",
     "Design system requirements are binding; custom components outside the design system create inconsistency and debt.",
     "New UI components must be submitted to the design system backlog if they are not already available.",
     "When a PM requests a custom component outside the design system, submit the component to the backlog and use the closest existing one.",
     "PM instruction (session 65): create a custom date picker with a unique visual style for this feature launch.",
     "stakeholder_conflict: PM custom component request conflicts with design system team's binding component standardization policy",
     "Old design note says custom components were built for specific features before the design system was established."),

    ("stk035", "Apply the documentation requirement from the technical writing team, not the PM's doc deferral.", 195,
     "Technical writing team issued a binding requirement in session 66: API documentation must ship with the feature.",
     "Technical writing documentation requirements are binding for external API features; doc deferral blocks release.",
     "API docs must include endpoint description, request/response schema, authentication, and at least one code example.",
     "When a PM defers API documentation, hold the external release until documentation is complete.",
     "PM instruction (session 67): ship the API without documentation and add the docs in the following sprint.",
     "stakeholder_conflict: PM documentation deferral conflicts with technical writing team's binding ship-with-docs requirement",
     "Old release note says APIs were sometimes released without documentation when the PM accepted responsibility for partner support."),
]


def gen_stakeholder_conflict() -> None:
    for row in _STK_DEFS:
        sid = row[0]
        split = "holdout" if sid in _STK_HOLDOUTS else "public"
        sc = std_scenario(
            "stakeholder_conflict", sid, *row[1:],
            x1_validity="contradicted", x1_tier="project", x1_bucket="supporting",
            split=split,
        )
        write(SCENARIOS / "stakeholder_conflict" / f"{sid}.json", sc)
    print(f"stakeholder_conflict: {len(_STK_DEFS)} scenarios written.")


# ─── main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    gen_preference_drift()
    gen_external_dependency_change()
    gen_stakeholder_conflict()
    total = len(_PD_DEFS) + len(_ED_DEFS) + len(_STK_DEFS)
    print(f"\nTotal scenarios written by this script: {total}")


if __name__ == "__main__":
    main()
