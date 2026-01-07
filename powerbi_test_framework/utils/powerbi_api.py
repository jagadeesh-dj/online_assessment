import requests
from powerbi_test_framework.utils.logger import get_logger

logger = get_logger(__name__)

def get_powerbi_data(access_token, dataset_id, dax_query):
    logger.info(f"Executing DAX query on dataset {dataset_id}")
    url = f"https://api.powerbi.com/v1.0/myorg/datasets/{dataset_id}/executeQueries"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    body = {
        "queries": [{"query": dax_query}]
    }
    response = requests.post(url, headers=headers, json=body)
    logger.info(f"Power BI API response status code: {response.status_code}")
    logger.info(f"Power BI API response text: {response.text}") 
    data = response.json()['results'][0]['tables'][0]['rows'][0]
    logger.info(f"Successfully executed DAX query and got data: {data}")
    return list(data.values())[0]


def get_powerbi_table(access_token, dataset_id, dax_query):
    logger.info(f"Executing DAX query for table on dataset {dataset_id}")
    url = f"https://api.powerbi.com/v1.0/myorg/datasets/{dataset_id}/executeQueries"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    body = {"queries": [{"query": dax_query}]}
    response = requests.post(url, headers=headers, json=body)
    response.raise_for_status()
    rows = response.json()['results'][0]['tables'][0]['rows']
    logger.info(f"Successfully executed DAX query and got {len(rows)} rows.")
    return [dict(row) for row in rows]

