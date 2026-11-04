# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**VibeMatch 1.0**, a small content-based music recommender.

---

## 2. Intended Use  

**Goal:** VibeMatch suggests the top 5 songs from a small catalog that best fit one listener's taste. You give it a favorite genre, a favorite mood, how energetic you want the music to be, and whether you like acoustic sound. It scores every song and explains why each pick made the list.

**Intended use:**

- Classroom exploration of how recommenders turn data into suggestions.
- Trying out scoring weights and seeing how the rankings change.
- Showing, step by step, why one song beat another.

**Not intended for:**

- Real users or a real music app. The catalog is 18 made-up songs.
- Judging what music is "good". It only measures how close a song is to what you typed.
- Listeners whose taste doesn't fit one genre and one mood. It can't represent "I like both jazz and metal".
- Any decision that matters. The numbers for the songs were invented, not measured from audio.

---

## 3. How the Model Works  

The recommender works like a judge holding a score sheet. You tell it four things about your taste: your favorite genre, your favorite mood, how energetic you want the music to be (from 0, very calm, to 1, very intense), and whether you prefer acoustic or produced sound. The judge then goes through every song in the catalog, one at a time, and hands out points:

- **2 points** if the song is your favorite genre. Genre counts the most because it describes the overall sound.
- **1 point** if the song has your favorite mood.
- **Up to 1.5 points** for energy. A song whose energy exactly matches what you asked for gets all 1.5 points, and the points drop the further away it is. Being close is what counts, not being higher or lower.
- **Up to 0.5 points** for sound. A very acoustic song earns the most if you like acoustic music; a very produced song earns the most if you don't.

A perfect match scores 5. Once every song has a score, the recommender sorts them from highest to lowest and shows you the top five, along with the list of reasons each song earned its points, so you can see why it was picked.

**Changes from the starter logic:** the starter code returned the first songs in the file no matter who was asking. Now every song is actually scored against the user's taste. Song data is read from the CSV with numbers turned into real numbers so they can be compared, and each recommendation comes with an explanation. Tempo, danceability and valence are loaded but not scored yet, because in this catalog they mostly rise and fall with energy.

---

## 4. Data  

- **Size:** 18 songs in `data/songs.csv`. The starter file had 10, and I added 8 more.
- **Features per song:** title, artist, genre, mood, energy, tempo (BPM), valence, danceability and acousticness. The scoring uses genre, mood, energy and acousticness. As a stretch feature I added popularity, release decade, detailed mood tags, instrumentalness and an explicit flag. These only count when a profile asks for them.
- **Variety:** 15 genres and 14 moods. I added the 8 new songs to cover genres and moods the starter file didn't have: hip-hop, classical, metal, reggae, country, edm, r&b and folk.
- **Limits:**
  - Most genres have only one song. Lofi has 3 and pop has 2.
  - All songs and artists are fictional, and their numbers (energy and so on) were made up by hand or by AI, not measured from real audio.
  - There are no lyrics, languages, release years, vocals or popularity data, so whole parts of musical taste are missing.
  - Mood is a single word per song, even though real songs can feel several ways at once.

---

## 5. Strengths  

- **Clear tastes get clear results.** Pop/happy, lofi/chill and rock/intense listeners all got the top song I'd expect ("Sunrise City", "Library Rain" and "Storm Runner").
- **Opposites really are opposites.** The lofi and rock lists share no songs, because energy and acoustic preference push them to opposite ends of the catalog.
- **Close counts, not just high or low.** The energy score rewards songs near your target, so a calm listener isn't buried in loud songs, and the reverse.
- **Every pick is explained.** Each recommendation lists exactly where its points came from (for example "genre match (+2.0)"), so a surprising result can be traced instead of guessed at.

---

## 6. Limitations and Bias 

**Main weakness: labels beat feel.** Genre and mood together are worth 3 of the 5 points, while energy can only move a score by 1.5, so a song with the right *labels* beats songs with the right *feel*. The clearest example was a user who asked for sad folk at high energy (0.90): the system recommended "Paper Boats" first, a quiet acoustic folk song with energy 0.30, which is the opposite of what that person wanted to feel. Every song that actually matched their energy scored about 1.7 points lower just because it wasn't labeled folk or sad. This also creates a filter bubble: a listener only ever sees songs from their one favorite genre at the top, even when a song from another genre fits their mood and energy better.

