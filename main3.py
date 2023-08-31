from tkinter import *
from PIL import ImageTk, Image
import pyttsx3 as pt
import speech_recognition as sr
import threading
import re
import numpy as np
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
# from pymongo import MongoClient
# import spacy

engine = pt.init()

voices = engine.getProperty('voices')
print(voices)

# engine.setProperty('voice', voices[0].id)  # for male
engine.setProperty('voice', voices[1].id)  # for female


def speak(word):
    engine.say(word)
    engine.runAndWait()


def scroll_to_end():
    msg.see(END)


def remove_punctuation(sentence):
    # Use regex to remove punctuation
    return re.sub(r'[^\w\s]', '', sentence)


main = Tk()
main.geometry("350x575")
main.title("P's Recipe Bot")


def talk_to_bot():
    s = sr.Recognizer()
    with sr.Microphone() as mic:
        print("I am listening....")
        audio = s.listen(mic)
        try:
            query = s.recognize_google(audio, language="en")
            print(query)
            entry.delete(0, END)
            entry.insert(0, query)
            ask_from_bot()
        except Exception as e:
            print(e)
            print("Unrecognized")


with open("convo.json", "r") as file:
    data = json.load(file)

# Extract the questions and replies from the JSON data
questions = [item["msg"] for item in data]

# Flatten the questions list
questions_flat = [msg for sublist in questions for msg in sublist]


def ask_from_bot():
    text1 = entry.get()
    target_question = remove_punctuation(text1).lower()
    msg.insert(END, "You:  " + text1 + "\n", "custom_tag")
    entry.delete(0, END)

    vectorizer = TfidfVectorizer()
    question_vectors = vectorizer.fit_transform(questions_flat + [target_question])

    # Calculate TF-IDF vector for the user input
    user_question_vector = vectorizer.transform([target_question])

    # Calculate cosine similarity between user input and each candidate question
    similarity_scores = cosine_similarity(user_question_vector, question_vectors[:-1])

    print(similarity_scores)

    # Find the index of the most similar question
    most_similar_index = np.argmax(similarity_scores)

    print(similarity_scores[0][most_similar_index])
    # Check if the similarity score is greater than 0.75
    if similarity_scores[0][most_similar_index] > 0.5:
        # Retrieve the most similar question and its corresponding reply
        most_similar_question = questions_flat[most_similar_index]

        # Find the corresponding reply from the JSON data based on the most similar question
        target_reply = None
        for item in data:
            if most_similar_question in item["msg"]:
                target_reply = item["reply"]
                break

        # If a relevant reply is found, display it
        if target_reply:
            msg.insert(END, "Bot :  " + target_reply + "\n")
            # speak(target_reply)
        # speak(target_reply)
    else:
        string = "Sorry, could not understand"
        msg.insert(END, "Bot: " + string + "\n")
        speak(string)

    entry.delete(0, END)
    msg.yview(END)
    scroll_to_end()


# GUI
main.configure(bg="#F98B88")

image_path = "bot2.png.png"
image = Image.open(image_path)
photo = ImageTk.PhotoImage(image)

# Display the image and text using a Label
label = Label(main, image=photo)
label.pack(pady=5)
label = Label(main, text="Want yummy recipes? Ask me!", fg="red")
label.pack(pady=5)

frame = Frame(main, bg="#F4C2C2")

msg = Text(frame, width=80, height=20, font=("Helvetica", 11), fg="#11009E", bg="#C5DFF8")

sc = Scrollbar(frame, command=msg.yview)

sc.pack(side=RIGHT, fill=Y)

msg.configure(yscrollcommand=sc.set)
msg.tag_config("custom_tag", foreground="#EF6262")
msg.pack(side=LEFT, fill=BOTH, pady=10, padx=10)

frame.pack(pady=10)

entry = Entry(main, font=("Verdana", 15))
entry.pack(fill=X, pady=10)

btn = Button(main, text="Enter", font=("Helvetica", 20), bg="#43C6DB", fg="black", command=ask_from_bot)
btn.pack()


# for triggering the enter command
def enter_func(event):
    btn.invoke()


main.bind('<Return>', enter_func)


def rep():
    while True:
        talk_to_bot()


t = threading.Thread(target=rep)
t.start()

main.mainloop()
