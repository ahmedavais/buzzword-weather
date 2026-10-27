# Spec Delta

## Purpose

Show visitors which words Hacker News story titles are suddenly using more than usual, one finished week at a time, so
the app tells this week's story as well as the long history of known buzzwords.

## ADDED Requirements

### Requirement: Weeks are recorded once, after they finish
The system SHALL record a week only after it has ended. A week runs from Monday 00:00 UTC to the next Monday 00:00 UTC.
A recorded week SHALL NOT be recorded again. The weekly record SHALL be committed to the repository, so visitors never
wait on Hacker News for this section.

#### Scenario: Recording on a Monday
- **WHEN** the weekly recording runs on Monday 2 November 2026
- **THEN** it records the week from 26 October to 1 November 2026 inclusive and no later week

#### Scenario: A week already in the record
- **WHEN** the recording runs again for a week that is already recorded
- **THEN** the record is unchanged and nothing is committed

#### Scenario: Recording runs late
- **WHEN** the recording has missed a week, such as after a failed run
- **THEN** the next run records every finished week the record lacks, oldest first

### Requirement: Only story titles are counted
The system SHALL count words in the titles of Hacker News stories posted during the week. It SHALL NOT count comments
or story text. Each week's record SHALL include how many titles were counted.

#### Scenario: A comment mentions a word
- **WHEN** a word appears only in comments during the week
- **THEN** that word's count for the week is zero

### Requirement: Words and two-word phrases
The system SHALL count single words and two-word phrases from each title, ignoring case and surrounding punctuation.
A word or phrase SHALL count at most once per title. When a two-word phrase ranks, its single words SHALL NOT also be
shown if most of their mentions that week were inside that phrase.

#### Scenario: A product with a two-word name
- **WHEN** "Claude Code" rises and nearly all mentions of "code" that week are in "Claude Code"
- **THEN** the list shows "Claude Code" and not "code"

#### Scenario: Repeated word in one title
- **WHEN** a title says "Rust, Rust everywhere"
- **THEN** "rust" counts once for that title

### Requirement: Noise is not counted
The system SHALL ignore common English words; HN boilerplate such as "Show HN", "Ask HN", "Launch HN", "Tell HN",
bracketed tags like "[pdf]" and "[video]", and bare numbers and years; and any word that is part of the domain the story
links to. A word or phrase SHALL rank only if at least 3 different stories used it that week.

#### Scenario: Show HN
- **WHEN** 400 titles in a week start with "Show HN"
- **THEN** neither "show", "hn" nor "show hn" appears in the ranking

#### Scenario: A word in the story's own domain
- **WHEN** a story titled "GitHub Copilot pricing" links to github.blog
- **THEN** "github" is not counted for that title, and "copilot" is

#### Scenario: A one-story wonder
- **WHEN** a word appears in only 2 different stories this week
- **THEN** it does not rank, however high its rise

### Requirement: Rise is measured against the 12 weeks before
For each word, the system SHALL compare this week's mentions per 10,000 titles with its average rate over the 12
recorded weeks before. The 10 words with the largest rise SHALL be shown, largest first. A word with no mentions in
those 12 weeks SHALL rank as new and be shown ahead of the others, with ties broken by mentions this week.

#### Scenario: A word jumps
- **WHEN** "crowdstrike" has 0.5 per 10,000 over the past 12 weeks and 40 per 10,000 this week
- **THEN** it ranks with a rise of 80 times usual

#### Scenario: Fewer than 12 weeks of history
- **WHEN** the record holds fewer than 13 weeks
- **THEN** the section says the forecast is still gathering data and shows no ranking

### Requirement: Heat words
Each ranked word SHALL get a heat word from its rise: "new front" when it was never mentioned in the 12 weeks before,
"wildfire" at 6 times usual or more, "heatwave" at 3 times or more, and "warm" otherwise. Only words at 2 times usual
or more SHALL rank, so fewer than 10 can be shown in a quiet week.

#### Scenario: A quiet week
- **WHEN** only 4 words reach 2 times their usual rate
- **THEN** the section shows those 4 words

### Requirement: This week on HN section
The app SHALL show "This week on HN" above the buzzword forecast, naming the recorded week. Each row SHALL show the word,
its heat word, its rise against usual and its mentions per 10,000 titles. Raw counts SHALL NOT be shown. Opening a row
SHALL show up to 3 of that week's titles using the word, each linking to its Hacker News discussion.

#### Scenario: Visitor opens a riser
- **WHEN** a visitor opens the row for "crowdstrike"
- **THEN** they see up to 3 titles from that week containing "crowdstrike", each linking to its news.ycombinator.com item

#### Scenario: Record is missing or unreadable
- **WHEN** the weekly record is absent or cannot be read
- **THEN** the section is hidden and the rest of the app works as before
