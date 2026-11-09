# Access Review Tool v0.1
# Tests a user access export against MFA, dormancy and admin-MFA controls.
# Usage: py access_review.py

import csv
from datetime import date


# --- Settings ---

DORMANT_DAYS = 90
INPUT_FILE = "sample_data/users.csv"
OUTPUT_FILE = "findings_register.csv"
REVIEW_DATE = date.today().isoformat()


# --- Control checks ---

def has_no_mfa(user):
    return not user["mfa"]


def is_dormant(user, limit):
    return user["days"] > limit


def is_admin_without_mfa(user):
    return user["admin"] and not user["mfa"]


# --- Helper: record a finding ---

def add_finding(register, user, control, detail):
    register.append({
        "user": user["name"],
        "control": control,
        "result": "FAIL",
        "detail": detail,
        "date": REVIEW_DATE,
    })


# --- Load users ---

def load_users(filename):
    users = []
    data_issues = []

    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert days to a number; report and skip bad values
            try:
                row["days"] = int(row["days"])
            except ValueError:
                print(f"DATA ISSUE | {row['name']} | invalid days value: '{row['days']}'")
                data_issues.append(row)
                continue

            # Convert mfa and admin to True/False; tidy the name
            row["mfa"] = row["mfa"].strip().lower() == "true"
            row["admin"] = row["admin"].strip().lower() == "true"
            row["name"] = row["name"].strip()
            users.append(row)

    return users, data_issues


# --- Main review ---

try:
    users, data_issues = load_users(INPUT_FILE)
except FileNotFoundError:
    print(f"ERROR: {INPUT_FILE} not found. Check the file name and folder.")
    raise SystemExit

dormant = 0
mfa_fails = 0
admin_fails = 0
total_findings = 0
findings_register = []

for user in users:
    findings = 0

    if has_no_mfa(user):
        print(f"{user['name']} | FAIL | MFA not enabled")
        add_finding(findings_register, user, "MFA", "MFA not enabled")
        findings += 1
        mfa_fails += 1

    if is_dormant(user, DORMANT_DAYS):
        detail = f"Dormant ({user['days']} days since last login)"
        print(f"{user['name']} | FAIL | {detail}")
        add_finding(findings_register, user, "Dormant Account", detail)
        findings += 1
        dormant += 1

    if is_admin_without_mfa(user):
        print(f"{user['name']} | FAIL | Admin account mfa is not enabled")
        add_finding(findings_register, user, "Admin MFA", "Admin account mfa is not enabled")
        findings += 1
        admin_fails += 1

    if findings == 0:
        print(f"{user['name']} | PASS")

    total_findings += findings

with open(OUTPUT_FILE, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["user", "control", "result", "detail", "date"])
    writer.writeheader()
    writer.writerows(findings_register)

print(f"Saved {len(findings_register)} findings to {OUTPUT_FILE}")


# --- Summary ---

print("--- Summary ---")
print(f"Users reviewed: {len(users)}")
print(f"No MFA: {mfa_fails}")
print(f"Dormant (>{DORMANT_DAYS} days): {dormant}")
print(f"Admin without MFA: {admin_fails}")
print(f"Total findings: {total_findings}")
print(f"Rows skipped (data issues): {len(data_issues)}")
print(f"Rows in file: {len(users) + len(data_issues)}")