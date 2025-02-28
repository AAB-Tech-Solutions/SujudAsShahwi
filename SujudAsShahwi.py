# -*- coding: utf-8 -*-

import re
import unicodedata
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fuzzywuzzy import process
from flask import Flask, request, jsonify, render_template
from waitress import serve


class SujudAsShahwi:
    def __init__(self):
        self.corrections = {
            "missed sujud": "Sit, perform the missed sujud, then do Sujud Ba’Adiyya.",
            "missed ruku": "Stand up, perform ruku, then do Sujud Ba’Adiyya.",
            "extra rakaah": "Perform Sujud Ba’Adiyya after completing the prayer.",
            "doubting rakaat": "Assume the lower number, complete prayer, then do Sujud Qabliyya.",
        }
        
        self.keyword_to_mistake = {word: mistake for mistake in self.corrections for words in mistake.split() for word in words.split()}
        
        self.keywords = {
            "sujud": ["sujud", "sajda"],
            "ruku": ["ruku"],
            "rakaah": ["rakaah", "rakah", "rakats"],
            "qabliyya": ["qabliyya"],
            "baadiyya": ["baadiyya"],
        }
        
        self.vectorizer = TfidfVectorizer()
    
        self.rules = {
            "When to Perform Sujood As-Sahw": {
                "Before Salam (Qabli)": [
                    "Forgetting a wajib (necessary act), such as a Rukū or sujūd.",
                    "Being unsure whether you prayed three or four raka’āt. Assume the lower number and complete the prayer, then perform Sujud Qabla Asalam (Sujud before Salam)."
                ],
                "After Salam (Ba’Adiyya)": [
                    "Praying five raka’āt in a four-raka’āt prayer.",
                    "Reciting aloud in a prayer that should be silent (e.g., Dhuhr).",
                    "Making an extra rukū‘ or sujūd."
                ],
                "If Both Addition & Omission Occur": [
                    "If both omit and add something, the omission takes priority, so you do Qabli before salam."
                ]
            },
            "When Sujood As-Sahw Expires": [
                "If a long time has passed (e.g., you left the mosque), you cannot perform Qabli anymore.",
                "Ba’Adiyya can still be done, even after a delay.",
                "If major mistakes accumulate (e.g., multiple pillars are missed), the prayer may become invalid and must be repeated."
            ],
            "Following the Imam in Forgetfulness": [
                "Imam forgets something: Follower says SubhanAllāh.",
                "Imam rises after 2 raka’āt instead of sitting: If his hands are lifted, stand with him; otherwise, remain sitting.",
                "Imam adds a raka’ah mistakenly: Only follow if unsure; if certain it’s extra, remain sitting.",
                "Imam makes salam early: Say SubhanAllāh to signal him; if he corrects, do Ba’Adiyya.",
                "Imam doubts his prayer: He may ask two trustworthy people, and speaking is allowed.",
                "Follower joins late: Follow Imam’s Qabli prostration but delay Ba’Adiyya until completing the prayer."
            ],
            "Correcting Missed Actions": {
                "Forgetting Rukū‘ and remembering in Sujūd": "Stand up, recite Qur’an, then bow.",
                "Forgetting Sujūd and remembering after standing": "Sit, perform Sujūd, then Ba’Adiyya.",
                "Standing up instead of sitting after 2 raka’āt": "If hands still near ground, return to sitting; otherwise, continue & do Qabli.",
                "Forgetting Rukū‘ or Sujūd and remembering after a long time": "In obligatory prayer, repeat the whole prayer; in optional prayer, do nothing."
            },
            "Forgetfulness in Shaf’ and Witr": [
                "In Shaf’, if you forget something, prostrate after salām, then perform Witr as usual.",
                "Speaking between Shaf’ and Witr is disliked but does not require Sujood.",
                "If you miss a raka’ah with the Imam in Witr, do not prostrate with him unless you caught at least one raka’ah.",
                "If you forget Qabli, revert to general Sujood rules."
            ],
            "More Rules on Forgetfulness": [
                "If a person sighs but does not speak, nothing is owed. However, speaking intentionally invalidates the prayer.",
                "If the Imam makes an obvious mistake, a follower may correct him verbally by saying SubhanAllāh.",
                "If a person misses Sujood As-Sahw but remembers quickly, they can perform it immediately.",
                "If a mistake occurs in Jama’ah (congregation), someone should step forward to replace the Imam if necessary."
            ],
            "Conclusion": [
                "These rules ensure that minor mistakes do not invalidate the prayer but are corrected in a proper way.",
                "The rulings are based on the principles of ease and correction in worship.",
                "As long as a person tries their best, their prayer is accepted by Allah’s mercy.",
                "All praise belongs to Allah, the Exalted, the Most Apparent, the Most Hidden, the First and the Last."
            ]
        } 
    def display_rules(self):
        """This function properly prints the rules of Sujood As-Sahw."""
        print("\n📜 **Rules of Sujood As-Shahwi:**")
        for section, content in self.rules.items():
            print("\n➡ {}:".format(section))  # Main section title


            if isinstance(content, dict):
                for sub_section, details in content.items():
                    print("\n🔹 {}:".format(sub_section))  # Sub-section title


                    if isinstance(details, list):  # Ensure lists print correctly
                        for item in details:
                           print("   - {}".format(item))  # Bullet point for each rule

            else:  # Ensure string values print properly
                   print("- {}".format(details))
    
    def view_all_rules(self):
        """This function returns all the rules of Sujood As-Sahw."""
        return self.rules

    def search_mistake(self, user_input):
        if not user_input.strip():
            return "Invalid input. Please enter a prayer mistake."
        
        user_input = self.preprocess_text(user_input)
        keywords_in_input = self.extract_keywords(user_input)
        
        if not keywords_in_input:
            return "No relevant keywords found in your input."
        
        for keyword in keywords_in_input:
            if keyword in self.keyword_to_mistake:
                mistake = self.keyword_to_mistake[keyword]
                return "Mistake: {}\nCorrection: {}".format(mistake, self.corrections[mistake])
        
        best_match = None
        best_score = 0
        
        mistake_texts = list(self.corrections.keys())
        tfidf_matrix = self.vectorizer.fit_transform(mistake_texts + [user_input])
        similarity_scores = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1]).flatten()
        
        for idx, score in enumerate(similarity_scores):
            if score > best_score:
                best_score = score
                best_match = mistake_texts[idx]
        
        if best_match and best_score > 0.3:
            return "Mistake: {}\nCorrection: {}".format(best_match, self.corrections[best_match])
        else:
            return "No specific correction found for this mistake type."

    def get_correction(self, mistake_type):
        # General corrections for common mistakes
        corrections = {

            "missed sujud": "Sit, perform the missed sujud, then do Sujud Ba’Adiyya.",
            "missed ruku": "Stand up, perform ruku, then do Sujud Ba’Adiyya.",
            "extra rakaah": "Perform Sujud Ba’Adiyya after completing the prayer.",
            "doubting rakaat": "Assume the lower number, complete prayer, then do Sujud Qabliyya.",
            "doubting whether you prayed 3 or 4 raka’āt": "Assume the lowest number i.e 3 and completing the 4th, then do sujud after salam (Sujud Qabliyya).",
            "adding an extra raka’ah": "Perform sujud before salam (sujud ba'adiyya).",
            "saying salam before completing the prayer": "Complete what ever you're missing , then perform sujud before salam (Sujud Ba'adiyya).",
            "missing a rukū‘ and remembering while in sujūd": "Stand up, perform the missed rukū‘, and do sujud before salam (sujud ba'adiyya).",
            "forgetting a sujūd and remembering after standing": "Sit back down, do the sujūd, and do sujud before salam (sujud ba'adiyya).",
            "missed 1 sujud": "Sit, perform the missed sujūd, then complete the prayer with Sujud Ba'Adiyya.",
            "missed a sujud": "Sit, perform the missed sujūd, then complete the prayer with Sujud Ba'Adiyya.",
            "forget 1 sujud": "Sit, perform the missed sujūd, then complete the prayer with Sujud Ba'Adiyya.",
            "forgetting sujud": "Sit, perform the missed sujūd, then complete the prayer with Sujud Ba'Adiyya.",
            "extra rukū‘": "Perform Sujud Ba'Adiyya after completing the prayer.",
            "added extra raka’ah": "Perform Sujud Ba'Adiyya after completing the prayer.",
            "unsure about raka’at": "Assume the lower number and complete the prayer, then do Sujud Qabliyya.",
            "missing rukū‘": "If you remember in sujūd, stand up, perform rukū‘, and then complete the prayer with Sujud Ba'Adiyya.",
            "forgot to do Sujud or Sajdas": "Perform 2 sajdas after salam (Sujud Qabliyya) after completing your prayer.",
            "did extra sajdas": "Perform sajda before salam (Sujud Ba'Adiyya) for the extra sajda.",
            "saying salam too early": "Complete the prayer and perform a sajda after salam (Sujud Qabliyya).",
            "doubting if I did 2 or 3 sajdas": "Assume the lower number; perform a sajda after salam (Sujud Qabliyya) if necessary.",
            "forgetting qunūt": "No sajdahs required, but avoid doing it intentionally.",
            "missing rukū‘": "If remembered in sujūd, return to rukū‘, then perform sajda after salam (sujud qabliyya).",
            "adding extra raka’ah": "Perform a sajda after salam (sujud qabliyya) after the prayer.",
            "doubting after making salam": "If far from the masjid, the salāh is invalid.",
            "forgetting to perform the sajdas after an omission": "Perform 2 sajdas after salam (sujud qabliyya) after completing your prayer.",
            "adding an extra sajda": "Perform sajda before salam (sujud ba'adiyya) for the extra sajda.",
            "saying salam before completing prayer": "Complete your prayer, then perform a sajda after salam (sujud qabliyya) for the early salam.",
            "forgetting a rukū‘ while in sujūd": "Stand up, perform the missed rukū‘, and do sajda after salam (sujud qabliyya).",
            "forgetting a sujūd after standing": "Sit back down, do the sujūd, and then perform sajda after salam (sujud qabliyya).",
            "forgetting to recite silently after speaking": "Do a sajda after salam (sujud qabliyya) since it’s a forgetfulness.",
            "forgetting a sunnah act more than three times": "Your obligatory prayer becomes invalid.",
            "forgetting to recite a Surah in the last two raka’āt": "You do not owe anything.",
            "laughing during prayer": "Laughter invalidates the prayer; restart your prayer.",
            "unsure if in Witr": "Consider it the second raka’ah of Shaf‘ and prostrate after salam (sujud qabliyya).",
            "forgetting to recite Fātiḥa": "Repeat Fātiḥa and perform a sajda after salam (sujud qabliyya) for forgetfulness.",
            "accidentally adding extra raka’āt": "Perform a sajda after salam (sujud qabliyya) after completing the prayer.",
            "not catching a raka’ah": "If you do not catch a raka’ah, you cannot prostrate with the Imam, and your salāh becomes invalid.",
            "forgetting to perform sujud after catching a raka’ah": "You revert back to the basic rules of prostrations of forgetfulness and perform a sujud after salam (sujud qabliyya).",
            "owing both sujuds": "If you owe both sujud qabliyya and sujud ba'adiyya, a sujud qabliyya suffices; just prostrate before salam.",
            "forgetting a rukū‘ and remembering in sujūd": "Return to standing, recite a bit of Qur’ān, and proceed to bow.",
            "remembering a sajdah after standing": "If you haven't sat yet, return to sitting and perform a sujud after salam (sujud qabliyya).",
            "remembering a rukū‘ after rising": "Proceed with your salāh and add a raka’ah later, prostrating after salam (sujud qabliyya).",
            "invalidating salāh due to mistakes": "Repeat the whole prayer if multiple mistakes occur; if unsure, proceed with the prayer."
            "missed 1 sujud': 'You should sit, perform the missed sujud, then do Ba’Adiyya.",
            
            # Intention (Niyyah)
            "forgot to make intention": "Your Salah is invalid; you must restart with the correct intention.",
            "made intention for wrong prayer": "If you realize before Takbir, change your intention. If after, restart the prayer.",
            "doubt in intention after starting": "If strong doubt arises, restart the prayer; otherwise, continue.",
            
            # Takbir (Allahu Akbar)
            "forgot to say Takbiratul Ihram": "Your prayer has not started; restart the Salah properly.",
            "mispronounced Takbir": "If unintentional, continue; if intentional and changes meaning, restart.",
            "delayed Takbir": "Takbir must precede movements; if delayed significantly, restart Salah.",
            
            # Surah Al-Fatiha
            "forgot to recite Al-Fatiha": "Recite it immediately if still in the same raka'ah. If remembered after Ruku’, restart the Salah.",
            "mispronounced Al-Fatiha": "If it changes meaning, restart Salah; if minor, continue.",
            "revert cannot recite Al-Fatiha": "Recite what you can, read from a book, or say 'SubhanAllah' in place.",
            "forgot a verse in Al-Fatiha": "Recite the missing verse if in the same raka'ah; if skipped completely, restart Salah.",
            "recited Fatiha incorrectly but realized later": "If meaning is changed, redo the prayer; otherwise, continue.",
            
            # Surah after Al-Fatiha
            "forgot to recite a Surah after Al-Fatiha": "It is Sunnah; no need for Sujud Sahw.",
            "recited Surah before Al-Fatiha": "Prayer is invalid; restart the Salah.",
            "skipped Surah in first raka'ah but recited in second": "No Sujud Sahw required, continue prayer.",
            
            # Ruku' (Bowing)
            "missed Ruku' and remembered in Sujood": "Stand up, perform Ruku', and redo Sujood, then do Sujud Sahw.",
            "did extra Ruku'": "Perform Sujud Ba'Adiyya after completing the prayer.",
            
            # Sujood (Prostration)
            "missed one Sujood": "Sit and perform the missed Sujood, then do Sujud Ba'Adiyya.",
            "missed both Sujoods": "Prayer is invalid; restart Salah.",
            "did extra Sujood": "Perform Sujud Ba'Adiyya after completing the prayer.",
            
            # Tashahhud (Sitting)
            "forgot Tashahhud in the middle": "No need for Sujud Sahw; continue prayer.",
            "forgot final Tashahhud": "Prayer is incomplete; if not much time has passed, return and complete it, then do Sujud Sahw.",
            
            # Salam (Ending the Prayer)
            "said Salam before completing the prayer": "Complete the prayer and do Sujud Ba'Adiyya.",
            "forgot to say Salam": "Your Salah is incomplete; say Salam immediately.",
            
            # Doubt in Raka'at
            "doubting whether prayed 3 or 4 raka’āt": "Assume the lower number and complete the prayer, then do Sujud Sahw.",
            "added an extra raka’ah": "Perform Sujud Ba'Adiyya after completing the prayer.",
            "unsure about the number of Sajdah": "Assume the lower number and perform Sujud Sahw.",
            
            # Other Mistakes
            "laughed during prayer": "Salah is invalid; restart.",
            "spoke unintentionally": "Continue Salah, no Sujud Sahw required unless it was a full sentence.",
            "spoke intentionally": "Salah is invalid; restart.",
            "ate or drank during prayer": "Prayer is invalid; restart.",
            "prayed in the wrong direction (Qibla)": "If realized during Salah, correct immediately. If after, Salah is valid if mistaken unintentionally.",
            "performed prayer with unclean clothes": "Salah is invalid; redo it after purification.",
            
            # Witr & Special Prayers
            "forgot Qunoot in Witr": "No Sujud Sahw required.",
            "unsure if in Witr or another prayer": "Continue Salah and perform Sujud Sahw.",
            
            # Catching Up with Imam
            "missed first raka'ah with the Imam": "Join and make up for missed raka'ah after the Imam’s Salam.",
            "missed entire Ruku' with the Imam": "Raka'ah is not counted; you must add one after the Imam finishes.",
            
            # Sujud Shahwi (Forgetfulness Prostration)
            "missed Sujud Shahwi": "If time hasn’t passed, perform it immediately. If too late, no need to redo Salah.",
            "owing both Sujud Qabliyyah and Ba'Adiyya": "Perform only Sujud Qabliyyah before Salam."



        
        }
       
             
        
    
        self.keyword_to_mistake = {word: mistake for mistake in self.corrections for words in mistake.split() for word in words.split()}
        
        
        self.keywords = {
            "sujud": ["sujud", "sajda"],
            "ruku": ["ruku"],
            "rakaah": ["rakaah", "rakah", "rakats"],
            "qabliyya": ["qabliyya"],
            "baadiyya": ["baadiyya"],
        }
        
        self.vectorizer = TfidfVectorizer()
        
    
    def preprocess_text(self, text):
        # Add your text preprocessing logic here
        return text.strip().lower()

    def extract_keywords(self, text):
        matched_keywords = set()
        for category, words in self.keywords.items():
            for word in words:
                if word in text:
                    matched_keywords.add(category)
        return list(matched_keywords)

