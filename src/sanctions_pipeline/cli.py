import pathlib
import typer
import httpx

app = typer.Typer(
    help="Sanctions pipeline CLI"
)

@app.command()
def extract(
    url: str,
    out: str = "data/raw/source.json"
) -> None:
    """Download a URL to a local file."""
    p = pathlib.Path(out)
    p.parent.mkdir(parents=True, exist_ok=True)
    
    with httpx.Client(timeout=30) as client:
        r = client.get(url)
        r.raise_for_status()
        p.write_bytes(r.content)
    
    typer.echo(f"Saved {out}")

@app.command()
def transform(
    input: str = "data/raw/ofac_sdn.csv",
    output: str = "data/ftm/entities.jsonl"
) -> None:
    """Convert a CSV to FollowTheMoney JSONL entities."""
    from .transform import transform_csv_to_ftm
    n = transform_csv_to_ftm(input, output)
    typer.echo(f"Wrote {n} entities to {output}")

if __name__ == "__main__":
    app()