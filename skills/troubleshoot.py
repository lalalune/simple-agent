# think about things that are going on
from core.language import use_language_model, compose_prompt
from core.memory import add_event
from core.constants import agent_name


def get_skills():
    return {
        "troubleshoot": {
            "payload": {
                "name": "troubleshoot",
                "description": "Try to figure out what is wrong. Are we stuck in a loop? Is there an error? Assess how to fix out problem.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "assessment": {
                            "type": "string",
                            "description": "What do you think is wrong?",
                        },
                    },
                    "required": ["assessment"],
                },
            },
            "handler": troubleshoot,
        },
    }


def troubleshoot(arguments):
    assessment = arguments.get("assessment", None)
    user_prompt = compose_prompt("troubleshooting", assessment)

    messages = [
        {
            "role": "user",
            "content": user_prompt,
        },
    ]
    response = use_language_model(messages=messages)
    response_message = response.get("message", None)
    if response_message != None:
        add_event(response_message, agent_name, type="troubleshooting")