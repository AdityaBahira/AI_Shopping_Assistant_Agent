# Threat Modeling Assessment: `shopping-assistant`

This document details the STRIDE threat modeling assessment conducted on the `shopping-assistant` codebase and architecture.

---

## 1. System Boundaries and Data Flow

### System Entry Points
*   **Agent Runtime App (`app/agent_runtime_app.py`)**: Exposes the `async_stream_query` interface for user queries and the `register_feedback` interface for scoring.
*   **LLM Tool Execution**: The `redeem_discount_code` tool is executed by the agent runtime on behalf of the user when requested.

### Data Storage & External Connections
*   **Memory Store (`app/agent.py`)**: In-memory databases `DISCOUNT_CODES` and `REGISTERED_USERS`.
*   **Model API Connection**: Custom `Gemini` client connection using a hardcoded mock API key (`AIzaSyD-mock-key-value-12345`).

---

## 2. STRIDE Assessment

### 👤 Spoofing (Identity Spoofing)
*   **Finding**: The tool `redeem_discount_code(user_id: str, code: str)` accepts `user_id` as a raw argument.
*   **Risk**: The system lacks cryptographic session or token verification to prove that the caller is indeed `user_id`. An attacker can spoof their identity (e.g., claiming to be `kaggle_student` in their chat inputs), and the LLM will forward that identity to the tool.
*   **Severity**: **HIGH**

### 💾 Tampering (Data Modification)
*   **Finding**: `DISCOUNT_CODES` is stored as a global in-memory dictionary.
*   **Risk**:
    *   State is lost on process restart, resetting all single-use discount code redemptions.
    *   Lack of transaction locks or concurrency-safe checks creates a Time-of-Check to Time-of-Use (TOCTOU) race condition, allowing concurrent requests to redeem a single-use code multiple times.
*   **Severity**: **MEDIUM**

### 📜 Repudiation (Non-Repudiation Failures)
*   **Finding**: Transactions are marked in-memory on the `DISCOUNT_CODES` dictionary with no persistent audit trails.
*   **Risk**: If a discount is contested or abused, there is no permanent, tamper-resistant transaction log (e.g., in a database or dedicated audit trail) to prove who performed the redemption.
*   **Severity**: **LOW**

### 🔑 Information Disclosure (Data Leakage)
*   **Finding**: The simulated API key is hardcoded directly inside `app/agent.py` (`api_key = "AIzaSyD-mock-key-value-12345"`).
*   **Risk**: Secrets checked into codebases will be leaked via version control (e.g., Git history).
*   **Severity**: **HIGH** (Simulated for gating demonstration)

### 💥 Denial of Service (Service Exhaustion)
*   **Finding**: The application does not implement rate limiting on prompt inputs or tool executions.
*   **Risk**: Malicious users can flood the agent with rapid-fire inputs, causing downstream model rate limits to be hit, exhausting API credits, or depleting application runtime resources.
*   **Severity**: **MEDIUM**

### 🔓 Elevation of Privilege (Access Bypass)
*   **Finding**: Access to `redeem_discount_code` is governed entirely by the LLM agent's behavior.
*   **Risk**: Through Prompt Injection, a malicious user can manipulate the LLM agent to bypass user registration checks, overwrite context variables, or execute tools with arguments they shouldn't have access to.
*   **Severity**: **HIGH**

---

## 3. Mitigation Strategy

1.  **Authentication**: Pass a cryptographically signed user token (JWT) from the client web layer to the runtime, and let the backend decode and verify the `user_id` before passing it to the tool.
2.  **Secret Management**: Replace the hardcoded API key in `app/agent.py` with environment variable resolution (`os.environ.get("GEMINI_API_KEY")`) or GCP Secret Manager.
3.  **Concurrency Locking**: Implement threading/async locks when updating the state of `DISCOUNT_CODES` to prevent race conditions.
4.  **Persistent Audit Logs**: Write transaction logs to a persistent database (e.g., Cloud SQL or Firestore) during the tool execution phase.
