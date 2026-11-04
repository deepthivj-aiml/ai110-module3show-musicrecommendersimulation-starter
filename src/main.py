"""
Command line runner for the Music Recommender Simulation.

Run from the project root with:  python -m src.main
Options:
  --mode genre-first | mood-first | energy-focused   (default: genre-first)
  --diverse                                         penalize repeat artists/genres
  -k N                                              how many songs to show (default: 5)
"""

import argparse
import textwrap

from src.recommender import SCORING_MODES, load_songs, max_score, recommend_songs

PROFILES = {
    "Default pop/happy": {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.80,
        "likes_acoustic": False,
    },
    # Taste profile: a calm, acoustic study listener
    "Lofi study": {
        "favorite_genre": "lofi",
        "favorite_mood": "chill",
        "target_energy": 0.40,
        "likes_acoustic": True,
    },
    "Deep intense rock": {
        "favorite_genre": "rock",
        "favorite_mood": "intense",
        "target_energy": 0.90,
        "likes_acoustic": False,
    },
    # Edge cases: profiles designed to trick the scoring logic
    "Edge: sad but high energy": {
        "favorite_genre": "folk",
        "favorite_mood": "sad",
        "target_energy": 0.90,
        "likes_acoustic": False,
    },
    "Edge: genre not in catalog": {
        "favorite_genre": "k-pop",
        "favorite_mood": "happy",
        "target_energy": 0.70,
        "likes_acoustic": None,
    },
    "Edge: capitalized labels": {
        "favorite_genre": "Pop",
        "favorite_mood": "Happy",
        "target_energy": 0.80,
        "likes_acoustic": False,
    },
    # Advanced profiles: use the extra song attributes
    "Throwback night drive": {
        "favorite_genre": "synthwave",
        "favorite_mood": "nostalgic",
        "target_energy": 0.65,
        "likes_acoustic": False,
        "desired_tags": ["nostalgic", "late-night", "dreamy"],
        "favorite_decade": 1980,
        "likes_popular": False,
        "wants_instrumental": True,
    },
    "Clean workout": {
        "favorite_genre": "pop",
        "favorite_mood": "intense",
        "target_energy": 0.90,
        "likes_acoustic": False,
        "desired_tags": ["energetic", "adrenaline"],
        "likes_popular": True,
        "allow_explicit": False,
    },
}

BASIC_KEYS = ("favorite_genre", "favorite_mood", "target_energy", "likes_acoustic")
REASON_WIDTH = 42


def describe_profile(user_prefs: dict) -> str:
    """Return a one-line summary of a profile's preferences."""
    parts = [
        f"genre={user_prefs['favorite_genre']}",
        f"mood={user_prefs['favorite_mood']}",
        f"energy={user_prefs['target_energy']:.2f}",
        f"likes_acoustic={user_prefs.get('likes_acoustic')}",
    ]
    for key, value in user_prefs.items():
        if key not in BASIC_KEYS:
            parts.append(f"{key}={value}")
    return ", ".join(parts)


def format_table(recommendations: list) -> str:
    """Render recommendations as an ASCII table with one reason per line."""
    headers = ["#", "Song", "Genre / Mood", "Score", "Reasons"]
    rows = []
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        reasons = []
        for reason in explanation.split("; "):
            reasons.extend(textwrap.wrap(reason, REASON_WIDTH, subsequent_indent="  "))
        rows.append([
            [str(rank)],
            [song["title"], f"by {song['artist']}"],
            [song["genre"], f"/ {song['mood']}"],
            [f"{score:.2f}"],
            reasons,
        ])

    widths = [
        max(len(headers[col]), *(len(line) for row in rows for line in row[col]))
        for col in range(len(headers))
    ]
    border = "+" + "+".join("-" * (w + 2) for w in widths) + "+"

    def render(cells):
        height = max(len(cell) for cell in cells)
        lines = []
        for i in range(height):
            parts = [(cell[i] if i < len(cell) else "").ljust(w) for cell, w in zip(cells, widths)]
            lines.append("| " + " | ".join(parts) + " |")
        return lines

    out = [border, *render([[h] for h in headers]), border.replace("-", "=")]
    for row in rows:
        out += render(row)
        out.append(border)
    return "\n".join(out)


def main() -> None:
    parser = argparse.ArgumentParser(description="Music Recommender Simulation")
    parser.add_argument("--mode", choices=SCORING_MODES, default="genre-first", help="ranking strategy")
    parser.add_argument("--diverse", action="store_true", help="penalize repeat artists and genres")
    parser.add_argument("-k", type=int, default=5, help="number of recommendations per profile")
    args = parser.parse_args()
    mode = SCORING_MODES[args.mode]

    songs = load_songs("data/songs.csv")
    print(f"Mode: {mode.name}  |  Diversity penalty: {'on' if args.diverse else 'off'}")
    print()
    for name, user_prefs in PROFILES.items():
        recommendations = recommend_songs(user_prefs, songs, k=args.k, mode=mode, diverse=args.diverse)
        print(f"Profile: {name}  (best possible score {max_score(user_prefs, mode):.2f})")
        print(f"  {describe_profile(user_prefs)}")
        print(format_table(recommendations))
        print()


if __name__ == "__main__":
    main()
