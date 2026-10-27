# Design

## Context

The app reads committed data (`almanac.json`) and asks Hacker News only for what that file lacks. The monthly refresh
Action records new counts, runs the tests and commits, which redeploys the app. This feature follows the same pattern
with a weekly cadence. The Algolia search API returns at most 1,000 hits per query (`paginationLimitedTo`), and
Hacker News gets roughly 1,000 to 1,500 stories a day. This session couldn't reach hn.algolia.com, so those volumes
are assumptions that an integration test checks.

## Goals / Non-Goals

**Goals:**
- Visitors load the section from a committed file, with no Hacker News requests.
- A week of recording costs about 10 to 20 requests, paced like `record_almanac.py`.
- Every piece of logic is a small module with sociable, state-based tests, and outside systems are nullables.

**Non-Goals:**
- Comments, story text, scores or front-page status.
- Any window shorter than a week, and live updates during a week.
- Weather (a 24-month forecast) for words that aren't in the catalog. They get heat words only.
- Grouping the picker by era. That's a separate improvement.

## Decisions

**Fetch titles in slices under the cap.** `HackerNews.story_titles(start, end)` queries `search_by_date` with
`tags=story`, `hitsPerPage=1000` and the time window, asking only for `title`, `url` and `objectID`
(`attributesToRetrieve`). It splits a week into slices of 6 hours (28 requests) by default. When a slice comes back
with `nbHits` above what it returned, it halves the slice and retries, so a busy week can't lose titles silently.
The alternative, the official Firebase API one item at a time, would take 50,000+ requests a week.

**Store counts, not titles.** `weekly_words.json` maps each ISO week (`2026-W44`) to its title count and, for every word
or phrase that appeared in at least 3 stories, its story count plus up to 3 example items (id, title). Words below 3
stories are dropped at record time. That rule already applies to ranking, and dropping them keeps the file at roughly
30 to 60 KB a week. Thirteen weeks of history are kept, plus the 4 weeks the candidate rule needs (it fits inside the
13). Older weeks are pruned, so the file stays under 1 MB.

  Alternative: store raw titles and count in the app. That gives a bigger file, repeats the work on every visit, and
  puts other people's titles in the repo in bulk.

**Tokenizing.** `titles.py` lowercases, strips the "Show HN:"-style prefix and bracketed tags, splits on anything but
letters, digits, `+`, `#` and `.` inside a word (so "c++", "c#" and "node.js" survive), and drops trailing dots. It
removes stopwords and bare numbers, then forms bigrams from adjacent kept tokens in the original order. The stopwords
are a small list in code, around 150 words, with no NLP dependency. The words of the story's domain (`github.blog` gives
"github" and "blog") are removed from that title's tokens.

**Phrase over parts.** When a bigram ranks and one of its words had 70% or more of its story count inside that bigram
this week, that word is hidden from the ranking. This happens at ranking time, so the record stays plain counts.

**Rate and rise.** rate = stories using the word / titles counted × 10,000. usual = mean rate over the 12 previous
recorded weeks, with missing words counted as 0. rise = rate / usual. Words with usual 0 are "new front" and sort
first by this week's rate. A word must have rise ≥ 2 to rank. Heat thresholds: ≥ 6 wildfire, ≥ 3 heatwave, else warm.

**Weeks are ISO weeks in UTC.** A `Week` value type, kin to `Month` and `Quarter` in `periods.py`, gives `starts_at`
and `ends_at` as Unix seconds and an ISO label. The recording script records every finished week the record lacks, up
to 13 back, so the first run doubles as the 12-week backfill (about 13 × 28 requests, paced).

**One Action, two jobs.** `.github/workflows/record-weekly-words.yml` runs Mondays at 07:23 UTC. Job one records,
runs `uv run pytest` and commits `weekly_words.json` to main, like the almanac. Job two finds candidates with
`find_candidates.py`, which prints JSON. For each candidate without an existing PR (searched by the branch name
`candidate/<slug>` in open and closed PRs), it adds a line to `CATALOG` with `add_candidate.py`, a small text edit
that inserts `_buzzword("<Name>", "rising")` after the last catalog entry. Then it runs the tests and opens a PR with
`gh pr create`. Names keep the casing most common in the example titles ("MCP", "Claude Code").

  Alternative: candidates shown in the app only. Rejected in the grilling: Ahmed wants a PR to merge.

**App section.** `rising.py` holds the ranking and heat logic and returns rows. `app.py` renders the rows with
`st.expander` per word for the example titles, linking `https://news.ycombinator.com/item?id=<id>`. It's cached with
`st.cache_data` keyed on the file's content version, so the existing deploy reload clears it.

## Risks / Trade-offs

- [The Algolia cap or volumes differ from the assumptions] → Adaptive slice halving, plus an integration test that
  fetches one real 6-hour slice and asserts it returns every hit it reports.
- [Weekly commits to main redeploy the app every Monday] → The same deploy-reload path the almanac uses, already
  proven. The commit happens only after the tests pass.
- [Risers dominated by news, not tech, such as elections or deaths] → Accepted: the section is "This week on HN", not
  "this week's buzzwords". Candidate PRs are Ahmed's filter.
- [Stopword list misses produce junk risers] → Sensor test in `sensors/` that fails if a stopword-looking word (3
  letters or fewer, all common) ranks in the latest real week.
- [Tokenizing quirks such as "C++", "Node.js", "GPT-5"] → Unit tests for each. Hyphenated words stay one token
  ("gpt-5", "low-code").
- [Candidate PR edits Python source] → Tests run in the PR's CI, and the adversarial review sees it like any other
  PR.

## Migration Plan

1. Merge the code with an empty `weekly_words.json`. The section hides itself (spec: record missing).
2. Run the Action by hand once to backfill 13 weeks. The section appears on the next deploy.
3. Rollback: delete the workflow and `weekly_words.json`, and the section hides itself.

## Open Questions

- The exact stopword list. It will be tuned against the backfilled weeks before launch, without changing behavior or
  tasks.
