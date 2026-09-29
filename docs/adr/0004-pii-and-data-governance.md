# ADR 0004: PII and Data Governance

## Status
Accepted

## Context
Citizen complaints can contain personal information — names, addresses, and phone numbers — since the form allows a free-text description, a location, and an optional contact field. When `TRIAGE_PROVIDER=llm`, this text is sent to Groq, a third-party hosted API, so we need to decide what actually leaves the machine and whether that is acceptable.

## Decision
Only the complaint `text` and `location` fields are sent to Groq for classification. The `reporter_contact` field (phone or email, if the citizen provided one) is never included in the prompt sent to the LLM — it stays in our own database only.

The complaint text itself is not redacted before sending. A citizen might still type a phone number or address inside the free-text description, and that text is sent to Groq as-is, since automatically detecting and stripping every possible form of personal information from free text is unreliable and out of scope for this assignment.

We accept this exposure for the following reasons:
- The system is a public civic complaint form — citizens already expect their complaint (including its location) to be read and acted on by municipal staff.
- Groq's free tier is used only for classification (category, priority, summary), not stored or displayed anywhere beyond our own database.
- The `reporter_contact` field, which is the most clearly identifying piece of data, is deliberately excluded from every LLM call.
- The API key is never logged, is read only from an environment variable, and is never committed to the repository.
- Anyone who wants zero data leaving their machine can set `TRIAGE_PROVIDER=ollama`, which runs the same classification locally with no network call and no third party involved.

## Consequences
- Free-text complaint content (which may occasionally contain a name or an address a citizen typed themselves) is sent to Groq's API when the LLM provider is active. This is a deliberate, documented trade-off, not an oversight.
- The `reporter_contact` field is never exposed to any third party, regardless of which provider is active.
- Teams or deployments with stricter privacy requirements can switch to `TRIAGE_PROVIDER=ollama` with no code changes, since it implements the same `TriageProvider` interface.
- If stricter redaction is needed later, it would be added as a step inside `LLMTriage.triage()`, before the prompt is sent — this is the one place all outbound text already passes through.
