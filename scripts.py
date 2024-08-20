import os
import subprocess
import sys


def migrate(args=sys.argv):
    subprocess.check_call(["alembic", "revision", "--autogenerate", "-m"] + args[1:])


def build(args=sys.argv):
    pass


def lint(args=sys.argv):
    report_command = ""
    if "report" in args:
        os.path.exists("reports") or os.makedirs("reports")
        report_command = " --output-format concise -o reports/lint-report.txt"

    # in this case we use os.system to avoid checking the return code since we want lint to continue
    # even if there are errors
    os.system("ruff check ." + report_command)


def lint_fix():
    # we use os.system for the same reason as in the lint script
    print("\n👉 RUFF")
    os.system("ruff check . --fix")
    os.system("ruff format .")
