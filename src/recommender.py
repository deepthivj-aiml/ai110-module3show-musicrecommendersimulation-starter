import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict

GENRE_POINTS = 2.0
MOOD_POINTS = 1.0
ENERGY_POINTS = 1.5
ACOUSTIC_POINTS = 0.5

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top k Song objects for this user, highest score first."""
        return sorted(
            self.songs,
            key=lambda song: score_song(asdict(user), asdict(song))[0],
            reverse=True,
        )[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a readable list of the reasons behind a song's score."""
        _, reasons = score_song(asdict(user), asdict(song))
        return "; ".join(reasons)

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            row["id"] = int(row["id"])
            row["tempo_bpm"] = int(row["tempo_bpm"])
            for field in ("energy", "valence", "danceability", "acousticness"):
                row[field] = float(row[field])
            songs.append(row)
    print(f"Loaded songs: {len(songs)}")
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py
    """
    score = 0.0
    reasons = []

    if song["genre"] == user_prefs["favorite_genre"]:
        score += GENRE_POINTS
        reasons.append(f"genre match (+{GENRE_POINTS:.1f})")

    if song["mood"] == user_prefs["favorite_mood"]:
        score += MOOD_POINTS
        reasons.append(f"mood match (+{MOOD_POINTS:.1f})")

    # Closer to the target energy earns more points; distance is at most 1.0
    gap = abs(song["energy"] - user_prefs["target_energy"])
    energy_points = ENERGY_POINTS * (1 - gap)
    score += energy_points
    reasons.append(f"energy {song['energy']:.2f} vs target {user_prefs['target_energy']:.2f} (+{energy_points:.2f})")

    likes_acoustic = user_prefs.get("likes_acoustic")
    if likes_acoustic is not None:
        fit = song["acousticness"] if likes_acoustic else 1 - song["acousticness"]
        acoustic_points = ACOUSTIC_POINTS * fit
        score += acoustic_points
        label = "acoustic" if likes_acoustic else "produced"
        reasons.append(f"{label} sound (+{acoustic_points:.2f})")

    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        scored.append((song, score, "; ".join(reasons)))
    return sorted(scored, key=lambda item: item[1], reverse=True)[:k]