def preprocess_text(self, text):
        text = text.lower()
        text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
        text = re.sub(r'[^a-zA-Z0-9 ]', '', text)
        return text
    
def extract_keywords(self, text):
        matched_keywords = set()
        for category, words in self.keywords.items():
            for word in words:
                if word in text:
                    matched_keywords.add(category)
        return list(matched_keywords)
    
def search_mistake(self, user_input):
        if not user_input.strip():
            return "Invalid input. Please enter a prayer mistake."
        
        user_input = self.preprocess_text(user_input)
        keywords_in_input = self.extract_keywords(user_input)
        
        if not keywords_in_input:
            return "No relevant keywords found in your input."
        
        for keyword in keywords_in_input:
            if keyword in self.keyword_to_mistake:
                mistake = self.keyword_to_mistake[keyword]
                return "Mistake: {}\nCorrection: {}".format(mistake, self.corrections[mistake])
        
        best_match = None
        best_score = 0
        
        mistake_texts = list(self.corrections.keys())
        tfidf_matrix = self.vectorizer.fit_transform(mistake_texts + [user_input])
        similarity_scores = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1]).flatten()
        
        for idx, score in enumerate(similarity_scores):
            if score > best_score:
                best_score = score
                best_match = mistake_texts[idx]
        
        if best_match and best_score > 0.3:
            return "Mistake: {}\nCorrection: {}".format(best_match, self.corrections[best_match])
        else:
            return "No specific correction found for this mistake type."

