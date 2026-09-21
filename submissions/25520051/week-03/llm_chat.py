"""Week 03 — model call and meter, trimmed from week-02's tools_shared.py.

The contract net needs no tools, only a system prompt and one user message
per bid, so ToolCall/run_tools are dropped and Reply is just text.

Provider is picked from the environment:
  ANTHROPIC_API_KEY set          -> Anthropic SDK (pip install anthropic)
  otherwise                      -> OpenAI-compatible (pip install openai)
                                    OPENAI_API_KEY, optional OPENAI_BASE_URL
                                    (https://openrouter.ai/api/v1 for OpenRouter)
  AGENT_MODEL                    optional model override for either provider
  AGENT_TEMPERATURE              optional float, default 0.7
"""
import os
from dataclasses import dataclass

PROVIDER = "anthropic" if os.environ.get("ANTHROPIC_API_KEY") else "openai"
MODEL = os.environ.get(
    "AGENT_MODEL",
    "claude-sonnet-4-5" if PROVIDER == "anthropic" else "gpt-4o-mini")
TEMPERATURE = float(os.environ.get("AGENT_TEMPERATURE", "0.7"))

_client = None


def _get_client():
    global _client
    if _client is None:
        if PROVIDER == "anthropic":
            import anthropic
            _client = anthropic.Anthropic()
        else:
            from openai import OpenAI
            _client = OpenAI()
    return _client


class Meter:
    """Tokens and model-call count, same idea as week 02's Meter."""

    def __init__(self):
        self.tokens = 0
        self.calls = 0

    def add(self, input_tokens: int, output_tokens: int):
        self.tokens += int(input_tokens or 0) + int(output_tokens or 0)
        self.calls += 1


@dataclass
class Reply:
    text: str


class Chat:
    """One conversation with the model: a system prompt plus user turns."""

    def __init__(self, system: str, meter: Meter):
        self.system = system
        self.meter = meter
        self.messages = []
        if PROVIDER == "openai":
            self.messages.append({"role": "system", "content": system})

    def add_user(self, text: str):
        self.messages.append({"role": "user", "content": text})

    def send(self) -> Reply:
        if PROVIDER == "anthropic":
            return self._send_anthropic()
        return self._send_openai()

    def _send_anthropic(self) -> Reply:
        resp = _get_client().messages.create(
            model=MODEL, max_tokens=300, temperature=TEMPERATURE,
            system=self.system, messages=self.messages)
        self.meter.add(resp.usage.input_tokens, resp.usage.output_tokens)
        text = "".join(b.text for b in resp.content if b.type == "text")
        self.messages.append({"role": "assistant", "content": resp.content})
        return Reply(text)

    def _send_openai(self) -> Reply:
        resp = _get_client().chat.completions.create(
            model=MODEL, temperature=TEMPERATURE, messages=self.messages)
        usage = resp.usage
        self.meter.add(getattr(usage, "prompt_tokens", 0),
                        getattr(usage, "completion_tokens", 0))
        msg = resp.choices[0].message
        self.messages.append({"role": "assistant", "content": msg.content or ""})
        return Reply(msg.content or "")
