# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

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

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran  

No need for numeric metrics unless you created some.

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  
