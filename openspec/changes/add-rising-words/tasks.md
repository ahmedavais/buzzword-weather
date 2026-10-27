# Tasks

## 1. Weeks and titles

- [x] 1.1 Add a `Week` period (ISO week, UTC Monday start, `starts_at`/`ends_at`/label) and "finished weeks the record lacks, up to 13 back" in `periods.py`; verify with `periods_test.py` cases for year boundaries and a Monday run
- [x] 1.2 Add `titles.py`: tokenize a title into words and two-word phrases with prefix/tag/number/stopword/domain removal, once per title; verify with `titles_test.py` covering "Show HN", "[pdf]", "C++", "Node.js", "GPT-5", repeated words and `github.blog`

## 2. Fetching and recording

- [x] 2.1 Add `HackerNews.stories(starts_at, ends_at)` with 6-hour slices that halve when `nbHits` exceeds what came back, plus a nullable that serves configured titles; verify with `hacker_news_test.py` using the null and an output tracker
- [x] 2.2 Add an integration test fetching one real 6-hour slice and asserting it returned every hit it reports; verify with `uv run pytest -m integration` from CI or locally
- [x] 2.3 Add `weekly_words.py` and `week_recorder.py`: the record (from/to JSON, keep 13 weeks) and counting a week (drop words in fewer than 3 stories, store its risers with up to 3 examples); verify with `weekly_words_test.py`
- [x] 2.4 Add `record_weekly_words.py` that records every missing finished week, paced like `record_almanac.py`; verify with a test against the null Hacker News that a rerun changes nothing

## 3. Ranking

- [x] 3.1 Add `rising.py`: rate per 10,000 titles, 12-week usual, rise, the 2× floor, new-front ordering, heat words and phrase-over-parts hiding; verify with `rising_test.py` covering each spec scenario
- [x] 3.2 Show "still gathering" when fewer than 13 weeks are recorded; verify in `rising_test.py`

## 4. App

- [x] 4.1 Render "This week on HN" above the forecast in `app.py`, with one expander per word, heat, rise, rate and up to 3 linked titles, hidden when the record is missing or unreadable; verify by running the app on a sample record and with the file absent
- [x] 4.2 Add a sensor in `sensors/` that fails if a stopword or number ever ranks, a week counted under 2,000 titles, or the record falls 2 weeks behind; verify with `uv run pytest`

## 5. Candidates

- [x] 5.1 Add the "rising" era to `catalog.py`; verify with `catalog_test.py`
- [x] 5.2 Add `candidates.py`: words ranked in at least 3 of the last 4 weeks and not in the catalog, named with their most common casing; verify with `candidates_test.py`
- [x] 5.3 Add `find_candidates.py` (prints JSON) and `add_candidate.py` (inserts a `_buzzword(..., "rising")` line); verify that a test adds a candidate to a copy of `catalog.py` and the catalog still imports and passes `catalog_test.py`

## 6. Action and docs

- [x] 6.1 Add `.github/workflows/record-weekly-words.yml`: Mondays 07:23 UTC plus manual runs; record, test and commit; then one PR per new candidate on `candidate/<slug>`, skipping slugs with any existing PR; verify with a manual dispatch on a branch
- [ ] 6.2 Commit an empty `weekly_words.json`, then backfill by dispatching the Action after merge; verify that the section appears on the live app
- [x] 6.3 Update `README.md`, `CLAUDE.md` and `AGENTS.md` for the new Action, data file and era, and fix the outdated "app.py only renders" line; verify by reading the diff
- [x] 6.4 Run `uv run ruff check .` and `uv run pytest` clean before opening the PR

## Workflow follow-up

- Archive the change with `/opsx:archive` after it ships, which turns the delta specs into `openspec/specs/`.
