# Contains utilities for creating and managing OpenAI GPT-3 based conversations.
# It also involves writing the chat logs and managing the token counts of messages.
import sys

# if this module is run directly, set the sys path to ../
if __name__ == "__main__":
    sys.path.append("../")

import os
import openai
import tiktoken
from core.memory import add_event
from datetime import datetime

from core.constants import (
    default_text_model,
    default_max_tokens,
    long_text_model,
    openai_api_key,
    agent_name,
)

# Set OpenAI API key
openai.api_key = openai_api_key

# Get encoding for default text model
encoding = tiktoken.encoding_for_model(default_text_model)

def use_language_model(messages, functions=None, long=False):
    """
    Creates a chat completion using OpenAI API and writes the completion to a log file.
    
    Parameters:
    messages: List of message objects to be sent to the chat model.
    functions: List of function calls to be sent to the chat model (Optional).
    long: If true, uses the long text model. Default is the default text model (Optional).
    
    Returns:
    A dictionary containing the response message and an optional function call.
    """

    # Select model based on the 'long' parameter
    model = long_text_model if long else default_text_model
    messages = trim_messages(messages, default_max_tokens)
    # Make API request and get response
    if(functions):
        response = openai.ChatCompletion.create(
            model=model, messages=messages, functions=functions
        )
    else:
        response = openai.ChatCompletion.create(model=model, messages=messages)

    # Log model, functions, messages, and response to a text file
    file_content = f"*** MODEL: {model}\n*** FUNCTIONS: {functions}\n*** MESSAGES: {messages}\n*** RESPONSE: {response}"

    # Create directory if not exists
    os.makedirs("logs/completions", exist_ok=True)

    # Get current timestamp
    now = datetime.now()

    # Write the log file with timestamp
    with open("logs/completions/" + now.strftime("%Y-%m-%d_%H-%M-%S") + ".txt", "w") as f:
        f.write(file_content)

    # Extract response content and function call from response
    response_data = response["choices"][0]["message"]
    message = response_data["content"]
    function_call = response_data.get("function_call")

    return {"message": message, "function_call": function_call}

def trim_messages(messages, max_tokens):
    """
    Trims the messages to fit within the max token limit.
    If there are too many tokens, the messages are trimmed from the top.
    
    Parameters:
    messages: List of message objects to be trimmed.
    max_tokens: Maximum token limit.
    
    Returns:
    A list of trimmed message objects.
    """

    new_messages = []
    tokens_per_message = 3
    tokens_per_name = 1
    original_num_tokens = count_tokens_from_chat_messages(messages)

    if original_num_tokens <= max_tokens:
        return messages
    
    # quick shortcut - remove the system message, then check if it fits
    # find any messages in messages that are system messages ("role": "system")
    system_messages = [message for message in messages if message.get("role") == "system"]
    if system_messages:
        # remove all system messages from messages
        messages = [message for message in messages if message not in system_messages]
        # check if the messages fit
        new_num_tokens = count_tokens_from_chat_messages(messages)
        if new_num_tokens <= max_tokens:
            return messages

    # Calculate the total number of tokens used and remove messages if over the limit
    num_tokens = 0
    break_outer = False
    for message in messages:
        if break_outer:
            break

        num_tokens_temp = num_tokens + tokens_per_message
        for key, value in message.items():
            num_tokens_temp += tokens_per_name if key == "name" else len(encoding.encode(value))

            if num_tokens_temp > max_tokens:
                break_outer = True
                break

        if not break_outer:
            new_messages.append(message)
            num_tokens = num_tokens_temp

    if not new_messages:
        # If no messages are included, include the last message of messages.
        # Ensure that it does not exceed max_tokens by trimming it.
        new_messages.append(trim_last_message(messages, max_tokens))

    return new_messages

def trim_last_message(messages, max_tokens):
    """
    Trim the last message to fit within the max token limit.
    
    Parameters:
    messages: List of message objects, where the last message will be trimmed.
    max_tokens: Maximum token limit.
    
    Returns:
    A trimmed message object.
    """

    message = messages[-1]
    new_num_tokens = count_tokens_from_chat_messages([message])

    while new_num_tokens > max_tokens:
        message["content"] = message["content"][10:]  # remove the first 10 characters from the message
        new_num_tokens = count_tokens_from_chat_messages([message])

    return message

