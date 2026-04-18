
# Project Build Journal
## Regional Demand Forecasting & Inventory Optimizer V2

Author: Arvind Swami  
Project type: Capstone + portfolio + client-style build  
Mode: Continuity-first, production-aware, business-focused

---

## Purpose of this journal

This file is the long-form technical working journal for the project.

It is meant to capture:
- session-by-session technical decisions
- data findings
- broken assumptions
- modeling notes
- implementation trade-offs
- debugging details
- business interpretation notes
- next-step thinking

This is intentionally more detailed and less polished than the README.
It is closer to real DE/DS working notes.

Related files:
- `docs/current_status.yaml` → current source of truth
- `docs/session_log.md` → shorter chronological session log
- `reports/project_build_journal.md` → detailed technical/project journal

---

## Working conventions

### What goes here
- actual findings from the data
- why certain implementation decisions were made
- what changed from original assumptions
- technical risks
- business realism notes
- what should happen next

### What does not need to go here
- polished final storytelling for recruiters
- repeated notebook outputs
- raw code dumps
- generic explanations

### Tone
Keep this practical and honest.
If something is messy, note it.
If something is a hack, note it.
If something is “good enough for now,” note it.

---

# Session Notes

---

## 2026-04-17 — Day 1
### Session focus
Restore V2 continuity, reconnect the repo in Colab, locate the real processed dataset, and make the data/validation/preprocessing stack usable again.

### Starting state
At the beginning of the session:
- V2 repo scaffold already existed
- bootstrap/session continuity utilities were in place
- docs structure existed
- actual dataset hookup was still unresolved
- modeling had not resumed in V2

Main blocker:
There was still uncertainty around where the processed dataset actually lived and whether it matched the old modeling assumptions.

---

### Environment / repo notes
Started from a fresh Colab session, so repo state had to be restored manually.

Actions taken:
- checked current working directory
- confirmed repo was not present in `/content`
- cloned the V2 repo from GitHub
- moved into repo root
- added repo to `sys.path` for clean imports
- verified git remote and active branch
- later configured git user name/email because Colab did not retain identity

Repo path used:
`/content/regional-demand-forecasting-optimizer-v2`

Git remote:
`https://github.com/arvindswami014uk/regional-demand-forecasting-optimizer-v2.git`

Branch:
`main`

Practical note:
This is normal Colab friction, not a project issue. Need to treat repo bootstrap + git identity setup as part of the real session start routine.

---

### Data discovery
Searched for candidate processed/modeling files in the repo and available locations.

Files found:
- `data/processed/weekly_demand_aggregated.csv`
- `data/raw/daily_demand.csv`

Key realization:
The processed dataset present in V2 is not a ready-made feature table. It is a weekly aggregated demand table.

This is important because the earlier assumption was that V2 might be able to reconnect directly to the old modeling flow with minimal changes. That assumption did not hold.

Canonical processed file for V2 as of Day 1:
`/content/regional-demand-forecasting-optimizer-v2/data/processed/weekly_demand_aggregated.csv`

---

### Schema inspection results
Inspected `weekly_demand_aggregated.csv`.

Observed shape:
- 5000 rows
- 4 columns

Columns:
- `week`
- `sku_id`
- `region`
- `units_ordered`

Dtypes:
- `week`: object
- `sku_id`: object
- `region`: object
- `units_ordered`: int64

Null profile:
- no missing values in any column

Interpretation:
This is a clean weekly base demand table at SKU-region-week grain.

It does not yet include:
- category
- lag features
- rolling features
- promotional/event variables
- inventory-side attributes
- split markers for training/evaluation

So although the file is called “processed,” it is not model-ready in the same sense as a final forecasting table.

---

### Assumption mismatch discovered
Earlier project framing assumed:
- region-category combinations
- category-level diagnostics
- potentially richer demand feature engineering already in place

The actual V2 processed file currently available is:
- SKU-region based
- weekly
- no category field in this file

Need to be careful here.

Possible explanations:
1. current capstone dataset is fundamentally SKU-region based
2. category mapping exists elsewhere and has not been joined yet
3. earlier narrative and current V2 data are only partially aligned

Decision made:
Do not force-fit earlier assumptions onto the actual data during Day 1.
Better to stabilize around what is really available.

This is the more honest and maintainable path.

---

### Loader updates
Updated `src/data/loader.py`.

Reason:
The discovered processed file name (`weekly_demand_aggregated.csv`) was not included in the loader’s default file search list.

Changes made:
- added `weekly_demand_aggregated.csv` to filename candidates
- preserved CSV/Parquet support
- kept path discovery simple
- expanded dataset summary handling to include:
  - `week`
  - `sku_id`
  - `region`
  - `units_ordered`

