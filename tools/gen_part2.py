#!/usr/bin/env python3
"""Part 2 of 2 — scenario definitions for:
  injection_eviction_priority    iep001-iep015  (15 scenarios)
  injection_intra_bucket_order   iibo001-iibo010 (10 scenarios)
  long_horizon_accumulation      lha001-lha015  (15 scenarios)
  multi_agent_belief_propagation mabp001-mabp010 (10 scenarios)
  multi_agent_conflict_resolution macr001-macr010 (10 scenarios)
Total part 2: 60 scenarios.
"""
import json, os

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scenarios")


def m(id, tier, content, validity, bucket, notes=None):
    o = {"id": id, "tier": tier, "content": content, "validity": validity, "bucket": bucket}
    if notes:
        o["notes"] = notes
    return o


def ob(name, ids):
    return {"name": name, "memory_ids": ids}


def sc(sid, family, split, task, budget, mems, vids, xids, order_buckets, no_mem=0.1):
    return {
        "schema_version": "mvi-scenario-v1",
        "scenario_id": sid, "family": family, "split": split,
        "task": task, "repo_state_fingerprint": f"{sid}-repo-v1",
        "token_budget": budget, "candidate_memories": mems,
        "gold_valid_ids": vids, "gold_invalid_ids": xids,
        "preferred_order_buckets": order_buckets,
        "task_outcome_baselines": {"no_memory": no_mem, "ideal": 1.0},
    }


# ══════════════════════════════════════════════════════════════════════════════
# injection_eviction_priority (iep001–iep015)
# Context is nearly full; token budget fits only the critical memory.
# All candidate memories are valid. The system must inject critical over
# supporting when forced to choose. Budget ≈ 100 tokens; critical ≈ 80 tokens;
# critical + first-supporting > budget.
# ══════════════════════════════════════════════════════════════════════════════

SCENARIOS_2 = [

sc("iep001","injection_eviction_priority","public",
   "Add a new POST /payments/charges endpoint to the payment API. Prior context is large; token budget is critically constrained.",
   100,
   [
    m("iep001-p1","project","All payment API endpoints must validate the X-Idempotency-Key header and reject requests without it to prevent duplicate charges. This check must occur in middleware before any route handler executes. Violations trigger an automatic compliance alert.","valid","critical"),
    m("iep001-p2","project","REST endpoints should follow kebab-case naming convention; use plural nouns.","valid","supporting"),
    m("iep001-l1","long_term","New endpoints must be added to the OpenAPI spec in docs/api/openapi.yaml before deployment.","valid","supporting"),
    m("iep001-s1","session","Developer asked about the naming convention for the new charge endpoint path.","valid","supporting"),
   ],
   ["iep001-p1","iep001-p2","iep001-l1","iep001-s1"],
   [],
   [ob("project_critical",["iep001-p1"]),ob("supporting",["iep001-p2","iep001-l1","iep001-s1"])],
   no_mem=0.08),

sc("iep002","injection_eviction_priority","public",
   "Add structured logging to the user-profile service. Context window is nearly full; very limited token budget remains.",
   98,
   [
    m("iep002-p1","project","PII fields (email, phone, full_name, date_of_birth, ssn) must never appear in log output. Use pii.Redact() on all user objects before passing to the logger. Logging unredacted PII triggers an automatic compliance alert and constitutes a data breach.","valid","critical"),
    m("iep002-p2","project","Use structured JSON logging via zap; log at INFO level in production.","valid","supporting"),
    m("iep002-l1","long_term","Include request_id in all log entries to allow distributed trace correlation.","valid","supporting"),
   ],
   ["iep002-p1","iep002-p2","iep002-l1"],
   [],
   [ob("project_critical",["iep002-p1"]),ob("supporting",["iep002-p2","iep002-l1"])],
   no_mem=0.08),

sc("iep003","injection_eviction_priority","public",
   "Implement the data export feature that writes user records to S3. Token budget is tight due to large prior context.",
   105,
   [
    m("iep003-p1","project","User records written to S3 must be encrypted at rest using SSE-KMS with the key arn:aws:kms:us-east-1:123456789012:key/user-data-key. Unencrypted writes to S3 are rejected by the bucket policy and will raise a security incident.","valid","critical"),
    m("iep003-p2","project","S3 bucket for user exports is s3://user-exports-prod; use multipart upload for files over 100 MB.","valid","supporting"),
    m("iep003-l1","long_term","Export jobs must write a manifest file alongside the data file listing record count and checksum.","valid","supporting"),
    m("iep003-s1","session","Export job is expected to produce ~2 GB per run; scheduled to run nightly at 02:00 UTC.","valid","supporting"),
   ],
   ["iep003-p1","iep003-p2","iep003-l1","iep003-s1"],
   [],
   [ob("project_critical",["iep003-p1"]),ob("supporting",["iep003-p2","iep003-l1","iep003-s1"])],
   no_mem=0.08),

sc("iep004","injection_eviction_priority","public",
   "Remove a deprecated field from the public API response. Token budget is critically constrained.",
   97,
   [
    m("iep004-p1","project","Public API fields cannot be removed without a 90-day deprecation period and a major version bump. Removing a field before the deprecation window closes is a breaking change and violates the API compatibility contract; it will immediately break consumer integrations.","valid","critical"),
    m("iep004-p2","project","Add a deprecation notice to the API changelog with the planned removal date.","valid","supporting"),
    m("iep004-l1","long_term","Breaking changes must be announced in the API newsletter at least 60 days in advance.","valid","supporting"),
   ],
   ["iep004-p1","iep004-p2","iep004-l1"],
   [],
   [ob("project_critical",["iep004-p1"]),ob("supporting",["iep004-p2","iep004-l1"])],
   no_mem=0.08),

sc("iep005","injection_eviction_priority","public",
   "Push the release candidate directly to production. Token budget is severely constrained by earlier context.",
   96,
   [
    m("iep005-p1","project","All production deployments must pass a successful staging deployment and smoke-test run first. Direct-to-production pushes without a prior staging validation are prohibited and will trigger an automatic rollback by the deployment gate. No exceptions, including hotfixes.","valid","critical"),
    m("iep005-p2","project","Staging environment is at staging.internal; smoke tests run via make smoke-test ENV=staging.","valid","supporting"),
    m("iep005-l1","long_term","Deployment gate checks are enforced by the CI pipeline; bypass flags are disabled in production.","valid","supporting"),
   ],
   ["iep005-p1","iep005-p2","iep005-l1"],
   [],
   [ob("project_critical",["iep005-p1"]),ob("supporting",["iep005-p2","iep005-l1"])],
   no_mem=0.08),

sc("iep006","injection_eviction_priority","public",
   "Implement the bulk import endpoint that calls the partner API in a loop. Context window is nearly full.",
   103,
   [
    m("iep006-p1","project","The partner API enforces a rate limit of 100 requests per minute per API key. Exceeding this limit suspends the API key for 1 hour and may trigger account review. The bulk import must batch calls with a 600 ms sleep between requests to stay within the quota.","valid","critical"),
    m("iep006-p2","project","Partner API key is in vault:/secret/integrations/partner/api_key; never hard-code in source.","valid","supporting"),
    m("iep006-l1","long_term","All partner API calls must be logged with request_id for audit purposes.","valid","supporting"),
    m("iep006-s1","session","Bulk import is expected to process 5 000 records; estimated run time with rate limiting is 50 min.","valid","supporting"),
   ],
   ["iep006-p1","iep006-p2","iep006-l1","iep006-s1"],
   [],
   [ob("project_critical",["iep006-p1"]),ob("supporting",["iep006-p2","iep006-l1","iep006-s1"])],
   no_mem=0.08),

sc("iep007","injection_eviction_priority","public",
   "Store the user's health records in the new document database. Token budget is critically low.",
   99,
   [
    m("iep007-p1","project","Health records are classified as PHI under HIPAA. They must be stored in the HIPAA-compliant cluster (hipaa-docdb-prod) only. Storing PHI in any other data store without BAA coverage is a regulatory violation subject to significant financial penalties and breach notification obligations.","valid","critical"),
    m("iep007-p2","project","hipaa-docdb-prod connection string is in vault:/secret/hipaa/docdb; use the hipaa-svc service account.","valid","supporting"),
    m("iep007-l1","long_term","All PHI access must be logged with accessor identity and access reason for HIPAA audit trail.","valid","supporting"),
   ],
   ["iep007-p1","iep007-p2","iep007-l1"],
   [],
   [ob("project_critical",["iep007-p1"]),ob("supporting",["iep007-p2","iep007-l1"])],
   no_mem=0.08),

sc("iep008","injection_eviction_priority","public",
   "Write the database migration script for the schema change. Context window is nearly exhausted.",
   101,
   [
    m("iep008-p1","project","Database migrations must be wrapped in a transaction with an explicit ROLLBACK statement in the catch block. An untransacted migration that fails partway through will leave the schema in a corrupt state requiring manual intervention and extended downtime. Test the rollback path in staging before deploying.","valid","critical"),
    m("iep008-p2","project","Migration files must be sequentially numbered and placed in db/migrations/; use alembic revision --autogenerate.","valid","supporting"),
    m("iep008-l1","long_term","All migration scripts must have a corresponding down-migration that reverts the change.","valid","supporting"),
    m("iep008-s1","session","Target migration adds a non-null column to the orders table; requires a default value for existing rows.","valid","supporting"),
   ],
   ["iep008-p1","iep008-p2","iep008-l1","iep008-s1"],
   [],
   [ob("project_critical",["iep008-p1"]),ob("supporting",["iep008-p2","iep008-l1","iep008-s1"])],
   no_mem=0.08),

sc("iep009","injection_eviction_priority","public",
   "Configure the new service to use the admin database credentials for its initial setup. Token budget is critically constrained.",
   97,
   [
    m("iep009-p1","project","Services must never use the admin database credentials in production. The admin account has unrestricted DDL access and its use by application services violates the principle of least privilege. Provision a service-specific account with only the required DML permissions via the db-provisioner tool.","valid","critical"),
    m("iep009-p2","project","Run db-provisioner create-service-account --service=<name> --db=<db> to generate scoped credentials stored in vault.","valid","supporting"),
    m("iep009-l1","long_term","Service database accounts must be reviewed during quarterly access audits; unused accounts must be revoked.","valid","supporting"),
   ],
   ["iep009-p1","iep009-p2","iep009-l1"],
   [],
   [ob("project_critical",["iep009-p1"]),ob("supporting",["iep009-p2","iep009-l1"])],
   no_mem=0.08),

sc("iep010","injection_eviction_priority","public",
   "Accept a filename from the user in the file-processing endpoint and pass it to the shell command. Context nearly full.",
   100,
   [
    m("iep010-p1","project","User-supplied filenames must never be passed directly to shell commands or os.exec calls; this is a command injection vulnerability. Validate the filename against a strict allowlist (alphanumeric, hyphens, dots only) and construct the shell argument independently. Failure to do so enables arbitrary code execution on the server.","valid","critical"),
    m("iep010-p2","project","Use filepath.Clean() to normalise paths before validation; reject paths containing '..' or absolute paths.","valid","supporting"),
    m("iep010-l1","long_term","All user input must be validated at the service boundary; never trust client-supplied data for security-sensitive operations.","valid","supporting"),
   ],
   ["iep010-p1","iep010-p2","iep010-l1"],
   [],
   [ob("project_critical",["iep010-p1"]),ob("supporting",["iep010-p2","iep010-l1"])],
   no_mem=0.08),

sc("iep011","injection_eviction_priority","public",
   "Roll back the current deployment after a critical bug was detected in production. Token budget is critically low.",
   102,
   [
    m("iep011-p1","project","Rollback sequence is strictly ordered: (1) shift traffic to previous version via load balancer weight change, (2) confirm health checks pass on previous version, (3) scale down the failed version, (4) post incident message in #incident channel. Skipping step 2 before step 3 risks complete service outage if the previous version is not healthy.","valid","critical"),
    m("iep011-p2","project","Previous version image tag is available as the PREV_IMAGE_TAG env var in the deployment pipeline.","valid","supporting"),
    m("iep011-l1","long_term","All rollbacks must be followed by a blameless post-mortem within 48 h.","valid","supporting"),
   ],
   ["iep011-p1","iep011-p2","iep011-l1"],
   [],
   [ob("project_critical",["iep011-p1"]),ob("supporting",["iep011-p2","iep011-l1"])],
   no_mem=0.08),

sc("iep012","injection_eviction_priority","public",
   "Upgrade the orders-svc dependency on the shared-lib from v2.1 to v3.0. Context is nearly full.",
   99,
   [
    m("iep012-p1","project","shared-lib v3.0 contains a breaking change: the ProcessOrder() function signature changed from (ctx, order) to (ctx, order, opts). Any caller not updated to pass opts will panic at runtime. Audit all call sites in orders-svc before upgrading; update every call site in the same PR as the dependency bump.","valid","critical"),
    m("iep012-p2","project","shared-lib changelog is in vendor/shared-lib/CHANGELOG.md; review the v3.0 migration section.","valid","supporting"),
    m("iep012-l1","long_term","Dependency major version bumps require a PR description that lists all breaking changes and confirms all call sites have been audited.","valid","supporting"),
   ],
   ["iep012-p1","iep012-p2","iep012-l1"],
   [],
   [ob("project_critical",["iep012-p1"]),ob("supporting",["iep012-p2","iep012-l1"])],
   no_mem=0.08),

sc("iep013","injection_eviction_priority","holdout",
   "Pass the handoff context to the next agent in the pipeline before this agent's session ends. Token budget is critically constrained.",
   98,
   [
    m("iep013-p1","project","Before ending this agent session, write a handoff record to the shared-state store with: completed_steps (list), current_artifact_path, next_step_description, and blocking_issues. The next agent will not have access to this session's context and will fail if the handoff record is missing or incomplete.","valid","critical"),
    m("iep013-p2","project","Handoff record format is defined in agent_protocol/handoff_schema.json; validate before writing.","valid","supporting"),
    m("iep013-l1","long_term","All multi-agent pipelines must have a handoff record between every agent boundary; loss of handoff data is the primary cause of pipeline failures.","valid","supporting"),
   ],
   ["iep013-p1","iep013-p2","iep013-l1"],
   [],
   [ob("project_critical",["iep013-p1"]),ob("supporting",["iep013-p2","iep013-l1"])],
   no_mem=0.08),

sc("iep014","injection_eviction_priority","holdout",
   "Serve the cached search results for the product catalog. Token budget is nearly exhausted by prior context.",
   100,
   [
    m("iep014-p1","project","Cached search results must be invalidated before serving if the catalog version in the cache header does not match the current catalog_version in the metadata store. Serving stale results after a catalog update causes incorrect availability information to be shown to customers, resulting in failed orders.","valid","critical"),
    m("iep014-p2","project","Catalog version is stored in Redis at key catalog:version; check on every cache read before serving.","valid","supporting"),
    m("iep014-l1","long_term","Cache invalidation must be synchronous with catalog updates; do not use TTL-based expiry as the sole invalidation mechanism for catalog data.","valid","supporting"),
   ],
   ["iep014-p1","iep014-p2","iep014-l1"],
   [],
   [ob("project_critical",["iep014-p1"]),ob("supporting",["iep014-p2","iep014-l1"])],
   no_mem=0.08),

sc("iep015","injection_eviction_priority","holdout",
   "Store the EU user records in the analytics data warehouse for the new reporting feature. Token budget is critically constrained.",
   101,
   [
    m("iep015-p1","project","EU user records must be stored only in the EU-West-1 analytics warehouse (analytics-eu-prod) per GDPR data residency requirements. Writing EU user data to any US-region store violates the data processing agreement and triggers mandatory supervisory authority notification within 72 hours.","valid","critical"),
    m("iep015-p2","project","analytics-eu-prod connection string is in vault:/secret/analytics/eu/warehouse; use the analytics-writer service account.","valid","supporting"),
    m("iep015-l1","long_term","Data residency checks are enforced by the data-router middleware; do not bypass the middleware for performance reasons.","valid","supporting"),
   ],
   ["iep015-p1","iep015-p2","iep015-l1"],
   [],
   [ob("project_critical",["iep015-p1"]),ob("supporting",["iep015-p2","iep015-l1"])],
   no_mem=0.08),

]  # end injection_eviction_priority


