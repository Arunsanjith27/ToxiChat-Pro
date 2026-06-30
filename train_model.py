"""
🧠 ToxiChat — Train Toxicity Detection ML Model
=================================================
This script trains a toxicity classifier and saves:
  - models/model.pkl          (Logistic Regression classifier)
  - models/tfidf_vectorizer.pkl (TF-IDF text vectorizer)

These files are loaded automatically by the backend.

Usage:
    python train_model.py
"""

import os
import re
import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

# ══════════════════════════════════════════════════════════════
# Output directory
# ══════════════════════════════════════════════════════════════
MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(MODEL_DIR, exist_ok=True)

# ══════════════════════════════════════════════════════════════
# Training Data — Curated toxic & non-toxic examples
# ══════════════════════════════════════════════════════════════
# Label: 1 = toxic, 0 = non-toxic

toxic_samples = [
    # Direct insults
    "you are so stupid and dumb",
    "what an idiot you are",
    "you're a complete moron",
    "shut up you fool",
    "you are worthless trash",
    "you're disgusting and pathetic",
    "what a loser you are",
    "you ugly piece of garbage",
    "you are a terrible person",
    "i hate you so much",
    "go die in a hole",
    "kill yourself nobody cares",
    "you are cancer to society",
    "you racist bigot scum",
    "you are the worst human being",
    "i hope you suffer",
    "you deserve nothing good",
    "everyone hates you",
    "you are a waste of space",
    "you make me sick",
    "you're nothing but a liar and a cheat",
    "stupid idiots like you should not exist",
    "you are a pathetic excuse for a human",
    "get lost you disgusting freak",
    "nobody likes you, you're annoying",
    "you are dumb as a rock",
    "what a horrible disgusting person",
    "i wish you would just disappear",
    "you are the biggest loser ever",
    "your opinions are garbage and stupid",
    "you ignorant fool shut your mouth",
    "you are a worthless piece of trash",
    "die already you moron",
    "you suck at everything you do",
    "you're a jerk and nobody likes you",
    "you are an ugly pathetic loser",
    "stop talking you annoying idiot",
    "you are scum of the earth",
    "how can someone be so stupid",
    "you disgust me you awful person",
    # Hate speech
    "all those people should be removed from the country",
    "those people are ruining everything",
    "they are all criminals and thugs",
    "people like them are the problem",
    "they should go back where they came from",
    # Threats
    "i will destroy you",
    "watch your back or else",
    "you will regret this forever",
    "i am going to ruin your life",
    "you better be scared",
    # Cyberbullying
    "nobody wants to be your friend",
    "you are always alone because you are terrible",
    "everyone laughs at you behind your back",
    "you will never amount to anything",
    "you are a failure at everything",
    "the world would be better without you",
    "you dont deserve to be happy",
    "everyone thinks you are a joke",
    "you should be ashamed of yourself",
    "you bring nothing but misery",
    # Profanity variations
    "what the hell is wrong with you",
    "you are a damn fool",
    "this is such crap",
    "you are full of it you jerk",
    "that is the most idiotic thing ever",
    # Aggressive ALL CAPS
    "YOU ARE SO STUPID",
    "SHUT UP ALREADY",
    "I HATE EVERYTHING ABOUT YOU",
    "YOU ARE GARBAGE",
    "WHAT AN IDIOT",
    "YOU ARE THE WORST",
    "NOBODY CARES ABOUT YOU",
    "GO AWAY YOU LOSER",
    "STOP BEING SO PATHETIC",
    "YOU MAKE EVERYONE SICK",
    # Profanity (Strong)
    "fuck off",
    "fucking idiot",
    "you are a bitch",
    "son of a bitch",
    "what the fuck",
    "go to hell",
    "i will kill you",
    "die today",
    "you are a loser",
]

non_toxic_samples = [
    # Friendly greetings
    "hello how are you today",
    "hi there nice to meet you",
    "hey whats up how have you been",
    "good morning everyone",
    "good evening hope you had a great day",
    # Positive messages
    "you did a great job on that project",
    "i really appreciate your help",
    "thank you so much for everything",
    "you are an amazing person",
    "great work keep it up",
    "that was a wonderful presentation",
    "i am so proud of you",
    "you always make me smile",
    "your work is really impressive",
    "i love working with you",
    # Everyday conversation
    "what time is the meeting tomorrow",
    "can you send me the report",
    "lets grab lunch together",
    "did you watch the game last night",
    "the weather is really nice today",
    "i just finished reading that book",
    "do you want to go for a walk",
    "i am working on the assignment",
    "lets plan a trip this weekend",
    "the movie was really good",
    # Questions and discussions
    "what do you think about this idea",
    "how do we solve this problem",
    "can you explain this concept to me",
    "what is the best approach here",
    "do you have any suggestions",
    "i think we should try a different method",
    "lets discuss this in the meeting",
    "what are your thoughts on the proposal",
    "can we schedule a call for tomorrow",
    "i need some help with this task",
    # Professional messages
    "please find the attached document",
    "i have updated the spreadsheet",
    "the deadline is next friday",
    "we need to review the requirements",
    "the code review is complete",
    "i have pushed the changes to the repository",
    "the test cases are passing now",
    "lets deploy the update tomorrow",
    "the client meeting went well",
    "i have sent the invoice",
    # Neutral statements
    "i went to the store yesterday",
    "traffic was really bad this morning",
    "i need to buy some groceries",
    "the restaurant was quite busy",
    "i am learning a new programming language",
    "the library has some great resources",
    "i started a new hobby recently",
    "my phone battery is running low",
    "i need to fix the bug in the code",
    "the update is downloading now",
    # Opinions (non-toxic)
    "i disagree with that approach",
    "i think there is a better way to do this",
    "i am not sure about that decision",
    "that might not be the best option",
    "i have a different perspective on this",
    "i respectfully disagree",
    "we could improve this further",
    "this needs some more work",
    "i have some concerns about this plan",
    "lets consider other alternatives",
    # Emotional but non-toxic
    "i am feeling a bit stressed today",
    "this situation is really frustrating",
    "i am disappointed with the results",
    "its been a tough day",
    "i am worried about the deadline",
    "i feel overwhelmed with work",
    "this is challenging but we can do it",
    "i am nervous about the interview",
    "i had a rough morning",
    "things are not going as planned",
    # Everyday Words (Calibrators)
    "father", "mother", "brother", "sister", "family", "parents",
    "bye", "goodbye", "see you later", "catch you tomorrow",
    "the library is quiet", "i am reading a book", "nature is beautiful",
    "this is my favorite food", "i like to play football",
    "can you help me with this", "thank you for your support",
    "have a wonderful weekend", "it was nice talking to you",
]

