import sys

from .tool import SubstituteTool


def main() -> int:
    tool = SubstituteTool(sys.argv[1:])
    return tool.run()


if __name__ == "__main__":
    code = main()
    exit(code)
