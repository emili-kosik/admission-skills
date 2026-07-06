# Maintainer runbook

## The annual refresh (run in the first week of August)

Aug 1 is the cycle boundary: Common App refreshes, the UC application opens,
and the new Requirements Grid appears. In order:

1. **Requirements Grid → deadlines**
   ```
   curl -L -o tools/_downloads/ReqGrid.pdf https://content.commonapp.org/Files/ReqGrid.pdf
   .venv/Scripts/python tools/build_reqgrid.py --pdf tools/_downloads/ReqGrid.pdf
   ```
   The tool fails loudly if the college count leaves 1000–1400 or the date
   parse rate drops below 98% (layout drift — inspect with pdfplumber before
   trusting anything).
2. **Review overrides** — `tools/overrides/deadlines_overrides.json`
   (UC/CSU/MIT/Georgetown/ApplyTexas anchors) and
   `tools/overrides/test_policy_overrides.json` (re-verify each entry against
   its cited admissions page; policies flipped repeatedly 2024–2026).
3. **Test policy** — `python tools/build_test_policy.py`.
4. **Test dates** — new SAT/ACT/PSAT/AP calendars from the pages in
   `data/sources.json`; update `data/test_dates.json` (keep the
   `lead_time_rules` in sync with the published tables).
5. **Essay prompts** — verify Common App prompts + UC PIQs (announced late
   Feb, but re-confirm) and the Challenges & Circumstances question status;
   update `data/essay_prompts.json`.
6. **AI policies** — re-fetch each URL in `data/ai_policies.json`; refresh
   quotes and `last_verified`; hunt policy changes at the majors.
7. **College index** — `python tools/build_college_index.py` (new IPEDS year).
8. **Milestones** — read through `data/milestones.json` for rule drift
   (dates are rules, so most years nothing changes).
9. **Gate**: `pytest` (dataset anchor tests), bump `_meta.cycle` fields,
   bump the patch version in `.claude-plugin/plugin.json`, update
   CHANGELOG.md, tag, release. Users on older versions can pull the new
   datasets immediately via `/admit:refresh-data`.

Mid-cycle: Common App re-issues the ReqGrid PDF occasionally (the header
carries an "Updated:" date) — re-run step 1 when it changes and ship a patch.

## Scheduled automation

`.github/workflows/refresh-data.yml` re-downloads sources on a schedule and
opens a PR with the rebuilt datasets and the validation report. **A human
merges** — PDF layout drift makes unattended merges unsafe.

## Dataset provenance rules

Every `data/*.json` carries `_meta` (cycle, source, built_at, last_verified).
Datasets are only changed by the build tools against primary sources — a
hand-edit without a cited source is grounds to reject a PR (see SECURITY.md).

## Dev loop

```
python -m venv .venv && .venv/Scripts/pip install -e ".[dev]"
pytest                       # offline, fast
ruff check .
claude --plugin-dir .        # live-load the plugin; /reload-plugins after edits
claude plugin validate .
```

The golden `.ics` fixture is byte-exact (CRLF; stored with `*.ics binary`).
Regenerate it only for intentional format changes — see
`tests/fixtures/golden/README.md`.
