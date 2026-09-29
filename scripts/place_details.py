#!/usr/bin/env python3
"""Fetch Google Places details (reviews, hours, summary) for research.

Usage: GOOGLE_PLACES_API_KEY=... python scripts/place_details.py PLACE_ID [PLACE_ID ...]
Writes data/research/<place_id>.json and prints a compact digest.
"""
import json
import os
import pathlib
import sys

import requests

ROOT = pathlib.Path(__file__).resolve().parent.parent
FIELDS = ("id,displayName,formattedAddress,websiteUri,nationalPhoneNumber,rating,userRatingCount,"
          "regularOpeningHours.weekdayDescriptions,editorialSummary,reviews")


def main():
    key = os.environ["GOOGLE_PLACES_API_KEY"]
    out = ROOT / "data/research"
    out.mkdir(parents=True, exist_ok=True)
    for pid in sys.argv[1:]:
        r = requests.get(f"https://places.googleapis.com/v1/places/{pid}",
                         headers={"X-Goog-Api-Key": key, "X-Goog-FieldMask": FIELDS}, timeout=30)
        r.raise_for_status()
        d = r.json()
        (out / f"{pid}.json").write_text(json.dumps(d, indent=2))
        print("=" * 80)
        print(d.get("displayName", {}).get("text"), "|", d.get("rating"), "/", d.get("userRatingCount"))
        print("hours:", "; ".join(d.get("regularOpeningHours", {}).get("weekdayDescriptions", [])))
        if d.get("editorialSummary"):
            print("summary:", d["editorialSummary"].get("text"))
        for rv in d.get("reviews", []):
            t = rv.get("text", {}).get("text", "").replace("\n", " ")
            print(f"  [{rv.get('rating')}* {rv.get('relativePublishTimeDescription')}] {t[:400]}")


if __name__ == "__main__":
    main()