Outcome:
Loader now reflects actual V2 data reality instead of assumed legacy file names.

Trade-off:
Still intentionally lightweight. No need yet to overengineer config-driven path routing while continuity is still being restored.

---

### Validation updates
Updated `src/data/validation.py`.

Reason:
Original validation assumptions did not match actual schema.

Earlier assumptions included columns like:
- `date`
- `category`
- `demand`

Actual file uses:
- `week`
- `sku_id`
- `region`
- `units_ordered`

Changes made:
- added flexible schema inference
- added candidate key column groups
- added target column inference
- duplicate key validation now uses inferred key columns
- retained non-negative target check
- added parseability check for `week`
- retained missingness summary

Outcome:
Validation now works against the real processed weekly dataset.

This is a small but important repo-hardening step. Better to fail loudly on wrong schema than quietly carry bad assumptions into modeling.

---

### Metrics module
Created/updated `src/evaluation/metrics.py`.

Included:
- WMAPE
- MAE
- RMSE
- Bias
- helper returning a metrics dictionary

Reason:
Needed a shared evaluation layer before rebuilding the forecasting path in V2.

Design choice:
Kept it intentionally simple. Diagnostics/backtesting utilities can come next once the first model pipeline is in place.

---

### Preprocessing scaffold
Created `src/data/preprocessing.py`.

Reason:
The processed dataset is a clean input table, not a final model feature table. Needed a bridge from weekly base demand to modeling-ready features.

Implemented:
- `prepare_weekly_demand_base()`
  - parse `week`
  - sort by `sku_id`, `region`, `week`
- `add_calendar_features()`
  - year
  - month
  - quarter
  - weekofyear
- `add_lag_features()`
  - lag_1
  - lag_2
  - lag_4
- `add_rolling_features()`
  - roll_2_mean
  - roll_4_mean
  - roll_8_mean
- `prepare_modeling_dataset()`
  - orchestrates the full feature prep flow

Interpretation:
This is the first V2-native modeling scaffold from the currently available weekly dataset.

Important note:
This is not necessarily identical to the earlier XGBoost feature set from the old project, so benchmark comparability needs to be handled carefully.

---

### Modeling readiness conclusion
Big conclusion from Day 1:

The historical validated benchmark values remain important reference points:
- XGBoost WMAPE: 11.06%
- Prophet WMAPE: 11.16%
- MA7 baseline WMAPE: 19.25%

But those values were **not reproduced today**, and should not be presented as if they were.

Reason:
The currently available processed file in V2 is only a weekly base table. A compatible model-ready training flow still needs to be rebuilt before benchmark revalidation is possible.

This is annoying, but honestly better to acknowledge now than pretend later.

---

### Naive benchmark
Built a basic weekly naive lag-1 benchmark.

Logic:
For each `sku_id` + `region` series:
- predict current week’s `units_ordered` using previous week’s `units_ordered`

Why this matters:
- gives V2 an immediate benchmark from the actual data in hand
- provides sanity check before tree models
- creates a first saved benchmark artifact in V2

Saved output:
`outputs/benchmarks/day1_naive_benchmark.csv`

Need to keep this benchmark visible because it becomes the first true V2-native comparison point.

---

### Documentation / continuity updates
Updated:
- `docs/current_status.yaml`
- `docs/session_log.md`

Reason:
Needed to preserve the fact that V2 processed data reality is different from the earlier assumption.

This is important because otherwise next session would probably restart from the wrong mental model.

Continuity status now reflects:
- actual data path
- actual processed schema
- preprocessing scaffold added
- full benchmark path still pending

---

### Git / session persistence notes
Initial commit failed because Colab git identity was unset.

Observed error:
- `Author identity unknown`

Fix applied:
- configured git user name
- configured git user email

Verified:
- remote URL correct
- branch = `main`

Push succeeded after identity fix.

This matters because Day 1 is now properly checkpointed in GitHub, not just sitting in an ephemeral notebook session.

---

### What went well
- repo continuity process now feels real and repeatable
- actual processed dataset identified quickly
- schema inspected before writing more model code
- validation logic corrected to match reality
- preprocessing scaffold now exists
- first V2-native benchmark saved
- git checkpoint completed successfully

Overall:
Good foundation day. Not flashy, but exactly the kind of work that prevents later confusion.

---

### What did not go as originally expected
- processed file was not feature-engineered as initially assumed
- old modeling flow cannot simply be resumed immediately
- earlier category-centric project narrative may need refinement depending on metadata availability
- historical benchmark values remain reference points only for now

None of this breaks the project, but it does change the rebuild path.

---

### Risks / open questions
#### 1. Grain mismatch
Need to decide whether final project should be framed as:
- weekly SKU-region forecasting and placement
or whether additional metadata will let it be translated into:
- category-region planning

