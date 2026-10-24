# Blueprint Studio Home Assistant Add-on Repository

Official Home Assistant Supervisor Add-on repository for [Blueprint Studio](https://github.com/ha-china/blueprint-studio).

[![Home Assistant Ingress](https://img.shields.io/badge/Home%20Assistant-Ingress-blue.svg)](https://www.home-assistant.io)
[![Version](https://img.shields.io/badge/version-3.0.3-green.svg)](https://github.com/soulripper13/blueprint-studio-addon)

Blueprint Studio is a powerful, integrated workspace for Home Assistant that combines visual blueprint creation, advanced YAML editing, Git version control, SFTP remote file management, an interactive web terminal, and an AI copilot.

---

## Add-ons in this Repository

| Add-on | Description |
| :--- | :--- |
| **[Blueprint Studio](blueprint-studio/)** | The full Blueprint Studio workspace seamlessly embedded in the Home Assistant sidebar via Ingress. |

---

## Installation

1. In your Home Assistant UI, go to **Settings** → **Add-ons** → **Add-on Store**.
2. Click the three dots (top right) → **Repositories**.
3. Add the following URL:
   ```text
   https://github.com/soulripper13/blueprint-studio-addon
   ```
4. Click **Add**, then close the dialog.
5. Search for **Blueprint Studio** and click **Install**.
6. Toggle **Show in sidebar**.
7. Click **Start**, then launch Blueprint Studio from your sidebar.

---

## Features

- **Full-featured YAML & File Editor**: Syntax highlighting, auto-complete for Home Assistant entities, services, and devices, live schema validation, bracket matching, and folding.
- **Visual Blueprint Studio**: Create, test, and export Home Assistant automations and script blueprints with visual form controls.
- **Built-in Git Version Control**: Stage, commit, push, pull, branch, and resolve merge conflicts with GitHub and Gitea integration.
- **Interactive Web Terminal**: Run shell commands directly in your configuration workspace.
- **Remote SFTP Management**: Browse, edit, and transfer files between Home Assistant and remote servers.
- **AI Copilot**: Grounded AI assistance supporting OpenAI, Anthropic, Gemini, Groq, Mistral, Ollama, and Home Assistant Conversation.
- **Secure Home Assistant Ingress**: Operates within an isolated Docker container while safely managing `/config` with zero external ports.

---

## Author & Maintainer

Maintained by **[@soulripper13](https://github.com/soulripper13)**.
Licensed under MIT.