def count_tokens_from_chat_messages(messages):
    """
    Counts the number of tokens in a list of chat messages.
    
    Parameters:
    messages: List of message objects.
    
    Returns:
    The total number of tokens in the messages.
    """

    tokens_per_message = 3
    tokens_per_name = 1
    num_tokens = 0

    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += tokens_per_name if key == "name" else len(encoding.encode(value))

    return num_tokens

def count_tokens(text):
    """
    Counts the number of tokens in a piece of text.
    
    Parameters:
    text: The text to be tokenized.
    
    Returns:
    The total number of tokens in the text.
    """

    return len(encoding.encode(text))

def compose_prompt(prompt_template_name, values_to_replace):
    """
    Given a template name and a dictionary of values, create a formatted string.

    prompt_template_name: the filename of the template, excluding extension
    values_to_replace: a dictionary where keys are placeholders in the template and values are the substitutions
    """
    # Fetch the template based on the template name
    prompt_template = get_prompt_template(prompt_template_name)

    # Substitute placeholders in the template with the corresponding values
    prompt_template = replace_all_in_string(prompt_template, values_to_replace)

    return prompt_template

def replace_all_in_string(string, replacements):
    """
    Replace all placeholders in the string with corresponding values.

    string: the string that contains placeholders
    replacements: a dictionary where keys are placeholders and values are the replacements
    """
    for key, value in replacements.items():
        string = string.replace("{" + key + "}", value)
    return string

def get_prompt_template(template_name):
    """
    Reads the content of a template file and returns it as a string.

    template_name: the filename of the template, excluding extension
    """
    # Build the template file path and open the file
    with open(f"templates/{template_name}.txt", "r") as f:
        # Read the file content and return it
        return f.read()

def messages_to_dialogue(messages):
    """
    Converts a list of messages into a string dialogue.

    messages: a dictionary that contains message ids, metadatas and documents
    """
    dialogue = "\n".join(
        f'{msg_meta["event_creator"]}: {msg_doc}'
        for msg_meta, msg_doc in zip(messages["metadatas"], messages["documents"])
    )
    return dialogue


if __name__ == "__main__":
    # Tests for trimmed_messages function
    test_messages = [{"role": "system", "content": "This is a test of the system."}, {"role": "user", "content": "Hi, how are you?"}]
    trimmed_messages = trim_messages(test_messages, 1000)
    assert test_messages == trimmed_messages
    test_messages = [{"role": "system", "content": "This is a test of the system."}, {"role": "user", "content": "123" + "0" * 8000 + "456"}]
    trimmed_messages = trim_messages(test_messages, 100)
    assert len(trimmed_messages) == 1
    assert trimmed_messages[0]["role"] == "user"
    assert trimmed_messages[0]["content"].endswith("456")

    # Tests for count_tokens_from_chat_messages function
    test_messages = [{"role": "system", "content": "This is a test of the system."}, {"role": "user", "content": "Hi, how are you?"}]
    assert count_tokens_from_chat_messages(test_messages) == 22 or (count_tokens_from_chat_messages(test_messages) > 18 and count_tokens_from_chat_messages(test_messages) < 26)

    # Tests for count_tokens function
    test_text = "This is a test."
    assert count_tokens(test_text) == 5 or (count_tokens(test_text) > 3 and count_tokens(test_text) < 7)

    # Tests for replace_all_in_string function
    string = "Hello {name}, how are you?"
    replacements = {"name": "John"}
    assert replace_all_in_string(string, replacements) == "Hello John, how are you?"

    # Tests for get_prompt_template function
    # For this test, you need a file named `test.txt` in `templates/` directory with content: "Hello, how are you?"
    template_name = "test"
    assert get_prompt_template(template_name) == "This file is used for test validation, please don't touch it."

    # Tests for messages_to_dialogue function
    messages = {"metadatas": [{"event_creator": "User"}], "documents": ["Hi, how are you?"]}
    assert messages_to_dialogue(messages) == "User: Hi, how are you?"

    print("All tests passed!")