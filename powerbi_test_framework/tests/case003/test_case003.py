import pytest
from powerbi_test_framework.utils.logger import  get_logger

logger = get_logger(__name__)
    
@pytest.mark.report("Wallmart_sales_report")
@pytest.mark.test_id("TC006_DEV_AUTO_TEST_CASE")
@pytest.mark.skip(reason="Feature not implemented yet - skipping test.")
def test_skipped_case():
    """
    Example of a skipped test case using pytest.skip.
    """
    logger.info("--- Test Case: test_skipped_case ---")
    logger.info("Objective: This test is skipped because the feature is pending.")
    # This test will be skipped automatically
    assert False  # Never executed

@pytest.mark.report("Wallmart_sales_report")
@pytest.mark.test_id("TC007_DEV_AUTO_TEST_CASE")
def test_error_case(test_msg):
    """
    Example of a test that raises an unexpected error.
    """
    test_msg.set_messages(success="success testing", failure="failure testing", description="description testing")

    try:
        num = 5/0
    except ZeroDivisionError as e:
        test_msg.on_failure(f"Some error occured: {e}")
        assert f"Some Error occured: {e}"
    
    logger.info("--- Test Case: test_error_case ---")
    logger.info("Objective: Simulate runtime error during test execution.")
    raise ValueError("An unexpected error occurred during test execution.")

@pytest.mark.report("Wallmart_sales_report")
@pytest.mark.test_id("TC008_DEV_AUTO_TEST_CASE")
@pytest.mark.xfail(reason="Bug known in validation logic - expecting failure.")
def test_known_failure_case():
    """
    Example of a known failure test using xfail.
    """
    logger.info("--- Test Case: test_known_failure_case ---")
    logger.info("Objective: Verify known bug behavior in calculation.")
    assert 1 == 2  # Will show as xfail

@pytest.mark.report("Wallmart_sales_report")
@pytest.mark.test_id("TC009_DEV_AUTO_TEST_CASE")
def test_unknown_case():
    """
    Example of an 'unknown' result simulation.
    This is not a native pytest outcome but can be simulated.
    """
    logger.info("--- Test Case: test_unknown_case ---")
    logger.info("Objective: Simulate uncertain or inconclusive test result.")
    try:
        # Simulate uncertain condition
        condition = None
        if condition is None:
            pytest.skip("Test result unknown — insufficient data for evaluation.")
    except Exception as e:
        pytest.fail(f"Unexpected error in unknown case: {e}")