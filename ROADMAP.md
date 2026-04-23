# SFTP Hardening Roadmap (2026)

## Vision
To build a resilient, "AI-Ready" SFTP platform that moves from deterministic file transfers to programmable, autonomous data orchestration.

See FUTURE_WORK.md for the current forward-looking roadmap.

## The 7 Sprints
1. **Sprint 1: Observability & Truth** - Structured JSON logging and correlation IDs for AI-assisted monitoring.
2. **Sprint 2: Programmable Plumbing** - Abstract Base Classes (ABCs) to decouple SFTP logic from storage vendors (S3, Disk, etc.).
3. **Sprint 3: Data Integrity** - SHA-256 sidecar generation and post-transfer verification "Math-based Truth."
4. **[CURRENT] Sprint 4: Stateful Resilience** - Partial transfer resume logic to solve SFTP "stickiness" challenges.
5. **Sprint 5: Zero Trust Identity** - SSH Key-pair dynamic loading and vault-based credentialing.
6. **Sprint 6: API-First Orchestration** - FastAPI wrapper to make the engine triggerable by external agents/webhooks.
7. **Sprint 7: Strategic Documentation** - "PowerPoint-style" README and visual architecture diagrams.
