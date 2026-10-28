# Spec Delta

## Purpose

Turn words that keep rising on Hacker News into proposed catalog buzzwords, so the catalog grows from evidence while
Ahmed stays its editor.

## ADDED Requirements

### Requirement: A word that keeps rising becomes a candidate
After each weekly recording, a word or phrase SHALL become a candidate when it was among the 7 risers the page shows in
at least 3 of the last 4 recorded weeks and no catalog buzzword already has it as its search phrase. A word ranked
below the 7 shown, including in weeks recorded before the cap of 7, SHALL NOT count, so only words a visitor saw can be
nominated.

#### Scenario: Ranked but not shown
- **WHEN** "mcp" ranked 8th in 3 of the last 4 weeks
- **THEN** it is not a candidate

#### Scenario: Rising for three weeks
- **WHEN** "mcp" ranked in weeks 1, 2 and 4 of the last 4 and is not in the catalog
- **THEN** "mcp" is a candidate

#### Scenario: One big week
- **WHEN** "crowdstrike" ranked in only 1 of the last 4 weeks
- **THEN** it is not a candidate

#### Scenario: Already in the catalog
- **WHEN** "vibe coding" keeps rising
- **THEN** it is not a candidate, because the catalog already has it

### Requirement: Candidates are proposed through a pull request
For each candidate, the system SHALL open one pull request that adds it to the catalog under the "rising" era, with a
description listing the weeks it rose and its example titles. It SHALL NOT merge the pull request. It SHALL NOT open a
second pull request for a candidate that already has one open or closed.

#### Scenario: Ahmed closes a candidate
- **WHEN** Ahmed closed the pull request for "rust"
- **THEN** later weeks never propose "rust" again

#### Scenario: Ahmed merges a candidate
- **WHEN** Ahmed merges the pull request for "mcp"
- **THEN** "MCP" appears in the picker under the "rising" era, and the next almanac refresh records its history

### Requirement: The watch list
Below this week's gusts, the app SHALL name the words not in the catalog that rose in 2 of the last 3 recorded weeks,
so one more rising week would nominate them, and say so. When there are none, it SHALL say how a word is nominated
and that none is that close yet. Words already proposed, and words whose pull request Ahmed closed without merging,
SHALL NOT be on the watch list. The weekly recording SHALL remember the closed candidates in the weekly record, so the
app knows them without asking GitHub.

#### Scenario: A word Ahmed passed over
- **WHEN** Ahmed closed the pull request for "rust", and "rust" rose in 2 of the last 3 weeks
- **THEN** the watch list leaves out "rust", because no nomination will come

#### Scenario: One week away
- **WHEN** "mcp" rose in 2 of the last 3 weeks and is not in the catalog
- **THEN** the app says "mcp" is on the watch list and that one more rising week nominates it for the forecast

#### Scenario: Nothing close
- **WHEN** no word rose in 2 of the last 3 weeks
- **THEN** the app says a word that rises three weeks out of four is nominated, and none is that close yet

### Requirement: The rising era
The catalog SHALL have a "rising" era for buzzwords promoted from rising words. Ahmed MAY move a buzzword out of it into
another era at any time.

#### Scenario: Picker offers rising buzzwords
- **WHEN** the catalog has buzzwords in the "rising" era
- **THEN** the picker offers them like any other buzzword, with history and a forecast
