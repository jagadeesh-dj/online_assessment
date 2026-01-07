import pytest
from powerbi_test_framework.utils.db_connection import get_sql_value
from powerbi_test_framework.utils.powerbi_api import get_powerbi_data, get_powerbi_table
from powerbi_test_framework.get_powerbi_token import get_powerbi_token
import requests
from powerbi_test_framework.utils.logger import get_logger
from datetime import datetime, date
import json

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

# class TestDepartmentFilterLogic(TestBase):
#
#     @pytest.mark.test_id("TC001_DEV_AUTO_TEST_CASE")
#     def test_department_filter_affects_quantity_card(self, test_msg):
#         logger.info("--- Test Case: test_department_filter_affects_quantity_card ---")
#         logger.info("Objective: Verify that the 'Sum of quantity' card changes when a department filter is applied.")
#         dax_unfiltered = '''
#         EVALUATE
#         SUMMARIZECOLUMNS(
#             "Sum of quantity", SUM('healthcaredata healthcare_services'[quantity])
#         )
#         '''
#         dax_filtered = '''
#         EVALUATE
#         SUMMARIZECOLUMNS(
#             "Sum of quantity",
#             CALCULATE(
#                 SUM('healthcaredata healthcare_services'[quantity]),
#                 'healthcaredata healthcare_services'[department] = "Cardiology"
#             )
#         )
#         '''
#         logger.info(f"Unfiltered DAX query: {dax_unfiltered}")
#         df_unfiltered = get_powerbi_table(access_token, self.dataset_id, dax_unfiltered)
#         logger.info(f"Filtered DAX query: {dax_filtered}")
#         df_filtered = get_powerbi_table(access_token, self.dataset_id, dax_filtered)
#
#         total_before = sum(row.get('[Sum of quantity]') for row in df_unfiltered)
#         total_after = sum(row.get('[Sum of quantity]') for row in df_filtered)
#         logger.info(f"Unfiltered result: {total_before}")
#         logger.info(f"Filtered result: {total_after}")
#         logger.info(f"Asserting that {total_before} != {total_after}")
#
#         test_msg.set_messages(
#             success="Quantity card value changed as expected after applying Department filter",
#             failure="Quantity card value did not change after applying Department filter",
#             description="Quantity descriptin"
#         )
#
#         assert total_before != total_after
#         logger.info("SUCCESS: Quantity card value changed as expected.")
#         logger.info("--- Test Case: test_department_filter_affects_quantity_card Complete ---")
#
#     @pytest.mark.test_id("TC002_DEV_AUTO_TEST_CASE")
#     def test_department_filter_affects_profit_card(self, test_msg):
#         logger.info("--- Test Case: test_department_filter_affects_profit_card ---")
#         logger.info("Objective: Verify that the 'Sum of profit' card value updates for the selected department.")
#         dax_unfiltered = '''
#         EVALUATE
#         ROW(
#             "Sum of profit",
#             SUM('healthcaredata healthcare_services'[profit])
#         )
#         '''
#         dax_filtered = '''
#         EVALUATE
#         ROW(
#             "Sum of profit",
#             CALCULATE(
#                 SUM('healthcaredata healthcare_services'[profit]),
#                 'healthcaredata healthcare_services'[department] = "Cardiology"
#             )
#         )
#         '''
#         logger.info(f"Unfiltered DAX query: {dax_unfiltered}")
#         df_unfiltered = get_powerbi_table(access_token, self.dataset_id, dax_unfiltered)
#         logger.info(f"Filtered DAX query: {dax_filtered}")
#         df_filtered = get_powerbi_table(access_token, self.dataset_id, dax_filtered)
#
#         profit_before = sum(row.get('[Sum of profit]') for row in df_unfiltered)
#         profit_after = sum(row.get('[Sum of profit]') for row in df_filtered)
#         logger.info(f"Unfiltered result: {profit_before}")
#         logger.info(f"Filtered result: {profit_after}")
#         logger.info(f"Asserting that {profit_before} != {profit_after}")
#
#         test_msg.set_messages(
#             success="Profit card did not update after applying Department filter.",
#             failure="Profit card did not update after applying Department filter.",
#             description="Profit descriptin"
#         )
#         assert profit_before == profit_after, "Profit card did not update after applying Department filter."
#         logger.info("SUCCESS: Profit card value changed as expected.")
#         logger.info("--- Test Case: test_department_filter_affects_profit_card Complete ---")
#
#     @pytest.mark.test_id("TC003_DEV_AUTO_TEST_CASE")
#     def test_department_filter_affects_total_amount_by_department_chart(self, test_msg):
#         logger.info("--- Test Case: test_department_filter_affects_total_amount_by_department_chart ---")
#         logger.info("Objective: Verify that the 'Sum of total amount' card value updates for the selected department.")
#         dax_unfiltered = '''
#         EVALUATE
#         ROW(
#             "Sum of total_amount",
#             SUM('healthcaredata healthcare_services'[total_amount])
#         )
#         '''
#         dax_filtered = '''
#         EVALUATE
#         ROW(
#             "Sum of total_amount",
#             CALCULATE(
#                 SUM('healthcaredata healthcare_services'[total_amount]),
#                 'healthcaredata healthcare_services'[department] = "Cardiology"
#             )
#         )
#         '''
#         logger.info(f"Unfiltered DAX query: {dax_unfiltered}")
#         df_unfiltered = get_powerbi_table(access_token, self.dataset_id, dax_unfiltered)
#         logger.info(f"Filtered DAX query: {dax_filtered}")
#         df_filtered = get_powerbi_table(access_token, self.dataset_id, dax_filtered)
#
#         profit_before = sum(row.get('[Sum of total_amount]') for row in df_unfiltered)
#         profit_after = sum(row.get('[Sum of total_amount]') for row in df_filtered)
#         logger.info(f"Unfiltered result: {profit_before}")
#         logger.info(f"Filtered result: {profit_after}")
#         logger.info(f"Asserting that {profit_before} != {profit_after}")
#
#         test_msg.set_messages(
#             success="Total amount card did not update after applying Department filter.",
#             failure="Total amount card update after applying Department filter.",
#             description="total amount description"
#         )
#         assert profit_before == profit_after
#         logger.info("SUCCESS: Total amount card value changed as expected.")
#         logger.info("--- Test Case: test_department_filter_affects_total_amount_by_department_chart Complete ---")
#
# class TestDateValidation():
#
#     @pytest.mark.test_id("TC004_DEV_AUTO_TEST_CASE")
#     def test_date_validation(self, test_msg):
#         group_id = "6182c697-e200-4ecd-9a3f-0d890351c639"
#         report_id = "ebe87da1-cdea-47a3-b4ff-b8a5effa0b0f"
#
#         headers = {"Authorization": f"Bearer {access_token}"}
#
#         # Get report details to fetch dataset_id
#         url_report = f"https://api.powerbi.com/v1.0/myorg/groups/{group_id}/reports/{report_id}"
#         report_response = requests.get(url_report, headers=headers)
#         report_data = report_response.json()
#         dataset_id = report_data.get("datasetId")
#
#         # Get all pages of the report
#         url_pages = f"https://api.powerbi.com/v1.0/myorg/groups/{group_id}/reports/{report_id}/pages"
#         pages_response = requests.get(url_pages, headers=headers)
#         pages = pages_response.json().get("value", [])
#
#         # System date
#         system_date = date(2026,11,12)
#
#         success_pages = []
#         failed_pages = []
#
#         # Loop through each page and validate date
#         for page in pages:
#
#             page_name = page.get("name")
#
#             # Construct DAX query to get current date from the report
#             dax_query = {
#                 "queries": [
#                     {
#                         "query": f"EVALUATE ROW(\"CurrentDate\", TODAY())"
#                     }
#                 ]
#             }
#
#             url_dax = f"https://api.powerbi.com/v1.0/myorg/groups/{group_id}/datasets/{dataset_id}/executeQueries"
#             dax_response = requests.post(url_dax, headers={**headers, "Content-Type": "application/json"}, json=dax_query)
#             dax_data = dax_response.json()['results'][0]['tables'][0]['rows']
#             # Extract the date from DAX response
#             report_date_str = dax_data[0]['[CurrentDate]']  # note the square brackets
#             report_date = datetime.strptime(report_date_str.split("T")[0], "%Y-%m-%d").date()
#
#             test_msg.set_messages(
#                 success=f"{page_name} FAIL Report date = {report_date} System date = {system_date}",
#                 failure=f"{page_name} Success Report date = {report_date} System date = {system_date}",
#                 description="page description"
#             )
#             assert report_date == system_date

