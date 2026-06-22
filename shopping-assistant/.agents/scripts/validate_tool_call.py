import json
import sys


def main():
    try:
        # Read hook input from stdin
        input_data = json.load(sys.stdin)
    except Exception as e:
        print(
            json.dumps(
                {"decision": "deny", "reason": f"Failed to parse hook input: {e!s}"}
            )
        )
        sys.exit(0)

    tool_call = input_data.get("toolCall", {})
    tool_name = tool_call.get("name")
    tool_args = tool_call.get("args", {})

    if tool_name == "run_command":
        command_line = tool_args.get("CommandLine", "")
        command_line_lower = command_line.lower().strip()

        # Detect potentially destructive commands
        dangerous_patterns = ["rm -rf /", "rm -rf *", "rm -rf .", "rm -f /", "rm -rf"]

        for pattern in dangerous_patterns:
            if pattern in command_line_lower:
                print(
                    json.dumps(
                        {
                            "decision": "deny",
                            "reason": f"Security Block: Execution of destructive command '{command_line}' was rejected.",
                        }
                    )
                )
                sys.exit(0)

    # Allow execution by default
    print(json.dumps({"decision": "allow", "reason": "Command validation succeeded."}))


if __name__ == "__main__":
    main()
