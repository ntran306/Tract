---
name: legal-flag-check
description: Surfaces legal/compliance considerations worth a human's attention while doing engineering work on Tract — third-party dependency licensing (copyleft vs permissive conflicts), data privacy/PII handling (storing, logging, or transmitting sensitive user data without consent), third-party API/ToS risk (scraping, rate limits, resale restrictions), and export-control or regulatory-shaped patterns (crypto, GDPR/CCPA-shaped data flows). Use this whenever adding a dependency, writing code that touches user data, integrating a third-party API or SDK, or scraping external sites — even if the user didn't ask about legal issues. This is NOT a substitute for a lawyer: it only flags things for the user to decide whether to escalate, it never issues legal conclusions or advice.
---

# Legal/Compliance Flag Check

You are not a lawyer, and this skill does not turn you into one. Its only job is to notice when engineering work touches an area where a mistake is expensive in a non-technical way — licensing, privacy, contracts, regulation — and say so plainly, so a human can decide whether it's worth a real lawyer's time. Silence on these topics is the actual risk: most legal exposure in software isn't from bad code, it's from nobody having thought to look until after the damage is done.

Stay in your lane: raise the flag, describe the concrete risk in plain language, and stop. Don't render a verdict on whether something is "legal" or "compliant" — you don't have the standing or the full picture (jurisdiction, business context, existing contracts) to do that.

## When to look

Check in whenever the change in front of you does one of these things — not on every turn, and not for changes that are purely internal logic with no external-facing or data-handling surface:

- **Adds or upgrades a dependency** (package.json, requirements.txt, go.mod, Cargo.toml, etc.)
- **Reads, writes, logs, or transmits data that could identify a person** — emails, names, IPs, device IDs, location, free-text user input, uploaded files
- **Calls, scrapes, or wraps a third-party API or website** that isn't Tract's own backend
- **Touches auth, consent, cookies, analytics/tracking, or anything with "GDPR," "CCPA," "PII," or "export" in the vicinity**
- **Introduces or modifies cryptography** in a way that could be export-controlled (this is a narrow, mostly-historical concern for US-origin software, but worth a one-line flag if it comes up)

If none of these apply, don't mention this skill at all — a flag on every PR is a flag nobody reads.

## What to flag, and how

Keep it to a few sentences, appended naturally to your normal response — not a formal report, not a wall of disclaimers. Name the specific thing, why it might matter, and what the human should decide.

**Dependency licensing.** When adding a new dependency, check its license (npm/PyPI/crates.io list it; `npm view <pkg> license` or the repo's LICENSE file work). Flag if:
- It's copyleft (GPL, AGPL, LGPL) and Tract's own license/distribution model isn't already compatible with that — copyleft licenses can require you to open-source code that links against them, which is a business decision, not just a technical one.
- It has no license file at all, or a non-standard/custom one — ambiguous licensing is itself the risk, independent of what the license says.
- Two dependencies you're combining have known-incompatible licenses (e.g., one GPL, one proprietary-only).

Example: "Heads up — `some-lib` is AGPL-3.0, which is more restrictive than the MIT/Apache dependencies you're using elsewhere. If Tract is closed-source, AGPL can require you to release your source or get a commercial license from the maintainer. Worth deciding if that's acceptable before this ships."

**Data privacy / PII.** When code stores, logs, or forwards anything that could identify a real person, flag:
- Sensitive data landing in logs, error trackers, or analytics without being redacted — logs often have looser access control and longer retention than the primary database.
- New data collection with no visible consent step, privacy notice, or documented retention/deletion path.
- Data being sent to a new third-party service (analytics, email provider, AI API) — that's a new place the data now lives, with its own terms.

Example: "This logs the full request body on error, which includes the user's email and IP — worth checking whether that should be redacted before it hits your logging provider, especially if any users are in the EU (GDPR gives people a right to know what's stored about them)."

**Third-party API / ToS risk.** When integrating or scraping an external service, flag:
- Scraping a site that likely has a ToS prohibiting it, or lacks a public API for the data being pulled — scraping itself isn't illegal, but breaching a ToS can be a contract issue even if no law is broken.
- Rate limits, resale/redistribution restrictions, or "no commercial use" clauses in a third-party API's terms that Tract's use case might bump into.

Example: "This pulls data via scraping rather than an official API — worth a quick look at the site's ToS/robots.txt, since scraping against explicit ToS terms is a contract risk even where it's not illegal outright."

**Export control / regulatory-shaped patterns.** Rare, but flag briefly if it comes up:
- Shipping non-standard cryptographic implementations (not just using TLS/standard libraries) to a global user base — historically subject to US export-control rules (EAR), though most standard crypto use is exempt.
- Code that clearly implements a GDPR/CCPA-shaped obligation (data export, right-to-delete, consent withdrawal) — flag if it looks partially implemented, since a half-built version can be worse than none (it creates an expectation the system doesn't actually meet).

## What not to do

- Don't block or refuse to write the code — flag it alongside doing the work, not instead of it.
- Don't cite specific statutes, case law, or give a compliance percentage/score — that reads as legal advice, which you're explicitly not providing.
- Don't flag defensively on things with no real external surface (pure internal refactors, test code, local dev tooling).
- Don't repeat the same flag every turn for a decision the user already made — if they said "we've accepted the AGPL risk," don't re-raise it next time you touch that file.
