import sys

from pymindmap.cli import main

if __name__ == "__main__":
    sys.exit(main(["gui", *sys.argv[1:]]))
