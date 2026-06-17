"""Command-line interface for generating analytics dashboards."""

from __future__ import annotations

import argparse

from .data_foundation import write_data_foundation_artifacts
from .dashboard import write_dashboard


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build sports analytics dashboards.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    dashboard = subparsers.add_parser("build-dashboard", help="Generate static dashboard pages.")
    dashboard.add_argument("--output", default="site", help="Output directory for HTML and JSON files.")
    foundation = subparsers.add_parser("build-data-foundation", help="Generate data foundation JSON artifacts.")
    foundation.add_argument("--output", default="site", help="Output directory for JSON files.")

    args = parser.parse_args(argv)
    if args.command == "build-dashboard":
        output = write_dashboard(args.output)
        print(f"Dashboard written to {output}")
        return 0
    if args.command == "build-data-foundation":
        output = write_data_foundation_artifacts(args.output)
        print(f"Data foundation artifacts written to {output}")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
