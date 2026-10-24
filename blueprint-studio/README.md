# Blueprint Studio for Home Assistant

[![Home Assistant Ingress](https://img.shields.io/badge/Home%20Assistant-Ingress-blue.svg)](https://www.home-assistant.io)
[![Version](https://img.shields.io/badge/version-3.0.4-green.svg)](https://github.com/soulripper13/blueprint-studio-addon)
[![Support Development](https://img.shields.io/badge/Support-Development-FF5E5B?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/soulripper13)
[![Support via PayPal](https://img.shields.io/badge/Support-PayPal-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/SKatoaroo)

**Blueprint Studio** is a complete, powerful, and secure developer workspace embedded right into your Home Assistant sidebar via Ingress. It brings together visual blueprint authoring, advanced YAML editing, Git version control, SFTP remote file synchronization, an interactive web terminal, and an AI copilot.

---

## ✨ Features

- **Full-featured YAML & File Editor**:
  - Live schema linting and validation for Home Assistant configurations.
  - Smart autocomplete for entities, services, and devices.
  - Multi-tab management, split-pane editing, bracket matching, code folding, and minimap.
  - Fast global regex search across all configuration files.

- **Visual Blueprint Studio**:
  - Visual authoring tool to build, customize, and export Home Assistant automation and script blueprints without syntax errors.

- **Built-in Git Version Control**:
  - Stage, commit, push, pull, and branch switching.
  - Visual diff viewer and three-way merge conflict resolution.
  - Secure GitHub and Gitea integration with OAuth device authentication.

- **Interactive Web Terminal**:
  - Full-featured bash terminal with xterm.js emulation directly inside your workspace.
  - Manage shell commands, run tests, and inspect logs.

- **Remote SFTP Management**:
  - Dual-pane file manager to transfer, upload, and synchronize files between Home Assistant and remote servers.

- **Multi-Provider AI Copilot**:
  - Context-aware code generation and error explanation.
  - Supports Anthropic Claude, OpenAI, Google Gemini, Groq, Mistral, Ollama, and Home Assistant Conversation.

- **Secure Home Assistant Ingress**:
  - Runs in an isolated Docker container with zero port forwarding required.
  - Fully authenticated and protected by Home Assistant Core.

---

## ⚙️ Configuration & Custom Home Directory

You can choose whichever directory you want Blueprint Studio to manage by visiting the **Configuration** tab:

| Option | Default | Description |
| :--- | :--- | :--- |
| `home_dir` | `/homeassistant` | The root workspace directory to manage in the editor and terminal. |
| `default_branch` | `main` | Default branch name when initializing new Git repositories. |

### Supported Workspace Locations:
- **`/homeassistant`** *(Default)*: Manage your primary Home Assistant configuration (`configuration.yaml`, automations, blueprints, custom components).
- **`/share`**: Manage shared files, network storage, and exports.
- **`/media`**: Manage local media files, audio, and images.
- **`/ssl`**: View and manage SSL certificates.
- **Subdirectories**: Point directly to a specific project folder like `/homeassistant/blueprints` or `/homeassistant/custom_components`.

---

## 🚀 Getting Started

1. Click **Start** on this add-on page.
2. Toggle **Show in sidebar** so you can open Blueprint Studio anytime with one click.
3. Click **Open Web UI** (or launch from the sidebar) to begin editing!

---

## ☕ Support the Project

Blueprint Studio is developed and maintained in spare time for the Home Assistant community. If you enjoy using it, your support is greatly appreciated!

- **Ko-fi**: [https://ko-fi.com/soulripper13](https://ko-fi.com/soulripper13)
- **PayPal**: [https://paypal.me/SKatoaroo](https://paypal.me/SKatoaroo)
- **GitHub Sponsors**: [https://github.com/sponsors/soulripper13](https://github.com/sponsors/soulripper13)
- **Author**: [@soulripper13](https://github.com/soulripper13)
