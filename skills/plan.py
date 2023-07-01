# plan about things that are going on
from core.completion import create_chat_completion
from core.memory import add_event, get_all_values_for_text
from core.utils import compose_prompt, write_log
from core.constants import agent_name


def get_skills():
    return {
        "plan": {
            "payload": {
                "name": "plan",
                "description": "Plan what you're going to do to achieve your goals or tasks.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "plan": {
                            "type": "string",
                            "description": "A detailed plan",
                        },
                    },
                    "required": ["plan"],
                },
            },
            "handler": plan,
        },
    }


def plan(arguments):
    plan = arguments.get("plan", None)
    values_to_replace = get_all_values_for_text(plan)
    user_prompt = compose_prompt("plan", values_to_replace)
    system_prompt = compose_prompt("system", values_to_replace)

    messages = [
        {
            "role": "system",
            "content": system_prompt,
        },
        {
            "role": "assistant",
            "content": user_prompt,
        },
    ]
    response = create_chat_completion(messages=messages)
    response_message = response.get("message", None)
    if response_message != None:
        response_message = "(planning) " + response_message
        add_event(response_message, agent_name, type="plan")