

import os
from dotenv import load_dotenv

load_dotenv()
DB_URL = (
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)
FASTF1_CACHE = os.getenv("FASTF1_CACHE")