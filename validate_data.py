from pathlib import Path
from src.validator import load_and_validate

ROOT = Path(__file__).parent
components, prices, issues = load_and_validate(ROOT / "data")
print(f"Component rows: {len(components)}")
print(f"Price observations: {len(prices)}")
if issues:
    print(f"Issues found: {len(issues)}")
    for issue in issues:
        print(f"- {issue}")
    raise SystemExit(1)
print("Validation passed. Note: an empty template is valid, but it cannot generate recommendations yet.")
