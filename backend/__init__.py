from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_FRONTEND_BACKEND = _PROJECT_ROOT / "frontend" / "backend"

if _FRONTEND_BACKEND.exists():
    __path__ = [str(_FRONTEND_BACKEND)]
