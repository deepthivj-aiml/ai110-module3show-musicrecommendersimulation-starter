import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict, field

@dataclass(frozen=True)
class ScoringMode:
    """A named set of weights; swapping the mode swaps the ranking strategy."""
    name: str
    genre: float
    mood: float
    energy: float
    acoustic: float = 0.5
    popularity: float = 0.5
    decade: float = 0.75
    tag: float = 0.25
    max_tag_points: float = 0.75
    instrumental: float = 0.5
    explicit_penalty: float = 1.0

SCORING_MODES = {
    "genre-first": ScoringMode("genre-first", genre=2.0, mood=1.0, energy=1.5),
    "mood-first": ScoringMode("mood-first", genre=1.0, mood=2.0, energy=1.5, tag=0.5, max_tag_points=1.0),
    "energy-focused": ScoringMode("energy-focused", genre=0.5, mood=0.5, energy=3.0),
}
DEFAULT_MODE = SCORING_MODES["genre-first"]

# Diversity penalties, applied once per song of the same artist/genre already picked
ARTIST_PENALTY = 1.0
GENRE_PENALTY = 0.5

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
    popularity: int = 50
    release_decade: int = 0
    mood_tags: List[str] = field(default_factory=list)
    instrumentalness: float = 0.0
    explicit: bool = False

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
    def __init__(self, songs: List[Song], mode: ScoringMode = DEFAULT_MODE):
        self.songs = songs
        self.mode = mode

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top k Song objects for this user, highest score first."""
        return sorted(
            self.songs,
            key=lambda song: score_song(asdict(user), asdict(song), self.mode)[0],
            reverse=True,
        )[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a readable list of the reasons behind a song's score."""
        _, reasons = score_song(asdict(user), asdict(song), self.mode)
        return "; ".join(reasons)

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            for field_name in ("id", "tempo_bpm", "popularity", "release_decade"):
                row[field_name] = int(row[field_name])
            for field_name in ("energy", "valence", "danceability", "acousticness", "instrumentalness"):
                row[field_name] = float(row[field_name])
            row["mood_tags"] = row["mood_tags"].split(";") if row["mood_tags"] else []
            row["explicit"] = row["explicit"] == "1"
            songs.append(row)
    print(f"Loaded songs: {len(songs)}")
    return songs

