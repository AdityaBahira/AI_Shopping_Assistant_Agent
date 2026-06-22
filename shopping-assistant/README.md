# 🛍️ AI Shopping Assistant Agent

A production-ready AI shopping assistant for a retail store built using the **ADK 2.0 (Agent Development Kit)** and the **Gemini API**. It helps customers find products, answer questions, redeem discount codes, and award loyalty points securely.

---

## 🚀 Key Features

*   **Discount Code Redemption Tool**: A secure, single-use discount code redemption logic checking for codes like `WELCOME50` and `SUMMER20` for registered users.
*   **Loyalty Points Tool**: Awards loyalty points to registered users following successful purchases with built-in input validation.
*   **Security Gating**: Configured with a local **Semgrep** scanner and **Pre-commit hooks** to identify security vulnerabilities (like hardcoded API credentials).
*   **Pre-Tool Execution Hook**: Intercepts shell execution commands to block malicious actions (e.g. `rm -rf`).
*   **Threat Model**: Documented STRIDE threat model located at `threat_model.md`.

---

## 📁 Project Structure

```text
shopping-assistant/
├── .agents/                    # Customization directory
│   ├── CONTEXT.md              # Secure coding standards & TDD planning gate
│   ├── hooks.json              # Hook rules (intercepting command executions)
│   ├── scripts/                # Verification scripts (validate_tool_call.py)
│   └── skills/                 # Custom agent skills (stride-threat-model)
├── .semgrep/                   # Custom Semgrep configuration
│   └── rules.yaml              # Rules detecting hardcoded secrets
├── app/                        # Main application logic
│   ├── agent.py                # Main agent declaration & tool actions
│   └── agent_runtime_app.py    # FastAPI server wrapper for Agent Engine
├── tests/                      # Verification suite
│   ├── test_agent.py           # Security & business logic guardrail unit tests
│   └── unit/test_dummy.py      # Unit tests for tools
├── threat_model.md             # STRIDE threat model assessment
└── pyproject.toml              # Project dependencies (pre-commit, semgrep, ruff)
```

---

## 🛠️ Getting Started

### Prerequisites
Make sure you have:
*   [uv](https://docs.astral.sh/uv/getting-started/installation/) installed.
*   Your Gemini API key exported to your environment:
    ```powershell
    $env:GEMINI_API_KEY = "your-actual-api-key"
    ```

### 1. Installation
Install all dependencies using `uv`:
```bash
uvx google-agents-cli setup
agents-cli install
```

### 2. Launching the Local Playground
To chat with your agent in a visual UI:
```bash
agents-cli playground
```
This launches a development web server at `http://127.0.0.1:8080`.

---

## 🧪 Testing and Security Checks

### Run Unit Tests
Verify all business logic and tool safety guardrails pass:
```bash
uv run pytest tests/
```

### Run Linter & Type Checker
Perform code styling, syntax, and type checking:
```bash
agents-cli lint
```

### Trigger Pre-commit Security Checks
Run the pre-commit environment manually:
```bash
uv run pre-commit run --all-files
```
*(Note: This check is designed to fail/block because we hardcoded a simulated API key in `app/agent.py` to demonstrate security gating).*
