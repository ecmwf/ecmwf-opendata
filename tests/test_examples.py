import os
import sys

import pytest

README = os.path.realpath(
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "README.md")
)


def example_list():
    examples = []
    code = []
    python = False

    with open(README, "rt", encoding="utf-8") as f:
        for line in f:
            if line.startswith("```python"):
                python = True
                continue
            if python and line.startswith("```"):
                if any("from ecmwf.opendata import Client" in c for c in code):
                    examples.append(code)
                python = False
                code = []
                continue
            if python:
                code.append(line)

    return sorted(examples)


@pytest.mark.parametrize("example", example_list())
def xxx_test_example(example):
    code = "".join(example)
    try:
        exec(code, dict(__file__=README), {})
    except Exception as e:
        print("===========", file=sys.stderr)
        print(code, file=sys.stderr)
        print("===========", file=sys.stderr)
        raise ValueError("Exception: %s\n%s" % (e, code))


if __name__ == "__main__":
    for e in example_list():
        try:
            xxx_test_example(e)
        except Exception:
            pass
