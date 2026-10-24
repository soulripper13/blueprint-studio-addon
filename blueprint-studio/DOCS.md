# Home Assistant Add-on: Blueprint Studio

Blueprint Studio is a powerful, integrated workspace for Home Assistant that combines visual blueprint creation, advanced YAML editing, Git version control, SFTP remote file management, an interactive web terminal, and an AI copilot.

## Features

- **Full-featured YAML & File Editor**: Syntax highlighting, auto-complete for Home Assistant entities, services, and devices, live schema validation, bracket matching, and folding.
- **Visual Blueprint Studio**: Create, test, and export Home Assistant automations and script blueprints with visual form controls.
- **Built-in Git Version Control**: Stage, commit, push, pull, branch, and resolve merge conflicts with GitHub and Gitea integration.
- **Interactive Web Terminal**: Run shell commands directly in your configuration workspace.
- **Remote SFTP Management**: Browse, edit, and transfer files between Home Assistant and remote servers.
- **AI Copilot**: Grounded AI assistance supporting OpenAI, Anthropic, Gemini, Groq, Mistral, Ollama, and Home Assistant Conversation.
- **Home Assistant Ingress**: Seamlessly embedded into the Home Assistant sidebar with zero network exposure.

## Installation

1. Add this repository to your Home Assistant Add-on Store:
   `https://github.com/soulripper13/blueprint-studio-addon`
2. Find **Blueprint Studio** in the Add-on Store and click **Install**.
3. Toggle **Show in sidebar**.
4. Click **Start**, then open **Blueprint Studio** from the sidebar.

## Configuration

The add-on works out-of-the-box with default settings. You can customize the workspace directory and git branch in the **Configuration** tab.

| Option | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `home_dir` | string | `/homeassistant` | The root workspace directory to manage in Blueprint Studio and terminal (`/homeassistant`, `/share`, `/media`, `/ssl`, or any subfolder). |
| `default_branch` | string | `main` | Default branch used when initializing new Git repositories. |

## Network & Security

Blueprint Studio uses Home Assistant's secure **Ingress** system:
- No open ports are required on your router or local network.
- Authentication is handled directly by Home Assistant.
- Operates within an isolated container while safely managing `/config`.

## Support the Project ❤️

If you enjoy Blueprint Studio and would like to support ongoing maintenance and new features:
- **Ko-fi**: [https://ko-fi.com/soulripper13](https://ko-fi.com/soulripper13)
- **PayPal**: [https://paypal.me/SKatoaroo](https://paypal.me/SKatoaroo)
- **GitHub Sponsors**: [https://github.com/sponsors/soulripper13](https://github.com/sponsors/soulripper13)
