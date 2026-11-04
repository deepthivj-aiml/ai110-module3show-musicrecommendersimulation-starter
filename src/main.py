"""
Command line runner for the Music Recommender Simulation.

Run from the project root with:  python -m src.main
"""

from src.recommender import load_songs, recommend_songs

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
}


def print_recommendations(name: str, user_prefs: dict, recommendations: list) -> None:
    """Print one profile's top recommendations with scores and reasons."""
    print("=" * 60)
    print(f"Profile: {name}")
    print(
        f"  genre={user_prefs['favorite_genre']}, mood={user_prefs['favorite_mood']}, "
        f"energy={user_prefs['target_energy']:.2f}, likes_acoustic={user_prefs['likes_acoustic']}"
    )
    print("-" * 60)
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"{rank}. {song['title']} by {song['artist']}  [{song['genre']}/{song['mood']}]")
        print(f"   Score: {score:.2f} / 5.00")
        for reason in explanation.split("; "):
            print(f"     - {reason}")
    print()


def main() -> None:
    songs = load_songs("data/songs.csv")
    print()
    for name, user_prefs in PROFILES.items():
        recommendations = recommend_songs(user_prefs, songs, k=5)
        print_recommendations(name, user_prefs, recommendations)


if __name__ == "__main__":
    main()
