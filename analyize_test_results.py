import os
import xml.etree.ElementTree as ET
from collections import defaultdict

RESULTS_DIRS = {
    "actuator": "spring-boot-project/spring-boot-actuator/build/test-results/test",
    "autoconfigure": "spring-boot-project/spring-boot-autoconfigure/build/test-results/test"
}

all_test_classes = defaultdict(list)
empty_files = []
error_files = []

print("🔍 Starte XML-Analyse...\n")

for batch, path in RESULTS_DIRS.items():
    print(f"📁 Analysiere Batch: {batch}")
    if not os.path.exists(path):
        print(f"Ordner nicht gefunden: {path}\n")
        continue

    for file in os.listdir(path):
        if not file.endswith(".xml"):
            continue

        full_path = os.path.join(path, file)
        try:
            tree = ET.parse(full_path)
            root = tree.getroot()
            testcases = root.findall(".//testcase")

            if not testcases:
                empty_files.append((batch, file))
                continue

            for case in testcases:
                classname = case.attrib.get("classname")
                if classname:
                    all_test_classes[classname].append((batch, file))

        except ET.ParseError:
            error_files.append((batch, file))

print("\n📊 Ergebnis:")

print(f"\n🆗 Gesamtzahl unterschiedlicher Testklassen: {len(all_test_classes)}")
print(f"🧾 Gesamtzahl Testklasse-Zuordnungen (inkl. Mehrfachzuordnung): {sum(len(v) for v in all_test_classes.values())}")

# Doppelt gelaufene Klassen
duplicates = {cls: files for cls, files in all_test_classes.items() if len(files) > 1}

print(f"\nTestklassen mehrfach ausgeführt: {len(duplicates)}")
for cls, uses in list(duplicates.items())[:10]:  # nur erste 10
    print(f" - {cls} ({len(uses)}x): {[f'{b}/{f}' for b, f in uses]}")

# Leere Dateien
if empty_files:
    print(f"\nLeere XML-Dateien (ohne <testcase>): {len(empty_files)}")
    for batch, file in empty_files:
        print(f" - {batch}/{file}")

# Fehlerhafte Dateien
if error_files:
    print(f"\nFehlerhafte XML-Dateien: {len(error_files)}")
    for batch, file in error_files:
        print(f" - {batch}/{file}")
