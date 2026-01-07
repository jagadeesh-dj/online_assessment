import pytest
# from powerbi_test_framework.utils.db_connection import get_sql_value, get_sql_table
from powerbi_test_framework.utils.powerbi_api import get_powerbi_data, get_powerbi_table
from powerbi_test_framework.get_powerbi_token import get_powerbi_token
import requests
from powerbi_test_framework.utils.logger import get_logger
from datetime import datetime, date
import json

import powerbi_test_framework.utils.loader as loader

logger = get_logger(__name__)
access_token = get_powerbi_token()

class TestBase:
    dataset_id = None
    group_id = "6182c697-e200-4ecd-9a3f-0d890351c639"
    report_id = "ebe87da1-cdea-47a3-b4ff-b8a5effa0b0f"

    @classmethod
    def setup_class(cls):

        logger.info("--- Test Suite Setup ---")
        logger.info(f"Fetching dataset ID for report '{cls.report_id}' in group '{cls.group_id}'.")
        url = f"https://api.powerbi.com/v1.0/myorg/groups/{cls.group_id}/reports/{cls.report_id}"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(url, headers=headers)
        data = response.json()
        cls.dataset_id = data.get("datasetId")
        assert cls.dataset_id, "Dataset ID not found from Power BI report API."
        logger.info(f"Successfully fetched dataset ID: {cls.dataset_id}")
        logger.info("--- Test Suite Setup Complete ---")

class TestDuplicate(TestBase):
    
    @pytest.mark.report("Weather_forecast_report")
    @pytest.mark.test_id("TC005_DEV_AUTO_TEST_CASE")
    def test_department_duplicate_card(self, test_msg):
        print(f"🔧 Config Loaded for {loader.ENVIRONMENT}")
        print(f"MONDAY_API_KEY: {loader.MONDAY_API_KEY}")
        print(f"MONDAY_API_URL: {loader.MONDAY_API_URL}")
        print(f"MONDAY_FILE_URL: {loader.MONDAY_FILE_URL}")
        print(f"BOARD_NAME: {loader.BOARD_NAME}")
        print(f"GROUP_NAME: {loader.GROUP_NAME}")
        print(f"REPORT_PATH: {loader.REPORT_PATH}")
        print(f"ENVIRONMENT: {loader.ENVIRONMENT}")
        
        logger.info("--- Test Case: test_department_filter_affects_quantity_card ---")
        logger.info("Objective: Verify that the 'Sum of quantity' card changes when a department filter is applied.")
        dax_unfiltered = '''
        EVALUATE
        SUMMARIZECOLUMNS(
            "Sum of quantity", SUM('healthcaredata healthcare_services'[quantity])
        )
        '''
        dax_filtered = '''
        EVALUATE
        SUMMARIZECOLUMNS(
            "Sum of quantity",
            CALCULATE(
                SUM('healthcaredata healthcare_services'[quantity]),
                'healthcaredata healthcare_services'[department] = "Cardiology"
            )
        )
        '''
        logger.info(f"Unfiltered DAX query: {dax_unfiltered}")
        df_unfiltered = get_powerbi_table(access_token, self.dataset_id, dax_unfiltered)
        logger.info(f"Filtered DAX query: {dax_filtered}")
        df_filtered = get_powerbi_table(access_token, self.dataset_id, dax_filtered)

        total_before = sum(row.get('[Sum of quantity]') for row in df_unfiltered)
        total_after = sum(row.get('[Sum of quantity]') for row in df_filtered)
        logger.info(f"Unfiltered result: {total_before}")
        logger.info(f"Filtered result: {total_after}")
        logger.info(f"Asserting that {total_before} != {total_after}")

        test_msg.set_messages(
            success="Duplicate Quantity card value did not change after applying Department filter.",
            failure="duplicate Quantity card value did not change after applying Department filter. failer",
            description="In essence, Pytest streamlines the testing process in Python, making it accessible for beginners while offering advanced features for complex testing scenarios, ultimately contributing to higher quality and more reliable software."
        )
        assert total_before != total_after
        logger.info("SUCCESS: Quantity card value changed as expected.")
        logger.info("--- Test Case: test_department_filter_affects_quantity_card Complete ---")