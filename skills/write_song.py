# think about things that are going on
from core.language import use_language_model, compose_prompt
from core.memory import add_event, get_all_values_for_text
from core.constants import agent_name


def get_skills():
    return {
        "write_song": {
            "payload": {
                "name": "write_song",
                "description": "Write a song about everything that is going on.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "The topic to think about. Can be detailed and complicated.",
                        },
                    },
                    "required": ["topic"],
                },
            },
            "handler": write_song,
        },
    }


def write_song(arguments):
    topic = arguments.get("topic", None)
    values_to_replace = get_all_values_for_text(topic)
    user_prompt = compose_prompt("song", values_to_replace)
    # replace {topic} with topic in user_prompt
    user_prompt = user_prompt.replace("{topic}", topic)

    messages = [
        {
            "role": "user",
            "content": user_prompt,
        },
    ]
    response = use_language_model(messages=messages)
    response_message = response.get("message", None)
    if response_message != None:
        add_event(response_message, agent_name, type="song")