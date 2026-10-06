# Low-effort instrumentation

The SDK supports manual event emission today. Existing optional integrations
cover LangChain, LangGraph, LiteLLM, and OpenAI Agents. They remain opt-in and
must not silently capture prompts, bodies, or credentials.

Future `blocklog init` tooling should detect dependencies and propose explicit
integration configuration. Framework adapters should emit through the same
event pipeline, preserve caller context, and provide field redaction and
per-integration opt-out. No source rewriting or global instrumentation is
performed by this SDK.
