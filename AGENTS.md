# Buzzword weather

A Streamlit toy from ahmedavais.com: how often Hacker News mentions each engineering buzzword, and its weather now.
`README.md` explains how it works and how it's put together; read it before changing behavior.

## Checks

- CI (`.github/workflows/ci.yml`) runs on every pull request and push to main: `uv run ruff check .` and
  `uv run pytest`, which includes the sensors in `sensors/`. Run both before calling any change done.
- `uv run pytest -m integration` checks the real Hacker News search API. CI leaves it out.
- Adversarial review: `.github/workflows/adversarial-review.yml` has Claude Code review every pull request with the
  shared workflow and brief from [karkhana](https://github.com/ahmedavais/karkhana). Comments only. The reviewer takes
  this repo's checks and conventions from this file, so keep them current here.
- The refresh Action runs the tests before it commits a new almanac. Keep-awake visits the app every 6 hours.

## Conventions

- Community Cloud deploys main on its own, so a push or merge to main is a deploy.
- Logic lives in `buzzword_weather/` as small modules, each with a `*_test.py` next to it. `app.py` only renders.
- Tests are sociable and state-based. No mocking libraries: outside systems are nullables with `create()` and
  `create_null()`, as `hacker_news.py` and `http_client.py` do. Tests never touch the network unless marked
  `integration`.
- No comments in code. Names and small functions carry the meaning.
- Counts are mentions per 10,000 posts, never raw counts: Hacker News posts far more now than in 2008.
- Ruff is lint only, no formatter.
- `playground/` is for throwaway exploration. Ahmed's global gitignore keeps it out of git, not this repo's `.gitignore`.
