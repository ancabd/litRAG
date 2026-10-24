"""FastAPI app: the API under /api, and the built web UI (web/dist) at /.

Adding a feature = a router in app/routers + a page in web/src/pages. A future
/api/ask route plugs in the same way, reusing ChunkService for retrieval.
"""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from .config import Settings
from .deps import Services
from .routers import ask, evals, meta, papers, questions, search

API_PREFIX = "/api"


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings.from_env()
    app = FastAPI(title="litrag", version="0.1.0", docs_url="/api/docs", openapi_url="/api/openapi.json")
    app.state.services = Services.build(settings)
    # the Vite dev server runs on another port during development
    app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
                       allow_methods=["*"], allow_headers=["*"])
    for r in (meta.router, papers.router, questions.router, search.router, evals.router, ask.router):
        app.include_router(r, prefix=API_PREFIX)
    _mount_ui(app, settings.web_dist)
    return app


def _mount_ui(app: FastAPI, dist: Path) -> None:
    index = dist / "index.html"
    if (dist / "assets").is_dir():
        app.mount("/assets", StaticFiles(directory=dist / "assets"), name="assets")

    @app.get("/{path:path}", include_in_schema=False)
    def spa(path: str):
        if path.startswith("api/"):
            raise HTTPException(404, f"No API route /{path}")
        if not index.exists():
            return HTMLResponse(
                "<p>The API is running (see <a href='/api/docs'>/api/docs</a>), but the UI isn't built yet. "
                "Run <code>npm run build</code> in <code>web/</code>, or use <code>npm run dev</code> and open "
                "<a href='http://localhost:5173'>localhost:5173</a>.</p>")
        candidate = (dist / path).resolve()
        if path and candidate.is_file() and dist.resolve() in candidate.parents:
            return FileResponse(candidate)
        return FileResponse(index)  # client-side routing: /papers/W123 etc.


app = create_app()
