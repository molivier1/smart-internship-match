import json, os

RAW_FT_PATH = "data/offers/raw_offers.json"
JOBSPY_PATH = "data/offers/jobspy_offers.json"
MERGED_PATH = "data/offers/merged_offers.json"

def normalize_france_travail(raw_offers):
    # France Travail's raw fields, confirmed by extract_offers.py's own field
    # access below -- this project's most-tested France Travail assumptions.
    # url/date_posted are left None deliberately: no confirmed real field name
    # for either exists yet in this manual (Step 10 hadn't returned real, non-empty
    # results when this was written) -- once your own Step 10 run has real offers,
    # inspect one in data/offers/raw_offers.json yourself and add the real field
    # name here if you want working links, rather than this guessing a third time.
    normalized = []
    for o in raw_offers:
        normalized.append({
            "id": f"ft_{o['id']}",
            "source": "france_travail",
            "title": o.get("intitule"),
            "company": (o.get("entreprise") or {}).get("nom"),
            "location": (o.get("lieuTravail") or {}).get("libelle"),
            "description": o.get("description", ""),
            "url": None,
            "date_posted": None,
            "is_apprenticeship": o.get("alternance", False),
            "accessible_disability": o.get("accessibleTH", False),
            "publishable": True,  # official open government data -- safe to publish
        })
    return normalized

def load_jobspy():
    if not os.path.exists(JOBSPY_PATH):
        print(f"{JOBSPY_PATH} not found -- skipping (fine if you didn't do Step 11b).")
        return []
    with open(JOBSPY_PATH, encoding="utf-8") as f:
        data = json.load(f)
    return [
        {**o, "is_apprenticeship": False, "accessible_disability": False,
         "publishable": False}  # scraped content -- never published, see Step 11b
        for o in data["offers"]
    ]

def load_france_travail():
    if not os.path.exists(RAW_FT_PATH):
        print(f"{RAW_FT_PATH} not found -- skipping France Travail.")
        return []
    with open(RAW_FT_PATH, encoding="utf-8") as f:
        raw = json.load(f)
    return normalize_france_travail(raw["offers"])

def main():
    ft_offers = load_france_travail()
    jobspy_offers = load_jobspy()

    if not ft_offers and not jobspy_offers:
        raise FileNotFoundError(
            "No offer source is available. Add data/offers/raw_offers.json "
            "or data/offers/jobspy_offers.json before merging."
        )

    merged = ft_offers + jobspy_offers
    print(f"Merged {len(ft_offers)} France Travail + {len(jobspy_offers)} jobspy = {len(merged)} total")

    os.makedirs("data/offers", exist_ok=True)
    with open(MERGED_PATH, "w", encoding="utf-8") as f:
        json.dump({"offers": merged}, f, indent=2, ensure_ascii=False)
    print(f"Wrote {MERGED_PATH} ({len(merged)} offers) -- gitignored, local only")

if __name__ == "__main__":
    main()
