# Proposal

## Why

The app tells the story of buzzwords we already know about. It can't show what Hacker News is starting to talk about this
week, which is where new buzzwords come from. Seven rising words a week give visitors a reason to come back and give the
catalog a steady source of new entries. Their weather comes later, once they've earned it.

## What Changes

- A weekly GitHub Action records the story titles of the finished week (Monday to Sunday, UTC), counts the words and
  two-word phrases in them, and commits the counts to a new `weekly_words.json`, the same way the almanac is committed.
- The app ranks the 7 words that rose most this week against their usual rate over the 12 weeks before, in mentions
  per 10,000 titles, and shows them at the top of the page as "This week's gusts", below one sentence that tells how a
  gusting word becomes a buzzword, and above "The long-range forecast" and a watch list of words one week from it. Each row has a heat word (warm,
  heatwave, wildfire, or new front) and a few example titles that link to Hacker News.
- Noise is stripped out: common English words, HN boilerplate ("Show HN", "[pdf]", years), the site a story links to,
  and words that appear in fewer than 3 different stories that week.
- When a word has been rising in 3 of the last 4 weeks and isn't in the catalog yet, the Action opens a pull request
  that adds it to the catalog under a new "rising" era. Ahmed merges it or closes it.
- A one-time backfill records the 12 weeks before launch, so the ranking works from day one.

## Capabilities

### New Capabilities

- `rising-words`: records each week's story-title word counts from Hacker News, ranks the week's risers against their
  12-week baseline, and shows them in the app with heat words and example titles.
- `buzzword-candidates`: proposes words that keep rising for the buzzword catalog through a pull request, under the
  "rising" era.

### Modified Capabilities

None. No specs exist yet. This is the repo's first OpenSpec change.

## Impact

- New modules in `buzzword_weather/` for tokenizing titles, the weekly record, ranking and heat, each with tests.
- `hacker_news.py` gains story-title fetching by time slice. Its nullable gains title responses.
- New `record_weekly_words.py` script and `.github/workflows/record-weekly-words.yml`. The workflow needs
  `pull-requests: write` for candidate PRs.
- `catalog.py` gains the "rising" era.
- `app.py` renders the new section above the forecast.
- New committed data file `weekly_words.json`. It adds one redeploy a week on top of the monthly almanac refresh.
- `README.md` and `CLAUDE.md`/`AGENTS.md` describe the new Action and data file.
