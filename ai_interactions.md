# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agentic Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

Challenge 1 (Advanced Song Features): add at least five new attributes to `data/songs.csv` and update the scoring in `src/recommender.py` to use them. The same agent session also did Challenges 2–4 (scoring modes, diversity penalty and a table layout for the output).

**Prompts used:**

> Introduce 5 or more complex attributes to your dataset that are not currently present in the baseline data, such as Song Popularity (0-100), Release Decade, or Detailed Mood Tags (e.g., "nostalgic," "aggressive," "euphoric"). Update both data/songs.csv and the scoring logic in src/recommender.py so scoring accounts for the new attributes.

> Build two or more different ranking strategies (e.g., "Genre-First," "Mood-First," or "Energy-Focused") so a user can switch between modes in main.py. [...] brainstorm a design pattern (like a simple "Strategy" pattern) that keeps your code modular.

> Implement a "Diversity Penalty" that prevents the recommender from suggesting too many songs from the same artist or genre in the top results. [...] penalize a song's score if its artist is already present in the top recommendations list.

> [...] use a library like tabulate or simple ASCII formatting to display your top recommendations. [...] the table must include the "reasons" for each score.

**What did the agent generate or change?**

- **`data/songs.csv`:** added 5 columns to all 18 songs:
  - `popularity` (0–100)
  - `release_decade` (1970–2020)
  - `mood_tags` (2–3 detailed tags separated by `;`, like `nostalgic;late-night;dreamy`)
  - `instrumentalness` (0.0–1.0)
  - `explicit` (0/1)

  The values were made up by the AI to fit each song's genre and mood.
- **`src/recommender.py`:**
  - `load_songs` now parses the new columns into int, float, list and bool.
  - `score_song` has five new optional checks, each adding its own reason:
    - shared mood tags: +0.25 each, up to +0.75
    - same decade: +0.75 (one decade away: +0.38)
    - popular pick or hidden gem: up to +0.5
    - instrumental vs. vocals: up to +0.5
    - explicit lyrics: −1.0, when the profile sets `allow_explicit: False`
  - Each check only runs when the profile sets that preference, so the original profiles score exactly as before.
  - New `ScoringMode` strategy objects with three modes, a `max_score()` helper, and a `pick_diverse()` step for the diversity penalty.
  - `Song` has the new fields with default values, so the original tests still build songs the old way.
- **`src/main.py`:**
  - Two new profiles that use the new preferences ("Throwback night drive", "Clean workout").
  - `--mode`, `--diverse` and `-k` command-line options.
  - An ASCII table with one reason per line. It uses only the standard library, so no `tabulate` dependency was added.
- **`tests/test_recommender.py`:** 4 new tests covering the new columns, the mood-first mode, the explicit penalty and the diversity penalty.
- **`README.md`:** updated the feature list, the run instructions and the sample output.

**What did you verify or fix manually?**

- **Old results unchanged.** Before the change I saved the output for the six original profiles. After it, I compared all 30 rows (6 profiles × top 5): every title and score was identical, so the new attributes didn't silently change any existing rankings.
- **Max scores.** I checked by hand that the "best possible score" printed for the new profiles is right: 7.50 for "Throwback night drive" and 6.00 for "Clean workout".
- **A failing test.** The first version of the diversity test failed. The cause was the test data, not the penalty: the "other artist" song was rock, so it missed the 2.0 genre points, which is more than the 1.5 penalty. I changed it to a pop song that differs only by artist, and the test then passed. All 6 tests pass.
- **A surprising result.** "Gym Hero" is explicit but still wins "Clean workout" (5.87 − 1.0 = 4.87, vs. 4.20 for Sunrise City). A user who says "no explicit songs" probably expects them filtered out, not just nudged down. This is a weakness I'd fix next with a hard filter.
- **Made-up data.** The new numbers were invented by the AI, so they're plausible but not measured from real songs.

---

## Design Pattern (SF10)

> Document how AI helped you choose or implement a design pattern.

**Which design pattern did you use?**

**Strategy.** Each scoring mode is an interchangeable strategy object, and the scoring and ranking code doesn't care which one it's given.

**How did AI help you brainstorm or implement it?**

I asked the AI how to support "Genre-First", "Mood-First" and "Energy-Focused" modes without copying the scoring function three times. It compared two versions of the Strategy pattern:

1. **A class per strategy:** a base class with a `score()` method, and one subclass per mode.
2. **A data-only strategy:** one small frozen dataclass holding the weights, with one shared scoring function that reads them.

The three modes only differ in how many points each factor is worth, not in *how* a song is judged, so we chose option 2. It keeps all the scoring rules in one place, and adding a mode is one line. The AI also suggested making the dataclass `frozen` so a mode can't be changed by accident while songs are being scored, and selecting the mode with an `argparse` choice so a typo gives a clear error. I considered prototyping the mood-first mode on a separate `experiment/mood-first` branch, but because a mode is just a new set of weights, the change was small enough to make on `main` and check with tests.

**How does the pattern appear in your final code?**

- **`ScoringMode` dataclass** in `src/recommender.py`: the strategy. It holds the weights for genre, mood, energy and the advanced attributes.
- **`SCORING_MODES` dict:** the three strategies.
  - `genre-first`: 2.0 / 1.0 / 1.5 for genre / mood / energy.
  - `mood-first`: 1.0 / 2.0 / 1.5, and mood tags are worth double.
  - `energy-focused`: 0.5 / 0.5 / 3.0.
- **The code that uses a strategy:**
  - `score_song(user_prefs, song, mode)`, `recommend_songs(..., mode=...)` and `max_score(user_prefs, mode)` take a mode and read its weights. They have no `if mode == ...` branches.
  - `Recommender(songs, mode=...)` stores one for the OOP interface.
- **`src/main.py`:** picks the strategy at runtime with `--mode`.
