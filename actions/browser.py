# actions/browser.py

import uuid

from core.events import create_event
from agentbrowser import browser


def create_page(arguments):
    site = arguments.get("site")
    page = browser.loop.run_until_complete(browser.browser.newPage())
    page_id = str(uuid.uuid4())
    create_event(
        "I created a new page in the virtual browser for page ID " + page_id,
        type="virtual_browser",
    )
    # if site is not null
    if site:
        browser.loop.run_until_complete(page.goto(site))
        create_event(
            "I navigated to " + site + " in the virtual browser for page ID " + page_id,
            type="virtual_browser",
        )
    browser.pages[page_id] = page
    return page_id


def close_page(arguments):
    page_id = arguments.get("page_id")
    if page_id in browser.pages:
        page = browser.pages[page_id]
        browser.loop.run_until_complete(page.close())
        del browser.pages[page_id]
        if browser.current_page_id == page_id:
            browser.current_page_id = None
        create_event(
            "I closed a page in the virtual browser for page ID " + page_id,
            type="virtual_browser",
        )
    else:
        create_event(
            "I tried to close a page in the virtual browser, but it didn't exist. The page ID was "
            + page_id,
            type="virtual_browser",
        )
        raise ValueError(f"Page ID {page_id} does not exist.")


def navigate_to(arguments):
    url = arguments.get("url")
    if not browser.current_page_id:
        raise ValueError("No active page.")

    page = browser.pages[browser.current_page_id]
    browser.loop.run_until_complete(page.goto(url))
    create_event(
        "I navigated to "
        + url
        + " in the virtual browser for page ID "
        + browser.current_page_id,
        type="virtual_browser",
    )


def get_html(arguments):
    if not browser.current_page_id:
        raise ValueError("No active page.")

    page = browser.pages[browser.current_page_id]

    create_event(
        "I got the HTML from the virtual browser for page ID "
        + browser.current_page_id,
        type="virtual_browser",
    )

    return browser.loop.run_until_complete(page.content())


def get_body_text(arguments):
    if not browser.current_page_id:
        raise ValueError("No active page.")

    page = browser.pages[browser.current_page_id]

    create_event(
        "I got the text from the virtual browser for page ID "
        + browser.current_page_id,
        type="virtual_browser",
    )

    return browser.loop.run_until_complete(
        page.Jeval("body", "(element) => element.textContent")
    )


def search_google(arguments):
    query = arguments.get("query")
    navigate_to({"url": "https://www.google.com/search?q=" + query})
    create_event(
        "I searched Google for "
        + query
        + " in the virtual browser for page ID "
        + browser.current_page_id,
        type="virtual_browser",
    )


def execute_pyppeteer_code(arguments):
    code = arguments.get("code")
    create_event(
        "I tried to execute the following code in the virtual browser for page ID "
        + browser.current_page_id
        + ": "
        + code,
        type="virtual_browser",
    )
    if not browser.current_page_id:
        create_event(
            "I tried to execute code in the virtual browser, but there was no active page.",
            type="virtual_browser",
        )
        raise ValueError("No active page.")
    else:
        page = browser.pages[browser.current_page_id]
        browser.loop.run_until_complete(page.evaluate(code))
        create_event(
            "I executed code in the virtual browser for page ID "
            + browser.current_page_id,
            type="virtual_browser",
        )


def get_form_data(arguments):
    if not browser.current_page_id:
        raise ValueError("No active page.")

    page = browser.pages[browser.current_page_id]
    form_data = browser.loop.run_until_complete(
        page.Jeval(
            "form",
            """(form) => {
        let elements = form.elements;
        let data = {};
        for (let i = 0; i < elements.length; i++) {
            if (elements[i].name) {
                data[elements[i].name] = elements[i].value;
            }
        }
        return data;
    }""",
        )
    )
    return form_data


def fill_form_and_submit(arguments):
    data = arguments.get("data")
    if not browser.current_page_id:
        raise ValueError("No active page.")

    page = browser.pages[browser.current_page_id]
    browser.loop.run_until_complete(
        page.evaluate(
            """(data) => {
        let form = document.querySelector('form');
        for (let name in data) {
            form.elements[name].value = data[name];
        }
        form.submit();
    }""",
            data,
        )
    )


