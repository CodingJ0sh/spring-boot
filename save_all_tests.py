import os
import re
import json
from collections import OrderedDict

all_tests = {}
overview = {}

TEST_DIRS = {
    "spring-boot-actuator": "spring-boot-project/spring-boot-actuator/src/test/java",
    "spring-boot-autoconfigure": "spring-boot-project/spring-boot-autoconfigure/src/test/java"
}

# Regex: alle Methoden mit JUnit-Annotation erkennen
test_method_pattern = re.compile(
    r'(@(?:Test|ParameterizedTest|RepeatedTest|TestTemplate|TestFactory)[^\n]*\n(?:@\w+[^\n]*\n)*)'
    r'\s*(?:public|protected|private)?\s+\w[\w<>]*\s+(\w+)\s*\(',
    re.MULTILINE
)

# Regex: alle Klassen (inkl. innerer) erfassen
class_pattern = re.compile(
    r'(class|static class)\s+(\w+)[^{]*\{',
    re.MULTILINE
)

for module, base_dir in TEST_DIRS.items():
    all_tests[module] = {}
    testclass_counter = 0
    testmethod_counter = 0

    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".java"):
                class_path = os.path.join(root, file)

                with open(class_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Suche nach allen Klassen
                class_matches = class_pattern.finditer(content)

                for match in class_matches:
                    class_type, classname = match.groups()
                    # Versuche, Methoden im Bereich nach der Klassendeklaration zu finden
                    class_body = content[match.end():]
                    method_matches = test_method_pattern.findall(class_body)

                    methods = [
                        method for annotations, method in method_matches
                        if "@Disabled" not in annotations
                    ]

                    if not methods:
                        continue

                    # Erzeuge vollqualifizierten Klassennamen
                    rel_path = os.path.relpath(class_path, base_dir)
                    base_class = rel_path.replace(os.sep, ".").replace(".java", "")
                    full_classname = base_class + "$" + classname if classname != base_class else base_class

                    all_tests[module][full_classname] = methods
                    testclass_counter += 1
                    testmethod_counter += len(methods)

    overview[module] = {
        "#Testklassen": testclass_counter,
        "#Testmethoden": testmethod_counter
    }

# Ausgabe erzeugen
ordered = OrderedDict()
ordered["Overview"] = overview
for module in sorted(all_tests.keys()):
    ordered[module] = all_tests[module]

with open("all-tests.json", "w") as out:
    json.dump(ordered, out, indent=2)

print("Alle Tests gruppiert nach Modul gespeichert in all-tests.json")