Other limitations found during testing:

- **Exact text matching.** "Pop" with a capital P matches nothing, so the same pop/happy listener gets a hip-hop song first instead of "Sunrise City". "indie pop" also gets no credit for "pop".
- **Thin catalog.** Most genres have only one song, so fans of metal, folk or reggae get one real match and then filler from other genres.
- **Missing genres get a lower ceiling.** A k-pop fan can never earn the 2 genre points, so their best possible score is 2 points lower than everyone else's. The k-pop profile also has no acoustic preference, so its ceiling is just 2.5 out of 5.
- **Ignored features.** Tempo, valence and danceability are loaded but don't affect the score, so the system can't tell a dark, intense song from a bright one at the same energy.

---

## 7. Evaluation  

### Profiles tested

I ran six profiles through `python -m src.main` and looked at each top 5: three normal listeners and three edge cases built to trick the scoring.

| Profile | Genre | Mood | Energy | Acoustic? | What it tests |
|---|---|---|---|---|---|
| Default pop/happy | pop | happy | 0.80 | no | The assignment's baseline |
| Lofi study | lofi | chill | 0.40 | yes | The opposite end of the energy scale |
| Deep intense rock | rock | intense | 0.90 | no | A loud, high-energy listener |
| Edge: sad but high energy | folk | sad | 0.90 | no | Labels and energy pull in opposite directions |
| Edge: genre not in catalog | k-pop | happy | 0.70 | not set | A genre the catalog doesn't have |
| Edge: capitalized labels | Pop | Happy | 0.80 | no | Same as the default, typed with capitals |

For the three normal profiles the results felt right. The pop/happy list starts with "Sunrise City", the lofi list is all calm acoustic songs, and the rock list starts with "Storm Runner".

### What surprised me

- **"Gym Hero" shows up everywhere.** It's in the top 5 for four of the six profiles, including #2 for the person who wants happy pop. In plain terms: "Gym Hero" is labeled pop, it's very energetic (0.93), and it's heavily produced. A happy-pop listener gets 2 points just because it's pop, nearly full energy points because 0.93 is close to their 0.80, and the produced-sound bonus. The system never checks whether the song *sounds happy*. It's labeled "intense", and the only cost of that is missing out on the 1 mood point. A pop label is worth twice as much as a mood match, so "Gym Hero" still beats "Rooftop Lights", which really is happy but is labeled "indie pop".
- **The sad-but-energetic user got a quiet song first.** See Limitations above.
- **Capital letters break everything.** "Pop/Happy" earned zero genre and mood points, so the top song became a hip-hop track.

### Why did "Sunrise City" rank first for pop/happy?

It scored 4.88 out of 5. It's pop (+2.0) and happy (+1.0), its energy of 0.82 is only 0.02 from the target, so it keeps almost all of the 1.5 energy points (+1.47), and its low acousticness (0.18) earns most of the produced-sound bonus (+0.41). It's the only song with both labels. The runner-up, "Gym Hero", gets the pop points but not the happy point and lands at 3.78.

### Comparing profiles, pair by pair