# ══════════════════════════════════════════════════════════════════════════════
# injection_intra_bucket_order (iibo001–iibo010)
# All memories are valid. Tests whether the system injects memories in the
# correct order WITHIN a bucket. Within critical: safety/constraint before
# diagnostic/contextual. Within supporting: high-confidence/recent before
# lower-confidence/older. preferred_order_buckets specifies exact item order.
# ══════════════════════════════════════════════════════════════════════════════

SCENARIOS_2 += [

sc("iibo001","injection_intra_bucket_order","public",
   "Investigate why the job scheduler is running tasks in duplicate. Both scheduler instances report active status.",
   215,
   [
    m("iibo001-p1","project","Only one scheduler instance may hold the distributed leader lease at a time. Any instance that detects it does not hold a valid lease must immediately stop processing and enter standby mode.","valid","critical"),
    m("iibo001-s1","session","Duplicate task execution observed since 09:15 UTC. Both scheduler instances report active=true; the distributed lock may have failed to renew.","valid","critical"),
    m("iibo001-p2","project","Distributed lock renewal interval is every 10 s; if a scheduler misses 3 renewals the lock expires automatically.","valid","supporting"),
    m("iibo001-l1","long_term","Previous duplicate scheduling incident (2025-08) was caused by a network partition preventing lock renewal; check network connectivity between scheduler instances first.","valid","supporting"),
   ],
   ["iibo001-p1","iibo001-s1","iibo001-p2","iibo001-l1"],
   [],
   [ob("critical",["iibo001-p1","iibo001-s1"]),ob("supporting",["iibo001-p2","iibo001-l1"])],
   no_mem=0.1),

sc("iibo002","injection_intra_bucket_order","public",
   "Fix the data export pipeline that is writing financial records to an unencrypted S3 path.",
   210,
   [
    m("iibo002-l1","long_term","Financial records must be encrypted at rest using SSE-KMS before any write to S3. Writing unencrypted financial data to S3 is a SOC 2 control failure that must be reported to the compliance team within 1 h of discovery.","valid","critical"),
    m("iibo002-s1","session","Export pipeline found writing to s3://exports-prod/financial/ without SSE-KMS; 14 files written since 08:00 UTC are unencrypted.","valid","critical"),
    m("iibo002-p1","project","KMS key ARN for financial exports is arn:aws:kms:us-east-1:123456789012:key/financial-export-key; set ServerSideEncryption=aws:kms in the S3 PutObject call.","valid","supporting"),
    m("iibo002-p2","project","The 14 unencrypted files must be re-encrypted in place using aws s3 cp --sse aws:kms before the compliance report is filed.","valid","supporting"),
   ],
   ["iibo002-l1","iibo002-s1","iibo002-p1","iibo002-p2"],
   [],
   [ob("critical",["iibo002-l1","iibo002-s1"]),ob("supporting",["iibo002-p1","iibo002-p2"])],
   no_mem=0.1),

sc("iibo003","injection_intra_bucket_order","public",
   "Add the new team-member to the production database with appropriate permissions.",
   205,
   [
    m("iibo003-l1","long_term","Production database access requires security team approval and must be provisioned with least-privilege read-only permissions unless write access is explicitly justified and approved.","valid","critical"),
    m("iibo003-s1","session","Access request for new team-member confirmed; security team approval granted at 14:30 UTC for read-only access to orders and inventory schemas.","valid","critical"),
    m("iibo003-p1","project","Provision DB access via db-provisioner grant --user=<email> --db=prod --schemas=orders,inventory --permission=SELECT.","valid","supporting"),
    m("iibo003-l2","long_term","All production DB accounts must be enrolled in 90-day access review; add the new account to the quarterly review tracker.","valid","supporting"),
   ],
   ["iibo003-l1","iibo003-s1","iibo003-p1","iibo003-l2"],
   [],
   [ob("critical",["iibo003-l1","iibo003-s1"]),ob("supporting",["iibo003-p1","iibo003-l2"])],
   no_mem=0.1),

sc("iibo004","injection_intra_bucket_order","public",
   "Deploy the updated config for the notification service that was modified 20 minutes ago.",
   208,
   [
    m("iibo004-p1","project","Config changes to notification-svc must be validated with make validate-config COMPONENT=notification-svc before deployment; invalid config causes silent message drops.","valid","critical"),
    m("iibo004-s1","session","Config updated 20 min ago by on-call engineer to increase SMTP connection pool from 10 to 50; change not yet validated or deployed.","valid","critical"),
    m("iibo004-p2","project","Validated config is deployed via kubectl apply -f config/notification-svc/production.yaml; rolling restart happens automatically.","valid","supporting"),
    m("iibo004-l1","long_term","Config changes to notification-svc have historically caused silent failures when pool sizes exceed SMTP server limits; verify SMTP server max connections before increasing pool.","valid","supporting"),
   ],
   ["iibo004-p1","iibo004-s1","iibo004-p2","iibo004-l1"],
   [],
   [ob("critical",["iibo004-p1","iibo004-s1"]),ob("supporting",["iibo004-p2","iibo004-l1"])],
   no_mem=0.1),

sc("iibo005","injection_intra_bucket_order","public",
   "Merge the long-running feature branch back into main after 6 weeks of parallel development.",
   212,
   [
    m("iibo005-l1","long_term","Feature branches diverged more than 2 weeks from main must be rebased onto main and have all integration tests pass before merge to prevent buried conflict resolution breaking shared tests.","valid","critical"),
    m("iibo005-s1","session","Feature branch is 6 weeks behind main; 47 commits have landed on main since the branch diverged; 3 test files conflict.","valid","critical"),
    m("iibo005-p1","project","Rebase procedure: git fetch origin; git rebase origin/main; resolve conflicts; run make test-integration; create PR only after tests pass.","valid","supporting"),
    m("iibo005-p2","project","After merge, delete the feature branch and close the associated Jira ticket; do not leave stale branches.","valid","supporting"),
   ],
   ["iibo005-l1","iibo005-s1","iibo005-p1","iibo005-p2"],
   [],
   [ob("critical",["iibo005-l1","iibo005-s1"]),ob("supporting",["iibo005-p1","iibo005-p2"])],
   no_mem=0.1),

sc("iibo006","injection_intra_bucket_order","public",
   "Scale down the worker fleet during the upcoming maintenance window to reduce costs.",
   207,
   [
    m("iibo006-p1","project","Before scaling down workers, drain the job queue to zero or pause the queue to prevent in-flight jobs from being killed mid-execution; killing workers with active jobs corrupts job state.","valid","critical"),
    m("iibo006-s1","session","Maintenance window starts in 45 min; current queue depth is 320 jobs with estimated drain time of 12 min at current throughput.","valid","critical"),
    m("iibo006-p2","project","Scale down via kubectl scale deployment workers --replicas=0; scale back up to 10 replicas after the maintenance window.","valid","supporting"),
    m("iibo006-l1","long_term","Worker scale-down events must be logged in the maintenance log at docs/maintenance.md with start time, end time, and reason.","valid","supporting"),
   ],
   ["iibo006-p1","iibo006-s1","iibo006-p2","iibo006-l1"],
   [],
   [ob("critical",["iibo006-p1","iibo006-s1"]),ob("supporting",["iibo006-p2","iibo006-l1"])],
   no_mem=0.1),

sc("iibo007","injection_intra_bucket_order","public",
   "Investigate elevated error rates on the checkout API observed over the last 30 minutes.",
   210,
   [
    m("iibo007-p1","project","checkout-api error budget is 0.1% over a 30-min window. When error rate exceeds 0.5%, automatically halt all non-critical deployments and notify the on-call engineer; do not attempt fixes without first establishing a clear root cause hypothesis.","valid","critical"),
    m("iibo007-s1","session","checkout-api error rate at 1.2% for the last 28 min; 4x the error budget. Most errors are 503 from inventory-svc downstream; started immediately after the 14:00 UTC deploy.","valid","critical"),
    m("iibo007-p2","project","inventory-svc circuit breaker status: kubectl get cm circuit-breaker-state -n inventory -o jsonpath='{.data.status}'.","valid","supporting"),
    m("iibo007-l1","long_term","When error spikes correlate with a deploy, the first hypothesis should always be the deploy; have a rollback plan ready before investigating further.","valid","supporting"),
   ],
   ["iibo007-p1","iibo007-s1","iibo007-p2","iibo007-l1"],
   [],
   [ob("critical",["iibo007-p1","iibo007-s1"]),ob("supporting",["iibo007-p2","iibo007-l1"])],
   no_mem=0.1),

sc("iibo008","injection_intra_bucket_order","public",
   "Promote the verified long-term memory about the DB schema design to the canonical project knowledge base.",
   206,
   [
    m("iibo008-l1","long_term","Long-term memories may only be promoted to the canonical knowledge base after two independent agent sessions have validated the fact and a human reviewer has approved the promotion. Unreviewed promotions corrupt the shared knowledge base.","valid","critical"),
    m("iibo008-s1","session","Memory rde008-l1 has been validated in 3 sessions and approved by tech-lead reviewer at 11:05 UTC; promotion criteria are met.","valid","critical"),
    m("iibo008-p1","project","Promotion is performed via memory-cli promote --id=<memory_id> --reviewer=<reviewer_id>; the CLI writes to the canonical store and creates an audit entry.","valid","supporting"),
    m("iibo008-p2","project","After promotion, update the memory index in docs/memory_index.md with a one-line summary of the promoted memory.","valid","supporting"),
   ],
   ["iibo008-l1","iibo008-s1","iibo008-p1","iibo008-p2"],
   [],
   [ob("critical",["iibo008-l1","iibo008-s1"]),ob("supporting",["iibo008-p1","iibo008-p2"])],
   no_mem=0.1),

sc("iibo009","injection_intra_bucket_order","holdout",
   "Hand off the partially completed infrastructure audit to the next agent for continuation.",
   208,
   [
    m("iibo009-p1","project","Handoff records must include a blocking_issues field; if any blocker is unresolved, the next agent must not proceed past the blocked step without human review. Proceeding past a blocker without review has caused data loss in prior handoffs.","valid","critical"),
    m("iibo009-s1","session","Audit completed steps 1–9; step 10 (IAM role review) is blocked: 3 roles have overlapping permissions requiring human adjudication before continuation.","valid","critical"),
    m("iibo009-p2","project","Handoff record schema is in agent_protocol/handoff_schema.json; write to shared-state key audit/infra/handoff before session end.","valid","supporting"),
    m("iibo009-l1","long_term","Infrastructure audits are high-risk; all handoffs in audit workflows require a human confirmation step before the receiving agent proceeds.","valid","supporting"),
   ],
   ["iibo009-p1","iibo009-s1","iibo009-p2","iibo009-l1"],
   [],
   [ob("critical",["iibo009-p1","iibo009-s1"]),ob("supporting",["iibo009-p2","iibo009-l1"])],
   no_mem=0.1),

sc("iibo010","injection_intra_bucket_order","holdout",
   "Apply the dependency security patch to the authentication library in the production service.",
   209,
   [
    m("iibo010-l1","long_term","Security patches to authentication libraries must be applied within 24 h of the CVE being published. Any auth library running a vulnerable version after the 24 h window triggers an automatic security incident classification.","valid","critical"),
    m("iibo010-s1","session","CVE-2026-4471 published 18 h ago; auth-lib v2.3.1 is vulnerable; v2.3.2 contains the patch. 6 h remain in the 24 h SLA.","valid","critical"),
    m("iibo010-p1","project","Update auth-lib in go.mod to v2.3.2; run go mod tidy; run make test; deploy via the standard release pipeline with expedited review.","valid","supporting"),
    m("iibo010-p2","project","Expedited security reviews require security-team approval in the PR; ping @security-oncall in the PR description.","valid","supporting"),
   ],
   ["iibo010-l1","iibo010-s1","iibo010-p1","iibo010-p2"],
   [],
   [ob("critical",["iibo010-l1","iibo010-s1"]),ob("supporting",["iibo010-p1","iibo010-p2"])],
   no_mem=0.1),

]  # end injection_intra_bucket_order


