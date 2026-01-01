#!/usr/bin/env python3
"""
CLI for CODELANCER package.
Works in two modes:
- server -> starts the FastAPI server with uvicorn
- generate/correct/analyze -> calls the local engine directly (no HTTP)
"""

import argparse
import sys
import uvicorn
from codelancer.core import CodeGenerator, AutoCorrector

generator = CodeGenerator()
corrector = AutoCorrector()

def run_server(args):
    # Run uvicorn programmatically; keep reload off for programmatic runs
    uvicorn.run("codelancer.api.main:app", host=args.host, port=args.port, reload=args.reload)

def cmd_generate(args):
    description = args.description
    result = generator.generate(description)
    code = result["generated_code"]
    if args.output:
        with open(args.output, "w") as f:
            f.write(code)
        print(f"✅ Generated code saved to {args.output}")
    else:
        print(code)

def cmd_correct(args):
    if args.file:
        with open(args.file, "r") as f:
            code = f.read()
    else:
        print("Paste your code (Ctrl-D to end):")
        code = sys.stdin.read()
    result = corrector.correct(code)
    corrected = result["corrected"]
    if args.output:
        with open(args.output, "w") as f:
            f.write(corrected)
        print(f"✅ Corrected code saved to {args.output}")
    else:
        print(corrected)
    if result["corrections"]:
        print("\nCorrections:")
        for c in result["corrections"]:
            print(f"  • {c}")

def cmd_analyze(args):
    if args.file:
        with open(args.file, "r") as f:
            code = f.read()
    else:
        print("Paste your code (Ctrl-D to end):")
        code = sys.stdin.read()
    lines = code.count("\n") + 1
    chars = len(code)
    print("Code analysis:")
    print(f"  Lines: {lines}")
    print(f"  Characters: {chars}")
    avg = chars // max(1, lines)
    print(f"  Avg line length: {avg}")
    issues = []
    if "retrun" in code:
        issues.append("Found 'retrun' (should be 'return')")
    if issues:
        print("\nIssues found:")
        for i in issues:
            print(f"  • {i}")
    else:
        print("\nNo obvious issues found.")

def main():
    parser = argparse.ArgumentParser(prog="codelancer", description="CODELANCER CLI")
    sub = parser.add_subparsers(dest="cmd")

    srv = sub.add_parser("server", help="Start API server")
    srv.add_argument("--host", default="0.0.0.0")
    srv.add_argument("--port", type=int, default=8000)
    srv.add_argument("--reload", action="store_true", help="Enable reload (dev only)")

    gen = sub.add_parser("generate", help="Generate code from description")
    gen.add_argument("description")
    gen.add_argument("--output", "-o", help="Write output to file")

    corr = sub.add_parser("correct", help="Auto-correct code")
    corr.add_argument("--file", "-f", help="Input file")
    corr.add_argument("--output", "-o", help="Write corrected code to file")

    ana = sub.add_parser("analyze", help="Analyze code")
    ana.add_argument("--file", "-f", help="Input file")

    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        return

    if args.cmd == "server":
        run_server(args)
    elif args.cmd == "generate":
        cmd_generate(args)
    elif args.cmd == "correct":
        cmd_correct(args)
    elif args.cmd == "analyze":
        cmd_analyze(args)

if __name__ == "__main__":
    main()
