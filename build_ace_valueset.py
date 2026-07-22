"""
ACE Inhibitor Value Set Builder
--------------------------------
Queries the live NLM RxNorm / RxClass APIs to build a value set for
ACE inhibitors (ATC class C09A), from ingredient level down to NDC level.

Requires: pip install requests

Usage:
    python build_ace_valueset.py
Output:
    ace_inhibitors_ingredients.csv   (Step 3: RxNorm ingredients)
    ace_inhibitors_products.csv      (Step 4: clinical/branded drugs per ingredient)
    ace_inhibitors_ndcs.csv          (Step 5: NDCs per product)
"""

import csv
import time
import requests

BASE = "https://rxnav.nlm.nih.gov/REST"
ATC_CLASS_ID = "C09A"  # ACE inhibitors, plain


def get_json(url, params=None):
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    return r.json()


def step3_get_ingredients():
    """Get all RxNorm ingredients belonging to ATC class C09A."""
    url = f"{BASE}/rxclass/classMembers.json"
    data = get_json(url, {"classId": ATC_CLASS_ID, "relaSource": "ATC"})

    ingredients = []
    group = data.get("drugMemberGroup", {})
    for member in group.get("drugMember", []):
        concept = member["minConcept"]
        ingredients.append({
            "rxcui": concept["rxcui"],
            "name": concept["name"],
            "tty": concept["tty"],
        })

    with open("ace_inhibitors_ingredients.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["rxcui", "name", "tty"])
        w.writeheader()
        w.writerows(ingredients)

    print(f"Step 3 done: {len(ingredients)} ingredients -> ace_inhibitors_ingredients.csv")
    return ingredients


def step4_get_products(ingredients):
    """For each ingredient, get related clinical/branded drug products."""
    rows = []
    for ing in ingredients:
        url = f"{BASE}/rxcui/{ing['rxcui']}/related.json"
        data = get_json(url, {"tty": "SCD+SBD+GPCK+BPCK"})
        groups = data.get("relatedGroup", {}).get("conceptGroup", []) or []
        for grp in groups:
            for prop in grp.get("conceptProperties", []) or []:
                rows.append({
                    "ingredient_rxcui": ing["rxcui"],
                    "ingredient_name": ing["name"],
                    "product_rxcui": prop["rxcui"],
                    "product_name": prop["name"],
                    "tty": prop["tty"],
                })
        time.sleep(0.2)  # be polite to the free public API

    with open("ace_inhibitors_products.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=[
            "ingredient_rxcui", "ingredient_name",
            "product_rxcui", "product_name", "tty"
        ])
        w.writeheader()
        w.writerows(rows)

    print(f"Step 4 done: {len(rows)} products -> ace_inhibitors_products.csv")
    return rows


def step5_get_ndcs(products):
    """For each product, get all active NDCs."""
    rows = []
    seen = set()
    for prod in products:
        rxcui = prod["product_rxcui"]
        if rxcui in seen:
            continue
        seen.add(rxcui)

        url = f"{BASE}/rxcui/{rxcui}/ndcs.json"
        data = get_json(url)
        ndc_group = data.get("ndcGroup", {})
        ndc_list = ndc_group.get("ndcList", {}).get("ndc", []) or []
        for ndc in ndc_list:
            rows.append({
                "product_rxcui": rxcui,
                "product_name": prod["product_name"],
                "ndc": ndc,
            })
        time.sleep(0.2)

    with open("ace_inhibitors_ndcs.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["product_rxcui", "product_name", "ndc"])
        w.writeheader()
        w.writerows(rows)

    print(f"Step 5 done: {len(rows)} NDCs -> ace_inhibitors_ndcs.csv")
    return rows


if __name__ == "__main__":
    print("Building ACE inhibitor value set from live RxNorm/RxClass API...\n")
    ingredients = step3_get_ingredients()
    products = step4_get_products(ingredients)
    ndcs = step5_get_ndcs(products)
    print("\nDone. Three CSV files written to the current directory.")
