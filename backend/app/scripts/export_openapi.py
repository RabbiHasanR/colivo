import json
from pathlib import Path

from app.main import app

# api/openapi.json at the repo root: the contract the web and mobile clients use.
OPENAPI_FILE = Path(__file__).resolve().parents[3] / "api" / "openapi.json"


def export_openapi(path: Path = OPENAPI_FILE) -> None:
    """Write the app's OpenAPI document to ``path`` (``make api-export``).

    Args:
        path: Where to write the JSON file.
    """
    path.write_text(json.dumps(app.openapi(), indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    export_openapi()
