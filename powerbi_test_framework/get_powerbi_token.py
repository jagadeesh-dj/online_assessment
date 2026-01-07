# get_powerbi_token.py
from msal import ConfidentialClientApplication
from powerbi_test_framework.utils.logger import get_logger
import os
from dotenv import load_dotenv

load_dotenv()
logger = get_logger(__name__)

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TENANT_ID = os.getenv("TENANT_ID")

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPE = ["https://analysis.windows.net/powerbi/api/.default"]

def get_powerbi_token():
    """Generates and returns a Power BI access token using MSAL client credentials."""
    logger.info("Attempting to get Power BI token.")
    app = ConfidentialClientApplication(
        CLIENT_ID, authority=AUTHORITY, client_credential=CLIENT_SECRET
    )

    result = app.acquire_token_silent(SCOPE, account=None)
    if not result:
        logger.info("No token in cache, acquiring new token.")
        result = app.acquire_token_for_client(scopes=SCOPE)
    else:
        logger.info("Token acquired from cache.")

    if "access_token" not in result:
        logger.error(f"Token generation failed: {result.get('error_description', result)}")
        raise Exception(f"Token generation failed: {result.get('error_description', result)}")

    logger.info("Successfully acquired Power BI access token.")
    return result["access_token"]


if __name__ == '__main__':
    get_powerbi_token()