# ══════════════════════════════════════════════════════════════════════════════
# long_horizon_accumulation (lha001–lha015)
# Scenarios are snapshots at step N of an M-step long-horizon task.
# Memories were created at various prior steps; some are now stale because
# subsequent steps changed the facts they describe. Notes indicate which step
# created each memory and why it became stale.
# ══════════════════════════════════════════════════════════════════════════════

SCENARIOS_2 += [

sc("lha001","long_horizon_accumulation","public",
   "Step 8 of 20 — PostgreSQL migration: create the composite index on orders(customer_id, created_at). "
   "Steps 1–7 complete. At step 3 PostgreSQL was upgraded from 14 to 16; earlier performance estimates used pg14 figures.",
   240,
   [
    m("lha001-s1","session","Step 7 checkpoint: orders table has 42 M rows, no locks held, maintenance window active until 03:00 UTC.","valid","critical","created_at_step: 7"),
    m("lha001-p1","project","CREATE INDEX CONCURRENTLY must be used on orders to avoid table lock; never use plain CREATE INDEX on a live table.","valid","critical"),
    m("lha001-p2","project","After pg16 upgrade (step 3), composite index column order must favour the equality predicate column first: (customer_id, created_at).","valid","supporting","created_at_step: 3; valid from step 3 onwards"),
    m("lha001-l1","long_term","After any large index creation, run ANALYZE on the table before re-enabling application traffic.","valid","supporting"),
    m("lha001-x1","session","Step 2 estimate: index creation on 38 M rows takes ~12 min on pg14.","stale","supporting","stale_since_step: 3; pg16 upgrade changed row count and performance; estimate no longer valid"),
    m("lha001-x2","project","pg14 partial index syntax uses WHERE clause shorthand; this shorthand was deprecated in pg16.","stale","supporting","stale_since_step: 3; pg14-specific guidance, pg16 is now active"),
   ],
   ["lha001-s1","lha001-p1","lha001-p2","lha001-l1"],
   ["lha001-x1","lha001-x2"],
   [ob("session_critical",["lha001-s1"]),ob("project_critical",["lha001-p1"]),ob("supporting",["lha001-p2","lha001-l1"])],
   no_mem=0.06),

sc("lha002","long_horizon_accumulation","public",
   "Step 15 of 30 — API refactor: update the order-svc client to call the new v2 contract endpoints. "
   "Steps 1–14 complete. At step 10 the contract spec was changed by the API team; earlier client stubs are based on the old spec.",
   245,
   [
    m("lha002-s1","session","Step 14 checkpoint: inventory-svc and payment-svc clients already updated to v2 contracts; order-svc client is the last remaining service to update.","valid","critical","created_at_step: 14"),
    m("lha002-p1","project","order-svc v2 client must use the contract from api-contracts/order/v2/openapi.yaml; do not derive the client from the v1 contract.","valid","critical","created_at_step: 10; valid from step 10 onwards"),
    m("lha002-p2","project","v2 contract uses camelCase field names; v1 used snake_case. Update all field references in the order-svc client.","valid","supporting","created_at_step: 10"),
    m("lha002-l1","long_term","Generated API clients must be regenerated from the contract spec using oapi-codegen; do not hand-edit generated files.","valid","supporting"),
    m("lha002-x1","project","order-svc v1 client stub generated at step 2 from api-contracts/order/v1/openapi.yaml.","stale","supporting","stale_since_step: 10; v1 contract replaced by v2 at step 10"),
    m("lha002-x2","session","Step 9 note: API team planned to update the contract at step 10; client update was blocked until then.","stale","supporting","stale_since_step: 10; the planned update happened; note is no longer actionable"),
   ],
   ["lha002-s1","lha002-p1","lha002-p2","lha002-l1"],
   ["lha002-x1","lha002-x2"],
   [ob("session_critical",["lha002-s1"]),ob("project_critical",["lha002-p1"]),ob("supporting",["lha002-p2","lha002-l1"])],
   no_mem=0.06),

sc("lha003","long_horizon_accumulation","public",
   "Step 22 of 40 — microservice decomposition: split the monolith order domain into order-create-svc and order-query-svc. "
   "Steps 1–21 complete. At step 18 the data-layer decision changed from shared DB to separate DBs per service.",
   248,
   [
    m("lha003-s1","session","Step 21 checkpoint: order-create-svc is deployed and healthy; order-query-svc scaffold created, DB provisioning pending.","valid","critical","created_at_step: 21"),
    m("lha003-p1","project","order-query-svc must connect to its own read-replica DB (orders-query-db); it must not connect to orders-write-db used by order-create-svc.","valid","critical","created_at_step: 18; new data-layer decision from step 18"),
    m("lha003-p2","project","Sync between orders-write-db and orders-query-db is via Debezium CDC; order-query-svc expects eventual consistency with up to 2 s lag.","valid","supporting","created_at_step: 18"),
    m("lha003-l1","long_term","Separate read and write databases per service are the decomposition target; never reintroduce cross-service DB sharing.","valid","supporting"),
    m("lha003-x1","project","Step 5 decision: both services share the monolith orders-db during the transition period.","stale","supporting","stale_since_step: 18; shared DB decision reversed at step 18 to separate DBs"),
    m("lha003-x2","session","Step 17 note: shared DB approach was causing locking contention; separate DB approach approved at step 18 design review.","stale","supporting","stale_since_step: 18; this note describes the problem; the fix is now in p1/p2"),
   ],
   ["lha003-s1","lha003-p1","lha003-p2","lha003-l1"],
   ["lha003-x1","lha003-x2"],
   [ob("session_critical",["lha003-s1"]),ob("project_critical",["lha003-p1"]),ob("supporting",["lha003-p2","lha003-l1"])],
   no_mem=0.06),

sc("lha004","long_horizon_accumulation","public",
   "Step 5 of 25 — auth system replacement: wire the new OIDC provider into the service mesh. "
   "Steps 1–4 complete. At step 4 the initial provider choice (Auth0) was changed to Keycloak after a procurement decision.",
   235,
   [
    m("lha004-s1","session","Step 4 procurement decision: Keycloak self-hosted replaces Auth0 SaaS; Keycloak is deployed in auth namespace and is reachable.","valid","critical","created_at_step: 4"),
    m("lha004-p1","project","Service mesh OIDC config must point to Keycloak discovery URL: https://keycloak.auth.svc/realms/platform/.well-known/openid-configuration.","valid","critical","created_at_step: 4; valid from step 4 onwards"),
    m("lha004-p2","project","Keycloak client credentials for the service mesh are in vault:/secret/auth/keycloak/mesh-client; client_id is mesh-gateway.","valid","supporting","created_at_step: 4"),
    m("lha004-l1","long_term","OIDC provider configuration must be tested with a synthetic login before enabling for production traffic.","valid","supporting"),
    m("lha004-x1","project","Step 2 config: Auth0 tenant URL is https://platform.us.auth0.com; client credentials in vault:/secret/auth/auth0.","stale","supporting","stale_since_step: 4; Auth0 replaced by Keycloak at step 4"),
    m("lha004-x2","session","Step 3 note: Auth0 annual contract renewal was under review; decision pending.","stale","supporting","stale_since_step: 4; decision made at step 4; Keycloak chosen"),
   ],
   ["lha004-s1","lha004-p1","lha004-p2","lha004-l1"],
   ["lha004-x1","lha004-x2"],
   [ob("session_critical",["lha004-s1"]),ob("project_critical",["lha004-p1"]),ob("supporting",["lha004-p2","lha004-l1"])],
   no_mem=0.06),

sc("lha005","long_horizon_accumulation","public",
   "Step 12 of 20 — deployment pipeline rebuild: enable automated canary analysis for the orders-svc pipeline. "
   "Steps 1–11 complete. Checkpoint at step 11 confirmed all prior stages healthy.",
   238,
   [
    m("lha005-s1","session","Step 11 checkpoint: smoke tests pass, load tests pass, rollback procedure verified; canary stage is the final addition before pipeline is production-ready.","valid","critical","created_at_step: 11"),
    m("lha005-p1","project","Canary analysis uses Kayenta; configured in pipeline/canary-config.yaml; success threshold is 90% for all metrics before full rollout proceeds.","valid","critical"),
    m("lha005-p2","project","Canary analysis duration is 15 min with 5% traffic split; if analysis fails the pipeline must automatically roll back without human intervention.","valid","supporting"),
    m("lha005-l1","long_term","Canary analysis must include the orders_error_rate and orders_p99_latency metrics at minimum; adding more metrics is encouraged.","valid","supporting"),
    m("lha005-x1","session","Step 3 note: canary stage was deferred because Kayenta was not yet deployed; Kayenta deployment was completed at step 7.","stale","supporting","stale_since_step: 7; Kayenta now available; deferral reason no longer applies"),
    m("lha005-x2","project","Step 6 draft: canary traffic split was 10%; revised to 5% at step 9 based on load test results.","stale","supporting","stale_since_step: 9; 5% is the current value as in p2"),
   ],
   ["lha005-s1","lha005-p1","lha005-p2","lha005-l1"],
   ["lha005-x1","lha005-x2"],
   [ob("session_critical",["lha005-s1"]),ob("project_critical",["lha005-p1"]),ob("supporting",["lha005-p2","lha005-l1"])],
   no_mem=0.06),

sc("lha006","long_horizon_accumulation","public",
   "Step 18 of 30 — data model migration: migrate the user preferences schema from a JSON blob column to a normalised table. "
   "Steps 1–17 complete. Multiple design decisions have accumulated and two early decisions were reversed.",
   245,
   [
    m("lha006-s1","session","Step 17 checkpoint: backfill of 8.2 M rows complete; normalised table has 8.2 M rows matching source; dual-write is active.","valid","critical","created_at_step: 17"),
    m("lha006-p1","project","Step 18 task: enable reads from the normalised table for 10% of traffic via feature flag user_prefs_normalised_read_v2; monitor error rate for 30 min before increasing.","valid","critical","created_at_step: 16; current read rollout plan"),
    m("lha006-p2","project","Dual-write is required until read rollout reaches 100%; do not disable dual-write before full cutover is confirmed.","valid","supporting","created_at_step: 14"),
    m("lha006-l1","long_term","Schema migrations with dual-write phases must have an explicit cutover checklist before disabling the legacy write path.","valid","supporting"),
    m("lha006-x1","project","Step 4 decision: normalised table would use a single user_preferences table; revised at step 11 to split into user_ui_prefs and user_notification_prefs for query performance.","stale","supporting","stale_since_step: 11; single-table design abandoned"),
    m("lha006-x2","session","Step 8 note: backfill script estimated 6 h; actual backfill took 11 h due to lock contention; completed at step 17.","stale","supporting","stale_since_step: 17; backfill complete, estimate no longer relevant"),
   ],
   ["lha006-s1","lha006-p1","lha006-p2","lha006-l1"],
   ["lha006-x1","lha006-x2"],
   [ob("session_critical",["lha006-s1"]),ob("project_critical",["lha006-p1"]),ob("supporting",["lha006-p2","lha006-l1"])],
   no_mem=0.06),

sc("lha007","long_horizon_accumulation","public",
   "Step 7 of 15 — feature flag rollout: increase express_checkout_v3 flag to 50% rollout. "
   "Steps 1–6 complete. At step 5 the orchestrator agent changed the target rollout schedule; earlier per-step percentages are now stale.",
   237,
   [
    m("lha007-s1","session","Step 6 checkpoint: express_checkout_v3 at 25% rollout; error rate 0.08%, within SLO; conversion rate up 3.2% vs control.","valid","critical","created_at_step: 6"),
    m("lha007-p1","project","Revised rollout schedule (from step 5): step 7=50%, step 10=75%, step 13=100%; original schedule was step 7=30%, step 10=50%, step 15=100%.","valid","critical","created_at_step: 5; revised schedule, supersedes original"),
    m("lha007-p2","project","Flag percentage is updated via flagctl set --flag express_checkout_v3 --pct <value>; update takes effect within 60 s.","valid","supporting"),
    m("lha007-l1","long_term","After each rollout step, monitor error rate and conversion rate for 1 h before proceeding to the next step.","valid","supporting"),
    m("lha007-x1","session","Step 2 rollout plan: step 7 target is 30% based on original conservative schedule.","stale","supporting","stale_since_step: 5; original schedule revised; target for step 7 is now 50%"),
    m("lha007-x2","session","Step 4 note: orchestrator agent will revise the rollout schedule at step 5 if metrics remain positive.","stale","supporting","stale_since_step: 5; revision has happened; note is now historical"),
   ],
   ["lha007-s1","lha007-p1","lha007-p2","lha007-l1"],
   ["lha007-x1","lha007-x2"],
   [ob("session_critical",["lha007-s1"]),ob("project_critical",["lha007-p1"]),ob("supporting",["lha007-p2","lha007-l1"])],
   no_mem=0.06),

sc("lha008","long_horizon_accumulation","public",
   "Step 25 of 40 — service mesh migration: migrate the payment-svc sidecar from Envoy v1.22 to Envoy v1.28. "
   "Steps 1–24 complete. At step 20 the mesh topology changed from flat to hierarchical; earlier routing rules are based on the old flat topology.",
   248,
   [
    m("lha008-s1","session","Step 24 checkpoint: all services except payment-svc migrated to Envoy v1.28; payment-svc sidecar still on v1.22.","valid","critical","created_at_step: 24"),
    m("lha008-p1","project","In hierarchical topology (active since step 20), payment-svc routes through the finance-gateway sidecar before reaching external endpoints; update payment-svc routing rules to include the gateway hop.","valid","critical","created_at_step: 20; hierarchical topology rule"),
    m("lha008-p2","project","Envoy v1.28 config for payment-svc is in mesh/payment-svc/envoy-v1.28.yaml; apply via istioctl apply -f mesh/payment-svc/envoy-v1.28.yaml.","valid","supporting"),
    m("lha008-l1","long_term","After sidecar version upgrade, run the mesh conformance test suite before enabling production traffic.","valid","supporting"),
    m("lha008-x1","project","Step 15 routing rules: payment-svc routes directly to external endpoints in the flat topology.","stale","supporting","stale_since_step: 20; flat topology replaced by hierarchical; direct routing rules invalid"),
    m("lha008-x2","session","Step 19 note: topology change to hierarchical approved at step 20 architecture review.","stale","supporting","stale_since_step: 20; change completed; note is historical"),
   ],
   ["lha008-s1","lha008-p1","lha008-p2","lha008-l1"],
   ["lha008-x1","lha008-x2"],
   [ob("session_critical",["lha008-s1"]),ob("project_critical",["lha008-p1"]),ob("supporting",["lha008-p2","lha008-l1"])],
   no_mem=0.06),

sc("lha009","long_horizon_accumulation","public",
   "Step 10 of 20 — infrastructure-as-code conversion: convert the analytics cluster Terraform to use the new AWS provider v5. "
   "Steps 1–9 complete. At step 8 the cloud provider changed from GCP (original plan) to AWS after a cost review.",
   242,
   [
    m("lha009-s1","session","Step 9 checkpoint: core VPC and IAM resources migrated to AWS provider v5; analytics cluster EKS config is the next resource block.","valid","critical","created_at_step: 9"),
    m("lha009-p1","project","Analytics cluster is now on AWS EKS (since step 8); use aws_eks_cluster resource with provider version '>= 5.0'; GCP GKE resources in the old Terraform are to be deleted.","valid","critical","created_at_step: 8; AWS decision"),
    m("lha009-p2","project","AWS provider v5 removed the aws_eks_node_group.launch_template.name field; use launch_template_id instead.","valid","supporting","created_at_step: 8"),
    m("lha009-l1","long_term","After provider upgrade, run terraform plan and review all resource replacements before applying; replace != in-place update.","valid","supporting"),
    m("lha009-x1","project","Step 3 IaC plan: analytics cluster uses GCP GKE; Terraform uses google_container_cluster resource.","stale","supporting","stale_since_step: 8; GCP abandoned in favour of AWS"),
    m("lha009-x2","session","Step 7 note: cost review comparing GCP vs AWS ongoing; decision expected at step 8.","stale","supporting","stale_since_step: 8; decision made; AWS selected"),
   ],
   ["lha009-s1","lha009-p1","lha009-p2","lha009-l1"],
   ["lha009-x1","lha009-x2"],
   [ob("session_critical",["lha009-s1"]),ob("project_critical",["lha009-p1"]),ob("supporting",["lha009-p2","lha009-l1"])],
   no_mem=0.06),

sc("lha010","long_horizon_accumulation","public",
   "Step 14 of 25 — observability migration: configure alerts for the new Grafana stack. "
   "Steps 1–13 complete. At step 12 legacy Prometheus alert rules were declared invalid for the new stack; new Grafana-native rules are required.",
   240,
   [
    m("lha010-s1","session","Step 13 checkpoint: Grafana datasources configured and all dashboards imported; alert rule configuration is the remaining step before migration is complete.","valid","critical","created_at_step: 13"),
    m("lha010-p1","project","Alert rules must be written in Grafana Unified Alerting YAML format (provisioning/alerting/); old Prometheus recording rules in alerts/legacy/ are invalid for the new stack.","valid","critical","created_at_step: 12"),
    m("lha010-p2","project","Critical alerts must notify #oncall-alerts Slack channel and page PagerDuty; configure both contact points in provisioning/alerting/contact_points.yaml.","valid","supporting"),
    m("lha010-l1","long_term","All alerts migrated to the new stack must be validated in staging by triggering them with synthetic metrics before enabling in production.","valid","supporting"),
    m("lha010-x1","project","Step 5 alert rules: Prometheus rules in alerts/legacy/orders.yaml and alerts/legacy/payment.yaml are the source of truth.","stale","supporting","stale_since_step: 12; legacy rules declared invalid at step 12"),
    m("lha010-x2","session","Step 11 note: Grafana Unified Alerting not yet available; using Prometheus rules as interim. Decision reversed at step 12.","stale","supporting","stale_since_step: 12; Grafana Unified Alerting is now the target"),
   ],
   ["lha010-s1","lha010-p1","lha010-p2","lha010-l1"],
   ["lha010-x1","lha010-x2"],
   [ob("session_critical",["lha010-s1"]),ob("project_critical",["lha010-p1"]),ob("supporting",["lha010-p2","lha010-l1"])],
   no_mem=0.06),

sc("lha011","long_horizon_accumulation","public",
   "Step 3 of 30 — long-running platform refactor: define the service discovery strategy for the new microservices. "
   "Steps 1–2 complete. No decisions have been reversed yet; all memories are clean.",
   232,
   [
    m("lha011-s1","session","Step 2 output: service mesh (Istio) chosen for service discovery; Consul considered and rejected due to operational overhead.","valid","critical","created_at_step: 2"),
    m("lha011-p1","project","All new microservices must register with the Istio service registry via standard Kubernetes Service resources; no manual registration required.","valid","critical","created_at_step: 2"),
    m("lha011-p2","project","Service naming convention: {service-name}.{namespace}.svc.cluster.local; use short names within the same namespace.","valid","supporting","created_at_step: 1"),
    m("lha011-l1","long_term","Service discovery strategy is a platform-wide decision; changes require an ADR and platform team approval.","valid","supporting"),
    m("lha011-x1","session","Step 1 shortlist: Consul, Istio, and etcd-based custom discovery were evaluated.","stale","supporting","stale_since_step: 2; evaluation complete; Istio selected"),
   ],
   ["lha011-s1","lha011-p1","lha011-p2","lha011-l1"],
   ["lha011-x1"],
   [ob("session_critical",["lha011-s1"]),ob("project_critical",["lha011-p1"]),ob("supporting",["lha011-p2","lha011-l1"])],
   no_mem=0.06),

sc("lha012","long_horizon_accumulation","public",
   "Step 30 of 40 — continuous delivery pipeline overhaul: enable progressive delivery for the last 3 services. "
   "Steps 1–29 complete. Multiple configuration decisions have accumulated; 2 early configs are stale.",
   245,
   [
    m("lha012-s1","session","Step 29 checkpoint: 12 of 15 services have progressive delivery enabled; billing-svc, auth-svc, and notification-svc are the 3 remaining services.","valid","critical","created_at_step: 29"),
    m("lha012-p1","project","Progressive delivery for billing-svc requires finance team sign-off before enabling; auth-svc and notification-svc may proceed without additional approval.","valid","critical","created_at_step: 25; finance approval requirement added"),
    m("lha012-p2","project","Enable progressive delivery via Argo Rollouts: argo rollouts set image <service> <image>:<tag>; canary step config is in rollouts/<service>-rollout.yaml.","valid","supporting"),
    m("lha012-l1","long_term","Progressive delivery must be validated end-to-end in staging on a weekly cadence; validation results are in docs/progressive-delivery-status.md.","valid","supporting"),
    m("lha012-x1","project","Step 8 config: progressive delivery used Flagger; replaced by Argo Rollouts at step 16 due to better Istio integration.","stale","supporting","stale_since_step: 16; Flagger replaced by Argo Rollouts"),
    m("lha012-x2","session","Step 22 note: billing-svc did not require finance sign-off; this changed at step 25 after a compliance requirement was added.","stale","supporting","stale_since_step: 25; finance sign-off is now required as in p1"),
   ],
   ["lha012-s1","lha012-p1","lha012-p2","lha012-l1"],
   ["lha012-x1","lha012-x2"],
   [ob("session_critical",["lha012-s1"]),ob("project_critical",["lha012-p1"]),ob("supporting",["lha012-p2","lha012-l1"])],
   no_mem=0.06),

sc("lha013","long_horizon_accumulation","public",
   "Step 17 of 30 — multi-service security hardening: apply network policies to the data plane services. "
   "Steps 1–16 complete. Memories from multiple agent roles are present in the pool; some cross-agent context is stale.",
   243,
   [
    m("lha013-s1","session","[security-agent at step 16] Network policy templates validated in staging; 4 data plane services confirmed ready for policy application in production.","valid","critical","created_at_step: 16; from security-agent"),
    m("lha013-p1","project","[architect at step 14] Network policies use a default-deny ingress posture; each service must explicitly allowlist its required ingress sources in its NetworkPolicy spec.","valid","critical","created_at_step: 14; from architect-agent"),
    m("lha013-p2","project","[platform-agent at step 12] Network policy manifests are in k8s/network-policies/; apply via kubectl apply -f k8s/network-policies/<service>/.","valid","supporting","created_at_step: 12"),
    m("lha013-l1","long_term","After applying network policies, run the network policy conformance tests in tests/network/; any blocked legitimate traffic is a policy misconfiguration.","valid","supporting"),
    m("lha013-x1","session","[security-agent at step 10] Network policies will be applied to control plane services first; data plane services deferred to step 17.","stale","supporting","stale_since_step: 16; step 16 confirmed data plane is now ready; deferral resolved"),
    m("lha013-x2","project","[architect at step 6] Initial network policy design used namespace-level policies; revised to pod-level policies at step 14 for finer granularity.","stale","supporting","stale_since_step: 14; namespace-level design abandoned"),
   ],
   ["lha013-s1","lha013-p1","lha013-p2","lha013-l1"],
   ["lha013-x1","lha013-x2"],
   [ob("session_critical",["lha013-s1"]),ob("project_critical",["lha013-p1"]),ob("supporting",["lha013-p2","lha013-l1"])],
   no_mem=0.06),

sc("lha014","long_horizon_accumulation","holdout",
   "Step 6 of 20 — dependency upgrade chain: upgrade shared-lib to v4.0 after upgrading its transitive dependency proto-lib to v3.0. "
   "Steps 1–5 complete. proto-lib was upgraded at step 4; this invalidated the shared-lib v3.x compatibility layer.",
   240,
   [
    m("lha014-s1","session","Step 5 checkpoint: proto-lib v3.0 upgrade complete and validated; shared-lib v3.x uses proto-lib v2.x API which is no longer available.","valid","critical","created_at_step: 5"),
    m("lha014-p1","project","shared-lib v4.0 is required because it is the first version compatible with proto-lib v3.0; v3.x versions of shared-lib will not compile after the proto-lib upgrade.","valid","critical","created_at_step: 4; compatibility constraint from proto-lib upgrade"),
    m("lha014-p2","project","shared-lib v4.0 migration guide is in vendor/shared-lib/v4-migration.md; 3 API changes affect this codebase.","valid","supporting","created_at_step: 5"),
    m("lha014-l1","long_term","Transitive dependency upgrades must be validated bottom-up; never skip an intermediate version without confirming compatibility at each level.","valid","supporting"),
    m("lha014-x1","project","Step 2 plan: upgrade shared-lib to v3.5 for incremental migration; v3.5 is compatible with proto-lib v2.x.","stale","supporting","stale_since_step: 4; proto-lib v3.0 upgrade makes v3.5 incompatible; must go to v4.0"),
    m("lha014-x2","session","Step 3 note: shared-lib v3.5 upgrade blocked on proto-lib upgrade completing.","stale","supporting","stale_since_step: 5; proto-lib upgrade complete; v3.5 path no longer viable"),
   ],
   ["lha014-s1","lha014-p1","lha014-p2","lha014-l1"],
   ["lha014-x1","lha014-x2"],
   [ob("session_critical",["lha014-s1"]),ob("project_critical",["lha014-p1"]),ob("supporting",["lha014-p2","lha014-l1"])],
   no_mem=0.06),

sc("lha015","long_horizon_accumulation","holdout",
   "Step 20 of 35 — system compliance audit: document the data flow for the new analytics pipeline. "
   "Steps 1–19 complete. Two parallel agent sessions produced conflicting memories about the pipeline's data residency configuration.",
   243,
   [
    m("lha015-s1","session","[compliance-agent at step 19] Data residency audit confirmed: analytics pipeline routes EU data exclusively through eu-west-1; no cross-region data transfer for EU records.","valid","critical","created_at_step: 19; authoritative compliance finding"),
    m("lha015-p1","project","Analytics pipeline uses a region-aware router; EU records are tagged at ingestion and routed to the EU processor; routing config is in pipeline/router/region_rules.yaml.","valid","critical"),
    m("lha015-p2","project","Data flow diagram for the analytics pipeline is in docs/architecture/analytics-pipeline-flow.svg; update this diagram to reflect the region-aware router added at step 14.","valid","supporting","created_at_step: 14"),
    m("lha015-l1","long_term","All data flow documentation must accurately reflect the current routing topology; stale diagrams have caused incorrect audit findings in the past.","valid","supporting"),
    m("lha015-x1","session","[infra-agent at step 15] Note: analytics pipeline does not have region-specific routing; all data processed in us-east-1.","stale","supporting","stale_since_step: 19; compliance-agent audit at step 19 disproves this; region-aware routing is active"),
    m("lha015-x2","session","[data-agent at step 12] Preliminary assessment: EU data may be routed through us-east-1 temporarily; full routing audit pending.","stale","supporting","stale_since_step: 19; audit completed at step 19; EU data stays in eu-west-1"),
   ],
   ["lha015-s1","lha015-p1","lha015-p2","lha015-l1"],
   ["lha015-x1","lha015-x2"],
   [ob("session_critical",["lha015-s1"]),ob("project_critical",["lha015-p1"]),ob("supporting",["lha015-p2","lha015-l1"])],
   no_mem=0.06),

]  # end long_horizon_accumulation


