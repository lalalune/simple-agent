# think about things that are going on
from core.completion import create_chat_completion
from core.memory import add_event, get_all_values_for_text, get_functions
from core.skill_handling import use_skill
from core.utils import compose_prompt, write_log
from core.constants import agent_name


def get_skills():
    return {
        "think": {
            "payload": {
                "name": "think",
                "description": "Think about a topic, consider what to do next or dig into a creative impulse.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "The topic to think about",
                        },
                    },
                    "required": ["topic"],
                },
            },
            "handler": think,
        },
    }


def think(arguments):
    print("thinking")
    topic = arguments.get("topic", None)
    values_to_replace = get_all_values_for_text(topic)
    user_prompt = compose_prompt("thought", values_to_replace)
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
        response_message = "(thinking) " + response_message
        add_event(response_message, agent_name, type="thought")