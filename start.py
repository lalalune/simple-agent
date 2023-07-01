import os
import shutil

# set TOKENIZERS_PARALLELISM environment variable to False to avoid warnings
os.environ["TOKENIZERS_PARALLELISM"] = "False"

# if .env doesn't exist, copy .env.example to .env
if not os.path.exists(".env"):
    shutil.copy(".env.example", ".env")
    print("Please edit the .env file and add your API key, then restart the agent")
    exit()

import time

from core.skills import register_skills

import core.loop

register_skills()

while True:
    time.sleep(int(os.getenv("UPDATE_INTERVAL")) or 7)
    core.loop.main()
