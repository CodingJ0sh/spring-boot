import json

ALL_TESTS_FILE = "all-tests.json"
EXECUTED_CLASSES_FILE = "executed-classes.json"
OUTPUT_MISSING = "missing-classes.txt"

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
            missing.append(class_name)

with open(OUTPUT_MISSING, "w") as f:
    for classname in sorted(missing):
        f.write(classname + "\n")

print(f"{len(missing)} fehlende Klassen erkannt und gespeichert in {OUTPUT_MISSING}")
