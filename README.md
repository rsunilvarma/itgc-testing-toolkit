# ITGC Testing Toolkit: Access Review (v0.1)

A Python tool that independently re-performs a user access review on a raw access export, so that auditors and small GRC teams can test every account against key access controls and produce reconciled, audit-ready evidence.

## Why it helps

- **For auditors:** traditional access reviews test a sample, often 25 accounts out of thousands, because manual testing is slow. This tool tests **100% of the population** in seconds, so conclusions rest on the full data set rather than a sample.
- **For small organisations:** teams without an identity governance platform can run their own periodic access reviews on a simple export, find issues before an audit does, and keep dated evidence of each review.

## What it does

1. Reads a user access export (`sample_data/users.csv`)
2. Validates each row; rows with invalid data are reported as data issues and excluded, instead of crashing the review
3. Tests every remaining user against three access controls
4. Writes every exception to a dated findings register (`findings_register.csv`)
5. Prints a summary that reconciles: control counts add up to total findings, and users reviewed plus rows skipped equals rows in the file

## Controls tested

| Control | Fails when |
| --- | --- |
| MFA not enabled | The account does not have multi-factor authentication |
| Dormant account | No login for more than 90 days (configurable) |
| Admin without MFA | An administrator account does not have multi-factor authentication |

## How to run

```
py access_review.py
```

On macOS or Linux, use `python3 access_review.py`.

Requires Python 3 (standard library only, no packages to install).

- **Input:** `sample_data/users.csv` with the columns `name, mfa, days, admin`
- **Output:** `findings_register.csv`, with the columns `user, control, result, detail, date`

Settings at the top of `access_review.py`:

| Setting | Default | Purpose |
| --- | --- | --- |
| `DORMANT_DAYS` | `90` | Days without login before an account counts as dormant |
| `INPUT_FILE` | `sample_data/users.csv` | Access export to review |
| `OUTPUT_FILE` | `findings_register.csv` | Where findings are saved |

## Sample output

```
DATA ISSUE | broken.user11 | invalid days value: ''
DATA ISSUE | broken.user12 | invalid days value: 'abc'
test.user01 | PASS
test.user02 | FAIL | MFA not enabled
test.user02 | FAIL | Dormant (120 days since last login)
test.user02 | FAIL | Admin account mfa is not enabled
...
Saved 10 findings to findings_register.csv
--- Summary ---
Users reviewed: 10
No MFA: 4
Dormant (>90 days): 4
Admin without MFA: 2
Total findings: 10
Rows skipped (data issues): 2
Rows in file: 12
```

## Framework mapping

| Control | ISO 27001:2022 | NIST SP 800-53 | SOC 2 |
| --- | --- | --- | --- |
| MFA not enabled | A.8.5 Secure authentication | IA-2(1), IA-2(2) | CC6.1 |
| Dormant account | A.5.18 Access rights | AC-2(3) | CC6.2 |
| Admin without MFA | A.8.2 Privileged access rights; A.8.5 | IA-2(1) | CC6.1 |

Mapping is indicative; confirm against the framework versions used in your engagement.

## Design decisions

- **Policy thresholds are settings, not hard-coded values.** Organisations define "dormant" differently (45, 60 or 90 days), so the threshold is changed in one place without touching the test logic.
- **Bad data is reported, not hidden or crashed on.** One blank cell should not stop a review of thousands of accounts, and excluded rows must still be visible, so each one is listed as a data issue.
- **Every total reconciles.** Control counts must add up to total findings, and reviewed plus skipped rows must equal rows in the file. Completeness of the population is proven, not assumed.
- **Control names are fixed.** Findings registers stay comparable across review periods.

## Sample data

All data in `sample_data/` is fictional and created for testing. Never run this tool on real employee data without authorisation from the data owner.

## Roadmap

- **v0.2:** validate every field (MFA and admin values, blank names, negative days)
- **v1.0:** settings file, dated evidence pack with an input file fingerprint (SHA-256), more access controls (orphaned, generic and unapproved privileged accounts)
- **Later:** test packs for AWS IAM, security groups, change management and vulnerability SLAs