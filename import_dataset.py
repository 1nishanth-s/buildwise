
import csv
import json
from pathlib import Path

DATA_DIR = Path("data")
SOURCE_FILE = DATA_DIR / "pc-builder-parts.json"
OUTPUT_FILE = DATA_DIR / "components.csv"

CATEGORIES = [
    "cpu",
    "gpu",
    "motherboard",
    "ram",
    "storage",
    "psu",
    "case",
    "cooler",
]
CATEGORY_ALIASES = {
    "cpu": "CPU",
    "gpu": "GPU",
    "motherboard": "Motherboard",
    "ram": "RAM",
    "storage": "Storage",
    "psu": "PSU",
    "case": "Case",
    "cooler": "Cooler",
}

SOURCE_NAME = "TechFuelHQ PC Builder Parts Dataset"
SOURCE_URL = "https://techfuelhq.com/tools/pc-builder/"
SOURCE_LICENSE = "CC BY 4.0"

FIELDS = [
    "component_id",
    "category",
    "brand",
    "model",
    "specs_json",
    "source_name",
    "source_url",
    "source_license",
    "identity_status",
]


def main():
    if not SOURCE_FILE.exists():
        raise FileNotFoundError(
            f"Could not find {SOURCE_FILE}. "
            "Run this script from your project root."
        )

    with SOURCE_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    rows = []

    for category in CATEGORIES:
        category_name = CATEGORY_ALIASES.get(category.casefold(), category)
        for item in data.get(category, []):
            component_id = item.get("id")

            if not component_id:
                raise ValueError(
                    f"Missing ID in category {category}: {item}"
                )

            # Preserve every source field except those mapped
            # separately into the CSV columns.
            specs = {
                key: value
                for key, value in item.items()
                if key not in {"id", "vendor", "model"}
            }
            rows.append({
                "component_id": component_id,
                "category": category_name,
                "brand": item.get("vendor", ""),
                "model": item.get("model", ""),
                "specs_json": json.dumps(
                    specs, ensure_ascii=False
                ),
                "source_name": SOURCE_NAME,
                "source_url": SOURCE_URL,
                "source_license": SOURCE_LICENSE,
                "identity_status": "needs_review",
            })

    # Prevent accidentally overwriting a catalog containing
    # records you entered manually.
    if OUTPUT_FILE.exists():
        with OUTPUT_FILE.open(
            "r", encoding="utf-8-sig", newline=""
        ) as file:
            existing = list(csv.DictReader(file))

        if existing:
            raise FileExistsError(
                f"{OUTPUT_FILE} already contains "
                f"{len(existing)} records. Back it up or "
                "merge deliberately before importing."
            )

    with OUTPUT_FILE.open(
        "w", encoding="utf-8-sig", newline=""
    ) as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Imported {len(rows)} components.")
    print(f"Saved to: {OUTPUT_FILE}")
    print("Price observations were not imported.")


if __name__ == "__main__":
    main()
