import pytest
from datetime import datetime, date
from powerbi_test_framework.utils.monday_client import MondayClient
import json
from powerbi_test_framework.utils.logger import get_logger
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from pathlib import Path
import requests
from powerbi_test_framework.utils.box_client import BoxClient
from powerbi_test_framework.utils.loader import load
from powerbi_test_framework.utils.config import MONDAY_API_KEY, MONDAY_API_URL, MONDAY_FILE_URL, BOARD_NAME, GROUP_NAME, REPORT_PATH, ENVIRONMENT
logger = get_logger(__name__)



# def pytest_addoption(parser):
#     parser.addoption(
#         "--env",
#         action="store",
#         required=True,
#         help="Environment to use: DEV or PROD"
#     )


# @pytest.fixture(scope="session", autouse=True)
# def load_environment(request):
#     """Automatically run before all tests and load config."""
#     env = request.config.getoption("--env").upper()
#     load(env)
#     print(f"\n🚀 Environment Loaded: {env}")
#     return env


test_results = []
test_metadata = {}
test_messages = {}

@pytest.fixture
def test_msg(request):
    """Fixture to set success and failure messages"""

    class TestMessage:
        def __init__(self, nodeid):
            self.nodeid = nodeid
            self.success_msg = None
            self.failure_msg = None
            self.description_msg = None

        def on_success(self, message):
            """Set message to display when test passes"""
            self.success_msg = message
            test_messages[self.nodeid] = {'success': message, 'failure': self.failure_msg}

        def on_failure(self, message):
            """Set message to display when test fails"""
            self.failure_msg = message
            if self.nodeid in test_messages:
                test_messages[self.nodeid]['failure'] = message
            else:
                test_messages[self.nodeid] = {'success': self.success_msg, 'failure': message}

        def set_messages(self, success, failure, description):
            """Set both messages at once"""
            self.success_msg = success
            self.failure_msg = failure
            self.description_msg = description
            test_messages[self.nodeid] = {'success': success, 'failure': failure, 'description': description}

    msg = TestMessage(request.node.nodeid)
    return msg

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Capture test results with detailed success/error messages"""
    outcome = yield
    report = outcome.get_result()

    if report.when == "call":
        marker = item.get_closest_marker('test_id')
        report_name_marker = item.get_closest_marker('report')

        test_id = marker.args[0] if marker and marker.args else item.name
        report_name = report_name_marker.args[0] if report_name_marker and report_name_marker.args else item.name

        # Get messages from fixture
        messages = test_messages.get(item.nodeid, {})

        # Get captured output
        stdout = getattr(report, 'capstdout', '')
        stderr = getattr(report, 'capstderr', '')

        if report.passed:
            message = messages.get('success', 'Test passed')
            error = None

        elif report.failed:
            message = messages.get('failure')
            error = str(report.longrepr)

        elif report.skipped:
            message = "Test skipped"
            error = str(report.longrepr) if hasattr(report, 'longrepr') else "Skipped by marker"
            details = error
        else:
            message = f"Test outcome: {report.outcome}"
            error = None
            details = stdout

        test_case_summary = f"""
                                TEST EXECUTION COMPLETED - {test_id}

                                Test Name: {item.name}
                                Status: {report.outcome}
                                Executed On: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                                
                                Summary:
                                The test case {item.name} executed successfully, with status {report.outcome}, reason {message} 
                            """

        test_results.append({
                'test_id': test_id,
                'test_name': item.name,
                'nodeid': item.nodeid,
                'outcome': report.outcome,
                'duration': report.duration,
                'timestamp': datetime.now().strftime("%Y-%m-%d"),
                'message': message,  # High-level message
                'error': error,  # Error details if failed
                'stdout': stdout,  # Captured stdout
                'stderr': stderr,  # Captured stderr
                'sections': dict(report.sections) if hasattr(report, 'sections') else {},
                'description': messages.get('description', 'default description'),
                'summary': test_case_summary,
                'report_name': report_name
            })


def generate_pdf_report(test_data, filename):
    """Generate properly aligned PDF using ReportLab"""

    pdf_filename = filename

    # Create PDF document
    doc = SimpleDocTemplate(
        pdf_filename,
        title=f"{test_data['test_name']}_{test_data['timestamp']}",
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm
    )

    elements = []
    styles = getSampleStyleSheet()

    # Determine colors based on outcome
    if test_data['outcome'] == 'passed':
        status_color = colors.green
        message_bg_color = colors.Color(232 / 255, 245 / 255, 233 / 255)
        border_color = colors.Color(76 / 255, 175 / 255, 80 / 255)
        title_text = 'Success Details:'
    elif test_data['outcome'] == 'failed':
        status_color = colors.red
        message_bg_color = colors.Color(255 / 255, 235 / 255, 238 / 255)
        border_color = colors.Color(244 / 255, 67 / 255, 54 / 255)
        title_text = 'Error Details:'
    elif test_data['outcome'] == 'skipped':
        status_color = colors.orange
        message_bg_color = colors.Color(255 / 255, 243 / 255, 224 / 255)
        border_color = colors.Color(255 / 255, 152 / 255, 0 / 255)
        title_text = 'Skipped Details:'
    else:
        status_color = colors.grey
        message_bg_color = colors.Color(245 / 255, 245 / 255, 245 / 255)
        border_color = colors.Color(158 / 255, 158 / 255, 158 / 255)
        title_text = 'Details:'

    # ===== HEADER SECTION (Using Table for Background) =====
    header_title_style = ParagraphStyle(
        'HeaderTitle',
        parent=styles['Heading1'],
        fontSize=12,
        textColor=colors.HexColor('#333333'),
        alignment=TA_LEFT,
        leading=14,
        SpaceAfter=2,
        spaceBefore=0
    )

    header_timestamp_style = ParagraphStyle(
        'HeaderTimestamp',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#333333'),
        alignment=TA_LEFT,
        leading=13,
        spaceBefore=0

    )

    # Create header as a table with background color
    header_data = [
        [Paragraph(f"<b>Test Report: {test_data['test_id']}</b>", header_title_style)],
        [Paragraph(f"Generated: {test_data['timestamp']}", header_timestamp_style)]
    ]

    header_table = Table(header_data, colWidths=[17 * cm])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#d3d3d3')),  # Light ash
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ('RIGHTPADDING', (0, 0), (-1, -1), 15),
        ('TOPPADDING', (0, 0), (0, 0), 15),
        ('TOPPADDING', (0, 1), (0, 1), 5),
        ('BOTTOMPADDING', (0, 0), (0, 0), 5),
        ('BOTTOMPADDING', (0, 1), (0, 1), 15),
    ]))

    elements.append(header_table)
    elements.append(Spacer(1, 0.5 * cm))

    # ===== TEST DETAILS SECTION =====
    section_heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#333333'),
        alignment=TA_LEFT,
        spaceAfter=10,
        spaceBefore=10
    )

    elements.append(Paragraph("<b>Test Details</b>", section_heading_style))

    # Define a normal paragraph style for wrapping
    cell_wrap_style = ParagraphStyle(
        'CellWrap',
        parent=styles['Normal'],
        fontSize=11,
        alignment=TA_LEFT,
        leading=14
    )

    # Create table data
    table_data = [
        ['Test ID', Paragraph(str(test_data['test_id']), cell_wrap_style)],
        ['Test Name', Paragraph(str(test_data['test_name']), cell_wrap_style)],
        ['Status', Paragraph(
            f'<font color="{status_color.hexval()}"><b>{test_data["outcome"].upper()}</b></font>',
            cell_wrap_style
        )],
        ['Duration', Paragraph(f"{test_data['duration']:.4f} seconds", cell_wrap_style)],
        ['Description', Paragraph(str(test_data['description']), cell_wrap_style)]
    ]

    # Create table with proper column widths
    table = Table(table_data, colWidths=[5 * cm, 12 * cm])

    # Apply table styling
    table.setStyle(TableStyle([
        # Header column styling
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e0e0e0')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#333333')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (0, -1), 11),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),

        # Data column styling
        ('BACKGROUND', (1, 0), (1, -1), colors.white),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.black),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (1, 0), (1, -1), 11),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (1, 0), (1, -1), 'MIDDLE'),

        # Status row special styling
        ('TEXTCOLOR', (1, 2), (1, 2), status_color),
        ('FONTNAME', (1, 2), (1, 2), 'Helvetica-Bold'),

        # Padding and borders
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dddddd')),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 0.7 * cm))

    # ===== MESSAGE BOX SECTION =====
    message_title_style = ParagraphStyle(
        'MessageTitle',
        parent=styles['Heading3'],
        fontSize=14,
        textColor=border_color,
        alignment=TA_LEFT,
        leading=18,
        spaceAfter=0,
        spaceBefore = 0
    )

    message_content_style = ParagraphStyle(
        'MessageContent',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.black,
        alignment=TA_LEFT,
        leading=16,
        fontName='Courier',
        spaceAfter=0,
        spaceBefore=0
    )

    # Create message box
    message_text = test_data.get('message', 'No message available')
    message_paragraph = Paragraph(
        message_text.replace('\n', '<br/>').replace('  ', '&nbsp;&nbsp;'),
        message_content_style
    )

    message_box_data = [
        [Paragraph(f"<b>{title_text}</b>", message_title_style)],
        [message_paragraph]
    ]

    message_table = Table(message_box_data, colWidths=[17 * cm])
    message_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), message_bg_color),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ('RIGHTPADDING', (0, 0), (-1, -1), 15),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LINEBEFORECOLOR', (0, 0), (0, -1), border_color),
        ('LINEBEFOREWIDTH', (0, 0), (0, -1), 5)
    ]))

    elements.append(message_table)

    # Build PDF
    doc.build(elements)
    return pdf_filename

def pytest_sessionfinish(session, exitstatus):
    """Generate individual HTML reports"""
    Path("reports").mkdir(exist_ok=True)

    client = MondayClient(MONDAY_API_KEY, MONDAY_API_URL, MONDAY_FILE_URL)
    box_client = BoxClient()

    board_id = client.get_or_create_board(board_name=BOARD_NAME)
    group_id = client.get_or_create_group(group_name=GROUP_NAME)
    
    # Creating the item details
    columns = client.get_columns()
    column_ids_map = {col['title']: col['id'] for col in columns}
    
    # status_label = "Completed" if test_summary["pass_rate"] >= 90 else "Pending"
    
    # Map actual column IDs dynamically from Monday board
    col_values = {
        column_ids_map["Test Date"]: {"date": date.today().strftime("%Y-%m-%d")},
        # column_ids_map["Total Tests"]: str(test_summary["total_tests"]),
        # column_ids_map["Passed Tests"]: str(test_summary["passed"]),
        column_ids_map["Environment"]: str(ENVIRONMENT),
        # column_ids_map["Failed Tests"]: str(test_summary["failed"]),
        # column_ids_map["Skipped Tests"]: str(test_summary["skipped"]),
        # column_ids_map["Pass Rate (%)"]: str(test_summary["pass_rate"]),
        # column_ids_map["Duration"]: str(test_summary["total_duration_seconds"]),
        # column_ids_map["Status"]: {"label": status_label},
        # column_ids_map["Summary"]: test_summary["summary"],
    }
    

    item_name = test_results[0].get('report_name')
    
    existing_item_id = client.get_item_id_by_name(item_name)

 
    
    logger.info(f"Checking for existing item: {item_name} - Found ID: {existing_item_id}")
    if existing_item_id:
        logger.info(f"Updating existing item: {item_name} (ID: {existing_item_id}) with values: {col_values}")
        item_id = client.update_item(existing_item_id, col_values)
    else:
        logger.info(f"Creating item: {item_name} with values: {col_values}, group ID: {group_id}")
        item_id = client.create_item(group_id, item_name, col_values)
    
    
    subitem_board_id = client.get_subitem_board_id()
    columns = client.get_subitem_columns(subitem_board_id)
    sub_item_column_ids_map = {col['title']: col['id'] for col in columns}

    print("sub item column ids map:",sub_item_column_ids_map)
    print("existing item id:",existing_item_id)
    #deleting old sub items before creating new ones
    if existing_item_id:
        list_of_subitem_ids = client.get_all_subitems(existing_item_id,sub_item_column_ids_map['Date'])
        print("subitem ids to be deleted:",list_of_subitem_ids)
        if list_of_subitem_ids:
            client.delete_old_sub_items(list_of_subitem_ids)
    
    users = ["jagadeesh@adhiraninfotech.com"]
    people_id = client.get_all_users(users)

    for test in test_results:

        report_file = f"reports/{test['test_id']}_{test['timestamp']}.pdf"
        file_name = generate_pdf_report(test, report_file)

        test_func_name = test.get("test_id")
        test_report_date = test.get("timestamp")
        sub_item_name = test_func_name.split("::")[-1].strip()
        modified_sub_item_name = f"{sub_item_name}_{test_report_date}"
        sub_item_status = test.get("outcome")
        sub_item_duration = test.get("duration")
        
        modified_status = "Done" if sub_item_status == "passed" else "Stuck"
        
        sub_item_col_values = {
            sub_item_column_ids_map["Status"]: {"label": modified_status},
            sub_item_column_ids_map["Date"]: {"date": test["timestamp"]},
            sub_item_column_ids_map["Type"]: {"label": "Daily"},
            sub_item_column_ids_map["Environment"]: str(ENVIRONMENT),
            sub_item_column_ids_map["Owner"]:{
                                                "personsAndTeams": [{"id": pid, "kind": "person"} for pid in people_id]
                                            }
        
        }
        # Checking existing sub items
        existing_sub_item_id = client.get_subitem_by_name(item_id, modified_sub_item_name)
        
        if existing_sub_item_id:
            subitem_id = client.update_subitem(subitem_board_id, existing_sub_item_id, sub_item_col_values)
            client.clear_file_column(subitem_board_id, subitem_id, sub_item_column_ids_map['Report'])
        else:
            subitem_id = client.create_sub_item(item_id, modified_sub_item_name, sub_item_col_values)
            client.clear_file_column(subitem_board_id, subitem_id, sub_item_column_ids_map['Report'])
        
        
        update_id = client.create_update(subitem_id, test["summary"])
        logger.info(f"Created update (ID: {update_id})")
        
        client.upload_file(existing_sub_item_id, file_name, sub_item_column_ids_map['Report'])
        logger.info("Report uploaded and item updated on Monday.com!")


        # Upload the report file to Box platform

        box_client.upload_file(file_name)