"""def main_menu():
    sujood = SujudAsShahwi()

    wprint("\n📌 **Sujud As-Shahwi Helper**")
        print("1. View All Rules")
        print("2. Search for a Mistake")
        print("3. Exit")

        choice = input("Enter your choice (1/2/3): ").strip()

        if choice == "1":
            sujood.display_rules()  # ✅ Calls the new method correctly
        elif choice == "2":
            user_query = input("\nEnter your prayer mistake: ").strip()
            result = sujood.search_mistake(user_query)
            print(result)
        elif choice == "3":
hile True:
print("\n📌 **Sujud As-Shahwi Helper**")
        print("1. View All Rules")
        print("2. Search for a Mistake")
        print("3. Exit")

        choice = input("Enter your choice (1/2/3): ").strip()

        if choice == "1":
            sujood.display_rules()  # ✅ Calls the new method correctly
        elif choice == "2":
            user_query = input("\nEnter your prayer mistake: ").strip()
            result = sujood.search_mistake(user_query)
            print(result)
        elif choice == "3":
            print("\nGoodbye! May Allah accept your prayers. 🤲")
            break
        else:
            print("⚠ Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main_menu() """


# Initialize Flask
app = Flask(__name__)  
app.config['DEBUG'] = True
app.config['TEMPLATES_AUTO_RELOAD'] = False  # Disable auto-reload for templates
sujood_helper = SujudAsShahwi()  # Initialize helper

# Home Page
@app.route('/')
def home():
    return render_template("index.html")

# View Rules
@app.route('/rules')
def rules():
    return jsonify(sujood_helper.rules)

# Search for a mistake
@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    user_input = data.get("mistake", "")
    result = sujood_helper.search_mistake(user_input)
    return jsonify({"correction": result})

@app.route('/healthz')
def health_check():
    return 'Healthy', 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)  # Disable the use of the reloader` 




