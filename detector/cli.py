import sys

from .api import DownDetector
from .rconsole import console


def main():
    if len(sys.argv) != 2:
        console.print("[bold]Usage[/]: python -m detector 'service_name_here'")
        sys.exit(1)

    service_name = sys.argv[1]
    DownDetector(service_name).get_status()
