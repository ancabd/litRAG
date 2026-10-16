"""python -m app [--port 8000] [--reload]"""
import argparse

import uvicorn


def main() -> None:
    ap = argparse.ArgumentParser(description="Run the litrag server")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--reload", action="store_true", help="restart on code changes (development)")
    args = ap.parse_args()
    print(f"litrag: http://{args.host}:{args.port}   (API docs at /api/docs)")
    uvicorn.run("app.main:app", host=args.host, port=args.port, reload=args.reload)


if __name__ == "__main__":
    main()
