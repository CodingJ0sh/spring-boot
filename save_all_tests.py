import os
import re
import json
from collections import OrderedDict

# Map von Batchnamen auf Testverzeichnisse
BATCHES = {
    "actuator": "spring-boot-project/spring-boot-actuator/src/test/java",
    "autoconfigure": "spring-boot-project/spring-boot-autoconfigure/src/test/java"
}

test_class_list = OrderedDict()
overview = {}

# Regex für JUnit-Testmethoden
test_method_pattern = re.compile(
    r'(@(?:Test|ParameterizedTest|RepeatedTest|TestTemplate|TestFactory)[^\n]*\n(?:@\w+[^\n]*\n)*)'
    r'\s*(?:public|protected|private)?\s+\w[\w<>]*\s+(\w+)\s*\(',
    re.MULTILINE
)

# Regex für Klassendeklarationen
class_pattern = re.compile(
    r'(class|static class)\s+(\w+)[^{]*\{',
    re.MULTILINE
)

# Sammle Tests pro Batch
for batch, base_dir in BATCHES.items():
    test_class_list[batch] = []
    testclass_counter = 0
    testmethod_counter = 0

    for root, _, files in os.walk(base_dir):
        for file in files:
            if not file.endswith(".java"):
                continue

            class_path = os.path.join(root, file)
            with open(class_path, "r", encoding="utf-8") as f:
                content = f.read()

            class_matches = class_pattern.finditer(content)
            for match in class_matches:
                class_body = content[match.end():]
                method_matches = test_method_pattern.findall(class_body)

                methods = [
                    method for annotations, method in method_matches
                    if "@Disabled" not in annotations
                ]

                if not methods:
                    continue

                rel_path = os.path.relpath(class_path, base_dir)
                base_class = rel_path.replace(os.sep, ".").replace(".java", "")
                class_name = match.group(2)
                full_classname = f"{base_class}${class_name}" if class_name != base_class else base_class

                test_class_list[batch].append(full_classname)
                testclass_counter += 1
                testmethod_counter += len(methods)

    overview[batch] = {
        "#Testklassen": testclass_counter,
        "#Testmethoden": testmethod_counter
    }

# JSON speichern
output = OrderedDict()
output["Overview"] = overview
output.update(test_class_list)

with open("all-tests.json", "w") as out:
    json.dump(output, out, indent=2)

print("Tests nach Batch gruppiert gespeichert in all-tests.json")
