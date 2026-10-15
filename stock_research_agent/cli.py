# -*- coding: utf-8 -*-
"""
cli.py — Command line interface for the Stock Research Agent.

  python -m stock_research_agent NVDA [AAPL MSFT ...]   research one or many
  python -m stock_research_agent "Inditex"               company names work too
  python -m stock_research_agent --list                  list KB coverage
  python -m stock_research_agent serve --port 8000       interactive web app
  python -m stock_research_agent --help
"""
from __future__ import annotations

import argparse
import sys

from . import research, report_html


def _print_summary(result: dict) -> None:
    print("\n".join(research.summary_lines(result)))


def cmd_research(args: argparse.Namespace) -> int:
    queries = args.tickers
    if not queries:
        print("Nothing to research. Pass a ticker or company name.", file=sys.stderr)
        return 2
    ok = 0
    for q in queries:
        try:
            result = research.run(q)
            _print_summary(result)
            html = report_html.build(result)
            path = research.save_report(result, html)
            print(f"  HTML report: {path}\n")
            ok += 1
        except Exception as e:  # noqa: BLE001
            print(f"  [error] {q}: {e}\n", file=sys.stderr)
    return 0 if ok else 1


def cmd_list(_args: argparse.Namespace) -> int:
    from .knowledge_base import list_profiles
    profs = list_profiles()
    print(f"Knowledge base coverage ({len(profs)} deep profiles, Oct 2026)\n")
    for p in profs:
        print(f"  {p['ticker']:<9} {p['name']:<44} {p['sector']}")
    print("\nAny other ticker/company name is resolved via the S&P 500 list and the")
    print("dynamic sector synthesizer (clearly-labelled estimates).")
    return 0


def cmd_serve(args: argparse.Namespace) -> int:
    from .server import serve
    serve(host=args.host, port=args.port)
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="stock_research_agent",
        description="Reusable on-demand Stock Research Agent — 7-stage pipeline "
                    "with self-contained HTML reports.")
    ap.add_argument("tickers", nargs="*", help="tickers or company names to research")
    ap.add_argument("--list", action="store_true", help="list KB coverage and exit")
    ap.add_argument("--serve", action="store_true", help="run the interactive web app")
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--port", type=int, default=8000)
    args = ap.parse_args(argv)

    if args.serve:
        return cmd_serve(args)
    if args.list:
        return cmd_list(args)
    return cmd_research(args)


if __name__ == "__main__":
    raise SystemExit(main())
