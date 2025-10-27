import pathlib
import typer
import httpx

app = typer.Typer(
    help="Sanctions pipeline CLI"
)

@app.command()
def extract(url: str, out: str = "data/raw/source.json") -> None:
    """
    Download a URL to a local file.

    Args:
        url: URL to download
        out: Output file path (default: data/raw/source.json)
    """
    p = pathlib.Path(out)
    p.parent.mkdir(parents=True, exist_ok=True)
    
    with httpx.Client(timeout=30) as client:
        r = client.get(url)
        r.raise_for_status()
        p.write_bytes(r.content)
    
    typer.echo(f"Saved {out}")

if __name__ == "__main__":
    app()