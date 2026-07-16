# Find Your Line — data and build

The interactive tool, set up so the industry and loss data lives in one place you
can edit without touching the page.

## Folder layout

```
find-your-line.html              the tool (fetches the data below)
data/
  industry_losses.json           the data the tool reads  ← edit this
  Geometrisk_Industry_Risk_Lookup.xlsx   the same data as a workbook (optional master)
scripts/
  build_data.py                  Excel  -> industry_losses.json (only for bulk edits)
  validate_data.py               checks the JSON before you commit
```

## How it works

The page loads `data/industry_losses.json` each time it opens. Change that file,
commit, and the live site shows the new data on the next deploy. No rebuild, no
inlined copy to keep in sync.

There is a small offline copy embedded in the page as a fallback, so opening the
file straight off disk still works. `build_data.py` refreshes it; you never edit
it by hand.

## Editing the data — two ways

**1. Directly (the normal way).** Open `data/industry_losses.json` in GitHub's web
editor or in Claude Code. Each industry is one block:

```json
{
  "id": "electrician",
  "label": "Electrician",
  "anzsic": "E3232",
  "division": "Construction",
  "keywords": "sparky, electrical contractor, wiring",
  "small": [
    ["Tools stolen from the van overnight", 7000, "THEFT"]
  ],
  "large": [
    ["A fire is traced back to your work, and you're sued", 350000, "PROD"]
  ]
}
```

Each loss is `[what could go wrong, indicative dollars, peril tag]`. `keywords`
are what an owner might type in the search (nicknames welcome: sparky, chemist).
To add an industry, copy a block, change the `id` to something new and unique,
and edit the rest. Commit when done.

**2. In bulk, from the workbook.** For big changes, edit
`data/Geometrisk_Industry_Risk_Lookup.xlsx` (Industries and Losses sheets), then
run:

```
python scripts/build_data.py
```

That rewrites `industry_losses.json` from the workbook and refreshes the page's
offline fallback. Commit the changed files.

> Pick one master and stick to it. If you edit the JSON directly, treat the JSON
> as the source of truth (the workbook will drift). If you prefer the workbook,
> always edit there and run the build. Don't edit both.

## Before you commit

```
python scripts/validate_data.py
```

Catches broken JSON, missing fields, non-number costs and empty loss lists, so a
typo never ships to the live tool.

## Deploy

If the repo is served by GitHub Pages, Netlify or Vercel, committing to the main
branch publishes automatically within a minute — nothing else to do. If Pages is
not switched on yet, it is a two-click job in the repo's Settings → Pages.

## Local preview

Because the page fetches a file, some browsers block that when you open it straight
off disk (`file://`). The embedded fallback means it still works, but to preview
against the live JSON, serve the folder:

```
python -m http.server 8000
```

then open `http://localhost:8000/find-your-line.html`.

## Scope and disclaimer

Loss figures are indicative only and not tailored to any business. Scope is
short-tail general insurance and liability (property, business interruption,
theft, public and products liability, professional indemnity, cyber). Worker
injury and workers compensation are excluded — that cover is mandatory and held
regardless. General information only, not advice.