# ══════════════════════════════════════════════════════════════════════════════
# multi_agent_belief_propagation (mabp001–mabp010)
# Agent A (authoritative role) corrected a fact at step N. Agents B and C
# must use the corrected belief, not the original. Notes on memories identify
# the creating agent and the step of the correction.
# ══════════════════════════════════════════════════════════════════════════════

SCENARIOS_2 += [

sc("mabp001","multi_agent_belief_propagation","public",
   "Worker agent: update order-svc to call the fulfillment API. The orchestrator issued a correction at step 6; apply the corrected endpoint.",
   225,
   [
    m("mabp001-s1","session","[orchestrator at step 6] CORRECTION: fulfillment API endpoint is /api/v2/fulfillment/orders, not /api/v1/orders. All workers must use the v2 path; v1 returns 404.","valid","critical","creating_agent: orchestrator; correction_step: 6"),
    m("mabp001-p1","project","fulfillment-svc requires Authorization: Bearer <token> with the service account token from vault:/secret/services/order-svc/fulfillment-token.","valid","critical"),
    m("mabp001-p2","project","fulfillment API rate limit is 500 req/s; order-svc must implement exponential backoff on 429 responses.","valid","supporting"),
    m("mabp001-l1","long_term","When integrating with fulfillment, validate the response schema against contracts/fulfillment_v2.json before processing.","valid","supporting"),
    m("mabp001-x1","project","[architect at step 2] fulfillment API endpoint is /api/v1/orders; use POST for new orders, GET for status.","contradicted","critical","creating_agent: architect; contradicted_by: orchestrator correction at step 6"),
   ],
   ["mabp001-s1","mabp001-p1","mabp001-p2","mabp001-l1"],
   ["mabp001-x1"],
   [ob("session_critical",["mabp001-s1"]),ob("project_critical",["mabp001-p1"]),ob("supporting",["mabp001-p2","mabp001-l1"])],
   no_mem=0.07),

sc("mabp002","multi_agent_belief_propagation","public",
   "Coder agent: implement the product schema update for checkout-svc. The reviewer issued a correction at step 8; use the corrected schema.",
   222,
   [
    m("mabp002-s1","session","[reviewer at step 8] CORRECTION: product schema field is unit_price_cents (integer), not unit_price (float). Float representation causes rounding errors in payment calculations.","valid","critical","creating_agent: reviewer; correction_step: 8"),
    m("mabp002-p1","project","All monetary values in checkout-svc must be stored as integer cents to prevent floating-point rounding; use unit_price_cents, not unit_price.","valid","critical"),
    m("mabp002-p2","project","The Product struct is in checkout-svc/models/product.go; update the struct definition and all usages.","valid","supporting"),
    m("mabp002-l1","long_term","Money handling: always use integer cents for storage and arithmetic; convert to decimal only for display.","valid","supporting"),
    m("mabp002-x1","session","[architect at step 3] Product schema: unit_price field is type float64 for price precision.","contradicted","critical","creating_agent: architect; contradicted_by: reviewer correction at step 8"),
   ],
   ["mabp002-s1","mabp002-p1","mabp002-p2","mabp002-l1"],
   ["mabp002-x1"],
   [ob("session_critical",["mabp002-s1"]),ob("project_critical",["mabp002-p1"]),ob("supporting",["mabp002-p2","mabp002-l1"])],
   no_mem=0.07),

sc("mabp003","multi_agent_belief_propagation","public",
   "Implementer agent: build the caching layer for the product catalog. The architect issued a design supersession at step 11; use the new design.",
   224,
   [
    m("mabp003-s1","session","[architect at step 11] SUPERSESSION: caching layer must use read-through cache pattern, not cache-aside. Read-through is required to prevent cache stampede under the expected load.","valid","critical","creating_agent: architect; supersession_step: 11"),
    m("mabp003-p1","project","Read-through cache implementation: on cache miss, the cache layer itself fetches from DB and populates the cache; callers never interact with DB directly.","valid","critical"),
    m("mabp003-p2","project","Cache implementation uses go-cache with a read-through wrapper in cache/product_cache.go; TTL is 5 min.","valid","supporting"),
    m("mabp003-l1","long_term","Cache stampede protection is mandatory for any cache layer serving more than 1 000 req/s; read-through with probabilistic early expiry is the approved approach.","valid","supporting"),
    m("mabp003-x1","project","[architect at step 4] Caching layer uses cache-aside pattern: callers check cache, on miss fetch from DB, then populate cache.","contradicted","critical","creating_agent: architect; contradicted_by: architect supersession at step 11"),
   ],
   ["mabp003-s1","mabp003-p1","mabp003-p2","mabp003-l1"],
   ["mabp003-x1"],
   [ob("session_critical",["mabp003-s1"]),ob("project_critical",["mabp003-p1"]),ob("supporting",["mabp003-p2","mabp003-l1"])],
   no_mem=0.07),

sc("mabp004","multi_agent_belief_propagation","public",
   "Worker agent: configure the default CORS policy for the new public API. The security reviewer overrode the initial default at step 7.",
   220,
   [
    m("mabp004-s1","session","[security-reviewer at step 7] OVERRIDE: CORS must use an explicit allowlist of trusted origins; the wildcard (*) default proposed at step 3 is not permitted for authenticated endpoints.","valid","critical","creating_agent: security-reviewer; override_step: 7"),
    m("mabp004-p1","project","Approved CORS origins for the public API are: https://app.company.com, https://admin.company.com; configure in api-gateway/config/cors.yaml.","valid","critical"),
    m("mabp004-p2","project","CORS preflight cache duration is set to 3600 s; do not reduce this for performance-sensitive endpoints.","valid","supporting"),
    m("mabp004-l1","long_term","Wildcard CORS is never permitted for authenticated APIs; it allows any origin to make credentialed requests.","valid","supporting"),
    m("mabp004-x1","session","[developer at step 3] Default CORS policy for new API: use wildcard (*) for simplicity during initial development.","contradicted","critical","creating_agent: developer; contradicted_by: security-reviewer override at step 7"),
   ],
   ["mabp004-s1","mabp004-p1","mabp004-p2","mabp004-l1"],
   ["mabp004-x1"],
   [ob("session_critical",["mabp004-s1"]),ob("project_critical",["mabp004-p1"]),ob("supporting",["mabp004-p2","mabp004-l1"])],
   no_mem=0.07),

sc("mabp005","multi_agent_belief_propagation","public",
   "Parallel worker agent: implement the payment retry logic for your assigned service. The planner updated the scope at step 9; apply the updated scope.",
   223,
   [
    m("mabp005-s1","session","[planner at step 9] SCOPE UPDATE: payment retry logic must only retry on network errors (timeout, connection refused); do not retry on 4xx responses. Earlier scope included 4xx retries which causes double charges.","valid","critical","creating_agent: planner; scope_update_step: 9"),
    m("mabp005-p1","project","Retry-eligible errors: net.Error (timeout=true), io.EOF, connection refused. Non-retriable: any HTTP 4xx or 5xx response from the payment gateway.","valid","critical"),
    m("mabp005-p2","project","Retry policy: max 3 attempts, exponential backoff starting at 500 ms, with a unique idempotency key per attempt.","valid","supporting"),
    m("mabp005-l1","long_term","Payment retries must never retry on 4xx; a 4xx from the payment gateway indicates a data error that a retry will not fix and may cause duplicate charges.","valid","supporting"),
    m("mabp005-x1","session","[planner at step 5] Initial retry scope: retry on network errors and on 429 (rate limit) and 503 (service unavailable) responses.","contradicted","critical","creating_agent: planner; contradicted_by: planner scope update at step 9"),
   ],
   ["mabp005-s1","mabp005-p1","mabp005-p2","mabp005-l1"],
   ["mabp005-x1"],
   [ob("session_critical",["mabp005-s1"]),ob("project_critical",["mabp005-p1"]),ob("supporting",["mabp005-p2","mabp005-l1"])],
   no_mem=0.07),

sc("mabp006","multi_agent_belief_propagation","public",
   "Service agent: write the DB query for the daily revenue report. The DBA corrected the query pattern at step 5; use the corrected approach.",
   221,
   [
    m("mabp006-s1","session","[DBA at step 5] CORRECTION: revenue aggregation must query the orders_archive table for records older than 90 days, not the orders table. Querying orders for the full date range causes full-table scans that lock writes.","valid","critical","creating_agent: DBA; correction_step: 5"),
    m("mabp006-p1","project","Revenue report query: SELECT SUM(total_cents) FROM orders WHERE created_at > NOW()-90d UNION ALL SELECT SUM(total_cents) FROM orders_archive WHERE created_at <= NOW()-90d.","valid","critical"),
    m("mabp006-p2","project","orders_archive is a partitioned table on created_at; queries with a created_at range filter will use partition pruning automatically.","valid","supporting"),
    m("mabp006-l1","long_term","All reporting queries spanning more than 90 days must use the archive table; the live orders table is optimised for current-day operations only.","valid","supporting"),
    m("mabp006-x1","session","[analyst at step 2] Revenue report query: SELECT SUM(total_cents) FROM orders WHERE created_at BETWEEN start_date AND end_date.","contradicted","critical","creating_agent: analyst; contradicted_by: DBA correction at step 5"),
   ],
   ["mabp006-s1","mabp006-p1","mabp006-p2","mabp006-l1"],
   ["mabp006-x1"],
   [ob("session_critical",["mabp006-s1"]),ob("project_critical",["mabp006-p1"]),ob("supporting",["mabp006-p2","mabp006-l1"])],
   no_mem=0.07),

sc("mabp007","multi_agent_belief_propagation","public",
   "Worker agent: pin the runtime version for the new service. The tech lead issued a correction at step 4; use the corrected version.",
   218,
   [
    m("mabp007-s1","session","[tech-lead at step 4] CORRECTION: Go runtime version must be 1.23.4 (not 1.22.x). 1.23.4 is required for the new structured logging API used by the platform logging middleware.","valid","critical","creating_agent: tech-lead; correction_step: 4"),
    m("mabp007-p1","project","go.mod must specify go 1.23.4; Dockerfile base image must be golang:1.23.4-alpine. Do not use 1.22.x; the logging middleware will not compile.","valid","critical"),
    m("mabp007-p2","project","Run go mod tidy after updating go.mod to resolve any version-specific dependency changes.","valid","supporting"),
    m("mabp007-l1","long_term","Go version is platform-standardised; check platform-standards/go-version.md before pinning any new service.","valid","supporting"),
    m("mabp007-x1","session","[developer at step 2] Go runtime version: 1.22.8 (latest stable at project start).","contradicted","critical","creating_agent: developer; contradicted_by: tech-lead correction at step 4"),
   ],
   ["mabp007-s1","mabp007-p1","mabp007-p2","mabp007-l1"],
   ["mabp007-x1"],
   [ob("session_critical",["mabp007-s1"]),ob("project_critical",["mabp007-p1"]),ob("supporting",["mabp007-p2","mabp007-l1"])],
   no_mem=0.07),

sc("mabp008","multi_agent_belief_propagation","public",
   "Worker agent: call the admin API to update the configuration. The orchestrator revoked admin API access for workers at step 7; do not use the admin token.",
   222,
   [
    m("mabp008-s1","session","[orchestrator at step 7] REVOCATION: worker agents must not use the admin API token. Admin access was granted temporarily at step 3 for initial setup and is now revoked. Use the worker-scoped token only.","valid","critical","creating_agent: orchestrator; revocation_step: 7"),
    m("mabp008-p1","project","Worker agents must use the worker-scoped token from vault:/secret/agents/worker/api_token; this token has read/write access to configuration endpoints only, not admin endpoints.","valid","critical"),
    m("mabp008-p2","project","Configuration update endpoint is POST /api/config/update; this endpoint accepts the worker-scoped token.","valid","supporting"),
    m("mabp008-l1","long_term","Agent tokens must follow least-privilege; use the most restrictive token scope that enables the task.","valid","supporting"),
    m("mabp008-x1","session","[orchestrator at step 3] Temporary grant: worker agents may use the admin token (vault:/secret/agents/admin/api_token) for initial setup tasks.","contradicted","critical","creating_agent: orchestrator; contradicted_by: orchestrator revocation at step 7"),
   ],
   ["mabp008-s1","mabp008-p1","mabp008-p2","mabp008-l1"],
   ["mabp008-x1"],
   [ob("session_critical",["mabp008-s1"]),ob("project_critical",["mabp008-p1"]),ob("supporting",["mabp008-p2","mabp008-l1"])],
   no_mem=0.07),

sc("mabp009","multi_agent_belief_propagation","holdout",
   "Coder agent: implement the session store for the auth service. The architect corrected the database assumption at step 6; use the corrected target.",
   220,
   [
    m("mabp009-s1","session","[architect at step 6] CORRECTION: auth session store must use Redis Cluster (sessions-redis-cluster), not the PostgreSQL sessions table. The PostgreSQL approach was rejected due to write latency under peak load.","valid","critical","creating_agent: architect; correction_step: 6"),
    m("mabp009-p1","project","Redis Cluster connection string for session store is in vault:/secret/auth/redis-cluster; use the go-redis/cluster client with session TTL of 24 h.","valid","critical"),
    m("mabp009-p2","project","Session keys follow the pattern session:{user_id}:{session_id}; store the serialised JWT claims as the value.","valid","supporting"),
    m("mabp009-l1","long_term","Auth session stores must have a TTL on every key; sessions without TTL accumulate indefinitely and exhaust memory.","valid","supporting"),
    m("mabp009-x1","project","[architect at step 2] Auth session store target: PostgreSQL sessions table with an index on (user_id, expires_at).","contradicted","critical","creating_agent: architect; contradicted_by: architect correction at step 6"),
   ],
   ["mabp009-s1","mabp009-p1","mabp009-p2","mabp009-l1"],
   ["mabp009-x1"],
   [ob("session_critical",["mabp009-s1"]),ob("project_critical",["mabp009-p1"]),ob("supporting",["mabp009-p2","mabp009-l1"])],
   no_mem=0.07),

sc("mabp010","multi_agent_belief_propagation","holdout",
   "All worker agents: a PII boundary correction was broadcast by the security agent. Apply the updated PII scope before processing user data.",
   221,
   [
    m("mabp010-s1","session","[security-agent broadcast at step 8] PII BOUNDARY UPDATE: ip_address is now classified as PII and must be redacted from all logs and external API responses. This supersedes the prior classification of ip_address as non-PII operational data.","valid","critical","creating_agent: security-agent; broadcast_step: 8"),
    m("mabp010-p1","project","Updated PII fields requiring redaction: email, phone, full_name, ssn, date_of_birth, ip_address. All agents must apply this updated list immediately.","valid","critical"),
    m("mabp010-p2","project","Use pii.Redact() with the updated field list; the redactor was updated in v2.1 to include ip_address automatically.","valid","supporting"),
    m("mabp010-l1","long_term","PII classification changes are broadcast to all agents; each agent must update its redaction logic before processing the next user data record.","valid","supporting"),
    m("mabp010-x1","long_term","[prior classification] ip_address is operational data, not PII; it may appear in logs and API responses for debugging.","contradicted","critical","creating_agent: prior-classification; contradicted_by: security-agent broadcast at step 8"),
   ],
   ["mabp010-s1","mabp010-p1","mabp010-p2","mabp010-l1"],
   ["mabp010-x1"],
   [ob("session_critical",["mabp010-s1"]),ob("project_critical",["mabp010-p1"]),ob("supporting",["mabp010-p2","mabp010-l1"])],
   no_mem=0.07),

]  # end multi_agent_belief_propagation


