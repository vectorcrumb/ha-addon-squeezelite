#!/usr/bin/env python3
"""Report every finding; fail on any critical or fixable high finding."""
from collections import Counter
import json
import sys

report = json.load(open(sys.argv[1]))
findings = [v for result in report.get("Results", [])
            for v in result.get("Vulnerabilities", [])]
print("All findings by severity:", dict(Counter(v["Severity"] for v in findings)))
blocked = [v for v in findings if v["Severity"] == "CRITICAL"
           or (v["Severity"] == "HIGH" and v.get("FixedVersion"))]
for v in blocked:
    print("BLOCK:", v["VulnerabilityID"], v["PkgName"], v.get("FixedVersion", "unfixed"))
unfixed = [v for v in findings if v["Severity"] == "HIGH" and not v.get("FixedVersion")]
print("Unfixed high findings requiring human review:", len(unfixed))
print("Passing this gate is not deployment approval or a claim of no vulnerabilities.")
sys.exit(bool(blocked))
