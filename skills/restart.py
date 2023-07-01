# skills/restart.py

import os
import sys
from core.memory import add_event

def get_skills():
    return {
        "restart": {
            "payload": {
                "name": "restart",
                "description": "Restart yourself. Completely shut down and start back up.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "explanation": {
                            "type": "string",
                            "description": "Why are you restarting?",
                        },
                    },
                    "required": ["explanation"],
                },
            },
            "handler": restart,
        },
    }


def restart(arguments):
    explanation = arguments.get("explanation", None)
    add_event(
        "I am restarting. Explanation: " + explanation, type="restart"
    )
    python = sys.executable
    os.execl(python, python, *sys.argv)
