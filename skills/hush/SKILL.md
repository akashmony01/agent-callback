---
name: hush
description: Silence agent-callback alerts (sound and notifications) for every session at once.
disable-model-invocation: true
allowed-tools: Bash(${CLAUDE_PLUGIN_ROOT}/bin/agent-callback hush)
---

Run this command and report its output in one short line. Do nothing else.

```bash
${CLAUDE_PLUGIN_ROOT}/bin/agent-callback hush
```
