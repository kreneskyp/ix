from django.core.management.base import BaseCommand
import json


class Command(BaseCommand):
    help = "Display information about failed tests from a pytest JSON report"

    def add_arguments(self, parser):
        parser.add_argument(
            "report_file", type=str, help="Path to the pytest JSON report file"
        )

    def handle(self, *args, **options):
        report_file = options["report_file"]
        failed_tests = self.get_failed_tests(report_file)

        for test in failed_tests[:1]:
            # Pretty print the JSON data
            self.stdout.write("Full Test Data:\n")
            self.stdout.write(json.dumps(test, indent=4))

            # Print formatted summary
            self.stdout.write("\nFormatted Summary:\n")
            self.print_failed_test_info(test)

            self.stdout.write(
                "-----------------------------\n"
            )  # Separator between tests

    def get_failed_tests(self, report_file):
        with open(report_file, "r") as f:
            report = json.load(f)

        # Filter out passing and skipped tests
        failed_tests = [test for test in report["tests"] if test["outcome"] == "failed"]

        return failed_tests

    def print_failed_test_info(self, test):
        call = test.get("call", {})
        self.stdout.write(f"Test: {test.get('nodeid', 'N/A')}")
        self.stdout.write("Traceback:")
        self.stdout.write(call.get("longrepr", "N/A"))
        self.stdout.write("Log:")
        log = call.get("log", {})
        for datum in log:
            self.stdout.write(f"{datum['levelname']} {datum['msg']}")
        self.stdout.write("Standard output:")
        self.stdout.write(test.get("stdout", "N/A"))
