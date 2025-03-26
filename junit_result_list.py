import os
import re
import xml.etree.ElementTree as ET
import json
from collections import OrderedDict

RESULTS_DIRS = {
    "spring-boot-actuator": "spring-boot-project/spring-boot-actuator/build/test-results/test",
    "spring-boot-autoconfigure": "spring-boot-project/spring-boot-autoconfigure/build/test-results/test"
}

OUTPUT_FILE = "test-summary.json"
ALL_TESTS_FILE = "all-tests.json"

summary = {}
executed_tests = {}

# --- Ergebnisstruktur initialisieren ---
def init_module_summary(module):
    if module not in summary:
        summary[module] = {
            "BESTANDEN": {},
            "GEFAILED": {},
            "GESKIPPED": {},
            "NICHT_GELAUFEN": {}
        }

# --- Tests einsortieren ---
def add_test(module, result_type, classname, testname):
    init_module_summary(module)
    if classname not in summary[module][result_type]:
        summary[module][result_type][classname] = []
    summary[module][result_type][classname].append(testname)

# --- JUnit XML Ergebnisse einlesen ---
for module, dir_path in RESULTS_DIRS.items():
    executed_tests[module] = set()

    if not os.path.exists(dir_path):
        continue

    for filename in os.listdir(dir_path):
        if not filename.endswith(".xml"):
            continue

        file_path = os.path.join(dir_path, filename)
        tree = ET.parse(file_path)
        root = tree.getroot()

        for testcase in root.findall(".//testcase"):
            classname = testcase.attrib.get("classname")
            testname = testcase.attrib.get("name")
            testname = re.sub(r"\(\)$", "", testname)
            full = f"{classname}.{testname}"

            executed_tests[module].add(full)

            if testcase.find("failure") is not None:
                add_test(module, "GEFAILED", classname, testname)
            elif testcase.find("skipped") is not None:
                add_test(module, "GESKIPPED", classname, testname)
            else:
                add_test(module, "BESTANDEN", classname, testname)

# --- Vollständige Testliste laden ---
with open(ALL_TESTS_FILE) as f:
    all_tests = json.load(f)

# --- Fehlende Tests (nicht gelaufen) ---
for module, classes in all_tests.items():
    if module == "Overview":
        continue

    for classname, methods in classes.items():
        for method in methods:
            full = f"{classname}.{method}"
            if full not in executed_tests.get(module, set()):
                add_test(module, "NICHT_GELAUFEN", classname, method)

# --- Übersicht berechnen ---
overview = {}
for module in summary:
    overview[module] = {
        "TESTKLASSEN_GESAMT": len(all_tests.get(module, {})),
        "TESTS_GESAMT": sum(len(v) for v in all_tests.get(module, {}).values()),
        "BESTANDEN": sum(len(v) for v in summary[module].get("BESTANDEN", {}).values()),
        "GEFAILED": sum(len(v) for v in summary[module].get("GEFAILED", {}).values()),
        "GESKIPPED": sum(len(v) for v in summary[module].get("GESKIPPED", {}).values()),
        "NICHT_GELAUFEN": sum(len(v) for v in summary[module].get("NICHT_GELAUFEN", {}).values())
    }

# --- Finales JSON schreiben ---
ordered = OrderedDict()
ordered["Overview"] = overview
for module in sorted(summary.keys()):
    ordered[module] = summary[module]

with open(OUTPUT_FILE, "w") as f:
    json.dump(ordered, f, indent=2)

print(f"Testzusammenfassung geschrieben nach {OUTPUT_FILE}")
