"""A transparent baseline checker for known entities in a reference translation."""
import json
import re
from pathlib import Path

def normalize(text):
    return re.sub(r"\s+", " ", text.lower().strip())

def check(reference, hypothesis, entities):
    ref, hyp = normalize(reference), normalize(hypothesis)
    rows = []
    for item in entities:
        value = normalize(item["value"])
        present_in_ref = value in ref
        present_in_hyp = value in hyp
        rows.append({
            "type": item["type"], "value": item["value"],
            "expected_in_reference": present_in_ref,
            "found_in_hypothesis": present_in_hyp,
            "correct": present_in_ref == present_in_hyp
        })
    return {"checked": len(rows), "correct": sum(r["correct"] for r in rows),
            "accuracy": (sum(r["correct"] for r in rows) / len(rows)) if rows else None,
            "items": rows}

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--reference", required=True)
    p.add_argument("--hypothesis", required=True)
    p.add_argument("--entities-json", required=True, help='JSON array: [{"type":"amount","value":"five lakh"}]')
    a = p.parse_args()
    result = check(a.reference, a.hypothesis, json.loads(a.entities_json))
    print(json.dumps(result, indent=2))