#### 2. Historical benchmark comparability
Need to avoid sloppy comparison if:
- old XGBoost used a richer/different feature set
- new V2 model flow starts from the weekly base table only

#### 3. Feature sufficiency
Current feature scaffold is good enough for baseline tree models, but might not be rich enough to recover earlier best-case benchmark performance.

#### 4. Inventory compatibility
Need to decide whether inventory logic should operate at:
- SKU-region level
- aggregated region level
- category-like level if metadata exists

This becomes important before optimization and business-facing summaries.

---

### Recommended next step
Day 2 should focus on building the first real forecasting training pipeline from the weekly base table.

Priority sequence:
1. define time-based train/validation split
2. finalize feature set from preprocessing output
3. encode categorical variables cleanly
4. train LightGBM baseline
5. evaluate using WMAPE/MAE/RMSE/Bias
6. compare against naive lag-1 benchmark
7. save predictions and benchmark outputs
8. update continuity docs

If ahead of schedule:
- add CatBoost
- add region-level diagnostics
- inspect feature importances

---

### Personal note
Main win today was not model performance. It was clarity.

Before this session:
- data location uncertain
- processed table meaning unclear
- old modeling assumptions still hanging around

After this session:
- data location is known
- schema is known
- actual modeling gap is known
- next move is much clearer

Honestly, that’s what Day 1 needed.

---

## Future sessions
Append new sections below using the same structure:
- Session focus
- Starting state
- What changed
- Findings
- Trade-offs / issues
- Metrics / outputs
- Risks / open questions
- Next step

---


## 2026-04-18 — Day 2
### Session focus
Build the first real forecasting pipeline in V2 and establish a usable tree-model benchmark.

### Starting state
Day 1 restored continuity, validated the base weekly dataset, and added preprocessing and metrics scaffolding.
The plan going into Day 2 was to train the first tree-based model from the weekly SKU-region dataset.

### Major finding
The SKU-region forecasting plan failed structurally, not just technically.

Diagnostics showed:
- every `sku_id + region` series had exactly one observation
- all lag and rolling features were null at that grain
- usable training rows after lag/rolling feature creation were effectively zero

This means the current processed dataset is not forecastable as a proper time series at SKU-region grain.

That is a data-shape limitation, not a modeling bug.

### Pivot decision
Instead of forcing a broken SKU-level setup, the modeling grain was pivoted to weekly region-level aggregation.

Why this was the right move:
- preserves the temporal signal present in the data
- gives enough observations per region to support lag/rolling features
- creates a valid forecasting baseline quickly
- is more useful for the remaining 4-day sprint than spending hours trying to rescue a statistically invalid grain

This is a trade-off, but it is the right trade-off.

### Region-week pipeline built
Constructed a new modeling table at:
- region
- week

Feature set used:
- region
- year
- month
- quarter
- weekofyear
- lag_1
- lag_2
- roll_2_mean
- roll_4_mean

Validation strategy:
- time-based holdout using final ~20% of weeks

This is much more defensible than doing anything random or pretending the original SKU-level assumption still worked.

### Region-week LightGBM result
Validation metrics:
- WMAPE: 18.31%
- MAE: 325.8506
- RMSE: 694.99
- Bias: 160.0725

Naive lag-1 benchmark on the same validation window:
- WMAPE: 18.16%

Interpretation:
This is now the first valid V2-native forecasting benchmark that can actually support downstream planning work.

It is not directly comparable to the old historical XGBoost benchmark because:
- grain changed
- feature set changed
- underlying training structure changed

That distinction needs to stay explicit in all future documentation.

### Diagnostics note
A region-level diagnostic table was generated.
This is now more relevant than SKU-level diagnostics for the current V2 flow.

Need to watch whether any region remains consistently noisier, since that can feed directly into Day 3 uncertainty and inventory logic.

### Practical assessment
Main achievement today was not just training LightGBM.
It was identifying the correct forecasting grain for the current V2 dataset.

That matters because Day 3 and Day 4 depend on having forecast outputs that are actually defensible.

### Output artifacts created
- `outputs/predictions/day2_region_week_lgbm_predictions.csv`
- `outputs/benchmarks/day2_region_week_benchmarks.csv`

### Risks / open questions
1. Should category or SKU metadata be reintroduced later if another table exists, or do we stay region-level for the rest of the sprint?
2. Is CatBoost worth adding, or is LightGBM enough given current time pressure?
3. How much of the original project framing should now be reframed around region-level planning instead of SKU-region placement?

### Recommended next step
Use the region-week LightGBM pipeline as the working forecast engine and move into Day 3:
- uncertainty intervals
- safety stock linkage
- replenishment logic
- scenario comparison

That is now the highest-value path.

