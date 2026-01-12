from pathlib import Path


def find_project_root(start: Path) -> Path:
    for parent in [start, *start.parents]:
        if (parent / "pyproject.toml").exists():
            return parent
    raise FileNotFoundError("Could not find project root (pyproject.toml)")


PROJECT_ROOT = find_project_root(Path(__file__).resolve())
DATA_PATH = PROJECT_ROOT / "data"
CLEANED_DATA = DATA_PATH / "processed"
TAXI_CSV_PATH = DATA_PATH / "raw" / "taxi_trip_pricing.csv"
