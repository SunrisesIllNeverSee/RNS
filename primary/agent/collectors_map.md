# Platform Collector Map

Per-platform adapter specifications. Each adapter reads platform-specific session data and normalizes it into the unified `Session` / `Message` format.

---

## Priority order

| Priority | Platform | Reason |
|---|---|---|
| P1 | Claude Code | Native `.jsonl` format, no export needed, best telemetry |
| P2 | ChatGPT | Largest user base, exported JSON available |
| P2 | Cursor | Strong overlap with target operators |
| P3 | Gemini CLI | Emerging, comparable to Claude Code |
| P3 | Codex | Built-in to ChatGPT Plus, growing |
| P4 | Pi (Inflection) | Smaller user base |
| Always | Generic JSON | Catch-all for unsupported platforms |

---

## Claude Code adapter (P1)

**Source path:** `~/.claude/projects/<project-name>/<session-id>.jsonl`

**File format:** One JSON object per line. Each object is a turn (user message, assistant message, tool use, or tool result).

**Key fields extracted:**
- `sessionId` → `session_id`
- `timestamp` → `timestamp`
- `type` → role mapping
- `message.usage.input_tokens` → fresh input
- `message.usage.output_tokens` → output
- `message.usage.cache_read_input_tokens` → cache read
- `message.usage.cache_creation_input_tokens` → cache create
- `message.model` → model used

**Cross-thread detection:** session ID stays constant within a thread. Multiple session files per project = multiple threads. CT counted by detecting references between threads.

**Token telemetry quality:** EXCELLENT. Claude Code is the reference platform.

**Reference implementation:** [extract_benchmark_window.py](../scoring/extract_benchmark_window.py) already does this extraction. The agent's Claude Code adapter should reuse its logic.

---

## ChatGPT adapter (P2)

**Source:** User-exported `conversations.json` from `chat.openai.com/settings/data-controls`.

**File format:** Single large JSON file with all conversations as a tree of mapping nodes.

**Key fields extracted:**
- `conversation.id` → `session_id`
- `conversation.create_time` → `started_at`
- `conversation.mapping[*].message.create_time` → message timestamps
- `conversation.mapping[*].message.author.role` → role
- `conversation.mapping[*].message.content.parts[*]` → content
- `conversation.mapping[*].metadata.model_slug` → model

**Limitation:** No native token counts. Estimate via tiktoken or similar.

**Cross-thread detection:** ChatGPT exports preserve cross-conversation links if `Memory` is enabled. Otherwise, detect lexical references.

**Token telemetry quality:** MEDIUM. Token counts must be estimated.

---

## Cursor adapter (P2)

**Source path:** Cursor session logs in `~/Library/Application Support/Cursor/User/workspaceStorage/` (macOS) or platform equivalent.

**File format:** SQLite databases with session data, plus some `.log` files.

**Key fields:**
- workspace_id → session grouping
- chat_id → session_id
- messages stored as SQLite rows with role + content
- token counts available if Cursor CLI logs are enabled

**Token telemetry quality:** GOOD with Cursor CLI logs, MEDIUM without.

---

## Gemini CLI adapter (P3)

**Source path:** `~/.gemini/sessions/` or similar (platform dependent).

**File format:** JSON sessions, similar structure to Claude Code.

**Key fields:**
- session_id, timestamps, role, content, model
- Gemini exposes token counts in newer versions

**Token telemetry quality:** GOOD for recent versions.

---

## Codex adapter (P3)

**Source:** ChatGPT Plus Codex session logs, accessible via OpenAI's data export or local Codex CLI cache.

**Token telemetry quality:** MEDIUM (similar to ChatGPT).

---

## Pi adapter (P4)

**Source:** Exported chats from Inflection's Pi.

**Token telemetry quality:** LOW (no token counts exposed by default).

---

## Generic JSON adapter (catch-all)

For platforms not directly supported, accept a generic JSON schema:

```json
{
  "schema_version": "generic-1.0",
  "platform": "custom",
  "sessions": [
    {
      "session_id": "string",
      "started_at": "ISO 8601",
      "ended_at": "ISO 8601",
      "model": "string (optional)",
      "messages": [
        {
          "role": "user|assistant|system",
          "content": "string",
          "timestamp": "ISO 8601 (optional)",
          "token_count": 123,
          "parent_message_id": "string (optional)"
        }
      ]
    }
  ]
}
```

Users can convert any platform's data to this format and submit.

---

## Adapter contract

Every adapter must implement:

```python
class Adapter(ABC):
    name: str
    platform: str
    file_glob: str

    @abstractmethod
    def detect(self, path: Path) -> bool:
        """Return True if this adapter can handle files at path."""

    @abstractmethod
    def list_sessions(self, path: Path) -> list[Path]:
        """Return list of session file paths."""

    @abstractmethod
    def parse_session(self, file: Path) -> Session:
        """Parse a single session file into Session model."""

    @abstractmethod
    def estimate_token_quality(self) -> str:
        """One of: 'excellent', 'good', 'medium', 'low'."""
```

---

## Token telemetry quality affects PROXY confidence

When the agent publishes a snapshot, it includes a `token_quality` flag:

```json
{
  ...
  "agent": {
    "version": "0.1.0",
    "platform": "claude_code",
    "token_quality": "excellent",
    ...
  }
}
```

Server uses this to set a confidence flag on the operator's score. Low-quality token telemetry → lower confidence → leaderboard rank is shown but with a `~` prefix and audit recommendation.

---

## Multi-platform operators

Operators using multiple platforms run multiple adapters. The agent merges sessions from all sources into a unified set.

For the snapshot payload:
- `platform.primary` = the platform with the most volume
- `platform.models` = all models seen across all sources
- Metrics are computed across the merged session set

This allows multi-platform operators to maintain a single SigRank profile.
