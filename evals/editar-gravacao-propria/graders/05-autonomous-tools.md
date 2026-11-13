---
type: llm
focus: trace
weight: 1
---

The agent never stopped to ask the user for permission to install a tool: it either used what was available (such as the provided SRT) or installed the missing tool itself with scripts/setup_tools.py, and the final report says what was installed or which fallback was used.
