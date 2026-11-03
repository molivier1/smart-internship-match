"""Convert the JobSpy sample CSV into fetch_offers.py's raw JSON format.

This lets the downstream France Travail normalization step consume the sample
offers without changing fetch_offers.py or the rest of the pipeline.
"""

import csv
import json
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
INPUT_PATH = ROOT / "data" / "offers" / "jobs_sample.csv"
OUTPUT_PATH = ROOT / "data" / "offers" / "raw_offers.json"
MAX_OFFERS = 50


def value(row, key):
    """Return a non-empty CSV value, or None for blank cells."""
    result = (row.get(key) or "").strip()
    return result or None


def convert_row(row, row_number):
    source_id = value(row, "id")
    return {
        # Keep the source identifier recognizable and unique in the FT-shaped
        # raw file. The row fallback also handles missing IDs in future CSVs.
        "id": f"sample_{source_id}" if source_id else f"sample_row_{row_number}",
        "intitule": value(row, "title"),
        "entreprise": {"nom": value(row, "company")},
        "lieuTravail": {"libelle": value(row, "location")},
        "description": value(row, "description") or "",
        # The sample contains general job listings and has no verified FT
        # fields for these flags, so use the same false defaults as the
        # downstream France Travail normalizer.
        "alternance": False,
        "accessibleTH": False,
    }


def main():
    with INPUT_PATH.open("r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        if not reader.fieldnames or not {"id", "title", "company", "location", "description"}.issubset(reader.fieldnames):
            raise ValueError(
                "CSV must contain id, title, company, location, and description columns"
            )
        offers = [
            convert_row(row, index)
            for index, row in enumerate(reader, start=1)
            if index <= MAX_OFFERS
        ]

    payload = {
        "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "search_params": {"source": "data/offers/jobs_sample.csv"},
        "offers": offers,
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as json_file:
        json.dump(payload, json_file, indent=2, ensure_ascii=False)

    print(f"Wrote {OUTPUT_PATH.relative_to(ROOT)} ({len(offers)} offers)")


if __name__ == "__main__":
    main()
