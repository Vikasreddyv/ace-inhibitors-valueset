# ACE Inhibitors Value Set

A VSAC-style, ingredient-level value set for **ACE inhibitors** (ATC class `C09AA`),
defined using **RxNorm** ingredient concepts with **ATC** cross-references.

## Scope

- **Level:** Ingredient only (RxNorm TTY = `IN`)
- **Class:** ATC `C09AA` — ACE inhibitors, plain
- **Primary code system:** RxNorm
- **Cross-referenced code system:** ATC (WHO)
- **Definition type:** Extensional (explicit code list)

This value set intentionally stops at the ingredient level. It does **not** include
specific dose forms, branded products, packs, or NDC codes — those are a separate,
much larger, and more volatile "expansion" layer (see `scripts/` for how to generate
that on demand instead of hand-maintaining it here).

## Repo structure

```
ace-inhibitors-valueset/
├── README.md
├── LICENSE
├── data/
│   ├── ace_inhibitors_ingredients.csv     # the value set itself (source of truth)
│   └── ace-inhibitors-valueset.json       # same data as a FHIR ValueSet resource
├── scripts/
│   └── build_ace_valueset.py              # pulls live data from RxNorm/RxClass API
└── docs/
    └── methodology.md                     # how this was built, step by step
```

## How this value set was built

1. Identified the ATC class `C09AA` ("ACE inhibitors, plain") via RxClass.
2. Pulled all RxNorm ingredient concepts (`TTY=IN`) mapped to that class, with
   classification source set to **ATC** (not ATCPROD — that's product level).
3. Cross-referenced each RxNorm ingredient back to its ATC code.
4. Verified counts and codes against the live RxClass browser
   (`https://mor.nlm.nih.gov/RxClass/`).

Full narrative in [`docs/methodology.md`](docs/methodology.md).

## Regenerating / updating

RxNorm publishes monthly releases. To refresh this value set with current data:

```bash
pip install requests
python scripts/build_ace_valueset.py
```

This overwrites `data/ace_inhibitors_ingredients.csv` with a fresh pull from the
live API — treat that file as **regenerable**, not hand-edited, once the script
is in place.

## Status

⚠️ `data/ace_inhibitors_ingredients.csv` currently contains the ingredients
confirmed live via the RxClass browser so far. Confirm the full row count (14)
against your own RxClass export and update if any rows are missing — see
`docs/methodology.md` for what to check.

## License

MIT (see `LICENSE`). RxNorm and ATC data themselves are subject to their
respective source terms (NLM UMLS license for RxNorm; WHO for ATC).
