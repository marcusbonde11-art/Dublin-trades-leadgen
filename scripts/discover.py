#!/usr/bin/env python3
"""Find HVAC and plumbing businesses around Dublin, OH via the Google Places API (New).

Usage:
    GOOGLE_PLACES_API_KEY=... python scripts/discover.py [--known data/known_place_ids.txt]

Writes data/discovered.csv: one row per unique business with a basic fit
screen (distance, size, rating, franchise / multi-location flags). Businesses
already in the tracker (IDs listed in --known) are skipped so reruns only add
new ones. The API key is read from the environment and never stored.
"""
import argparse
import csv
import json
import math
import os
import pathlib
import re
import sys
import time

import requests
import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
ENDPOINT = "https://places.googleapis.com/v1/places:searchText"
FIELDS = ",".join(
    "places." + f
    for f in [
        "id", "displayName", "formattedAddress", "location", "nationalPhoneNumber",
        "websiteUri", "googleMapsUri", "rating", "userRatingCount", "businessStatus",
        "primaryType",
    ]
) + ",nextPageToken"
MAX_REQUESTS = 120  # safety cap per run, keeps usage inside the free monthly tier


def miles(a_lat, a_lng, b_lat, b_lng):
    r = 3958.8
    p1, p2 = math.radians(a_lat), math.radians(b_lat)
    dp, dl = p2 - p1, math.radians(b_lng - a_lng)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h))


def search(key, query, center, radius_mi, budget):
    headers = {"X-Goog-Api-Key": key, "X-Goog-FieldMask": FIELDS}
    body = {
        "textQuery": query,
        "pageSize": 20,
        "locationBias": {"circle": {"center": {"latitude": center["lat"], "longitude": center["lng"]},
                                    "radius": min(radius_mi * 1609.34, 50000.0)}},
    }
    while budget[0] > 0:
        budget[0] -= 1
        resp = requests.post(ENDPOINT, json=body, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        yield from data.get("places", [])
        token = data.get("nextPageToken")
        if not token:
            return
        body["pageToken"] = token
        time.sleep(1)


def domain(url):
    m = re.match(r"https?://(?:www\.)?([^/?#]+)", url or "")
    return m.group(1).lower() if m else ""


def screen(place, trade, cfg):
    q = cfg["qualification"]
    c = cfg["territory"]["center"]
    name = place.get("displayName", {}).get("text", "")
    loc = place.get("location", {})
    dist = miles(c["lat"], c["lng"], loc.get("latitude", 0), loc.get("longitude", 0))
    reviews = place.get("userRatingCount", 0) or 0
    rating = place.get("rating", 0) or 0
    site = place.get("websiteUri", "") or ""
    reasons = []
    if place.get("businessStatus") not in (None, "OPERATIONAL"):
        reasons.append("not operational")
    if dist > cfg["territory"]["max_distance_miles"]:
        reasons.append(f"{dist:.1f} mi away")
    if any(re.search(r"\b" + re.escape(p) + r"\b", name.lower()) for p in q["exclude_name_patterns"]):
        reasons.append("franchise/national brand")
    if any(p in site.lower() for p in q["multi_location_url_patterns"]):
        reasons.append("multi-location site")
    if reviews < q["min_reviews"]:
        reasons.append("too few reviews")
    if reviews > q["max_reviews"]:
        reasons.append("likely too large")
    if rating and rating < q["min_rating"]:
        reasons.append("low rating")
    if not site:
        reasons.append("no website")
    text = f"{name} {domain(site)}".lower()
    if not any(k in text for k in q["trade_keywords"]):
        reasons.append("not clearly HVAC/plumbing")
    elif any(k in text for k in q["exclude_keywords"]) and not any(
            k in text for k in ("hvac", "plumb", "heating")):
        reasons.append("adjacent trade")
    ptype = place.get("primaryType", "")
    if ptype and ptype not in q["allowed_primary_types"]:
        reasons.append(f"category: {ptype}")
    return {
        "place_id": place["id"],
        "business_name": name,
        "trade": trade,
        "address": place.get("formattedAddress", ""),
        "distance_mi": f"{dist:.1f}",
        "phone": place.get("nationalPhoneNumber", ""),
        "website": site,
        "maps_url": place.get("googleMapsUri", ""),
        "rating": rating,
        "reviews": reviews,
        "primary_type": place.get("primaryType", ""),
        "screen": "pass" if not reasons else "fail",
        "screen_reasons": "; ".join(reasons),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--known", default=str(ROOT / "data/known_place_ids.txt"))
    ap.add_argument("--out", default=str(ROOT / "data/discovered.csv"))
    ap.add_argument("--from-cache", action="store_true",
                    help="re-screen the last raw API results without calling the API")
    args = ap.parse_args()

    cfg = yaml.safe_load((ROOT / "config.yaml").read_text())
    known = set()
    if os.path.exists(args.known):
        known = {l.strip() for l in open(args.known) if l.strip()}

    cache = ROOT / "data/raw_places.json"
    budget = [MAX_REQUESTS]
    if args.from_cache:
        raw = json.loads(cache.read_text())
    else:
        key = os.environ.get("GOOGLE_PLACES_API_KEY")
        if not key:
            sys.exit("Set GOOGLE_PLACES_API_KEY")
        raw = []
        for trade, terms in cfg["trades"].items():
            for term in terms:
                for town in cfg["territory"]["towns"]:
                    for place in search(key, f"{term} in {town}, Ohio", cfg["territory"]["center"],
                                        cfg["territory"]["max_distance_miles"], budget):
                        raw.append([trade, place])
        os.makedirs(cache.parent, exist_ok=True)
        cache.write_text(json.dumps(raw))

    found = {}
    for trade, place in raw:
        pid = place["id"]
        if pid in known:
            continue
        if pid in found:
            if trade not in found[pid]["trade"]:
                found[pid]["trade"] += "+" + trade
            continue
        found[pid] = screen(place, trade, cfg)

    # One company often has several Google listings (per town / per trade).
    # Keep the closest passing listing per website domain; mark the rest.
    by_domain = {}
    for r in sorted(found.values(), key=lambda r: float(r["distance_mi"])):
        dom = domain(r["website"])
        if not dom or r["screen"] != "pass":
            continue
        if dom in by_domain:
            r["screen"] = "fail"
            r["screen_reasons"] = f"duplicate listing of {by_domain[dom]}"
        else:
            by_domain[dom] = r["business_name"]

    rows = sorted(found.values(), key=lambda r: (r["screen"] != "pass", float(r["distance_mi"])))
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ["place_id"])
        w.writeheader()
        w.writerows(rows)
    passed = sum(r["screen"] == "pass" for r in rows)
    print(f"{len(rows)} new businesses, {passed} pass screen, {MAX_REQUESTS - budget[0]} API requests -> {args.out}")


if __name__ == "__main__":
    main()
