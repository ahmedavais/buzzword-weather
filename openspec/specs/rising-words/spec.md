# rising-words Specification

## Purpose
Show visitors which words Hacker News story titles are suddenly using more than usual, one finished week at a time, so
the app tells this week's story as well as the long history of known buzzwords.

## Requirements

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
A word or phrase SHALL count at most once per title. A word or phrase SHALL NOT be shown when 70% or more of the
stories using it that week also use a word or phrase ranked above it, so one news story fills one row.

#### Scenario: One story, many words
- **WHEN** "emudhra" ranks first, and most titles using "emudhra intermediate", "certificates" and "compromised" also
  use "emudhra"
- **THEN** the list shows "emudhra" and none of the others

#### Scenario: A word with a life of its own
- **WHEN** "php2shell" ranks above "php", and most titles using "php" don't mention "php2shell"
- **THEN** the list shows both

#### Scenario: Repeated word in one title
- **WHEN** a title says "Rust, Rust everywhere"
- **THEN** "rust" counts once for that title

### Requirement: Noise is not counted
The system SHALL ignore common English words; HN boilerplate such as "Show HN", "Ask HN", "Launch HN", "Tell HN",
bracketed tags like "[pdf]" and "[video]", bare numbers and years, money amounts like "$25B", and CVE ids; and any word that is part of the domain the story
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
recorded weeks before. Weeks record only words that at least 3 stories used, so in a week where a word went
unrecorded it SHALL count as 2 stories, the most it could have had. A rise is therefore never overstated. The 7
words with the largest rise SHALL be shown, largest first. A word that went unrecorded in all 12 weeks before is new,
and ranks among the others by its rise against those 2 stories a week, not ahead of them.

#### Scenario: A word jumps
- **WHEN** "crowdstrike" has 0.5 per 10,000 over the past 12 weeks and 40 per 10,000 this week
- **THEN** it ranks with a rise of 80 times usual

#### Scenario: A word that sat just under the floor
- **WHEN** "mcp" was in 2 titles each week for 12 weeks and is in 3 this week, with the same number of titles
- **THEN** it does not rank, because 3 stories is only 1.5 times the 2 it may have had each week

#### Scenario: Fewer than 12 weeks of history
- **WHEN** the record holds fewer than 13 weeks
- **THEN** the section says the forecast is still gathering data and shows no ranking

### Requirement: Heat words
Each ranked word SHALL get a heat word from its rise: "new front" when it was under 3 stories in each of the 12 weeks
before (shown as "under 3 stories a week before" instead of a rise),
"wildfire" at 6 times usual or more, "heatwave" at 3 times or more, and "warm" otherwise. Only words at 2 times usual
or more SHALL rank, so fewer than 7 can be shown in a quiet week.

#### Scenario: A quiet week
- **WHEN** only 4 words reach 2 times their usual rate
- **THEN** the section shows those 4 words

### Requirement: The page tells one story
The page SHALL open with one sentence that tells the arc from a word Hacker News suddenly uses to a buzzword with a
forecast. The weekly section SHALL be titled "This week's gusts" and come first. The buzzword forecast SHALL be titled
"The long-range forecast" and come after it, with its title above the buzzword picker.

#### Scenario: A first-time visitor
- **WHEN** a visitor opens the app for the first time
- **THEN** they read, in order, the opening sentence, this week's gusts, how a word gets nominated for the forecast,
  and the long-range forecast

### Requirement: This week's gusts section
The app SHALL show "This week's gusts" above the long-range forecast, naming the recorded week. Each row SHALL show the word,
its heat word, its rise against usual and its mentions per 10,000 titles. Raw counts SHALL NOT be shown. Opening a row
SHALL show up to 3 of that week's titles using the word, each linking to its Hacker News discussion.

#### Scenario: Visitor opens a riser
- **WHEN** a visitor opens the row for "crowdstrike"
- **THEN** they see up to 3 titles from that week containing "crowdstrike", each linking to its news.ycombinator.com item

#### Scenario: Record is missing or unreadable
- **WHEN** the weekly record is absent or cannot be read
- **THEN** the section is hidden and the rest of the app works as before
