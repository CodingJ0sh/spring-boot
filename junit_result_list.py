import os
import re
import xml.etree.ElementTree as ET
import json
from collections import OrderedDict, defaultdict

RESULTS_DIRS = {
    "spring-boot-actuator": "spring-boot-project/spring-boot-actuator/build/test-results/test",
    "spring-boot-autoconfigure": "spring-boot-project/spring-boot-autoconfigure/build/test-results/test"
}

OUTPUT_SUMMARY = "test-summary.json"
OUTPUT_EXECUTED = "executed-classes.json"
ALL_TESTS_FILE = "all-tests.json"

summary = {}
executed_classes = defaultdict(set)  
executed_tests = defaultdict(set)   

def init_module(module):
    if module not in summary:
        summary[module] = {
            "BESTANDEN": {},
            "GEFAILED": {},
            "GESKIPPED": {},
        }

def add_test(module, result_type, classname, testname):
    summary[module][result_type].setdefault(classname, []).append(testname)

for module, path in RESULTS_DIRS.items():
    if not os.path.exists(path):
        continue

    init_module(module)

    for file in os.listdir(path):
        if not file.endswith(".xml"):
            continue

        tree = ET.parse(os.path.join(path, file))
        root = tree.getroot()

        for case in root.findall(".//testcase"):
            classname = case.attrib.get("classname")
            testname = re.sub(r"\(\)$", "", case.attrib.get("name"))
            full = f"{classname}.{testname}"

            executed_tests[module].add(full)
            executed_classes[module].add(classname)

            if case.find("failure") is not None:
                add_test(module, "GEFAILED", classname, testname)
            elif case.find("skipped") is not None:
                add_test(module, "GESKIPPED", classname, testname)
            else:
                add_test(module, "BESTANDEN", classname, testname)

with open(ALL_TESTS_FILE) as f:
    all_tests = json.load(f)

# Übersicht erzeugen
overview = {}
for module in summary:
    overview[module] = {
        "TESTKLASSEN_GESAMT": len(all_tests.get(module, {})),
        "TESTS_GESAMT": sum(len(v) for v in all_tests.get(module, {}).values()),
        "BESTANDEN": sum(len(v) for v in summary[module]["BESTANDEN"].values()),
        "GEFAILED": sum(len(v) for v in summary[module]["GEFAILED"].values()),
        "GESKIPPED": sum(len(v) for v in summary[module]["GESKIPPED"].values()),
    }

# JSON-Ausgaben schreiben
ordered_summary = OrderedDict()
ordered_summary["Overview"] = overview
for module in sorted(summary.keys()):
    ordered_summary[module] = summary[module]

with open(OUTPUT_SUMMARY, "w") as f:
    json.dump(ordered_summary, f, indent=2)

with open(OUTPUT_EXECUTED, "w") as f:
    json.dump({k: sorted(v) for k, v in executed_classes.items()}, f, indent=2)

print(f"Testübersicht gespeichert in {OUTPUT_SUMMARY}")
print(f"Erfolgreiche Klassen gespeichert in {OUTPUT_EXECUTED}")
