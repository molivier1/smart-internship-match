import csv, json, os, time

def normalize_skill(skill):
    """Make capitalization and repeated whitespace irrelevant for exact matching."""
    return " ".join(skill.casefold().split())

def load_profile(path="data/profile/my_skills.csv"):
    profile = {}
    with open(path, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            profile[row["skill"]] = {"level": int(row["level"]), "evidence": row["evidence"]}
    return profile

def score_offer(profile, required_skills):
    # Compare whole skill names (so C does not accidentally match C++) while
    # ignoring capitalization and extra whitespace.
    profile_skills = {normalize_skill(skill) for skill in profile}
    matched, gaps, seen = [], [], set()
    for skill in required_skills or []:
        if not isinstance(skill, str) or not skill.strip():
            continue
        key = normalize_skill(skill)
        if key in seen:
            continue
        seen.add(key)
        (matched if key in profile_skills else gaps).append(skill.strip())

    # No extracted requirements means there is no evidence of a match, so the
    # offer gets 0 coverage instead of an artificial perfect score.
    coverage = len(matched) / len(seen) if seen else 0.0
    return {"score": coverage, "coverage": coverage, "matched": matched, "gaps": gaps}

def build_output(results, profile):
    gap_counts = {}
    matched_counts = {}
    for r in results:
        for g in r["gaps"]:
            gap_counts[g] = gap_counts.get(g, 0) + 1
        for s in r["matched"]:
            matched_counts[s] = matched_counts.get(s, 0) + 1
    top_gaps = sorted(gap_counts.items(), key=lambda kv: kv[1], reverse=True)[:10]
    top_matched = sorted(matched_counts.items(), key=lambda kv: kv[1], reverse=True)[:10]
    n_with_comp = sum(1 for r in results if r.get("compensation_mentioned"))
    return {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "n_offers": len(results),
        "offers": results,
        "top_skill_gaps": [{"skill": s, "count": c} for s, c in top_gaps],
        # top_matched_skills mirrors top_skill_gaps but for what you're already
        # strong in -- ranked by how often it's actually asked for across your real
        # offers, with your own self-assessed level attached so the dashboard can
        # highlight "your most in-demand strength", not just "a skill you have".
        
        
        #"top_matched_skills": [{"skill": s, "count": c, "level": profile[s]["level"]} for s, c in top_matched],
        "top_matched_skills": [
            {
                "skill": s,
                "count": c,
                "level": next(
                    profile[original]["level"]
                    for original in profile
                    if normalize_skill(original) == normalize_skill(s)
                )
            }
            for s, c in top_matched
        ],


        # Set expectations, don't hide the gap: real testing (see Step 12's note)
        # found compensation stated explicitly in only ~6.5% of real postings, so
        # this is reported as a count, not built into a chart that would mostly be
        # empty space.
        "n_offers_with_compensation": n_with_comp,
    }

def main():
    profile = load_profile()
    with open("data/offers/structured_offers.json", encoding="utf-8") as f:
        data = json.load(f)

    results = []
    for offer in data["offers"]:
        m = score_offer(profile, offer["required_skills"])
        results.append({**offer, **m})

    results.sort(key=lambda r: r["score"], reverse=True)
    for r in results:
        print(f"  {r['score']:.3f}  {r['title']} @ {r['company']}  ({r['source']}, "
              f"coverage {r['coverage']:.0%}, gaps: {r['gaps']})")

    # Two outputs, not one: matches_all_local.json (every source, gitignored, for
    # your own eyes only) and docs/data/matches.json (publishable sources only,
    # committed, visible on your public Pages dashboard). "publishable" was set in
    # Step 11c -- True for France Travail's official data, False for anything from
    # jobspy (Step 11b). If you never did Step 11b, every offer is publishable and
    # the two files end up identical -- this split is a genuine no-op with one source.
    os.makedirs("data/offers", exist_ok=True)
    with open("data/offers/matches_all_local.json", "w", encoding="utf-8") as f:
        json.dump(build_output(results, profile), f, indent=2, ensure_ascii=False)
    print(f"Wrote data/offers/matches_all_local.json ({len(results)} offers) -- gitignored, local only")

    public_results = [r for r in results if r.get("publishable", False)]
    os.makedirs("docs/data", exist_ok=True)
    with open("docs/data/matches.json", "w", encoding="utf-8") as f:
        json.dump(build_output(public_results, profile), f, indent=2, ensure_ascii=False)
    print(f"Wrote docs/data/matches.json ({len(public_results)} of {len(results)} offers -- publishable sources only)")

if __name__ == "__main__":
    main()
