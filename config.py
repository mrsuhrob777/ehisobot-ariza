import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN") or "8891098308:AAHaVSxWlvTi1c8ku9hDBXpRbAvf6pPxoLM"
ADMIN_ID = int(os.getenv("ADMIN_ID", "7959327686"))
GROUP_ID = int(os.getenv("GROUP_ID", "-1004333077883"))
