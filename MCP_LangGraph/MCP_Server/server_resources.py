from mcp.server.fastmcp import FastMCP
from pathlib import Path

mcp = FastMCP("file-resource-server")

BASE_DIR = Path(__file__).parent / "data"

@mcp.resource(
    uri="file://docs/{filename}",
    name="Documentation file",
    description="Read-only text files from local data directory",
    mime_type="text/plain"
)
async def read_file_resource(filename: str):
    file_path = BASE_DIR / filename

    if not file_path.exists():
        return f"File not found: {filename}"

    return file_path.read_text(encoding="utf-8")


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
