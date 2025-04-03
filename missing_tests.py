import json

ALL_TESTS_FILE = "all-tests.json"
EXECUTED_CLASSES_FILE = "executed-classes.json"
OUTPUT_JSON = "remaining-tests.json"

with open(ALL_TESTS_FILE) as f:
    all_tests = json.load(f)

with open(EXECUTED_CLASSES_FILE) as f:
    executed = json.load(f)

missing = []

for batch, classes in all_tests.items():
    if batch == "Overview":
        continue
    for class_name in classes:
        if class_name not in executed.get(batch, []):
            missing.setdefault(batch, []).append(class_name)

with open(OUTPUT_JSON, "w") as f:
    json.dump(missing, f, indent=2)

print(f"{sum(len(v) for v in missing.values())} fehlende Klassen erkannt und gespeichert in '{OUTPUT_JSON}'")