| Pair | What changed, and why it makes sense |
|---|---|
| Pop/happy vs. Lofi study | No songs in common. Pop gets energetic, produced songs (0.75–0.93) and lofi gets calm, acoustic ones (0.28–0.42), because the energy targets and the acoustic preference are opposites. |
| Pop/happy vs. Deep intense rock | They share "Gym Hero" (#2 in both) and "Sunrise City". Both want loud, produced music, so the energy points overlap, and only the genre and mood labels decide who's #1. |
| Pop/happy vs. Sad but high energy | They share "Gym Hero", the overlapping high-energy song. The sad profile's list is otherwise the loudest songs in the catalog, except at #1, where one folk/sad label match pulls a quiet song to the top. |
| Pop/happy vs. Genre not in catalog | Four songs overlap, but the order changes. Without genre points, the two happy songs lead, and "Rooftop Lights" (energy 0.76) beats "Sunrise City" (0.82) because it's closer to the k-pop user's 0.70. "Gym Hero" drops out: no genre bonus, and 0.93 is far from 0.70. |
| Pop/happy vs. Capitalized labels | Same taste, very different list. "Sunrise City" falls from 4.88 to 1.88 and a hip-hop song takes #1, only because "Pop" isn't "pop". |
| Lofi study vs. Deep intense rock | Mirror images with no overlap. The rock list is high-energy and produced; the lofi list is low-energy and acoustic. |
| Lofi study vs. Sad but high energy | No overlap, but the sad profile's #1 ("Paper Boats", 0.30 energy, very acoustic) is really a lofi-listener song. It just misses the lofi top 5 (1.81 vs. 1.90). |
| Lofi study vs. Genre not in catalog | No overlap. The k-pop user's 0.70 energy target lands in the middle, away from lofi's calm 0.40. |
| Lofi study vs. Capitalized labels | No overlap. With no label matches, the capitalized profile behaves like a pure "energy 0.80, produced" listener, which is the opposite of lofi. |
| Deep intense rock vs. Sad but high energy | Places #2–#5 are the same four songs (Storm Runner, Gym Hero, Neon Pulse, Iron Verdict) because both want energy 0.90 and produced sound. Only #1 differs, which shows the labels alone decide the top spot. |
| Deep intense rock vs. Genre not in catalog | Only "Sunrise City" is shared. Rock aims at 0.90 energy and the k-pop user at 0.70, so their energy points favor different songs. |
| Deep intense rock vs. Capitalized labels | They share Storm Runner, Gym Hero and Sunrise City: two high-energy, produced profiles. Rock's labels still work, so "Storm Runner" leads by a wide margin; the capitalized profile's labels don't match anything. |
| Sad but high energy vs. Genre not in catalog | No overlap. The sad list is the loudest songs in the catalog, while k-pop gets mid-energy, happy songs. |
| Sad but high energy vs. Capitalized labels | They share Storm Runner and Gym Hero. Both profiles are effectively scoring on energy alone (the sad one matches labels for only one song), so the same high-energy songs fill both lists. |
| Genre not in catalog vs. Capitalized labels | Neither earns genre points, but the k-pop user typed "happy" in lowercase, so happy songs still get the mood point and lead the list. The capitalized "Happy" matches nothing, so happy songs lose to hip-hop. This isolates what the 1 mood point is worth. |

### Experiment: weight shift (energy ×2, genre ×½)

I changed the genre points from 2.0 to 1.0 and the energy points from 1.5 to 3.0, then reran all six profiles. The math stays valid: the energy gap is always between 0 and 1, so energy now gives 0–3 points and the maximum score becomes 5.5. Weights were restored afterwards.

| Profile | Baseline top 3 | Experiment top 3 |
|---|---|---|
| Default pop/happy | Sunrise City, Gym Hero, Rooftop Lights | Sunrise City, **Rooftop Lights, Gym Hero** |
| Lofi study | Library Rain, Midnight Coding, Focus Flow | **Midnight Coding, Library Rain**, Focus Flow |
| Deep intense rock | Storm Runner, Gym Hero, Neon Pulse | no change |
| Edge: sad but high energy | Paper Boats, Storm Runner, Gym Hero | **Storm Runner, Gym Hero, Neon Pulse** (Paper Boats drops to #5) |
| Edge: genre not in catalog | Rooftop Lights, Sunrise City, Night Drive Loop | no change |
| Edge: capitalized labels | Concrete Crown, Sunrise City, Night Drive Loop | no change in top 3 |

**More accurate, or just different?** Mostly just different, with one real improvement. For pop/happy, "Rooftop Lights" (truly happy) moving above "Gym Hero" (intense) feels more accurate. For the sad-but-energetic user, the high-energy songs now win, but they're intense, not sad, and nothing in the catalog is both sad and high energy, so the change trades one bad answer for another. The lofi swap is a 0.01 difference and means nothing. Where the labels didn't match anyway (k-pop, capitalized), the order barely moved.

### Full baseline output

```text
$ python -m src.main
Loaded songs: 18

============================================================
Profile: Default pop/happy
  genre=pop, mood=happy, energy=0.80, likes_acoustic=False
------------------------------------------------------------
1. Sunrise City by Neon Echo  [pop/happy]
   Score: 4.88 / 5.00
     - genre match (+2.0)
     - mood match (+1.0)
     - energy 0.82 vs target 0.80 (+1.47)
     - produced sound (+0.41)
2. Gym Hero by Max Pulse  [pop/intense]
   Score: 3.78 / 5.00
     - genre match (+2.0)
     - energy 0.93 vs target 0.80 (+1.30)
     - produced sound (+0.47)
3. Rooftop Lights by Indigo Parade  [indie pop/happy]
   Score: 2.77 / 5.00
     - mood match (+1.0)
     - energy 0.76 vs target 0.80 (+1.44)
     - produced sound (+0.33)
4. Concrete Crown by Block Theory  [hip-hop/confident]
   Score: 1.91 / 5.00
     - energy 0.78 vs target 0.80 (+1.47)
     - produced sound (+0.44)
5. Night Drive Loop by Neon Echo  [synthwave/moody]
   Score: 1.81 / 5.00
     - energy 0.75 vs target 0.80 (+1.42)
     - produced sound (+0.39)

============================================================
Profile: Lofi study
  genre=lofi, mood=chill, energy=0.40, likes_acoustic=True
------------------------------------------------------------
1. Library Rain by Paper Lanterns  [lofi/chill]
   Score: 4.85 / 5.00
     - genre match (+2.0)
     - mood match (+1.0)
     - energy 0.35 vs target 0.40 (+1.42)
     - acoustic sound (+0.43)
2. Midnight Coding by LoRoom  [lofi/chill]
   Score: 4.82 / 5.00
     - genre match (+2.0)
     - mood match (+1.0)
     - energy 0.42 vs target 0.40 (+1.47)
     - acoustic sound (+0.35)
3. Focus Flow by LoRoom  [lofi/focused]
   Score: 3.89 / 5.00
     - genre match (+2.0)
     - energy 0.40 vs target 0.40 (+1.50)
     - acoustic sound (+0.39)
4. Spacewalk Thoughts by Orbit Bloom  [ambient/chill]
   Score: 2.78 / 5.00
     - mood match (+1.0)
     - energy 0.28 vs target 0.40 (+1.32)
     - acoustic sound (+0.46)
5. Coffee Shop Stories by Slow Stereo  [jazz/relaxed]
   Score: 1.90 / 5.00
     - energy 0.37 vs target 0.40 (+1.46)
     - acoustic sound (+0.45)

============================================================
Profile: Deep intense rock
  genre=rock, mood=intense, energy=0.90, likes_acoustic=False
------------------------------------------------------------
1. Storm Runner by Voltline  [rock/intense]
   Score: 4.93 / 5.00
     - genre match (+2.0)
     - mood match (+1.0)
     - energy 0.91 vs target 0.90 (+1.48)
     - produced sound (+0.45)
2. Gym Hero by Max Pulse  [pop/intense]
   Score: 2.93 / 5.00
     - mood match (+1.0)
     - energy 0.93 vs target 0.90 (+1.46)
     - produced sound (+0.47)
3. Neon Pulse by Hyperdrive  [edm/euphoric]
   Score: 1.91 / 5.00
     - energy 0.95 vs target 0.90 (+1.43)
     - produced sound (+0.48)
4. Iron Verdict by Grave Signal  [metal/angry]
   Score: 1.88 / 5.00
     - energy 0.97 vs target 0.90 (+1.40)
     - produced sound (+0.48)
5. Sunrise City by Neon Echo  [pop/happy]
   Score: 1.79 / 5.00
     - energy 0.82 vs target 0.90 (+1.38)
     - produced sound (+0.41)

============================================================
Profile: Edge: sad but high energy
  genre=folk, mood=sad, energy=0.90, likes_acoustic=False
------------------------------------------------------------
1. Paper Boats by Willow & Pine  [folk/sad]
   Score: 3.64 / 5.00
     - genre match (+2.0)
     - mood match (+1.0)
     - energy 0.30 vs target 0.90 (+0.60)
     - produced sound (+0.04)
2. Storm Runner by Voltline  [rock/intense]
   Score: 1.93 / 5.00
     - energy 0.91 vs target 0.90 (+1.48)
     - produced sound (+0.45)
3. Gym Hero by Max Pulse  [pop/intense]
   Score: 1.93 / 5.00
     - energy 0.93 vs target 0.90 (+1.46)
     - produced sound (+0.47)
4. Neon Pulse by Hyperdrive  [edm/euphoric]
   Score: 1.91 / 5.00
     - energy 0.95 vs target 0.90 (+1.43)
     - produced sound (+0.48)
5. Iron Verdict by Grave Signal  [metal/angry]
   Score: 1.88 / 5.00
     - energy 0.97 vs target 0.90 (+1.40)
     - produced sound (+0.48)

============================================================
Profile: Edge: genre not in catalog
  genre=k-pop, mood=happy, energy=0.70, likes_acoustic=None
------------------------------------------------------------
1. Rooftop Lights by Indigo Parade  [indie pop/happy]
   Score: 2.41 / 5.00
     - mood match (+1.0)
     - energy 0.76 vs target 0.70 (+1.41)
2. Sunrise City by Neon Echo  [pop/happy]
   Score: 2.32 / 5.00
     - mood match (+1.0)
     - energy 0.82 vs target 0.70 (+1.32)
3. Night Drive Loop by Neon Echo  [synthwave/moody]
   Score: 1.42 / 5.00
     - energy 0.75 vs target 0.70 (+1.42)
4. Concrete Crown by Block Theory  [hip-hop/confident]
   Score: 1.38 / 5.00
     - energy 0.78 vs target 0.70 (+1.38)
5. Island Morning by Sunset Collective  [reggae/uplifting]
   Score: 1.32 / 5.00
     - energy 0.58 vs target 0.70 (+1.32)

============================================================
Profile: Edge: capitalized labels
  genre=Pop, mood=Happy, energy=0.80, likes_acoustic=False
------------------------------------------------------------
1. Concrete Crown by Block Theory  [hip-hop/confident]
   Score: 1.91 / 5.00
     - energy 0.78 vs target 0.80 (+1.47)
     - produced sound (+0.44)
2. Sunrise City by Neon Echo  [pop/happy]
   Score: 1.88 / 5.00
     - energy 0.82 vs target 0.80 (+1.47)
     - produced sound (+0.41)
3. Night Drive Loop by Neon Echo  [synthwave/moody]
   Score: 1.81 / 5.00
     - energy 0.75 vs target 0.80 (+1.42)
     - produced sound (+0.39)
4. Storm Runner by Voltline  [rock/intense]
   Score: 1.78 / 5.00
     - energy 0.91 vs target 0.80 (+1.33)
     - produced sound (+0.45)
5. Gym Hero by Max Pulse  [pop/intense]
   Score: 1.78 / 5.00
     - energy 0.93 vs target 0.80 (+1.30)
     - produced sound (+0.47)
```

---

## 8. Future Work  

1. **Fix label matching.** Compare genres and moods in lowercase so "Pop" matches "pop", and give partial credit for related labels ("indie pop" ≈ "pop", "relaxed" ≈ "chill").
2. **Let users like more than one thing.** Allow a list of favorite genres and moods, and add a target for valence so the system can tell happy songs from dark ones at the same energy.
3. **Add variety to the top 5.** Limit each artist (or genre) to one or two spots so the list isn't the same sound five times, and grow the catalog so every genre has several songs.

---

## 9. Personal Reflection  

**Biggest learning moment.** The biggest learning moment was the "sad but high energy" test. I expected the system to find energetic songs, but it picked a quiet folk song first, just because the genre and mood labels matched. That showed me that the weights *are* the system's opinion. Choosing 2 points for genre and 1.5 for energy quietly decides whose taste counts, and you only notice by trying a user who doesn't fit.

**How AI tools helped, and when I double-checked.** The AI assistant was fast at writing the loader, the scoring function and the CLI layout, and at suggesting edge-case profiles I wouldn't have thought of. But I still had to check its work. Its first write-up of the evaluation claimed two lists shared only two songs when they really shared four, and it gave the wrong maximum score for a profile with no acoustic preference. During the weight experiment, the rerun also briefly showed old results, because Python had loaded a stale cached copy of the file. Running the program again and comparing against the real output caught all of these. The lesson: AI can draft the explanation, but the terminal output is the source of truth.

**What surprised me.** I was surprised that a few `if` checks and some simple math can feel like a real recommendation. With reasons printed next to each song, the list reads like a friend's suggestion. That same simplicity also explains why "Gym Hero" keeps appearing for happy-pop fans. The system sounds confident even when it's only matching labels.

**What I'd try next.** I'd fix the capital-letter bug, add valence and a variety rule, and then test the same profiles against a larger real-world dataset to see if the genre bias gets better or worse with more songs.