def get_actions():
    return {
        "browser_create_tab": {
            "function": {
                "name": "browser_create_tab",
                "description": "Create a new page in the virtual browser and switch to it.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "site": {
                            "type": "string",
                            "description": "The site to go to in the new page.",
                        },
                    },
                    "required": [],
                },
            },
            "suggest_next_actions": [],
            "ignore_next_actions": [],
            "handler": create_tab,
        },
        "browser_switch_to": {
            "function": {
                "name": "browser_switch_to",
                "description": "Switch to an existing page in the virtual browser.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "page_id": {
                            "type": "string",
                            "description": "The id of the page/page to switch to.",
                        },
                    },
                    "required": ["page_id"],
                },
            },
            "suggest_next_actions": [],
            "ignore_next_actions": [],
            "handler": switch_to,
        },
        "execute_pyppeteer_code": {
            "function": {
                "name": "execute_pyppeteer_code",
                "description": "Execute arbitrary Pyppeteer code in the virtual browser.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "The Pyppeteer code to execute. Called using evaluate()",
                        },
                    },
                    "required": ["code"],
                },
            },
            "suggest_next_actions": [],
            "ignore_next_actions": [],
            "handler": execute_pyppeteer_code,
        },
        "browser_close_tab": {
            "function": {
                "name": "browser_close_tab",
                "description": "Close an existing page in the virtual browser.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "page_id": {
                            "type": "string",
                            "description": "The id of the page/page to close.",
                        },
                    },
                    "required": ["page_id"],
                },
            },
            "suggest_next_actions": [],
            "ignore_next_actions": [],
            "handler": close_tab,
        },
        "browser_navigate_to": {
            "function": {
                "name": "browser_navigate_to",
                "description": "Navigate to a URL in the current page of the virtual browser.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "The URL to navigate to.",
                        },
                    },
                    "required": ["url"],
                },
            },
            "suggest_next_actions": [],
            "ignore_next_actions": [],
            "handler": navigate_to,
        },
        "browser_get_html": {
            "function": {
                "name": "browser_get_html",
                "description": "Get the HTML content of the current page in the virtual browser.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "description": {
                            "type": "object",
                            "description": "What are we trying to do?.",
                        },
                    },
                    "required": ["description"],
                },
            },
            "suggest_next_actions": [],
            "ignore_next_actions": [],
            "handler": get_html,
        },
        "browser_get_body_text": {
            "function": {
                "name": "browser_get_body_text",
                "description": "Get all text from the body of the current page in the virtual browser.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "description": {
                            "type": "object",
                            "description": "What are we trying to do?.",
                        },
                    },
                    "required": ["description"],
                },
            },
            "suggest_next_actions": [],
            "ignore_next_actions": [],
            "handler": get_body_text,
        },
        "browser_search_google": {
            "function": {
                "name": "browser_search_google",
                "description": "Search google with the provided query.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The query to search in google.",
                        },
                    },
                    "required": ["query"],
                },
            },
            "suggest_next_actions": [],
            "ignore_next_actions": [],
            "handler": search_google,
        },
        "browser_get_form_data": {
            "function": {
                "name": "browser_get_form_data",
                "description": "Get all data from the first form on the current page in the virtual browser.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "description": {
                            "type": "object",
                            "description": "What are we trying to do?.",
                        },
                    },
                    "required": ["description"],
                },
            },
            "suggest_next_actions": [],
            "ignore_next_actions": [],
            "handler": get_form_data,
        },
        "browser_fill_form_and_submit": {
            "function": {
                "name": "browser_fill_form_and_submit",
                "description": "Fill out and submit the first form on the current page in the virtual browser.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "data": {
                            "type": "object",
                            "description": "The data to fill out in the form.",
                        },
                    },
                    "required": ["data"],
                },
            },
            "suggest_next_actions": [],
            "ignore_next_actions": [],
            "handler": fill_form_and_submit,
        },
    }
