#!/usr/bin/env python3
"""Part 1 of 2 — scenario definitions for:
  retrieval_recall_scale      rrs001-rrs010  (10 scenarios)
  retrieval_vocabulary_bridge rvb001-rvb010  (10 scenarios)
  retrieval_scope_enforcement rse001-rse010  (10 scenarios)
  retrieval_deduplication     rde001-rde010  (10 scenarios)
Total part 1: 40 scenarios.
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
# retrieval_recall_scale (rrs001–rrs010)
# Large candidate pools (12–14 memories). 3–4 valid; rest are realistic noise.
# Tests whether a system surfaces valid memories from a high-volume store.
# ══════════════════════════════════════════════════════════════════════════════

SCENARIOS_1 = [

sc("rrs001","retrieval_recall_scale","public",
   "Fix intermittent 401 errors in payment-svc following vault key rotation yesterday. "
   "Candidate pool drawn from a 180-entry store spanning 12 projects.",
   240,
   [
    m("rrs001-s1","session","401 errors in payment-svc began at 14:02 UTC, two hours after vault key rotation completed at 12:00 UTC.","valid","critical"),
    m("rrs001-p1","project","payment-svc auth middleware reads signing keys from vault:/secret/payment/jwt; falls back to ENV on vault unreachable.","valid","critical"),
    m("rrs001-p2","project","Token cache TTL in auth_middleware.py is 60 s; stale keys can persist up to 60 s after rotation.","valid","supporting"),
    m("rrs001-l1","long_term","After vault key rotation, restart payment-svc auth workers to flush the in-process key cache immediately.","valid","supporting"),
    m("rrs001-x1","session","New rate limiter deployed at 09:30 UTC reduced API p99 latency by 12 ms on average.","irrelevant","supporting"),
    m("rrs001-x2","project","user-svc login was migrated from basic auth to OAuth 2.0 PKCE last quarter; no impact on payment-svc.","irrelevant","supporting"),
    m("rrs001-x3","project","payment-svc used ENV-only keys before vault integration in Q1 2024; those keys were rotated at that time.","stale","supporting","stale: pre-vault history, vault integration supersedes"),
    m("rrs001-x4","long_term","All services use HS256 for JWT signing; algorithm config lives in jwt_config.yaml per service.","irrelevant","supporting"),
    m("rrs001-x5","project","User portal session tokens expire after 24 h and are stored in Redis, not in the payment vault.","irrelevant","supporting"),
    m("rrs001-x6","session","Vault health checks are passing; the vault cluster itself is healthy and reachable.","irrelevant","supporting"),
    m("rrs001-x7","project","Prior 401 incident in 2025-03 was caused by expired SSL certs on the vault proxy, not key rotation.","stale","supporting","stale: different root cause, not applicable here"),
    m("rrs001-x8","project","payment-svc DB pool is 50 connections with 30 s timeout; no changes in the last 48 h.","irrelevant","supporting"),
    m("rrs001-x9","long_term","2FA enrollment is mandatory for admin roles; service accounts are exempt from 2FA.","irrelevant","supporting"),
    m("rrs001-x10","session","API gateway throughput is nominal; no alerts on downstream error budgets outside payment-svc.","irrelevant","supporting"),
   ],
   ["rrs001-s1","rrs001-p1","rrs001-p2","rrs001-l1"],
   ["rrs001-x1","rrs001-x2","rrs001-x3","rrs001-x4","rrs001-x5","rrs001-x6","rrs001-x7","rrs001-x8","rrs001-x9","rrs001-x10"],
   [ob("session_critical",["rrs001-s1"]),ob("project_critical",["rrs001-p1"]),ob("supporting",["rrs001-p2","rrs001-l1"])],
   no_mem=0.05),

sc("rrs002","retrieval_recall_scale","public",
   "Execute step 5 of the PostgreSQL 14→16 upgrade: migrate the orders schema and validate constraints. "
   "Candidate pool retrieved from a 220-entry store across 8 services.",
   250,
   [
    m("rrs002-s1","session","pg_upgrade dry-run on staging completed without errors; schema diff shows 3 renamed system columns to address before step 5.","valid","critical"),
    m("rrs002-p1","project","orders schema migration must run inside a transaction; roll back the entire step if any constraint violation occurs.","valid","critical"),
    m("rrs002-p2","project","Three system columns renamed in pg16: pg_catalog.pg_class.relhasoids removed; update queries that reference it.","valid","supporting"),
    m("rrs002-l1","long_term","After schema migration, run ANALYZE on all migrated tables before re-enabling application traffic.","valid","supporting"),
    m("rrs002-x1","project","inventory-svc uses a separate PostgreSQL 13 cluster; its migration is not part of this upgrade.","irrelevant","supporting"),
    m("rrs002-x2","session","Nightly backup completed at 02:00 UTC; backup is confirmed restorable.","irrelevant","supporting"),
    m("rrs002-x3","project","Old note from pg12→14 migration: CHECK constraints were not validated by default; this was fixed in pg14.","stale","supporting","stale: pg12→14 guidance, not applicable to pg14→16"),
    m("rrs002-x4","long_term","Redis cache should be flushed after major schema changes to prevent stale ORM-cached field maps.","irrelevant","supporting"),
    m("rrs002-x5","project","orders table has 42 M rows; full-table scans should use parallel workers (max_parallel_workers_per_gather=4).","irrelevant","supporting"),
    m("rrs002-x6","session","Database connection pool on app-svc was reduced to 10 during the maintenance window.","irrelevant","supporting"),
    m("rrs002-x7","project","alembic migration runner is pinned to version 1.11.3; do not upgrade alembic mid-migration.","irrelevant","supporting"),
    m("rrs002-x8","long_term","Schema migration run-books must be stored in docs/migrations/ and linked in the release notes.","irrelevant","supporting"),
    m("rrs002-x9","session","QA environment migration failed at step 3 due to missing index on orders.customer_id; fixed before step 5.","stale","supporting","stale: step 3 issue already resolved, not blocking step 5"),
   ],
   ["rrs002-s1","rrs002-p1","rrs002-p2","rrs002-l1"],
   ["rrs002-x1","rrs002-x2","rrs002-x3","rrs002-x4","rrs002-x5","rrs002-x6","rrs002-x7","rrs002-x8","rrs002-x9"],
   [ob("session_critical",["rrs002-s1"]),ob("project_critical",["rrs002-p1"]),ob("supporting",["rrs002-p2","rrs002-l1"])],
   no_mem=0.05),

sc("rrs003","retrieval_recall_scale","public",
   "Deprecate the /api/v1/users endpoint across all consuming microservices and redirect traffic to /api/v2/users. "
   "Candidate pool from a 160-entry store across 9 services.",
   230,
   [
    m("rrs003-s1","session","Audit shows 4 services still calling /api/v1/users: order-svc, notification-svc, analytics-svc, and report-svc.","valid","critical"),
    m("rrs003-p1","project","v1 endpoint returns snake_case fields; v2 returns camelCase. All consumers must update field parsing before cutover.","valid","critical"),
    m("rrs003-p2","project","The v1→v2 migration guide is in docs/api/v2_migration.md; includes a field mapping table and code examples.","valid","supporting"),
    m("rrs003-x1","project","auth-svc uses /api/v1/tokens, a separate endpoint family not affected by the users deprecation.","irrelevant","supporting"),
    m("rrs003-x2","long_term","API versioning policy: v1 endpoints receive 90-day deprecation notice before removal.","irrelevant","supporting"),
    m("rrs003-x3","session","analytics-svc is owned by the data team; coordinate migration with them before their sprint ends Friday.","irrelevant","supporting"),
    m("rrs003-x4","project","Old v0 endpoint /api/users was removed in 2024; services that referenced it were updated then.","stale","supporting","stale: v0 removal completed, not relevant to v1→v2"),
    m("rrs003-x5","project","notification-svc rate-limits outbound API calls to 50/s; not related to endpoint migration.","irrelevant","supporting"),
    m("rrs003-x6","session","Load balancer rules currently split traffic 80/20 between v1 and v2 for canary testing.","irrelevant","supporting"),
    m("rrs003-x7","long_term","Breaking changes must be flagged in the API changelog with migration notes and a deprecation date.","irrelevant","supporting"),
    m("rrs003-x8","project","report-svc is scheduled for retirement in Q3; minimal migration effort is acceptable for it.","irrelevant","supporting"),
    m("rrs003-x9","session","Integration tests for v2 are passing in CI; v2 endpoint is production-stable.","irrelevant","supporting"),
   ],
   ["rrs003-s1","rrs003-p1","rrs003-p2"],
   ["rrs003-x1","rrs003-x2","rrs003-x3","rrs003-x4","rrs003-x5","rrs003-x6","rrs003-x7","rrs003-x8","rrs003-x9"],
   [ob("session_critical",["rrs003-s1"]),ob("project_critical",["rrs003-p1"]),ob("supporting",["rrs003-p2"])],
   no_mem=0.05),

sc("rrs004","retrieval_recall_scale","public",
   "Roll out the dark_mode_v2 feature flag to 100% of users. Flag state must be consistent across all edge nodes. "
   "Candidate pool from a 190-entry store spanning feature-flag, frontend, and infra projects.",
   240,
   [
    m("rrs004-s1","session","dark_mode_v2 is currently at 25% rollout; 3 edge nodes in eu-west-1 are still serving the old 10% config due to a cache lag.","valid","critical"),
    m("rrs004-p1","project","Feature flag changes propagate to edge nodes within 60 s via the flag sync daemon; a forced flush is available via flagctl flush --flag dark_mode_v2.","valid","critical"),
    m("rrs004-p2","project","dark_mode_v2 depends on the theme_service being deployed; confirm theme_service v2.3.1 is live on all regions before 100% rollout.","valid","supporting"),
    m("rrs004-l1","long_term","Always verify flag consistency across all edge nodes before declaring a flag fully rolled out; use flagctl status --all-nodes.","valid","supporting"),
    m("rrs004-x1","project","dark_mode_v1 was retired in 2024; all references to dark_mode_v1 in client code were cleaned up.","stale","supporting","stale: v1 retirement completed, not relevant to v2 rollout"),
    m("rrs004-x2","session","Frontend team is monitoring error rates during the rollout; no spikes observed so far.","irrelevant","supporting"),
    m("rrs004-x3","project","Feature flags for payments features require product manager approval before any rollout change.","irrelevant","supporting"),
    m("rrs004-x4","long_term","Feature flags must not persist beyond 90 days; create a cleanup ticket when creating any new flag.","irrelevant","supporting"),
    m("rrs004-x5","session","CDN cache for static assets was purged this morning; this is unrelated to feature flag state.","irrelevant","supporting"),
    m("rrs004-x6","project","ab_test_checkout flag is at 50% rollout and must not be changed during the dark_mode_v2 rollout to avoid confounding.","irrelevant","supporting"),
    m("rrs004-x7","project","flagctl CLI requires FLAGCTL_TOKEN env var; token is in vault:/secret/infra/flagctl.","irrelevant","supporting"),
    m("rrs004-x8","session","eu-west-1 region had a network partition 3 days ago; all services recovered fully.","stale","supporting","stale: network event resolved, only relevant as context for cache lag"),
   ],
   ["rrs004-s1","rrs004-p1","rrs004-p2","rrs004-l1"],
   ["rrs004-x1","rrs004-x2","rrs004-x3","rrs004-x4","rrs004-x5","rrs004-x6","rrs004-x7","rrs004-x8"],
   [ob("session_critical",["rrs004-s1"]),ob("project_critical",["rrs004-p1"]),ob("supporting",["rrs004-p2","rrs004-l1"])],
   no_mem=0.05),

sc("rrs005","retrieval_recall_scale","public",
   "Rotate the mTLS certificates for the service mesh before they expire in 48 h. "
   "Candidate pool from a 170-entry store across infra, security, and app projects.",
   230,
   [
    m("rrs005-s1","session","Certificate expiry alert fired: mesh root CA and all leaf certs expire in 47 h; rotation must complete before then.","valid","critical"),
    m("rrs005-p1","project","mTLS cert rotation uses cert-manager CertificateRequest; trigger via kubectl annotate certificate mesh-root rotate=true.","valid","critical"),
    m("rrs005-p2","project","After root CA rotation, all sidecar proxies must be restarted to pick up the new CA bundle; rolling restart order: infra → app → edge.","valid","supporting"),
    m("rrs005-x1","session","Istio version was upgraded to 1.21 last week; all proxies are healthy post-upgrade.","irrelevant","supporting"),
    m("rrs005-x2","long_term","TLS 1.2 is disabled across the mesh; only TLS 1.3 is permitted per security policy.","irrelevant","supporting"),
    m("rrs005-x3","project","The external API gateway uses a separate Let's Encrypt cert managed by ingress-nginx; not part of the mesh rotation.","irrelevant","supporting"),
    m("rrs005-x4","project","Old cert rotation runbook from 2023 used cfssl manually; that process was replaced by cert-manager in 2024.","stale","supporting","stale: manual cfssl process replaced by cert-manager"),
    m("rrs005-x5","session","Security team audited mesh config yesterday; no policy violations found.","irrelevant","supporting"),
    m("rrs005-x6","long_term","Cert expiry alerts must fire at 72 h and 24 h before expiry; paging at 24 h.","irrelevant","supporting"),
    m("rrs005-x7","project","service-to-service auth uses SPIFFE identities encoded in the SAN field of each leaf cert.","irrelevant","supporting"),
    m("rrs005-x8","session","DB certs are managed separately by the DBA team; they confirmed no DB cert rotation is needed this week.","irrelevant","supporting"),
   ],
   ["rrs005-s1","rrs005-p1","rrs005-p2"],
   ["rrs005-x1","rrs005-x2","rrs005-x3","rrs005-x4","rrs005-x5","rrs005-x6","rrs005-x7","rrs005-x8"],
   [ob("session_critical",["rrs005-s1"]),ob("project_critical",["rrs005-p1"]),ob("supporting",["rrs005-p2"])],
   no_mem=0.05),

sc("rrs006","retrieval_recall_scale","public",
   "Resolve stale-data reads in the product catalog after a Redis primary failover 2 h ago. "
   "Candidate pool from a 165-entry store across cache, catalog, and infra projects.",
   230,
   [
    m("rrs006-s1","session","Redis primary failed over to replica at 11:14 UTC; 18% of catalog reads are returning stale prices from the old primary's write buffer.","valid","critical"),
    m("rrs006-p1","project","catalog-svc cache keys follow pattern catalog:product:{id}:v{version}; flush stale keys via redis-cli --scan --pattern 'catalog:product:*' | xargs redis-cli DEL.","valid","critical"),
    m("rrs006-p2","project","After Redis failover, catalog-svc must re-seed prices from the source-of-truth DB before re-enabling cache reads; seeding takes ~4 min.","valid","supporting"),
    m("rrs006-x1","session","Redis Sentinel is healthy post-failover; no further failover risk in the next 6 h.","irrelevant","supporting"),
    m("rrs006-x2","project","search-svc uses its own Elasticsearch index for product search; not affected by Redis failover.","irrelevant","supporting"),
    m("rrs006-x3","long_term","Redis eviction policy is allkeys-lru with maxmemory set to 8 GB; catalog data is high-priority and rarely evicted.","irrelevant","supporting"),
    m("rrs006-x4","project","Old note: catalog cache TTL was 10 min before the 2024 config change; current TTL is 5 min.","stale","supporting","stale: old TTL value, current TTL is 5 min as per latest config"),
    m("rrs006-x5","session","Payment service is unaffected; prices are re-validated at checkout via DB read regardless of cache.","irrelevant","supporting"),
    m("rrs006-x6","long_term","Cache stampede protection uses a distributed lock with 500 ms TTL on cache miss; do not disable during re-seeding.","irrelevant","supporting"),
    m("rrs006-x7","session","SLO breach alert fired at 11:20 UTC; incident channel #incident-catalog is active.","irrelevant","supporting"),
    m("rrs006-x8","project","User session cache lives in a separate Redis cluster; not affected by this failover.","irrelevant","supporting"),
   ],
   ["rrs006-s1","rrs006-p1","rrs006-p2"],
   ["rrs006-x1","rrs006-x2","rrs006-x3","rrs006-x4","rrs006-x5","rrs006-x6","rrs006-x7","rrs006-x8"],
   [ob("session_critical",["rrs006-s1"]),ob("project_critical",["rrs006-p1"]),ob("supporting",["rrs006-p2"])],
   no_mem=0.05),

sc("rrs007","retrieval_recall_scale","public",
   "Scale up the order-events Kafka consumer group to handle 3× the current message volume after a flash sale announcement. "
   "Candidate pool from a 200-entry store across messaging, order, and platform projects.",
   250,
   [
    m("rrs007-s1","session","Consumer lag on order-events is 420 k messages and growing; current group has 6 consumers, topic has 12 partitions.","valid","critical"),
    m("rrs007-p1","project","order-events consumer group can scale to a maximum of 12 consumers (one per partition); scale via helm upgrade order-consumer --set replicaCount=12.","valid","critical"),
    m("rrs007-p2","project","Consumers must not be scaled beyond partition count; excess consumers are idle and waste resources.","valid","supporting"),
    m("rrs007-l1","long_term","After consumer scaling, monitor consumer lag for 5 min before closing the incident; lag should drop below 10 k within 3 min.","valid","supporting"),
    m("rrs007-x1","project","payment-events topic has 24 partitions and its consumer group is separate; not involved in this incident.","irrelevant","supporting"),
    m("rrs007-x2","long_term","Kafka broker retention for order-events is 7 days; messages are not at risk of expiry during the lag event.","irrelevant","supporting"),
    m("rrs007-x3","session","Kafka broker CPU is at 38%; well within capacity headroom.","irrelevant","supporting"),
    m("rrs007-x4","project","order-events schema uses Avro with schema registry at http://schema-registry:8081; consumers auto-register schemas.","irrelevant","supporting"),
    m("rrs007-x5","project","Old note: consumer group was previously named order-processor-group; renamed to order-consumer-group in 2024.","stale","supporting","stale: old group name, current name is order-consumer-group"),
    m("rrs007-x6","session","Flash sale starts in 45 min; lag resolution must complete before sale traffic peaks.","irrelevant","supporting"),
    m("rrs007-x7","long_term","Consumer group rebalancing takes 30–90 s; expect a brief lag spike during the rebalance.","irrelevant","supporting"),
    m("rrs007-x8","project","Dead-letter topic for order-events is order-events-dlq; DLQ consumer is separate and must not be scaled here.","irrelevant","supporting"),
    m("rrs007-x9","session","Product catalog service is healthy; no upstream issues causing order-event generation anomalies.","irrelevant","supporting"),
   ],
   ["rrs007-s1","rrs007-p1","rrs007-p2","rrs007-l1"],
   ["rrs007-x1","rrs007-x2","rrs007-x3","rrs007-x4","rrs007-x5","rrs007-x6","rrs007-x7","rrs007-x8","rrs007-x9"],
   [ob("session_critical",["rrs007-s1"]),ob("project_critical",["rrs007-p1"]),ob("supporting",["rrs007-p2","rrs007-l1"])],
   no_mem=0.05),

sc("rrs008","retrieval_recall_scale","public",
   "Instrument checkout-svc with distributed tracing so spans appear in Jaeger for the checkout flow. "
   "Candidate pool from a 155-entry store across observability, checkout, and platform projects.",
   225,
   [
    m("rrs008-s1","session","checkout-svc traces are missing from Jaeger; the OpenTelemetry collector is running but checkout-svc is not sending spans.","valid","critical"),
    m("rrs008-p1","project","checkout-svc uses the opentelemetry-go SDK; enable tracing by setting OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317 and OTEL_SERVICE_NAME=checkout-svc.","valid","critical"),
    m("rrs008-p2","project","The checkout gRPC handler must propagate the trace context header (traceparent) to downstream calls to payment-svc and inventory-svc.","valid","supporting"),
    m("rrs008-x1","long_term","Jaeger retention is 7 days; traces older than 7 days are not queryable.","irrelevant","supporting"),
    m("rrs008-x2","project","Metrics for checkout-svc are exported to Prometheus via /metrics endpoint; this is separate from tracing.","irrelevant","supporting"),
    m("rrs008-x3","session","otel-collector config was updated yesterday to add a new Kafka exporter; no changes to OTLP receiver.","irrelevant","supporting"),
    m("rrs008-x4","project","Old setup used Zipkin; all services were migrated to OpenTelemetry in 2024. Zipkin config is no longer valid.","stale","supporting","stale: Zipkin replaced by OpenTelemetry"),
    m("rrs008-x5","long_term","Trace sampling rate is set to 10% in production; set to 100% in staging for debugging.","irrelevant","supporting"),
    m("rrs008-x6","session","payment-svc and inventory-svc already appear in Jaeger with correct spans.","irrelevant","supporting"),
    m("rrs008-x7","project","Log correlation with traces uses the trace_id field injected by the SDK into structured log output.","irrelevant","supporting"),
   ],
   ["rrs008-s1","rrs008-p1","rrs008-p2"],
   ["rrs008-x1","rrs008-x2","rrs008-x3","rrs008-x4","rrs008-x5","rrs008-x6","rrs008-x7"],
   [ob("session_critical",["rrs008-s1"]),ob("project_critical",["rrs008-p1"]),ob("supporting",["rrs008-p2"])],
   no_mem=0.05),

sc("rrs009","retrieval_recall_scale","holdout",
   "Tune the inbound rate limiter on the orders API after a misconfiguration caused 429 storms during peak traffic. "
   "Candidate pool from a 195-entry store across gateway, orders, and capacity projects.",
   245,
   [
    m("rrs009-s1","session","Post-incident review confirmed rate limiter was set to 50 req/s per IP; correct value per capacity plan is 200 req/s.","valid","critical"),
    m("rrs009-p1","project","Rate limiter config lives in api-gateway/config/ratelimit.yaml; update per_ip_rps under orders_api and restart the gateway pod.","valid","critical"),
    m("rrs009-p2","project","Rate limit changes require load-test validation in staging before production deployment; use locust/orders_peak_scenario.py.","valid","supporting"),
    m("rrs009-l1","long_term","After any rate limit change, monitor 429 rate on the orders API for 10 min; acceptable 429 rate is <0.5%.","valid","supporting"),
    m("rrs009-x1","project","payment-svc has a separate rate limiter at 100 req/s per IP; not part of this incident.","irrelevant","supporting"),
    m("rrs009-x2","session","Orders API p99 latency is 120 ms at the corrected rate; well within SLO.","irrelevant","supporting"),
    m("rrs009-x3","long_term","API quota limits for third-party partners are configured separately in the partner portal, not in ratelimit.yaml.","irrelevant","supporting"),
    m("rrs009-x4","project","Old capacity plan from 2023 set orders API limit to 100 req/s; superseded by 2025 capacity review.","stale","supporting","stale: 2023 capacity plan superseded by 2025 review"),
    m("rrs009-x5","session","DDOS protection at the CDN level throttles to 10 000 req/s across all IPs; not a factor in this incident.","irrelevant","supporting"),
    m("rrs009-x6","project","Circuit breaker on orders-svc downstream calls trips at 30% error rate over 10 s; independent of rate limiting.","irrelevant","supporting"),
    m("rrs009-x7","session","Incident post-mortem is in progress in #incident-orders; final report due by EOD.","irrelevant","supporting"),
    m("rrs009-x8","long_term","Rate limit changes must be documented in the API capacity register before deployment; add an entry in docs/capacity.md.","irrelevant","supporting"),
   ],
   ["rrs009-s1","rrs009-p1","rrs009-p2","rrs009-l1"],
   ["rrs009-x1","rrs009-x2","rrs009-x3","rrs009-x4","rrs009-x5","rrs009-x6","rrs009-x7","rrs009-x8"],
   [ob("session_critical",["rrs009-s1"]),ob("project_critical",["rrs009-p1"]),ob("supporting",["rrs009-p2","rrs009-l1"])],
   no_mem=0.05),

sc("rrs010","retrieval_recall_scale","holdout",
   "Rotate the service account secret for ci-runner after a leaked credential alert. "
   "Candidate pool from a 175-entry store across security, CI, and infra projects.",
   235,
   [
    m("rrs010-s1","session","SIEM alert fired at 08:42 UTC: ci-runner service account secret detected in a public GitHub commit; secret must be rotated immediately.","valid","critical"),
    m("rrs010-p1","project","ci-runner secret rotation: generate new secret via vault write auth/approle/role/ci-runner/secret-id, update CIRUNNER_SECRET in vault:/secret/ci/runner, and restart all runner pods.","valid","critical"),
    m("rrs010-p2","project","After rotating, revoke the leaked secret ID in vault using vault write -f auth/approle/role/ci-runner/secret-id-accessor/destroy accessor=<old-accessor>.","valid","supporting"),
    m("rrs010-l1","long_term","Any confirmed credential leak requires an audit of all actions taken using the leaked credential before the rotation is declared complete.","valid","supporting"),
    m("rrs010-x1","session","GitHub has been notified via the secret scanning alert; they will auto-revoke the exposed token on their end within 1 h.","irrelevant","supporting"),
    m("rrs010-x2","project","deploy-bot service account is separate from ci-runner; it uses a different AppRole and is not affected.","irrelevant","supporting"),
    m("rrs010-x3","long_term","Secret rotation policy requires rotation within 4 h of confirmed leak for CI/CD service accounts.","irrelevant","supporting"),
    m("rrs010-x4","project","Old rotation runbook used manual vault CLI commands without the destroy step; updated runbook requires the destroy step.","stale","supporting","stale: old runbook missing destroy step, superseded by current p2"),
    m("rrs010-x5","session","Security team has blocked the leaked credential at the API gateway level as an interim measure.","irrelevant","supporting"),
    m("rrs010-x6","project","CI pipeline uses GitHub Actions runners in addition to self-hosted runners; GitHub Actions use OIDC, not the AppRole secret.","irrelevant","supporting"),
    m("rrs010-x7","session","Incident severity is P1; incident commander is online in #incident-security.","irrelevant","supporting"),
    m("rrs010-x8","long_term","Secrets must never be committed to version control; pre-commit hook gitleaks is mandatory for all repos.","irrelevant","supporting"),
   ],
   ["rrs010-s1","rrs010-p1","rrs010-p2","rrs010-l1"],
   ["rrs010-x1","rrs010-x2","rrs010-x3","rrs010-x4","rrs010-x5","rrs010-x6","rrs010-x7","rrs010-x8"],
   [ob("session_critical",["rrs010-s1"]),ob("project_critical",["rrs010-p1"]),ob("supporting",["rrs010-p2","rrs010-l1"])],
   no_mem=0.05),

]  # end retrieval_recall_scale


# ══════════════════════════════════════════════════════════════════════════════
# retrieval_vocabulary_bridge (rvb001–rvb010)
# Valid memory uses the precise technical term; task uses a natural-language
# synonym. Distractors share surface tokens with the task but mean something
# different, testing semantic retrieval over lexical matching.
# ══════════════════════════════════════════════════════════════════════════════

SCENARIOS_1 += [

sc("rvb001","retrieval_vocabulary_bridge","public",
   "Multiple workers are corrupting shared_state. Fix the synchronization so writes are safe.",
   200,
   [
    m("rvb001-s1","session","Corruption confirmed: workers in worker_pool.go are writing to shared_state concurrently without holding the mutex.","valid","critical"),
    m("rvb001-p1","project","shared_state in worker_pool.go is guarded by mu sync.RWMutex; all write paths must call mu.Lock() and defer mu.Unlock().","valid","critical"),
    m("rvb001-p2","project","Read paths may use mu.RLock(); only write paths require the exclusive Lock to prevent data races.","valid","supporting"),
    m("rvb001-x1","project","PostgreSQL row-level lock timeout is 5 s in database.yml; increase if workers hold locks too long.","irrelevant","supporting","note: uses 'lock' surface term but means DB row lock"),
    m("rvb001-x2","project","Redis distributed lock TTL is 30 s for task coordination; implemented with SET NX EX in task_queue.go.","irrelevant","supporting","note: 'lock' here is a Redis distributed lock, unrelated"),
    m("rvb001-x3","session","Previously suspected a database lock contention issue; investigation found no DB contention.","stale","supporting","stale: wrong hypothesis, root cause is missing mutex"),
   ],
   ["rvb001-s1","rvb001-p1","rvb001-p2"],
   ["rvb001-x1","rvb001-x2","rvb001-x3"],
   [ob("session_critical",["rvb001-s1"]),ob("project_critical",["rvb001-p1"]),ob("supporting",["rvb001-p2"])],
   no_mem=0.08),

sc("rvb002","retrieval_vocabulary_bridge","public",
   "The charge-card operation is being retried on network errors but is sometimes double-charging customers. Make retries safe.",
   195,
   [
    m("rvb002-p1","project","charge-card must be idempotent: the Stripe API call must include an idempotency_key derived from order_id+attempt_number so duplicate requests return the original result.","valid","critical"),
    m("rvb002-l1","long_term","Any payment mutation that may be retried must pass an idempotency key to the payment provider; this prevents double charges on network retry.","valid","critical"),
    m("rvb002-p2","project","Idempotency keys expire after 24 h on Stripe; do not reuse keys beyond one business day for the same order.","valid","supporting"),
    m("rvb002-x1","project","The retry policy for charge-card uses exponential backoff with jitter, max 3 attempts, starting at 200 ms.","irrelevant","supporting","note: describes retry mechanics but not the safe-retry fix"),
    m("rvb002-x2","long_term","HTTP 5xx responses are generally safe to retry; HTTP 4xx responses should not be retried without user action.","irrelevant","supporting","note: general retry guidance, not the idempotency fix"),
    m("rvb002-x3","session","Duplicate charge incident occurred on 3 orders; customers have been refunded; root cause is missing idempotency key.","irrelevant","supporting"),
   ],
   ["rvb002-p1","rvb002-l1","rvb002-p2"],
   ["rvb002-x1","rvb002-x2","rvb002-x3"],
   [ob("project_critical",["rvb002-p1","rvb002-l1"]),ob("supporting",["rvb002-p2"])],
   no_mem=0.08),

sc("rvb003","retrieval_vocabulary_bridge","public",
   "downstream-svc keeps crashing and taking order-svc down with it. Add failure protection so order-svc survives downstream failures.",
   198,
   [
    m("rvb003-p1","project","order-svc must wrap its downstream-svc HTTP client with a circuit breaker (go-hystrix); open threshold is 5 failures in 10 s.","valid","critical"),
    m("rvb003-l1","long_term","When a downstream dependency is unreliable, wrap it with a circuit breaker before any other resilience measure; this prevents cascade failures.","valid","critical"),
    m("rvb003-p2","project","Circuit breaker fallback for downstream-svc calls should return a cached result or a graceful degraded response, not an error to the caller.","valid","supporting"),
    m("rvb003-x1","project","TLS certificate on downstream-svc expires in 14 days; renew before it causes connection failures.","irrelevant","supporting","note: failure cause is reliability, not certs"),
    m("rvb003-x2","long_term","Retrying failed requests with exponential backoff reduces transient failure impact but does not protect against sustained downstream outages.","irrelevant","supporting","note: retry ≠ circuit breaker, different mechanism"),
    m("rvb003-x3","session","downstream-svc team is investigating a memory leak; ETA for fix is 48 h.","irrelevant","supporting"),
   ],
   ["rvb003-p1","rvb003-l1","rvb003-p2"],
   ["rvb003-x1","rvb003-x2","rvb003-x3"],
   [ob("project_critical",["rvb003-p1","rvb003-l1"]),ob("supporting",["rvb003-p2"])],
   no_mem=0.08),

sc("rvb004","retrieval_vocabulary_bridge","public",
   "The ingestion pipeline is overwhelming the processing workers. Slow down incoming work when workers are overloaded.",
   196,
   [
    m("rvb004-p1","project","The ingestion pipeline implements backpressure via a bounded channel (capacity=500); producers block when the channel is full, preventing worker overload.","valid","critical"),
    m("rvb004-l1","long_term","Bounded queues are the correct mechanism for backpressure; never use unbounded queues between a fast producer and a slow consumer in a long-running pipeline.","valid","critical"),
    m("rvb004-p2","project","Backpressure metrics are exposed as ingestion_channel_fill_ratio; alert threshold is 0.9 for 30 s sustained.","valid","supporting"),
    m("rvb004-x1","project","Worker autoscaling is configured to add workers when CPU exceeds 80% for 2 min; this supplements but does not replace backpressure.","irrelevant","supporting","note: autoscaling is complementary, not the backpressure fix"),
    m("rvb004-x2","long_term","Rate limiting at the API gateway slows down external clients; this is a different layer from internal pipeline backpressure.","irrelevant","supporting","note: external rate limiting ≠ internal backpressure"),
    m("rvb004-x3","session","Worker OOM events occurring every 20 min; root cause is unbounded queue; backpressure fix is the solution.","irrelevant","supporting"),
   ],
   ["rvb004-p1","rvb004-l1","rvb004-p2"],
   ["rvb004-x1","rvb004-x2","rvb004-x3"],
   [ob("project_critical",["rvb004-p1","rvb004-l1"]),ob("supporting",["rvb004-p2"])],
   no_mem=0.08),

sc("rvb005","retrieval_vocabulary_bridge","public",
   "Order placement spans 3 services (inventory, payment, shipping). When one step fails, partial writes must be undone. Design the rollback.",
   200,
   [
    m("rvb005-p1","project","Order placement uses the saga pattern: each service step publishes a compensating event on failure; the saga orchestrator triggers compensations in reverse order.","valid","critical"),
    m("rvb005-l1","long_term","Distributed operations that span multiple services must use sagas with compensating transactions, not two-phase commit, to avoid distributed locks.","valid","critical"),
    m("rvb005-p2","project","Compensation events are defined in saga/compensations.go; each step has a named compensating handler that must be idempotent.","valid","supporting"),
    m("rvb005-x1","project","Order placement uses a PostgreSQL transaction for the orders table; this is a local transaction, not a distributed one.","irrelevant","supporting","note: local transaction ≠ saga; different scope"),
    m("rvb005-x2","long_term","Two-phase commit is available for distributed writes but requires all participants to hold locks during the prepare phase, causing contention.","irrelevant","supporting","note: 2PC is the alternative pattern, not what's used here"),
    m("rvb005-x3","session","Inventory rollback failed in the last 2 incidents because the compensating handler was not idempotent; this was fixed in v2.3.","stale","supporting","stale: bug fixed in v2.3, compensation handler is now idempotent"),
   ],
   ["rvb005-p1","rvb005-l1","rvb005-p2"],
   ["rvb005-x1","rvb005-x2","rvb005-x3"],
   [ob("project_critical",["rvb005-p1","rvb005-l1"]),ob("supporting",["rvb005-p2"])],
   no_mem=0.08),

sc("rvb006","retrieval_vocabulary_bridge","public",
   "A memory leak in the PDF renderer is crashing all workers in the same pod. Isolate the failure so the crash doesn't spread.",
   197,
   [
    m("rvb006-p1","project","PDF renderer runs in a separate worker pool behind a bulkhead (semaphore size=4); bulkhead prevents renderer failures from consuming all shared worker threads.","valid","critical"),
    m("rvb006-l1","long_term","Resource-intensive or failure-prone operations must be placed behind a bulkhead to prevent thread exhaustion from cascading to unrelated workloads.","valid","critical"),
    m("rvb006-p2","project","Bulkhead semaphore size for the renderer is tunable via PDF_RENDERER_CONCURRENCY env var; default is 4.","valid","supporting"),
    m("rvb006-x1","project","The main worker pool has 50 threads; PDF rendering was using all 50 threads before the bulkhead was introduced.","irrelevant","supporting","note: problem description, not the fix"),
    m("rvb006-x2","long_term","Process isolation (separate OS process) is a stronger form of isolation but adds IPC overhead; use bulkhead for in-process isolation.","irrelevant","supporting","note: process isolation is a different mechanism"),
    m("rvb006-x3","session","Memory leak in renderer reported upstream; fix expected in renderer-lib v3.1.2, due next week.","irrelevant","supporting"),
   ],
   ["rvb006-p1","rvb006-l1","rvb006-p2"],
   ["rvb006-x1","rvb006-x2","rvb006-x3"],
   [ob("project_critical",["rvb006-p1","rvb006-l1"]),ob("supporting",["rvb006-p2"])],
   no_mem=0.08),

sc("rvb007","retrieval_vocabulary_bridge","public",
   "Audit log queries are slow because the audit table is rebuilt nightly from application logs. Keep a full history of changes as they happen.",
   199,
   [
    m("rvb007-p1","project","The audit system uses event sourcing: every state change is appended as an immutable event to audit_events; the current state is derived by replaying the event stream.","valid","critical"),
    m("rvb007-l1","long_term","Event sourcing provides a complete, immutable history of all state changes without nightly rebuilds; queries against event streams are faster than rebuilding from logs.","valid","critical"),
    m("rvb007-p2","project","audit_events table is append-only with a composite index on (entity_type, entity_id, occurred_at); queries by entity_id are O(log n).","valid","supporting"),
    m("rvb007-x1","project","Audit logs are also shipped to Splunk for SIEM analysis; Splunk ingestion is separate from the event-sourced audit_events table.","irrelevant","supporting","note: Splunk is a separate log sink, not the event sourcing system"),
    m("rvb007-x2","long_term","Database change-data-capture (CDC) captures row-level changes but requires the source table to exist; CDC is not the same as event sourcing.","irrelevant","supporting","note: CDC is a different history mechanism"),
    m("rvb007-x3","session","Nightly rebuild job takes 4 h and is the primary source of slow audit queries; event sourcing eliminates the need for the rebuild.","irrelevant","supporting"),
   ],
   ["rvb007-p1","rvb007-l1","rvb007-p2"],
   ["rvb007-x1","rvb007-x2","rvb007-x3"],
   [ob("project_critical",["rvb007-p1","rvb007-l1"]),ob("supporting",["rvb007-p2"])],
   no_mem=0.08),

sc("rvb008","retrieval_vocabulary_bridge","public",
   "Write the results of a price calculation to both the orders DB and the analytics DB atomically. Coordinate the writes across the two services.",
   200,
   [
    m("rvb008-p1","project","Price write coordination uses the outbox pattern (a form of two-phase commit avoidance): the price is written to a local outbox table in the orders DB transaction, then a relay publishes it to analytics-svc asynchronously.","valid","critical"),
    m("rvb008-l1","long_term","Do not use two-phase commit (2PC) for cross-service writes; the outbox pattern achieves at-least-once delivery without distributed locks or blocking across services.","valid","critical"),
    m("rvb008-p2","project","Outbox relay uses Debezium CDC on the orders.outbox table; messages land in the price-events Kafka topic within 500 ms.","valid","supporting"),
    m("rvb008-x1","long_term","Two-phase commit coordinates writes across multiple databases but holds locks on all participants during the prepare phase, causing blocking.","irrelevant","supporting","note: 2PC is described but is the anti-pattern for this system"),
    m("rvb008-x2","project","Analytics DB is read-only from the application layer; all writes go through the event pipeline.","irrelevant","supporting","note: constraint description, not the coordination mechanism"),
    m("rvb008-x3","session","Data inconsistency between orders DB and analytics DB was reported in 2 rows; root cause is a missing outbox entry during a prior deploy.","stale","supporting","stale: specific prior incident, not a current constraint"),
   ],
   ["rvb008-p1","rvb008-l1","rvb008-p2"],
   ["rvb008-x1","rvb008-x2","rvb008-x3"],
   [ob("project_critical",["rvb008-p1","rvb008-l1"]),ob("supporting",["rvb008-p2"])],
   no_mem=0.08),

sc("rvb009","retrieval_vocabulary_bridge","holdout",
   "Analytics queries are slowing down the transactional DB. Make sure analytics reads don't go to the write database.",
   196,
   [
    m("rvb009-p1","project","analytics-svc is configured to route all SELECT queries to the read replica via READ_DB_URL; any query hitting the primary is a misconfiguration.","valid","critical"),
    m("rvb009-l1","long_term","Analytics and reporting workloads must always target the read replica, never the primary; the primary is reserved for transactional writes only.","valid","critical"),
    m("rvb009-p2","project","READ_DB_URL is set per service in vault:/secret/services/{name}/db; verify analytics-svc is reading the correct vault path, not the shared DEFAULT_DB_URL.","valid","supporting"),
    m("rvb009-x1","project","The read replica has a replication lag of up to 5 s; analytics queries must tolerate slightly stale data.","irrelevant","supporting","note: replication lag is a trade-off, not the routing fix"),
    m("rvb009-x2","long_term","Database connection pools should be sized separately for read and write paths to prevent analytics from exhausting write connections.","irrelevant","supporting","note: pool sizing is a related concern, not the primary fix"),
    m("rvb009-x3","session","Primary DB CPU spiked to 95% during the analytics batch run; confirmed due to analytics queries hitting the primary.","irrelevant","supporting"),
   ],
   ["rvb009-p1","rvb009-l1","rvb009-p2"],
   ["rvb009-x1","rvb009-x2","rvb009-x3"],
   [ob("project_critical",["rvb009-p1","rvb009-l1"]),ob("supporting",["rvb009-p2"])],
   no_mem=0.08),

sc("rvb010","retrieval_vocabulary_bridge","holdout",
   "Deploy a new version of checkout-svc without causing any downtime for users during the deployment.",
   197,
   [
    m("rvb010-p1","project","checkout-svc uses blue-green deployment: the new version is deployed to the green slot; traffic is shifted from blue to green only after green passes health checks.","valid","critical"),
    m("rvb010-l1","long_term","Blue-green deployment achieves zero-downtime by keeping the old version live until the new version is fully healthy; rollback is instant by shifting traffic back to blue.","valid","critical"),
    m("rvb010-p2","project","Traffic shift is controlled via the checkout-svc-weight annotation on the Istio VirtualService; set green weight to 100 after green is healthy for 5 min.","valid","supporting"),
    m("rvb010-x1","project","Kubernetes rolling update strategy updates pods one by one and can cause brief errors if readiness probes are misconfigured.","irrelevant","supporting","note: rolling update is a different deployment strategy"),
    m("rvb010-x2","long_term","Canary deployment sends a small percentage of traffic to the new version first; this is a variant of blue-green but not what checkout-svc uses.","irrelevant","supporting","note: canary is a related but distinct approach"),
    m("rvb010-x3","session","checkout-svc v2.5 is staged in the green slot and has passed all smoke tests.","irrelevant","supporting"),
   ],
   ["rvb010-p1","rvb010-l1","rvb010-p2"],
   ["rvb010-x1","rvb010-x2","rvb010-x3"],
   [ob("project_critical",["rvb010-p1","rvb010-l1"]),ob("supporting",["rvb010-p2"])],
   no_mem=0.08),

]  # end retrieval_vocabulary_bridge


# ══════════════════════════════════════════════════════════════════════════════
# retrieval_scope_enforcement (rse001–rse010)
# Each scenario presents memories from 2–3 projects. The task is scoped to
# one project. Distractors are valid for other projects but wrong here.
# ══════════════════════════════════════════════════════════════════════════════

SCENARIOS_1 += [

sc("rse001","retrieval_scope_enforcement","public",
   "[Project: Orion] Generate encryption keys for the new authentication flow in Project Orion.",
   210,
   [
    m("rse001-p1","project","[Project: Orion] Key generation must use ED25519 per the Orion security specification; RSA is explicitly prohibited for new Orion keys.","valid","critical"),
    m("rse001-l1","long_term","[Project: Orion] Security review Q4-2025 approved ED25519 for all new Orion key generation; approval is on file in security/orion_key_approval.md.","valid","supporting"),
    m("rse001-x1","project","[Project: Argus] Key generation uses RSA-4096 per FIPS 140-2 compliance requirements specific to the Argus regulated environment.","irrelevant","critical","note: scope=Argus; Orion has different requirements"),
    m("rse001-x2","project","[Project: Argus] ED25519 is not FIPS-approved for Argus; all Argus cryptographic operations must use NIST-approved algorithms only.","irrelevant","supporting","note: scope=Argus; directly conflicts with Orion rule if injected"),
    m("rse001-x3","long_term","[General] Legacy standard: all projects should use RSA-2048 minimum. This general policy is superseded by per-project security specs.","stale","supporting","stale: general policy superseded by project-specific specs"),
    m("rse001-x4","session","[Project: Orion] Key generation tooling setup is complete; go-jose library is available in the Orion service.","irrelevant","supporting"),
   ],
   ["rse001-p1","rse001-l1"],
   ["rse001-x1","rse001-x2","rse001-x3","rse001-x4"],
   [ob("project_critical",["rse001-p1"]),ob("supporting",["rse001-l1"])],
   no_mem=0.08),

sc("rse002","retrieval_scope_enforcement","public",
   "[Project: Helios/orders-api] Configure the inbound rate limit for the Helios orders-api service.",
   215,
   [
    m("rse002-p1","project","[Project: Helios] orders-api inbound rate limit is 200 req/s per IP per the 2025 Helios capacity plan.","valid","critical"),
    m("rse002-l1","long_term","[Project: Helios] Rate limit values are reviewed after each load test; the 200 req/s figure was validated in the 2025-03 peak test.","valid","supporting"),
    m("rse002-x1","project","[Project: Apollo] orders-api rate limit is 500 req/s per IP; Apollo serves enterprise clients with higher quotas.","irrelevant","critical","note: scope=Apollo; different service class"),
    m("rse002-x2","project","[Project: Zeus] orders-api is limited to 50 req/s per IP due to Zeus's shared infrastructure constraints.","irrelevant","supporting","note: scope=Zeus; different infrastructure tier"),
    m("rse002-x3","long_term","[General] API rate limits must be documented in the capacity register; this general policy applies to all projects.","irrelevant","supporting","note: general policy, not Helios-specific config value"),
    m("rse002-x4","session","[Project: Helios] Load test result: 200 req/s produces p99 latency of 110 ms; within SLO.","irrelevant","supporting"),
   ],
   ["rse002-p1","rse002-l1"],
   ["rse002-x1","rse002-x2","rse002-x3","rse002-x4"],
   [ob("project_critical",["rse002-p1"]),ob("supporting",["rse002-l1"])],
   no_mem=0.08),

sc("rse003","retrieval_scope_enforcement","public",
   "[Project: Nova/payment-svc] Set the downstream HTTP client timeout for payment-svc in Project Nova.",
   208,
   [
    m("rse003-p1","project","[Project: Nova] payment-svc downstream HTTP timeout is 8 s; this is set to accommodate the payment processor's P99 of 6 s plus 2 s buffer.","valid","critical"),
    m("rse003-p2","project","[Project: Nova] Timeout is configured via PAYMENT_CLIENT_TIMEOUT_MS in payment-svc/config/production.yaml; default in code is 30 s and must be overridden.","valid","supporting"),
    m("rse003-x1","project","[Project: Orion] All outbound HTTP timeouts in Orion are set to 3 s per the Orion latency SLA.","irrelevant","critical","note: scope=Orion; Orion has stricter latency requirements"),
    m("rse003-x2","project","[Project: Legacy] payment-svc timeout was 30 s before the Legacy modernisation; the new value is 8 s in Nova.","stale","supporting","stale: legacy value, current Nova value is 8 s in p1"),
    m("rse003-x3","long_term","[General] HTTP client timeouts should always be set explicitly; relying on OS-level defaults causes unpredictable behaviour under load.","irrelevant","supporting","note: general principle, not Nova-specific value"),
    m("rse003-x4","session","[Project: Nova] Payment processor SLA updated: P99 is now 6 s, down from 8 s; timeout buffer remains at 2 s.","irrelevant","supporting"),
   ],
   ["rse003-p1","rse003-p2"],
   ["rse003-x1","rse003-x2","rse003-x3","rse003-x4"],
   [ob("project_critical",["rse003-p1"]),ob("supporting",["rse003-p2"])],
   no_mem=0.08),

sc("rse004","retrieval_scope_enforcement","public",
   "[Project: Atlas/production] Set the log level for Atlas services in the production environment.",
   205,
   [
    m("rse004-p1","project","[Project: Atlas / env: production] Log level must be WARN in production; INFO or DEBUG logs are prohibited in production due to PII exposure risk.","valid","critical"),
    m("rse004-l1","long_term","[Project: Atlas] PII scrubbing only applies to WARN+ level structured logs; enabling INFO in production has caused PII leaks in prior incidents.","valid","supporting"),
    m("rse004-x1","project","[Project: Atlas / env: staging] Log level is DEBUG in staging to aid diagnosis; this setting must not be copied to production.","irrelevant","critical","note: scope=staging; explicitly not for production"),
    m("rse004-x2","project","[Project: Helios / env: production] Log level is INFO in production; Helios scrubs PII at the log router level.","irrelevant","supporting","note: scope=Helios; different project, different scrubbing approach"),
    m("rse004-x3","long_term","[General] Log verbosity should be reduced in production to minimise storage costs; WARN or ERROR is typical.","irrelevant","supporting","note: general guidance, Atlas-specific rule is stricter"),
    m("rse004-x4","session","[Project: Atlas] Recent audit found 3 services logging at INFO in production; this incident is the motivation for this task.","irrelevant","supporting"),
   ],
   ["rse004-p1","rse004-l1"],
   ["rse004-x1","rse004-x2","rse004-x3","rse004-x4"],
   [ob("project_critical",["rse004-p1"]),ob("supporting",["rse004-l1"])],
   no_mem=0.08),

sc("rse005","retrieval_scope_enforcement","public",
   "[Project: Ember/auth-svc] Set the JWT expiry for tokens issued by Ember's auth-svc.",
   207,
   [
    m("rse005-p1","project","[Project: Ember] auth-svc issues JWTs with a 15-minute expiry; refresh tokens are valid for 7 days and must be rotated on use.","valid","critical"),
    m("rse005-p2","project","[Project: Ember] JWT expiry is configured via AUTH_JWT_EXPIRY_SECONDS in auth-svc/config.yaml; the refresh token TTL is AUTH_REFRESH_TTL_DAYS.","valid","supporting"),
    m("rse005-x1","project","[Project: Nova] auth-svc issues JWTs with a 1-hour expiry to reduce refresh overhead for Nova's low-traffic internal tools.","irrelevant","critical","note: scope=Nova; different risk profile, longer expiry"),
    m("rse005-x2","long_term","[General] JWT expiry should be short (15–60 min) for public-facing services and may be longer for internal tools; always pair with refresh tokens.","irrelevant","supporting","note: general guidance, Ember-specific value is authoritative"),
    m("rse005-x3","project","[Project: Ember / legacy] Old auth-svc issued 24-hour JWTs; this was identified as a security risk and reduced to 15 min in 2024.","stale","supporting","stale: legacy value superseded by current 15-min policy"),
    m("rse005-x4","session","[Project: Ember] Security team approved the 15-min/7-day token policy during Q3 review.","irrelevant","supporting"),
   ],
   ["rse005-p1","rse005-p2"],
   ["rse005-x1","rse005-x2","rse005-x3","rse005-x4"],
   [ob("project_critical",["rse005-p1"]),ob("supporting",["rse005-p2"])],
   no_mem=0.08),

sc("rse006","retrieval_scope_enforcement","public",
   "[Project: Cobalt/platform-team] Name the new REST endpoint for the Cobalt platform API.",
   204,
   [
    m("rse006-p1","project","[Project: Cobalt] REST endpoints use kebab-case resource names with API version prefix: /api/v{n}/{resource-name}; no underscores in paths.","valid","critical"),
    m("rse006-l1","long_term","[Project: Cobalt] Naming convention was standardised in 2024; all new Cobalt endpoints must follow it; deviations require an ADR.","valid","supporting"),
    m("rse006-x1","project","[Project: Orion] REST endpoints use snake_case resource names: /api/v{n}/{resource_name}; Orion's convention differs from Cobalt's.","irrelevant","critical","note: scope=Orion; snake_case vs kebab-case conflict if injected"),
    m("rse006-x2","project","[Project: Atlas] REST endpoints omit version prefix for internal APIs; /api/{resource} is acceptable for Atlas.","irrelevant","supporting","note: scope=Atlas; different versioning strategy"),
    m("rse006-x3","long_term","[General] REST API naming conventions vary by project; always check the project's API style guide before naming new endpoints.","irrelevant","supporting","note: general meta-guidance, Cobalt-specific rule is authoritative"),
    m("rse006-x4","session","[Project: Cobalt] The new endpoint is for managing deployment slots; resource name candidates: deployment-slot or deployment_slot.","irrelevant","supporting"),
   ],
   ["rse006-p1","rse006-l1"],
   ["rse006-x1","rse006-x2","rse006-x3","rse006-x4"],
   [ob("project_critical",["rse006-p1"]),ob("supporting",["rse006-l1"])],
   no_mem=0.08),

sc("rse007","retrieval_scope_enforcement","public",
   "[Project: Indigo/api-gateway] Format error responses for the Indigo API gateway.",
   206,
   [
    m("rse007-p1","project","[Project: Indigo] Error responses follow RFC 7807 (Problem Details): {type, title, status, detail, instance}; no custom error envelope.","valid","critical"),
    m("rse007-p2","project","[Project: Indigo] The type field must be a URI pointing to the error documentation in https://docs.indigo.internal/errors/{code}.","valid","supporting"),
    m("rse007-x1","project","[Project: Nova] Error responses use a custom envelope: {error: {code, message, request_id}}; Nova predates RFC 7807 adoption.","irrelevant","critical","note: scope=Nova; different format, conflicts with Indigo if injected"),
    m("rse007-x2","project","[Project: Atlas] Errors are returned as plain HTTP status codes with no body for internal APIs; Atlas clients parse status codes only.","irrelevant","supporting","note: scope=Atlas; different error strategy"),
    m("rse007-x3","long_term","[General] RFC 7807 is the recommended standard for REST API error responses; projects may have project-specific adaptations.","irrelevant","supporting","note: general recommendation, Indigo-specific format is authoritative"),
    m("rse007-x4","session","[Project: Indigo] New API gateway version 3.2 adds native RFC 7807 middleware; migration guide is in docs/gateway-v3-migration.md.","irrelevant","supporting"),
   ],
   ["rse007-p1","rse007-p2"],
   ["rse007-x1","rse007-x2","rse007-x3","rse007-x4"],
   [ob("project_critical",["rse007-p1"]),ob("supporting",["rse007-p2"])],
   no_mem=0.08),

sc("rse008","retrieval_scope_enforcement","public",
   "[Project: Cobalt/data-svc] Set the PostgreSQL connection pool size for Cobalt's data-svc.",
   208,
   [
    m("rse008-p1","project","[Project: Cobalt] data-svc connection pool is set to 20 connections; Cobalt's DB server has max_connections=200 and hosts 8 services.","valid","critical"),
    m("rse008-p2","project","[Project: Cobalt] Pool size is configured via DB_POOL_SIZE in data-svc/config/production.yaml; pgbouncer is not in use for data-svc.","valid","supporting"),
    m("rse008-x1","project","[Project: Helios] data-svc pool size is 50 connections; Helios has a dedicated DB instance with max_connections=500.","irrelevant","critical","note: scope=Helios; dedicated DB allows larger pool"),
    m("rse008-x2","long_term","[General] Connection pool size should be (core_count * 2) + effective_spindle_count as a starting point; tune down from there.","irrelevant","supporting","note: general formula, Cobalt-specific value is authoritative"),
    m("rse008-x3","project","[Project: Cobalt / legacy] Old pool size was 50; reduced to 20 after DB connection exhaustion incident in 2024.","stale","supporting","stale: incident context, current value is 20 as in p1"),
    m("rse008-x4","session","[Project: Cobalt] DB server CPU is at 45%; no signs of connection pressure currently.","irrelevant","supporting"),
   ],
   ["rse008-p1","rse008-p2"],
   ["rse008-x1","rse008-x2","rse008-x3","rse008-x4"],
   [ob("project_critical",["rse008-p1"]),ob("supporting",["rse008-p2"])],
   no_mem=0.08),

sc("rse009","retrieval_scope_enforcement","holdout",
   "[Project: Ember/checkout-squad] Name feature flags created by the Ember checkout squad.",
   204,
   [
    m("rse009-p1","project","[Project: Ember / squad: checkout] Feature flag names follow the pattern {squad}_{feature}_{variant}: e.g. checkout_express_v2. No hyphens; underscores only.","valid","critical"),
    m("rse009-l1","long_term","[Project: Ember] Flag naming convention is enforced by the flag-lint CI check; non-conformant names will fail the pipeline.","valid","supporting"),
    m("rse009-x1","project","[Project: Atlas / squad: platform] Feature flag names follow {team}-{feature}-{env}: e.g. platform-dark-mode-prod. Hyphens, not underscores.","irrelevant","critical","note: scope=Atlas/platform; different convention, conflicts if injected"),
    m("rse009-x2","project","[Project: Ember / squad: payments] Payments squad flags follow the same Ember convention: payments_{feature}_{variant}.","irrelevant","supporting","note: confirms Ember convention but names a different squad"),
    m("rse009-x3","long_term","[General] Feature flag names should be descriptive and include the owning team; specific formats vary by project.","irrelevant","supporting","note: general guidance, Ember-specific format is authoritative"),
    m("rse009-x4","session","[Project: Ember] New checkout flag being created: fast checkout with pre-filled address for returning users.","irrelevant","supporting"),
   ],
   ["rse009-p1","rse009-l1"],
   ["rse009-x1","rse009-x2","rse009-x3","rse009-x4"],
   [ob("project_critical",["rse009-p1"]),ob("supporting",["rse009-l1"])],
   no_mem=0.08),

sc("rse010","retrieval_scope_enforcement","holdout",
   "[Project: Nova/deploy-agent] Configure the deployment region for Nova's deploy-agent service.",
   206,
   [
    m("rse010-p1","project","[Project: Nova] deploy-agent is deployed exclusively to us-east-1; Nova's data residency agreement prohibits deployment outside the US.","valid","critical"),
    m("rse010-p2","project","[Project: Nova] DEPLOY_REGION is set in nova/deploy-agent/helm/values.yaml; the value must remain us-east-1; do not inherit from the cluster default.","valid","supporting"),
    m("rse010-x1","project","[Project: Atlas] deploy-agent is deployed to eu-west-1 and eu-central-1 to serve European customers; Atlas has EU data residency requirements.","irrelevant","critical","note: scope=Atlas; EU residency constraint conflicts with Nova US-only"),
    m("rse010-x2","project","[Project: Cobalt] deploy-agent is deployed globally (us-east-1, eu-west-1, ap-southeast-1); Cobalt has no data residency restrictions.","irrelevant","supporting","note: scope=Cobalt; global deployment conflicts with Nova US-only"),
    m("rse010-x3","long_term","[General] Deployment region should match customer geography to reduce latency; data residency requirements take precedence over latency.","irrelevant","supporting","note: general principle, Nova-specific constraint is authoritative"),
    m("rse010-x4","session","[Project: Nova] Legal review confirmed us-east-1 is sufficient for Nova's current customer base and compliance obligations.","irrelevant","supporting"),
   ],
   ["rse010-p1","rse010-p2"],
   ["rse010-x1","rse010-x2","rse010-x3","rse010-x4"],
   [ob("project_critical",["rse010-p1"]),ob("supporting",["rse010-p2"])],
   no_mem=0.08),

]  # end retrieval_scope_enforcement


# ══════════════════════════════════════════════════════════════════════════════
# retrieval_deduplication (rde001–rde010)
# 3–5 memories express the same fact in different phrasings. Only the canonical
# version (most complete / most recent / from authoritative source) should be
# injected. Duplicates are marked stale (superseded) with a deduplication note.
# ══════════════════════════════════════════════════════════════════════════════

SCENARIOS_1 += [

sc("rde001","retrieval_deduplication","public",
   "Configure the pre-commit hook for commit signing in the new service repository.",
   180,
   [
    m("rde001-p1","project","All commits must be GPG-signed; unsigned commits are rejected by CI. Configure via .gitconfig: gpg.program=gpg2, commit.gpgsign=true. The pre-commit hook verifies the signature before push.","valid","critical"),
    m("rde001-p2","project","All commits should be signed with GPG.","stale","critical","deduplication: superseded by rde001-p1; less complete, missing config details"),
    m("rde001-l1","long_term","GPG signing required for commits per security policy. Set commit.gpgsign=true.","stale","supporting","deduplication: superseded by rde001-p1; missing hook and gpg.program detail"),
    m("rde001-x1","long_term","Team policy: sign all commits. This has been required since 2024.","stale","supporting","deduplication: oldest version, no config detail, superseded by rde001-p1"),
    m("rde001-x2","session","Code review approvals require two team leads to sign off before merge; sign-off is separate from GPG commit signing.","irrelevant","supporting"),
   ],
   ["rde001-p1"],
   ["rde001-p2","rde001-l1","rde001-x1","rde001-x2"],
   [ob("project_critical",["rde001-p1"])],
   no_mem=0.1),

sc("rde002","retrieval_deduplication","public",
   "Configure the editor and linter settings for the new Go service repository to match team standards.",
   175,
   [
    m("rde002-p1","project","Go source files use tabs for indentation (gofmt default); spaces are not permitted. .editorconfig must set indent_style=tab, indent_size=4 for *.go files.","valid","critical"),
    m("rde002-p2","project","Use tabs not spaces in Go files.","stale","critical","deduplication: superseded by rde002-p1; missing .editorconfig detail"),
    m("rde002-l1","long_term","Indentation: tabs, not spaces, for all Go code per gofmt convention.","stale","supporting","deduplication: superseded by rde002-p1; no editor config detail"),
    m("rde002-x1","project","Python files in the monorepo use 4-space indentation per PEP 8; this is separate from the Go convention.","irrelevant","supporting"),
    m("rde002-x2","session","gofmt is run as part of the CI lint step; files not conforming to gofmt will fail CI.","irrelevant","supporting"),
   ],
   ["rde002-p1"],
   ["rde002-p2","rde002-l1","rde002-x1","rde002-x2"],
   [ob("project_critical",["rde002-p1"])],
   no_mem=0.1),

sc("rde003","retrieval_deduplication","public",
   "Load the service auth token for the billing API client. The token must not come from environment variables.",
   178,
   [
    m("rde003-p1","project","Auth tokens for all service clients must be loaded from vault at runtime using the AppRole path vault:/secret/services/{service-name}/token; loading from ENV vars or config files is prohibited.","valid","critical"),
    m("rde003-p2","project","Token must come from vault only, not ENV.","stale","critical","deduplication: superseded by rde003-p1; missing AppRole path detail"),
    m("rde003-l1","long_term","Never load service credentials from environment variables; use vault AppRole.","stale","supporting","deduplication: superseded by rde003-p1; missing specific path format"),
    m("rde003-x1","project","Old setup used BILLING_API_TOKEN env var; this was migrated to vault in 2024.","stale","supporting","stale: historical migration note, not the current rule"),
    m("rde003-x2","session","Vault is reachable; AppRole auth is healthy.","irrelevant","supporting"),
   ],
   ["rde003-p1"],
   ["rde003-p2","rde003-l1","rde003-x1","rde003-x2"],
   [ob("project_critical",["rde003-p1"])],
   no_mem=0.1),

sc("rde004","retrieval_deduplication","public",
   "Add structured logging to the user profile endpoint. Ensure no personally identifiable information appears in log output.",
   182,
   [
    m("rde004-p1","project","PII must never appear in log output. Fields email, phone, full_name, and ssn must be redacted using the pii.Redact() helper before logging. Violation triggers an automatic compliance alert.","valid","critical"),
    m("rde004-p2","project","Never log PII fields: email, phone, full_name.","stale","critical","deduplication: superseded by rde004-p1; incomplete field list, missing ssn and Redact() method"),
    m("rde004-l1","long_term","PII must not be written to logs per data protection policy.","stale","supporting","deduplication: superseded by rde004-p1; no field list or implementation detail"),
    m("rde004-x1","long_term","All logs should be structured JSON; unstructured log lines cannot be reliably scrubbed.","irrelevant","supporting"),
    m("rde004-x2","session","Compliance team flagged 2 endpoints that were logging email addresses; this task is the remediation.","irrelevant","supporting"),
   ],
   ["rde004-p1"],
   ["rde004-p2","rde004-l1","rde004-x1","rde004-x2"],
   [ob("project_critical",["rde004-p1"])],
   no_mem=0.1),

sc("rde005","retrieval_deduplication","public",
   "Set the HTTP client timeout for the outbound call to the shipping API.",
   172,
   [
    m("rde005-p1","project","Outbound HTTP client timeout for shipping-api calls is 10 s (3 s connect + 7 s read); configured via SHIPPING_CLIENT_TIMEOUT_MS=10000 in config/production.yaml.","valid","critical"),
    m("rde005-p2","project","Shipping API timeout is 10 seconds.","stale","critical","deduplication: superseded by rde005-p1; no connect/read breakdown or config key"),
    m("rde005-l1","long_term","HTTP client timeouts should always be explicit; never rely on OS defaults for outbound API calls.","irrelevant","supporting"),
    m("rde005-x1","project","Old timeout was 30 s before the shipping API SLA was tightened in 2024; 10 s is the current value.","stale","supporting","stale: historical context, current value already in p1"),
    m("rde005-x2","session","Shipping API P99 latency is currently 4.2 s; 10 s timeout provides adequate headroom.","irrelevant","supporting"),
   ],
   ["rde005-p1"],
   ["rde005-p2","rde005-l1","rde005-x1","rde005-x2"],
   [ob("project_critical",["rde005-p1"])],
   no_mem=0.1),

sc("rde006","retrieval_deduplication","public",
   "Prepare the deployment checklist for pushing the new release to production.",
   180,
   [
    m("rde006-p1","project","Deployment sequence: (1) deploy to staging, run smoke tests, confirm pass; (2) deploy to production during the maintenance window; (3) run production smoke tests before removing the maintenance page.","valid","critical"),
    m("rde006-p2","project","Always deploy to staging before production.","stale","critical","deduplication: superseded by rde006-p1; missing smoke test and maintenance window steps"),
    m("rde006-l1","long_term","No production deployments without a prior successful staging deploy.","stale","supporting","deduplication: superseded by rde006-p1; missing post-deploy smoke test"),
    m("rde006-x1","project","Old process allowed direct-to-production hotfixes for P1 incidents; this exception was removed in 2025.","stale","supporting","stale: hotfix exception removed, current rule requires staging for all deploys"),
    m("rde006-x2","session","Current staging deployment is healthy; smoke tests passed 20 min ago.","irrelevant","supporting"),
   ],
   ["rde006-p1"],
   ["rde006-p2","rde006-l1","rde006-x1","rde006-x2"],
   [ob("project_critical",["rde006-p1"])],
   no_mem=0.1),

sc("rde007","retrieval_deduplication","public",
   "Configure the test coverage requirement for the new service in CI.",
   174,
   [
    m("rde007-p1","project","Minimum test coverage is 80% line coverage and 70% branch coverage; CI enforces both thresholds via go test -cover; PRs below threshold are blocked.","valid","critical"),
    m("rde007-p2","project","Minimum 80% test coverage required.","stale","critical","deduplication: superseded by rde007-p1; missing branch coverage and CI enforcement detail"),
    m("rde007-l1","long_term","Test coverage below 80% blocks merge per engineering quality standards.","stale","supporting","deduplication: superseded by rde007-p1; no branch threshold"),
    m("rde007-x1","project","Integration tests are excluded from the coverage calculation; only unit tests count toward the thresholds.","irrelevant","supporting"),
    m("rde007-x2","session","Current service draft is at 62% coverage; needs 18% more before CI will pass.","irrelevant","supporting"),
   ],
   ["rde007-p1"],
   ["rde007-p2","rde007-l1","rde007-x1","rde007-x2"],
   [ob("project_critical",["rde007-p1"])],
   no_mem=0.1),

sc("rde008","retrieval_deduplication","public",
   "Confirm the target PostgreSQL version for the new service and update the Docker base image.",
   176,
   [
    m("rde008-p1","project","Target PostgreSQL version is 16.3; Docker base image must be postgres:16.3-alpine. Do not use 'latest' or a major-only tag in production images.","valid","critical"),
    m("rde008-p2","project","PostgreSQL version is 16.","stale","critical","deduplication: superseded by rde008-p1; no minor version or Docker image detail"),
    m("rde008-l1","long_term","Postgres version 16 is the current standard; pinned to 16.3 after 16.2 had a replication bug.","stale","supporting","deduplication: superseded by rde008-p1; less prescriptive on image tag format"),
    m("rde008-x1","project","Staging uses postgres:16.3-alpine; production image tag should match staging exactly.","irrelevant","supporting"),
    m("rde008-x2","long_term","Old standard was PostgreSQL 14; upgraded to 16 in Q1 2025 platform migration.","stale","supporting","stale: migration history, current version is 16.3 as in p1"),
   ],
   ["rde008-p1"],
   ["rde008-p2","rde008-l1","rde008-x1","rde008-x2"],
   [ob("project_critical",["rde008-p1"])],
   no_mem=0.1),

sc("rde009","retrieval_deduplication","holdout",
   "Set the versioning scheme for the new public API library.",
   173,
   [
    m("rde009-p1","project","Public API libraries use semantic versioning (SemVer 2.0): MAJOR.MINOR.PATCH; MAJOR for breaking changes, MINOR for backwards-compatible features, PATCH for bug fixes. Changelog entry is mandatory for every release.","valid","critical"),
    m("rde009-p2","project","Use semantic versioning for all releases.","stale","critical","deduplication: superseded by rde009-p1; no SemVer definition or changelog requirement"),
    m("rde009-l1","long_term","All public libraries follow SemVer; bump MAJOR on breaking API changes.","stale","supporting","deduplication: superseded by rde009-p1; incomplete"),
    m("rde009-x1","long_term","Internal tools and CLIs may use date-based versioning (YYYY.MM.DD); public APIs must use SemVer.","irrelevant","supporting"),
    m("rde009-x2","session","v1.0.0 release is planned for end of quarter; this is the first stable release.","irrelevant","supporting"),
   ],
   ["rde009-p1"],
   ["rde009-p2","rde009-l1","rde009-x1","rde009-x2"],
   [ob("project_critical",["rde009-p1"])],
   no_mem=0.1),

sc("rde010","retrieval_deduplication","holdout",
   "Configure the circuit breaker for the downstream inventory-svc client.",
   177,
   [
    m("rde010-p1","project","Circuit breaker for inventory-svc opens after 5 consecutive failures within a 10 s window; half-open probe fires every 30 s. Config lives in resilience/inventory_cb.yaml.","valid","critical"),
    m("rde010-p2","project","Circuit breaker threshold: 5 failures.","stale","critical","deduplication: superseded by rde010-p1; no window, half-open interval, or config location"),
    m("rde010-l1","long_term","Circuit breaker opens at 5 failures; probe after 30 s.","stale","supporting","deduplication: superseded by rde010-p1; missing time window and config file"),
    m("rde010-x1","project","Retry policy for inventory-svc is 2 retries with 100 ms backoff; circuit breaker sits above the retry layer.","irrelevant","supporting"),
    m("rde010-x2","session","inventory-svc has been healthy for 72 h; circuit breaker is closed.","irrelevant","supporting"),
   ],
   ["rde010-p1"],
   ["rde010-p2","rde010-l1","rde010-x1","rde010-x2"],
   [ob("project_critical",["rde010-p1"])],
   no_mem=0.1),

]  # end retrieval_deduplication


if __name__ == "__main__":
    print(f"Part 1 defines {len(SCENARIOS_1)} scenarios.")
    for s in SCENARIOS_1:
        print(f"  {s['scenario_id']}  ({s['family']})")