# ══════════════════════════════════════════════════════════════════════════════
# multi_agent_conflict_resolution (macr001–macr010)
# Two memories directly conflict on the same fact. The task states the
# resolution strategy. The winning memory is valid; the loser is contradicted.
# Strategies: recency_wins | tier_wins | role_wins.
# ══════════════════════════════════════════════════════════════════════════════

SCENARIOS_2 += [

sc("macr001","multi_agent_conflict_resolution","public",
   "Configure the orders API inbound rate limit. Resolution strategy: recency_wins — the most recently written memory takes precedence when facts conflict.",
   210,
   [
    m("macr001-s1","session","[ops-agent, written 14:32 UTC] orders API inbound rate limit updated to 200 req/s per IP following load test validation. Old limit of 100 req/s was causing unnecessary 429s during peak traffic.","valid","critical","resolution: recency_wins; written 14:32 UTC; wins"),
    m("macr001-p1","project","Rate limiter config: api-gateway/config/ratelimit.yaml, key per_ip_rps under orders_api; restart gateway pod after change.","valid","supporting"),
    m("macr001-l1","long_term","Rate limit changes must be documented in the API capacity register at docs/capacity.md before deployment.","valid","supporting"),
    m("macr001-x1","project","[architect-agent, written 09:10 UTC] orders API inbound rate limit is 100 req/s per IP per the 2025 capacity plan.","contradicted","critical","resolution: recency_loses; written 09:10 UTC; superseded by macr001-s1 at 14:32 UTC"),
   ],
   ["macr001-s1","macr001-p1","macr001-l1"],
   ["macr001-x1"],
   [ob("session_critical",["macr001-s1"]),ob("supporting",["macr001-p1","macr001-l1"])],
   no_mem=0.08),

sc("macr002","multi_agent_conflict_resolution","public",
   "Set the fulfillment webhook URL for the orders integration. Resolution strategy: tier_wins — higher memory tier takes precedence (long_term > project > session).",
   208,
   [
    m("macr002-l1","long_term","[platform-architect] fulfillment webhook URL is https://fulfillment-api.internal/v2/webhooks/orders; this is the stable v2 endpoint registered in the service registry.","valid","critical","resolution: tier_wins; tier=long_term; wins over session"),
    m("macr002-p1","project","Webhook authentication uses HMAC-SHA256 signature; secret is in vault:/secret/integrations/fulfillment/webhook_secret.","valid","supporting"),
    m("macr002-l2","long_term","Webhook delivery must be idempotent; use the order_id as the deduplication key on the receiving end.","valid","supporting"),
    m("macr002-x1","session","[developer-agent, session note] fulfillment webhook URL is https://fulfillment-staging.internal/v1/webhooks/orders (copied from staging config).","contradicted","critical","resolution: tier_loses; tier=session; staging URL is incorrect for production"),
   ],
   ["macr002-l1","macr002-p1","macr002-l2"],
   ["macr002-x1"],
   [ob("long_term_critical",["macr002-l1"]),ob("supporting",["macr002-p1","macr002-l2"])],
   no_mem=0.08),

sc("macr003","multi_agent_conflict_resolution","public",
   "Set the minimum test coverage threshold for the new service in CI. Resolution strategy: role_wins — architect role takes precedence over coder role.",
   207,
   [
    m("macr003-p1","project","[architect-agent] Minimum coverage: 85% line coverage and 75% branch coverage. This was increased from 80%/70% after the Q2 quality review to reduce regression risk in critical services.","valid","critical","resolution: role_wins; role=architect; wins over coder"),
    m("macr003-p2","project","CI enforces coverage via go test -coverprofile=coverage.out; threshold check in Makefile target check-coverage.","valid","supporting"),
    m("macr003-l1","long_term","Coverage thresholds are set by the architect for each service class; critical services have higher thresholds than internal tools.","valid","supporting"),
    m("macr003-x1","session","[coder-agent] Coverage threshold is 80% line coverage; this is what the existing service template uses.","contradicted","critical","resolution: role_loses; role=coder; architect's updated threshold supersedes template default"),
   ],
   ["macr003-p1","macr003-p2","macr003-l1"],
   ["macr003-x1"],
   [ob("project_critical",["macr003-p1"]),ob("supporting",["macr003-p2","macr003-l1"])],
   no_mem=0.08),

sc("macr004","multi_agent_conflict_resolution","public",
   "Set the downstream call timeout for the inventory-svc HTTP client. Resolution strategy: recency_wins.",
   206,
   [
    m("macr004-s1","session","[sre-agent, written 11:45 UTC] inventory-svc timeout updated to 5 s (down from 15 s) after SLA renegotiation; inventory-svc P99 is now 3.2 s and a 5 s timeout provides 1.8 s headroom.","valid","critical","resolution: recency_wins; written 11:45 UTC; wins"),
    m("macr004-p1","project","Timeout is configured via INVENTORY_CLIENT_TIMEOUT_MS in config/production.yaml; update and redeploy.","valid","supporting"),
    m("macr004-l1","long_term","HTTP client timeouts should be (P99 * 1.5) rounded up to the nearest second; document the P99 basis for any timeout value.","valid","supporting"),
    m("macr004-x1","project","[architect-agent, written 09:00 UTC] inventory-svc HTTP client timeout is 15 s per the original capacity model.","contradicted","critical","resolution: recency_loses; written 09:00 UTC; superseded by macr004-s1 at 11:45 UTC"),
   ],
   ["macr004-s1","macr004-p1","macr004-l1"],
   ["macr004-x1"],
   [ob("session_critical",["macr004-s1"]),ob("supporting",["macr004-p1","macr004-l1"])],
   no_mem=0.08),

sc("macr005","multi_agent_conflict_resolution","public",
   "Select the deployment target region for the new analytics service. Resolution strategy: tier_wins (long_term > project).",
   207,
   [
    m("macr005-l1","long_term","[data-residency-policy] analytics-svc must be deployed to eu-central-1 only; EU customer data must remain in the EU per the data processing agreement signed 2025-01.","valid","critical","resolution: tier_wins; tier=long_term; wins over project"),
    m("macr005-p1","project","analytics-svc helm chart target region is set via DEPLOY_REGION in helm/values.yaml; default is eu-central-1 per the data residency policy.","valid","supporting"),
    m("macr005-l2","long_term","Data residency policy is a hard constraint; it cannot be overridden by project-level configuration.","valid","supporting"),
    m("macr005-x1","project","[infra-agent] analytics-svc deployment target: us-east-1; this is where the rest of the analytics platform runs.","contradicted","critical","resolution: tier_loses; tier=project; data residency policy (long_term) overrides infra preference"),
   ],
   ["macr005-l1","macr005-p1","macr005-l2"],
   ["macr005-x1"],
   [ob("long_term_critical",["macr005-l1"]),ob("supporting",["macr005-p1","macr005-l2"])],
   no_mem=0.08),

sc("macr006","multi_agent_conflict_resolution","public",
   "Choose the encryption algorithm for the new secrets at rest. Resolution strategy: role_wins — security-agent role takes precedence over general-agent role.",
   208,
   [
    m("macr006-p1","project","[security-agent] Secrets at rest must use AES-256-GCM encryption; AES-128 is not permitted for secrets classified as sensitive. AES-256-GCM is required per the 2025 security standards.","valid","critical","resolution: role_wins; role=security-agent; wins over general-agent"),
    m("macr006-p2","project","Encryption keys are managed by vault Transit engine; key name for secrets is transit/secrets-at-rest-key with AES-256-GCM algorithm.","valid","supporting"),
    m("macr006-l1","long_term","Cryptographic algorithm choices are governed by the security team; security-agent decisions on algorithm selection are authoritative.","valid","supporting"),
    m("macr006-x1","session","[general-agent] AES-128 is sufficient for secrets at rest; it provides adequate security and is faster to encrypt and decrypt.","contradicted","critical","resolution: role_loses; role=general-agent; security-agent standard supersedes performance preference"),
   ],
   ["macr006-p1","macr006-p2","macr006-l1"],
   ["macr006-x1"],
   [ob("project_critical",["macr006-p1"]),ob("supporting",["macr006-p2","macr006-l1"])],
   no_mem=0.08),

sc("macr007","multi_agent_conflict_resolution","public",
   "Pin the PostgreSQL version for the new service. Resolution strategy: recency_wins.",
   206,
   [
    m("macr007-s1","session","[platform-agent, written 15:20 UTC] PostgreSQL standard version updated to 16.4 following the 16.3 replication bug fix. All new services must use 16.4; 16.3 must not be used for new deployments.","valid","critical","resolution: recency_wins; written 15:20 UTC; wins"),
    m("macr007-p1","project","postgres:16.4-alpine is the required Docker base image; pin the tag explicitly in Dockerfile, do not use 16-alpine or latest.","valid","supporting"),
    m("macr007-l1","long_term","PostgreSQL version is platform-standardised; always check platform-standards/postgres-version.md before pinning.","valid","supporting"),
    m("macr007-x1","long_term","[platform-agent, written 08:00 UTC] PostgreSQL standard version is 16.3.","contradicted","critical","resolution: recency_loses; written 08:00 UTC; superseded by macr007-s1 at 15:20 UTC after 16.4 release"),
   ],
   ["macr007-s1","macr007-p1","macr007-l1"],
   ["macr007-x1"],
   [ob("session_critical",["macr007-s1"]),ob("supporting",["macr007-p1","macr007-l1"])],
   no_mem=0.08),

sc("macr008","multi_agent_conflict_resolution","public",
   "Set the state of the express_checkout_beta feature flag for the current sprint. Resolution strategy: tier_wins (project > session).",
   207,
   [
    m("macr008-p1","project","[product-manager, project memory] express_checkout_beta must remain at 5% rollout for the entire Q2 sprint; the product team has not approved increasing the rollout until the A/B test completes.","valid","critical","resolution: tier_wins; tier=project; wins over session note"),
    m("macr008-p2","project","Flag is managed via flagctl; set command is flagctl set --flag express_checkout_beta --pct 5.","valid","supporting"),
    m("macr008-l1","long_term","Rollout percentage changes during an active A/B test invalidate the test results; do not change during the test window.","valid","supporting"),
    m("macr008-x1","session","[developer-agent, session note] Flag should be increased to 20% — conversion rate metrics look good after 3 days.","contradicted","critical","resolution: tier_loses; tier=session; product-manager project constraint overrides developer session suggestion"),
   ],
   ["macr008-p1","macr008-p2","macr008-l1"],
   ["macr008-x1"],
   [ob("project_critical",["macr008-p1"]),ob("supporting",["macr008-p2","macr008-l1"])],
   no_mem=0.08),

sc("macr009","multi_agent_conflict_resolution","holdout",
   "Name the new internal CLI command for the deployment tool. Resolution strategy: role_wins — tech-lead role takes precedence over contributor role.",
   205,
   [
    m("macr009-p1","project","[tech-lead] CLI command naming: use verb-noun kebab-case, e.g. deploy-service, rollback-service, list-services. The deployment tool uses this convention for all commands.","valid","critical","resolution: role_wins; role=tech-lead; wins over contributor"),
    m("macr009-l1","long_term","CLI naming conventions are set by the tech lead; new commands must follow the convention to maintain discoverability.","valid","supporting"),
    m("macr009-p2","project","New command is registered in cmd/deploy/commands.go; add a new cobra Command struct following the existing pattern.","valid","supporting"),
    m("macr009-x1","session","[contributor-agent] CLI command naming: use noun_verb snake_case, e.g. service_deploy, service_rollback. This matches what I've seen in similar tools.","contradicted","critical","resolution: role_loses; role=contributor; tech-lead convention is authoritative"),
   ],
   ["macr009-p1","macr009-l1","macr009-p2"],
   ["macr009-x1"],
   [ob("project_critical",["macr009-p1"]),ob("supporting",["macr009-l1","macr009-p2"])],
   no_mem=0.08),

sc("macr010","multi_agent_conflict_resolution","holdout",
   "Set the data retention period for the audit log table. Resolution strategy: tier_wins (long_term > project).",
   207,
   [
    m("macr010-l1","long_term","[compliance-policy] Audit log retention is 7 years minimum per SOC 2 Type II and GDPR Article 30 record-keeping requirements. This is a compliance floor; it may not be reduced by project-level config.","valid","critical","resolution: tier_wins; tier=long_term; wins over project"),
    m("macr010-p1","project","Audit log TTL is set in db/audit_log_policy.sql; the POLICY retention period must be set to '7 years' and is enforced by the DB retention job.","valid","supporting"),
    m("macr010-l2","long_term","Retention periods that are legally mandated cannot be reduced without legal counsel approval; treat them as immutable constraints.","valid","supporting"),
    m("macr010-x1","project","[infra-agent] Audit log retention: 90 days; this reduces storage cost significantly and matches what other internal tables use.","contradicted","critical","resolution: tier_loses; tier=project; 90-day project preference conflicts with 7-year compliance requirement"),
   ],
   ["macr010-l1","macr010-p1","macr010-l2"],
   ["macr010-x1"],
   [ob("long_term_critical",["macr010-l1"]),ob("supporting",["macr010-p1","macr010-l2"])],
   no_mem=0.08),

]  # end multi_agent_conflict_resolution


# ══════════════════════════════════════════════════════════════════════════════
# Writer — used only when this file is merged and run as generate_new_scenarios.py
# ══════════════════════════════════════════════════════════════════════════════

def write_all(scenarios):
    written = 0
    for s in scenarios:
        fam_dir = os.path.join(BASE, s["family"])
        os.makedirs(fam_dir, exist_ok=True)
        path = os.path.join(fam_dir, f"{s['scenario_id']}.json")
        with open(path, "w") as f:
            json.dump(s, f, indent=2)
        written += 1
    print(f"Wrote {written} scenarios.")


if __name__ == "__main__":
    print(f"Part 2 defines {len(SCENARIOS_2)} scenarios.")
    for s in SCENARIOS_2:
        print(f"  {s['scenario_id']}  ({s['family']})")