def score_song(user_prefs: Dict, song: Dict, mode: ScoringMode = DEFAULT_MODE) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py
    """
    score = 0.0
    reasons = []

    if song["genre"] == user_prefs["favorite_genre"]:
        score += mode.genre
        reasons.append(f"genre match (+{mode.genre:.1f})")

    if song["mood"] == user_prefs["favorite_mood"]:
        score += mode.mood
        reasons.append(f"mood match (+{mode.mood:.1f})")

    # Closer to the target energy earns more points; distance is at most 1.0
    gap = abs(song["energy"] - user_prefs["target_energy"])
    energy_points = mode.energy * (1 - gap)
    score += energy_points
    reasons.append(f"energy {song['energy']:.2f} vs target {user_prefs['target_energy']:.2f} (+{energy_points:.2f})")

    likes_acoustic = user_prefs.get("likes_acoustic")
    if likes_acoustic is not None:
        fit = song["acousticness"] if likes_acoustic else 1 - song["acousticness"]
        acoustic_points = mode.acoustic * fit
        score += acoustic_points
        label = "acoustic" if likes_acoustic else "produced"
        reasons.append(f"{label} sound (+{acoustic_points:.2f})")

    # The checks below only run when the profile sets the matching preference
    desired_tags = user_prefs.get("desired_tags")
    if desired_tags:
        shared = [tag for tag in song.get("mood_tags", []) if tag in desired_tags]
        if shared:
            tag_points = min(mode.tag * len(shared), mode.max_tag_points)
            score += tag_points
            reasons.append(f"tags {', '.join(shared)} (+{tag_points:.2f})")

    favorite_decade = user_prefs.get("favorite_decade")
    if favorite_decade and song.get("release_decade"):
        decade_gap = abs(song["release_decade"] - favorite_decade)
        if decade_gap == 0:
            score += mode.decade
            reasons.append(f"from the {favorite_decade}s (+{mode.decade:.2f})")
        elif decade_gap == 10:
            near_points = mode.decade / 2
            score += near_points
            reasons.append(f"close to the {favorite_decade}s (+{near_points:.2f})")

    likes_popular = user_prefs.get("likes_popular")
    if likes_popular is not None and "popularity" in song:
        share = song["popularity"] / 100
        fit = share if likes_popular else 1 - share
        popularity_points = mode.popularity * fit
        score += popularity_points
        label = "popular pick" if likes_popular else "hidden gem"
        reasons.append(f"{label}, popularity {song['popularity']} (+{popularity_points:.2f})")

    wants_instrumental = user_prefs.get("wants_instrumental")
    if wants_instrumental is not None and "instrumentalness" in song:
        fit = song["instrumentalness"] if wants_instrumental else 1 - song["instrumentalness"]
        instrumental_points = mode.instrumental * fit
        score += instrumental_points
        label = "instrumental" if wants_instrumental else "vocals"
        reasons.append(f"{label} (+{instrumental_points:.2f})")

    if user_prefs.get("allow_explicit") is False and song.get("explicit"):
        score -= mode.explicit_penalty
        reasons.append(f"explicit lyrics (-{mode.explicit_penalty:.1f})")

    return score, reasons

def max_score(user_prefs: Dict, mode: ScoringMode = DEFAULT_MODE) -> float:
    """Return the best score a perfect song could earn for this profile and mode."""
    total = mode.genre + mode.mood + mode.energy
    if user_prefs.get("likes_acoustic") is not None:
        total += mode.acoustic
    if user_prefs.get("desired_tags"):
        total += min(mode.tag * len(user_prefs["desired_tags"]), mode.max_tag_points)
    if user_prefs.get("favorite_decade"):
        total += mode.decade
    if user_prefs.get("likes_popular") is not None:
        total += mode.popularity
    if user_prefs.get("wants_instrumental") is not None:
        total += mode.instrumental
    return total

def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    mode: ScoringMode = DEFAULT_MODE,
    diverse: bool = False,
) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song, mode)
        scored.append((song, score, reasons))
    ranked = sorted(scored, key=lambda item: item[1], reverse=True)

    if not diverse:
        return [(song, score, "; ".join(reasons)) for song, score, reasons in ranked[:k]]
    return pick_diverse(ranked, k)

def pick_diverse(ranked: List[Tuple[Dict, float, List[str]]], k: int) -> List[Tuple[Dict, float, str]]:
    """Greedily fill the top k, penalizing songs whose artist or genre is already picked."""
    picked = []
    remaining = list(ranked)
    while remaining and len(picked) < k:
        best_index, best_score, best_reasons = None, None, None
        for index, (song, score, reasons) in enumerate(remaining):
            artist_repeats = sum(p[0]["artist"] == song["artist"] for p in picked)
            genre_repeats = sum(p[0]["genre"] == song["genre"] for p in picked)
            penalty = ARTIST_PENALTY * artist_repeats + GENRE_PENALTY * genre_repeats
            # Strict ">" keeps the higher original score when adjusted scores tie
            if best_score is None or score - penalty > best_score:
                extra = []
                if artist_repeats:
                    extra.append(f"artist already listed (-{ARTIST_PENALTY * artist_repeats:.2f})")
                if genre_repeats:
                    extra.append(f"genre already listed (-{GENRE_PENALTY * genre_repeats:.2f})")
                best_index, best_score, best_reasons = index, score - penalty, reasons + extra
        song = remaining.pop(best_index)[0]
        picked.append((song, best_score, "; ".join(best_reasons)))
    return picked
