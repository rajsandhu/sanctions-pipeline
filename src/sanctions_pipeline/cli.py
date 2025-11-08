import pathlib
import typer
import httpx
import logging

app = typer.Typer(help="Sanctions pipeline CLI")


@app.command()
def extract(url: str, out: str = "data/raw/source.json") -> None:
    """Download a URL to a local file."""
    logging.info(f"Downloading: {url}")
    p = pathlib.Path(out)
    p.parent.mkdir(parents=True, exist_ok=True)

    with httpx.Client(timeout=30) as client:
        r = client.get(url)
        r.raise_for_status()
        p.write_bytes(r.content)

    logging.info(f"Saved: {out}")
    typer.echo(f"Saved {out}")


@app.command()
def transform(
    input: str = "data/raw/ofac_sdn.csv",
    output: str = "data/ftm/entities.jsonl",
    format: str = typer.Option(
        "jsonl", "--format", "-f", help="Output format: jsonl or ftm"
    ),
) -> None:
    """
    Convert a CSV/XLSX file to either simplified JSONL or FollowTheMoney JSONL format.

    Args:
        input: Path to the input CSV/XLSX file
        output: Path where the transformed JSONL file will be saved
        format: Output format ('jsonl' or 'ftm')
    """
    from .transform import transform_csv_to_ftm, transform_to_simple_jsonl

    try:
        if format.lower() == "ftm":
            n = transform_csv_to_ftm(input, output)
            typer.echo(f"Wrote {n} FTM entities to {output}")
        else:
            n = transform_to_simple_jsonl(input, output)
            typer.echo(f"Wrote {n} simple entities to {output}")
    except Exception as e:
        typer.secho(f"Error during transformation: {str(e)}", fg=typer.colors.RED)
        raise typer.Exit(1)


@app.command()
def screen(
    input_csv: str = typer.Option(
        ..., "--input-csv", help="CSV file with names to screen"
    ),
    entities: str = typer.Option(
        "data/ftm/entities.jsonl", "--entities", help="JSONL entities file"
    ),
    output_csv: str = typer.Option(
        "data/screen/results.csv", "--output-csv", help="Output CSV with matches"
    ),
):
    """Match names in a CSV against entities; write matches to CSV."""
    from .screen import screen_names

    n = screen_names(input_csv, entities, output_csv)
    typer.echo(f"Matched {n} rows -> {output_csv}")


@app.command()
def validate(input: str = "data/ftm/entities.jsonl", min_rows: int = 1):
    """Validate a JSONL file: parses JSON and enforces min row count."""
    from .validate import validate_jsonl

    summary = validate_jsonl(input, min_rows=min_rows)
    typer.echo(f"Valid: {summary['total']} records")


@app.callback()
def main(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose logging")
):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")


if __name__ == "__main__":
    app()