class TestDataValidationFromSource(TestBase):
    
    @pytest.mark.report("Sales_Analysis_Report")
    @pytest.mark.test_id("TC010_DEV_AUTO_TEST_CASE")
    def test_total_quantity_matches_database(self, test_msg):
        logger.info("--- Test Case: test_total_quantity_matches_database ---")
        logger.info("Objective: Verify that the total quantity in the Power BI report matches the total quantity in the source database.")

        # 1. Get total quantity from Power BI
        dax_query = '''
        EVALUATE
        ROW(
            "TotalQuantity",
            SUM('healthcaredata healthcare_services'[quantity])
        )
        '''
        logger.info(f"Executing DAX query: {dax_query}")
        powerbi_data = get_powerbi_table(access_token, self.dataset_id, dax_query)
        powerbi_quantity = powerbi_data[0].get('[TotalQuantity]')
        logger.info(f"Total quantity from Power BI: {powerbi_quantity}")

        # 2. Get total quantity from SQL database
        sql_query = "SELECT SUM(quantity) FROM healthcare_services"
        logger.info(f"Executing SQL query: {sql_query}")
        sql_quantity = get_sql_value(sql_query)
        # The SQL query returns a Decimal type, so we cast it to match Power BI's integer/float type
        sql_quantity = int(sql_quantity)
        logger.info(f"Total quantity from SQL database: {sql_quantity}")

        # 3. Compare and assert
        test_msg.set_messages(
            success="Total quantity in Power BI matches the source database.",
            failure=f"Data mismatch: Power BI quantity ({powerbi_quantity}) does not match SQL quantity ({sql_quantity}).",
            description="Compares the 'Sum of quantity' from the Power BI model against the sum directly from the SQL source table to ensure data consistency."
        )

        logger.info(f"Asserting that {powerbi_quantity} == {sql_quantity}")
        assert powerbi_quantity == sql_quantity
        logger.info("SUCCESS: Total quantity in Power BI matches the source database.")
        logger.info("--- Test Case: test_total_quantity_matches_database Complete ---")


