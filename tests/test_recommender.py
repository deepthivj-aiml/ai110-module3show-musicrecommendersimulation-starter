from src.recommender import Song, UserProfile, Recommender

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


from src.recommender import SCORING_MODES, load_songs, recommend_songs, score_song


def _song(**overrides):
    song = {
        "id": 0, "title": "Song", "artist": "Artist", "genre": "pop", "mood": "happy",
        "energy": 0.8, "tempo_bpm": 120, "valence": 0.8, "danceability": 0.8,
        "acousticness": 0.2, "popularity": 50, "release_decade": 2010,
        "mood_tags": [], "instrumentalness": 0.0, "explicit": False,
    }
    song.update(overrides)
    return song


def test_load_songs_parses_advanced_attributes():
    songs = load_songs("data/songs.csv")
    first = songs[0]
    assert isinstance(first["popularity"], int)
    assert isinstance(first["release_decade"], int)
    assert isinstance(first["instrumentalness"], float)
    assert isinstance(first["mood_tags"], list) and first["mood_tags"]
    assert isinstance(first["explicit"], bool)


def test_mood_first_mode_prefers_mood_over_genre():
    prefs = {"favorite_genre": "pop", "favorite_mood": "happy", "target_energy": 0.8}
    genre_only = _song(title="Pop Intense", mood="intense")
    mood_only = _song(title="Indie Happy", genre="indie pop")

    genre_first = [s["title"] for s, _, _ in recommend_songs(prefs, [genre_only, mood_only], k=2)]
    mood_first = [s["title"] for s, _, _ in
                  recommend_songs(prefs, [genre_only, mood_only], k=2, mode=SCORING_MODES["mood-first"])]

    assert genre_first[0] == "Pop Intense"
    assert mood_first[0] == "Indie Happy"


def test_explicit_penalty_only_applies_when_disallowed():
    prefs = {"favorite_genre": "pop", "favorite_mood": "happy", "target_energy": 0.8}
    song = _song(explicit=True)
    allowed, _ = score_song(prefs, song)
    blocked, reasons = score_song({**prefs, "allow_explicit": False}, song)
    assert blocked == allowed - 1.0
    assert "explicit lyrics (-1.0)" in reasons


def test_diversity_penalty_demotes_repeat_artist():
    prefs = {"favorite_genre": "pop", "favorite_mood": "happy", "target_energy": 0.8}
    songs = [
        _song(title="Hit A", artist="Same Band"),
        _song(title="Hit B", artist="Same Band", energy=0.78),
        # Scores just below Hit B, so only the artist penalty can lift it above
        _song(title="Other", artist="New Band", energy=0.75),
    ]
    plain = [s["title"] for s, _, _ in recommend_songs(prefs, songs, k=2)]
    diverse = recommend_songs(prefs, songs, k=2, diverse=True)

    assert plain == ["Hit A", "Hit B"]
    assert [s["title"] for s, _, _ in diverse] == ["Hit A", "Other"]
