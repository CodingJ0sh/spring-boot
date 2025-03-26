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

# Regex zum Finden von Testmethoden
test_method_pattern = re.compile(
    r'(@(?:Test|ParameterizedTest|RepeatedTest|TestTemplate|TestFactory)[^\n]*\n(?:@\w+[^\n]*\n)*)'
    r'\s*(?:public|protected|private)?\s+\w[\w<>]*\s+(\w+)\s*\(',
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
                    
                matches = test_method_pattern.findall(content)
                
                methods = []
                for annotations, method in matches:
                    if annotations and "@Disabled" in annotations:
                        continue
                    methods.append(method)

                if not methods:
                    continue

                rel_path = os.path.relpath(class_path, base_dir)
                full_classname = rel_path.replace(os.sep, ".").replace(".java", "")

                all_tests[module][full_classname] = methods
                testclass_counter += 1
                testmethod_counter += len(methods)

    overview[module] = {
        "#Testklassen": testclass_counter,
        "#Testmethoden": testmethod_counter
    }

ordered = OrderedDict()
ordered["Overview"] = overview
for module in sorted(all_tests.keys()):
    ordered[module] = all_tests[module]

with open("all-tests.json", "w") as out:
    json.dump(ordered, out, indent=2)

print("Alle Tests gruppiert nach Modul gespeichert in all-tests.json")
