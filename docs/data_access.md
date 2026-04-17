# Data Access Notes

## Expected processed files

The project bootstrap currently looks for the following processed datasets:

- `data/processed/features.csv`
- `data/processed/processed_demand.csv`

## Current status

At the moment, these processed data files are not stored in the repository.
That is expected for now because data artifacts are usually excluded from git.

## Preferred external location

Current fallback path checked by the bootstrap:

`/content/drive/MyDrive/regional-demand-data/features.csv`

## Recommended Colab workflow

1. Start session and load the repo
2. Run the bootstrap checker
3. If data is missing, mount Google Drive
4. Either:
   - load directly from Drive, or
   - copy the processed file into `data/processed/`
5. Run validation before training any models

## Notes

- Raw and processed data are gitignored by design
- This repo tracks code, docs, and project structure — not large data files
- The loader should eventually support both local repo paths and Drive fallback paths

## TODO

- Add Drive-aware loader logic in `src/data/loader.py`
- Standardize processed feature filename
- Add a short data setup section to `docs/getting_started.md`