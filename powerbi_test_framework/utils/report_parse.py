# import os
# import re
# import logging
# from datetime import datetime
# from bs4 import BeautifulSoup
# import json
#
# logger = logging.getLogger(__name__)
#
# def parse_pytest_html_report(file_path):
#     """Extract total, passed, failed, skipped, and duration info from pytest HTML report(s)."""
#     logger.info(f"Parsing pytest HTML reports from: {file_path}")
#
#     report_files = [f for f in os.listdir(file_path) if f.endswith(".html")]
#
#     total = passed = failed = skipped = duration = 0
#
#     for report_file in report_files:
#         file_full_path = os.path.join(file_path, report_file)
#         with open(file_full_path, "r", encoding="utf-8") as f:
#             html = f.read()
#
#         # Extract counts using regex
#         total_match = re.search(r"(\d+)\s+test(?:s)?\s+took", html, re.IGNORECASE)
#         passed_match = re.search(r"(\d+)\s+Passed", html, re.IGNORECASE)
#         failed_match = re.search(r"(\d+)\s+Failed", html, re.IGNORECASE)
#         skipped_match = re.search(r"(\d+)\s+Skipped", html, re.IGNORECASE)
#         duration_match = re.search(r"took\s+(\d{2}:\d{2}:\d{2})", html, re.IGNORECASE)
#
#         # Safely extract integers
#         total += int(total_match.group(1)) if total_match else 0
#         passed += int(passed_match.group(1)) if passed_match else 0
#         failed += int(failed_match.group(1)) if failed_match else 0
#         skipped += int(skipped_match.group(1)) if skipped_match else 0
#
#         # Convert duration (hh:mm:ss) to seconds
#         if duration_match:
#             h, m, s = map(int, duration_match.group(1).split(":"))
#             duration += h * 3600 + m * 60 + s
#
#     # Calculate pass rate
#     pass_rate = round((passed / total) * 100, 2) if total else 0
#
#     # Summary string
#     summary = (
#         f"Total: {total}, Passed: {passed}, Failed: {failed}, "
#         f"Skipped: {skipped}, Duration: {duration}s, Pass Rate: {pass_rate}%"
#     )
#
#     report_data = {
#         "date": datetime.now().strftime("%Y-%m-%d"),
#         "total": total,
#         "passed": passed,
#         "failed": failed,
#         "skipped": skipped,
#         "duration": duration,
#         "pass_rate": pass_rate,
#         "summary": summary
#     }
#
#     logger.info(f"Parsed report data: {report_data}")
#     return report_data
#
# def extract_test_names_from_html(folder_path):
#     tests = []
#
#     for file in os.listdir(folder_path):
#         if not file.endswith(".html"):
#             continue
#
#         file_path = os.path.join(folder_path, file)
#         with open(file_path, "r", encoding="utf-8") as f:
#             soup = BeautifulSoup(f, "html.parser")
#
#         # ✅ Find the div with data-jsonblob attribute
#         data_container = soup.find("div", id="data-container")
#
#         if data_container and data_container.get("data-jsonblob"):
#             # Parse the JSON data
#             json_data = json.loads(data_container["data-jsonblob"])
#
#             # Extract test information from the tests object
#             if "tests" in json_data:
#                 for test_path, test_details_list in json_data["tests"].items():
#                     for test_detail in test_details_list:
#                         tests.append({
#                             "status": test_detail.get("result"),
#                             "name": test_detail.get("testId"),
#                             "duration": test_detail.get("duration")
#                         })
#
#     return tests