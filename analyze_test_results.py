import os
import xml.etree.ElementTree as ET
from collections import defaultdict, Counter

# Orte mit Test-XML-Dateien
RESULTS_DIRS = {
    "actuator": "spring-boot-project/spring-boot-actuator/build/test-results/test",
    "autoconfigure": "spring-boot-project/spring-boot-autoconfigure/build/test-results/test"
}

empty_files = []
invalid_files = []
class_counter = Counter()

print("Analyse der Test-Resultate...\n")

for batch, dir_path in RESULTS_DIRS.items():
    print("Scanne Batch '{batch}' ({dir_path})...")
    if not os.path.exists(dir_path):
        print(f"Verzeichnis existiert nicht: {dir_path}\n")
        continue

    for filename in os.listdir(dir_path):
        if not filename.endswith(".xml"):
            continue

        full_path = os.path.join(dir_path, filename)

        try:
            tree = ET.parse(full_path)
            root = tree.getroot()
            testcases = root.findall(".//testcase")

            if not testcases:
                empty_files.append(full_path)
            else:
                for case in testcases:
                    classname = case.attrib.get("classname")
                    if classname:
                        class_counter[classname] += 1

        except ET.ParseError:
            invalid_files.append(full_path)

# Ausgabe leere Dateien
print("Leere XML-Dateien (ohne <testcase>):")
if empty_files:
    for path in empty_files:
        print(f"  - {path}")
else:
    print("Keine leeren XML-Dateien gefunden.")

# Ausgabe unlesbare Dateien
print("Ungültige/kaputte XML-Dateien:")
if invalid_files:
    for path in invalid_files:
        print(f"  - {path}")
else:
    print("Keine kaputten XML-Dateien gefunden.")

# Mehrfach ausgeführte Klassen
print("Doppelt oder mehrfach ausgeführte Testklassen:")
duplicates = {cls: count for cls, count in class_counter.items() if count > 1}
if duplicates:
    for cls, count in duplicates.items():
        print(f"  - {cls}: {count}x")
else:
    print("Keine doppelten Testklassen.")

with open("test_xml_analysis.txt", "w", encoding="utf-8") as f:
    f.write("📁 Leere XML-Dateien (ohne <testcase>):\n")
    if empty_files:
        for path in empty_files:
            f.write(f"  - {path}\n")
    else:
        f.write("Keine leeren XML-Dateien gefunden.\n")

    f.write("\nUngültige/kaputte XML-Dateien:\n")
    if invalid_files:
        for path in invalid_files:
            f.write(f"  - {path}\n")
    else:
        f.write("Keine kaputten XML-Dateien gefunden.\n")

    f.write("\nDoppelt oder mehrfach ausgeführte Testklassen:\n")
    if duplicates:
        for cls, count in duplicates.items():
            f.write(f"  - {cls}: {count}x\n")
    else:
        f.write("Keine doppelten Testklassen.\n")

    f.write("\nAnalyse abgeschlossen.\n")
