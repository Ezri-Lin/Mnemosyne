#!/usr/bin/env python3
"""Start a static server for generated Book Analyst pages."""

import argparse
import json
import os
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Serve generated Book Analyst HTML. Static files update on refresh without restart.")
    parser.add_argument("--config", default=".book-analyst/config.json")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()

    config = json.loads(Path(args.config).expanduser().resolve().read_text(encoding="utf-8"))
    web_root = Path(config["webOutputRoot"]).expanduser().resolve()
    web_root.mkdir(parents=True, exist_ok=True)
    os.chdir(web_root)
    server = ThreadingHTTPServer((args.host, args.port), SimpleHTTPRequestHandler)
    print(f"Serving Book Analyst pages at http://{args.host}:{args.port}/")
    print(f"Web root: {web_root}")
    print("Refresh the browser after JSON/HTML regeneration; no service restart is required.")
    server.serve_forever()


if __name__ == "__main__":
    main()
