from __future__ import annotations

import argparse
import json

from .engine import DocumentSearchEngine


def main() -> None:
    parser = argparse.ArgumentParser(description="Industrial manual search with citations")
    parser.add_argument("--store", default="data/manual_index.json")
    sub = parser.add_subparsers(dest="command", required=True)

    ingest = sub.add_parser("ingest")
    ingest.add_argument("path")
    ingest.add_argument("--document-id", required=True)
    ingest.add_argument("--title", required=True)
    ingest.add_argument("--instrument", required=True)
    ingest.add_argument("--model")

    search = sub.add_parser("search")
    search.add_argument("query")
    search.add_argument("--instrument")
    search.add_argument("--model")
    search.add_argument("--top-k", type=int, default=5)

    args = parser.parse_args()
    engine = DocumentSearchEngine(args.store)
    if args.command == "ingest":
        engine.ingest_file(args.path, args.document_id, args.title, args.instrument, args.model)
        print(json.dumps({"status": "ok", "document_id": args.document_id}, ensure_ascii=False))
    else:
        print(json.dumps(engine.answer(args.query, instrument=args.instrument, model=args.model, top_k=args.top_k), ensure_ascii=False, indent=2))