# ══════════════════════════════════════════════════════════════
# Prepare dataset
# ══════════════════════════════════════════════════════════════
print("📊 Preparing training data...")

texts = toxic_samples + non_toxic_samples
labels = [1] * len(toxic_samples) + [0] * len(non_toxic_samples)

print(f"   Toxic samples:     {len(toxic_samples)}")
print(f"   Non-toxic samples: {len(non_toxic_samples)}")
print(f"   Total:             {len(texts)}")


# ══════════════════════════════════════════════════════════════
# Text cleaning
# ══════════════════════════════════════════════════════════════
def clean_text(text):
    text = text.lower()
    text = re.sub(r'http\S+|www\S+', '', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'[^a-z\s]', ' ', text)
    return ' '.join(text.split())


texts_cleaned = [clean_text(t) for t in texts]

# ══════════════════════════════════════════════════════════════
# Train/Test split
# ══════════════════════════════════════════════════════════════
X_train, X_test, y_train, y_test = train_test_split(
    texts_cleaned, labels, test_size=0.2, random_state=42, stratify=labels
)

print(f"\n📦 Train set: {len(X_train)} | Test set: {len(X_test)}")

# ══════════════════════════════════════════════════════════════
# TF-IDF Vectorization
# ══════════════════════════════════════════════════════════════
print("\n🔤 Building TF-IDF vectorizer...")
vectorizer = TfidfVectorizer(
    max_features=5000,
    ngram_range=(1, 2),     # unigrams + bigrams
    min_df=1,
    max_df=0.95,
    sublinear_tf=True
)

X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

print(f"   Vocabulary size: {len(vectorizer.vocabulary_)}")
print(f"   Feature matrix:  {X_train_tfidf.shape}")

# ══════════════════════════════════════════════════════════════
# Train Logistic Regression Model
# ══════════════════════════════════════════════════════════════
print("\n🧠 Training Logistic Regression model...")
model = LogisticRegression(
    C=1.0,
    max_iter=1000,
    solver='lbfgs',
    class_weight='balanced',
    random_state=42
)
model.fit(X_train_tfidf, y_train)

# ══════════════════════════════════════════════════════════════
# Evaluate
# ══════════════════════════════════════════════════════════════
y_pred = model.predict(X_test_tfidf)
accuracy = accuracy_score(y_test, y_pred)

print(f"\n📈 Results:")
print(f"   Accuracy: {accuracy:.2%}")
print(f"\n{classification_report(y_test, y_pred, target_names=['non-toxic', 'toxic'])}")

# ══════════════════════════════════════════════════════════════
# Save model files
# ══════════════════════════════════════════════════════════════
model_path = os.path.join(MODEL_DIR, "model.pkl")
tfidf_path = os.path.join(MODEL_DIR, "tfidf_vectorizer.pkl")

joblib.dump(model, model_path)
joblib.dump(vectorizer, tfidf_path)

print(f"✅ Model saved to:      {model_path}")
print(f"✅ Vectorizer saved to: {tfidf_path}")

# ══════════════════════════════════════════════════════════════
# Quick test predictions
# ══════════════════════════════════════════════════════════════
print("\n🧪 Quick test predictions:")
test_texts = [
    "you are so stupid and ugly",
    "hello how are you doing today",
    "i hate you so much you idiot",
    "lets go get coffee tomorrow",
    "you are a worthless pathetic loser",
    "great job on the presentation",
    "shut up you disgusting moron",
    "i appreciate your help thank you",
    "you are garbage and everyone hates you",
    "the weather is beautiful today",
]

for t in test_texts:
    cleaned = clean_text(t)
    features = vectorizer.transform([cleaned])
    proba = model.predict_proba(features)[0]
    score = proba[1]
    label = "🔴 TOXIC" if score >= 0.5 else "🟢 SAFE"
    flagged = "⚠️ FLAGGED" if score >= 0.7 else ""
    print(f"   {label} ({score:.2%}) {flagged:10s} → \"{t}\"")

print("\n🎉 Done! Restart the backend to load the new model.")
print("   Run: python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload")
