import os
import subprocess
from datetime import datetime
from pathlib import Path

def run_tests_with_separate_reports():
    """Runs each test file separately and generates individual HTML reports"""

    test_dir = Path("powerbi_test_framework/tests")
    test_files = [
        str(p)
        for p in test_dir.rglob("*.py")
        if "__pycache__" not in p.parts and p.name != "__init__.py"
    ]

    print(f"Found {len(test_files)} test files to run")

    # Create reports directory if it doesn't exist
    reports_dir = "reports"
    os.makedirs(reports_dir, exist_ok=True)

    results = []

    for test_file in test_files:
        # Extract test case name from file path (e.g., test_case001)
        test_case_name = os.path.splitext(os.path.basename(test_file))[0]
        report_path = os.path.join(reports_dir, f"{test_case_name}_report.html")

        # Run pytest for this specific test file
        result = subprocess.run(
            [
                "pytest",
                test_file,
                 "-v",
                "-s"
            ],
            check=False,
        )

        results.append({
            "test_file": test_case_name,
            "report_path": report_path,
            "exit_code": result.returncode,
            "status": "PASSED" if result.returncode == 0 else "FAILED"
        })


if __name__ == "__main__":
    run_tests_with_separate_reports()

