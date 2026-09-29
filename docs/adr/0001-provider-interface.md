# ADR 0001: TriageProvider Interface

## Status
Accepted

## Context
The system needs to classify citizen complaints into a category, priority, and summary. Today that classification can be done by a hosted LLM (Groq), an offline model (Ollama), or simple keyword rules. The specific method used will keep changing — a different model, a different vendor, or a fine-tuned classifier later. The rest of the system (routes, database, cache) should not need to change when the classification method changes.

## Decision
We defined a single `TriageProvider` interface (a Python `Protocol`) with one method:

```python
class TriageProvider(Protocol):
    name: str
    def triage(self, text: str, location: str) -> TriageResult: ...
```

Every provider returns the same `TriageResult` (category, priority, summary, confidence), validated with a Pydantic model. Four providers implement this interface:

- **LLMTriage** — calls Groq (hosted LLM), used in normal operation.
- **OllamaTriage** — calls a local Ollama model, fully offline.
- **RuleBasedTriage** — deterministic keyword matching, no network, never fails. Used as the fallback.
- **SimulatedTriage** — deterministic fake output, no network, used only in tests and CI.

A factory function reads the `TRIAGE_PROVIDER` environment variable (`llm`, `ollama`, `rules`, or `simulated`) and returns the matching provider. Nothing outside the factory needs to know which provider is active.

The triage service that calls a provider always wraps the call in a try/except. If the active provider raises any exception, the service falls back to `RuleBasedTriage` and records `triaged_by = "rules:fallback"`. This means a citizen never sees a failed request just because the LLM is slow, rate-limited, or down.

## Consequences
- Swapping providers, or adding a new one, only means writing a new class that matches the interface and adding one line to the factory. Routes, services, and the database schema do not change.
- Because `RuleBasedTriage` never makes a network call and never fails, it can always be used as the fallback, so the system stays available even when every external provider is unreachable.
- `SimulatedTriage` gives the test suite and CI a provider with no network dependency and no randomness, so tests are deterministic and never flaky.
- The trade-off is that all providers must agree on one output shape. A provider that wants to return something the schema doesn't support (extra fields, a different category set) can't do that without changing the shared schema, which affects every provider at once.
