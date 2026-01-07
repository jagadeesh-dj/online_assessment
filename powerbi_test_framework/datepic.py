import requests
from get_powerbi_token import get_powerbi_token
from powerbi_test_framework.utils.logger import get_logger

logger = get_logger(__name__)

# Replace these with your details
GROUP_ID = "6182c697-e200-4ecd-9a3f-0d890351c639"
REPORT_ID = "ebe87da1-cdea-47a3-b4ff-b8a5effa0b0f"

def get_report_details():
    """Fetch Power BI report details such as name, dataset, and web URL."""
    logger.info("Fetching Power BI report details.")
    access_token = get_powerbi_token()

    url = f"https://api.powerbi.com/v1.0/myorg/groups/{GROUP_ID}/datasets/cef736e3-b904-4c1f-90a1-16a32a41e3eb/executeQueries"

    dax_query = {
        "queries": [
            {
                "query": """
                EVALUATE
                ROW(
                    "ReportDate", [TodayDate]
                )
                """
            }
        ]
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, json=dax_query)

    if response.status_code != 200:
        logger.error(f"Error: {response.status_code}")
        logger.error(response.text)
    else:
        result = response.json()["results"][0]["tables"][0]["rows"][0]
        logger.info(f'Report Date: {result["[ReportDate]"]}')



if __name__ == "__main__":
    get_report_details()
