import tkinter as tk
from tkinter import ttk
from tkinter import LEFT, BOTH, SUNKEN
import datetime
import os
import webbrowser
import pyttsx3
import speech_recognition as sr
import wikipedia
import pywhatkit as kit
import requests
from PIL import Image, ImageTk
from threading import Thread
import sqlite3
import shutil
from ecapture import ecapture as ec
import subprocess
import time
import wolframalpha


# Constants for custom styling
BG_COLOR = "#D2C6E2"
BUTTON_COLOR = "#F9F4F2"
BUTTON_FONT = ("Arial", 14, "bold")
BUTTON_FOREGROUND = "black"
HEADING_FONT = ("Helvetica", 24, "bold")
INSTRUCTION_FONT = ("Helvetica", 14)

engine = pyttsx3.init("sapi5")
voices = engine.getProperty("voices")
engine.setProperty("voice", "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0")



def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
      
    except sqlite3.Error as e:
        print(e)
    return conn


def create_table(conn):
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS commands (
            id INTEGER PRIMARY KEY,
            command TEXT NOT NULL,
            response_id INTEGER,
            FOREIGN KEY (response_id) REFERENCES responses(id)
        )
        """
    )
    conn.commit()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY,
            response TEXT NOT NULL
        )
        """
    )
    conn.commit()

# Define the function to insert a command-response pair into the database
def insert_command(conn, command, response):
    cursor = conn.cursor()
    
    # Insert the response into the responses table
    cursor.execute("INSERT INTO responses(response) VALUES (?)", (response,))
    response_id = cursor.lastrowid
    
    # Insert the command and associate it with the response_id
    cursor.execute("INSERT INTO commands(command, response_id) VALUES (?, ?)", (command, response_id))
    
    conn.commit()


def speak(audio):
    engine.say(audio)
    engine.runAndWait()


# entry = None
# stop_flag = False  # Define the stop_flag variable at the top of the script


def wish_time():
    global entry
    x = entry.get()
    hour = datetime.datetime.now().hour
    if 0 <= hour < 6:
        speak("Good night! Sleep tight.")
    elif 6 <= hour < 12:
        speak("Good morning!")
    elif 12 <= hour < 18:
        speak("Good afternoon!")
    else:
        speak("Good evening!")
        
    speak(f"{x} How can I help you?")

def play_song(query):
    if "play" in query:
        song = query.replace(
            "play", ""
        ).strip()  # Remove 'play' and any leading/trailing whitespace
        try:
            print("Playing " + song)
            kit.playonyt(song)
        except Exception as e:
            print("Error:", e)
            print("Couldn't play the song.")


def open_application(application_path):
    try:
        subprocess.Popen(application_path)
        print(f"Successfully opened {application_path}")
    except FileNotFoundError:
        print(f"Error: Application '{application_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def take_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        speak("Say something")
        print("Say Something")
        speak("G-one is Listening...")
        print("Listening...")
        r.adjust_for_ambient_noise(source)

        audio = r.listen(source)

        try:
            query = r.recognize_google(audio, language='en-in')
            print(f"user said:{query}\n")

        except Exception :
            speak("Pardon me, please say that again")
            return ""
        return query


def search_file():
    speak("What file are you looking for?")
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        query = recognizer.recognize_google(audio).lower()
        print("You said:", query)
        speak("Searching for " + query)

        # Search for the file
        results = []
        for root, dirs, files in os.walk("C:\\"):
            for file in files:
                if query in file.lower():
                    results.append(os.path.join(root, file))

        if results:
            speak("I found the following files:")
            for idx, result in enumerate(results):
                print(f"{idx + 1}. {result}")
                speak(f"{idx + 1}. {result}")
        else:
            speak("Sorry, I couldn't find any matching files.")

    except sr.UnknownValueError:
        print("Sorry, I could not understand your voice.")
        speak("Sorry, I could not understand your voice.")
    except sr.RequestError as e:
        print(
            "Could not request results from Google Speech Recognition service; {0}".format(
                e
            )
        )
        speak("Could not request results from Google Speech Recognition service.")


def recognize_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for command...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio).lower()
        print("Command recognized:", command)
        return command
    except sr.UnknownValueError:
        print("Sorry, I couldn't understand that.")
        return None
    except sr.RequestError as e:
        print("Could not request results; {0}".format(e))
        return None


# Function to perform file copy based on command
def copy_file():
    speak("Please say the name of the file to copy.")
    file_to_copy = recognize_command()
    if file_to_copy:
        speak("Please say the destination folder.")
        destination = recognize_command()
        if destination:
            try:
                shutil.copy(file_to_copy, destination)
                speak("File copied successfully.")
            except FileNotFoundError:
                speak("File not found.")


# Function to perform file rename based on command
def rename_file():
    speak("Please say the name of the file to rename.")
    file_to_rename = recognize_command()
    if file_to_rename:
        speak("Please say the new name for the file.")
        new_name = recognize_command()
        if new_name:
            try:
                os.rename(file_to_rename, new_name)
                speak("File renamed successfully.")
            except FileNotFoundError:
                speak("File not found.")


# Function to perform file paste based on command
def paste_file():
    speak("Please say the name of the source file.")
    source = recognize_command()
    if source:
        speak("Please say the destination folder.")
        destination = recognize_command()
        if destination:
            try:
                shutil.move(source, destination)
                speak("File pasted successfully.")
            except FileNotFoundError:
                speak("File not found.")


# Function to perform file delete based on command
def delete_file():
    speak("Please say the name of the file to delete.")
    file_to_delete = recognize_command()
    if file_to_delete:
        try:
            os.remove(file_to_delete)
            speak("File deleted successfully.")
        except FileNotFoundError:
            speak("File not found.")


# Main function to listen for commands and perform file operations
def main():
    speak("Listening for command.")
    while True:
        command = recognize_command()
        if command:
            if "exit" in command:
                speak("Exiting program.")
                break
            elif "copy" in command:
                copy_file()
            elif "rename" in command:
                rename_file()
            elif "m o v e" in command:
                paste_file()
            elif "delete" in command:
                delete_file()
            else:
                speak("Command not recognized.")


def note(text):
    date = datetime.datetime.now()
    file_name = str(date).replace(":", "-") + "-note.txt"
    with open(file_name, "w") as f:
        f.write(text)

    subprocess.Popen(["notepad.exe", file_name])



def perform_task():
    conn = create_connection("assistant.db")
    create_table(conn)
    
    while True:
        query = take_command().lower()  # Converting user query into lower case
        if "wikipedia" in query:
            speak("Searching Wikipedia...")
            query = query.replace("wikipedia", "")
            try:
                results = wikipedia.summary(query, sentences=2)
                speak("According to Wikipedia")
                print(results)
                speak(results)
                insert_command(
                    conn, query, results
                )  # Insert command-response pair into the database

            except wikipedia.exceptions.DisambiguationError:
                # Handle disambiguation error (when the search term has multiple possible meanings)
                print(
                    f"There are multiple meanings for '{query}'. Please be more specific."
                )
                speak(
                    f"There are multiple meanings for '{query}'. Please be more specific."
                )
            except wikipedia.exceptions.PageError:
                # Handle page not found error (when the search term does not match any Wikipedia page)
                print(f"'{query}' does not match any Wikipedia page. Please try again.")
                speak(f"'{query}' does not match any Wikipedia page. Please try again.")
        elif "play" in query:
            song = query.replace("play", "")
            speak("Playing " + song)
            kit.playonyt(song)
        elif "open prime video" in query:
            webbrowser.open_new_tab("primevideo.com")
            speak("Amazon Prime Video open now")
            insert_command(conn, query, "Amazon prime video opened")

            time.sleep(5)

        elif "open netflix" in query:
            webbrowser.open_new_tab("netflix.com/browse")
            speak("Netflix open now")
            insert_command(
                conn, query, "Netlifx opened"
            )  # Insert command-response pair into the database

        elif "make a note" in query:
            query = query.replace("make a note", "")
            note(query)
            insert_command(
                conn, query, "Note Made Sucesfully"
            )  # Insert command-response pair into the database

        elif "note this" in query:
            query = query.replace("note this", "")
            note(query)
            speak(results)

        elif "open valorant" in query:
            application_path = r"C:\\Riot Games\\Riot Client\\RiotClientServices.exe"
            open_application(application_path)
        elif "open youtube" in query:
            webbrowser.open_new_tab("https://www.youtube.com")
            speak("youtube is open now")
            insert_command(
                conn, query, "Youtube opened"
            )  # Insert command-response pair into the database

            time.sleep(5)

        elif "open google" in query:
            webbrowser.open_new_tab("https://www.google.com")
            speak("Google chrome is open now")
            insert_command(conn, query, "Google chrome opened")
            time.sleep(5)

        elif "open gmail" in query:
            webbrowser.open_new_tab("gmail.com")
            speak("Google Mail open now")
            insert_command(conn, query, "Gmail open sucessfully")
            time.sleep(5)

        elif "search" in query:
            query = query.replace("search", "")
            webbrowser.open_new_tab(query)
            insert_command(conn, query, f"Search '{query}' is successful.")

        elif "the time" in query:
            str_time = datetime.datetime.now().strftime("%H:%M:%S")
            speak(f"Sir, the time is {str_time}")

        elif "open code" in query:
            code_path = (
                "C:\\Users\\DELL\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe"
            )
            os.startfile(code_path)

       

        elif "news" in query:
            webbrowser.open_new_tab(
                "https://timesofindia.indiatimes.com/home/headlines"
            )
            speak("Here are some headlines from the Times of India,Happy reading")
            insert_command(conn, query, "News sucessffully opened")

            time.sleep(6)

        elif "camera" in query or "take a photo" in query:
            try:
                ec.capture(0, "robo camera", "img.jpg")
                speak("Photo captured successfully.")
            except Exception as e:
                print("An error occurred while capturing the photo:", str(e))
                speak("Sorry, I encountered an error while capturing the photo.")

        elif "ask" in query:
            speak(
                "I can answer to computational and geographical questions and what question do you want to ask now"
            )
            question = take_command()
            # app_id = "R2K75H-7ELALHR35X"
            client = wolframalpha.Client("R2K75H-7ELALHR35X")
            res = client.query(question)
            answer = next(res.results).text
            speak(answer)
            print(answer)

        elif "weather" in query:
            api_key = "8ef61edcf1c576d65d836254e11ea420"
            base_url = "https://api.openweathermap.org/data/2.5/weather?"
            speak("whats the city name")
            city_name = take_command()
            complete_url = base_url + "appid=" + api_key + "&q=" + city_name
            response = requests.get(complete_url)
            x = response.json()
            if x["cod"] != "404":
                y = x["main"]
                current_temperature = y["temp"]
                current_humidity = y["humidity"]
                z = x["weather"]
                weather_description = z[0]["description"]
                speak(
                    " Temperature in kelvin unit is "
                    + str(current_temperature)
                    + "\n humidity in percentage is "
                    + str(current_humidity)
                    + "\n description  "
                    + str(weather_description)
                )
                print(
                    " Temperature in kelvin unit = "
                    + str(current_temperature)
                    + "\n humidity (in percentage) = "
                    + str(current_humidity)
                    + "\n description = "
                    + str(weather_description)
                )
            else:
                speak(" City Not Found ")

        elif "time" in query:
            strTime = datetime.datetime.now().strftime("%H:%M:%S")
            speak(f"the time is {strTime}")

        elif "who are you" in query or "what can you do" in query:
            speak(
                "I am G-one version 1 point O your persoanl assistant. I am programmed to minor tasks like"
                "opening youtube,google chrome,gmail and stackoverflow ,predict time,take a photo,search wikipedia,predict weather"
                "in different cities , get top headline news from times of india and you can ask me computational or geographical questions too!"
            )

        elif (
            "who made you" in query
            or "who created you" in query
            or "who discovered you" in query
        ):
            speak("I was built by Zuhair khan")
            print("I was built by Zuahir khan")

        elif "open stackoverflow" in query:
            webbrowser.open_new_tab("https://stackoverflow.com/login")
            speak("Here is stackoverflow")

        elif "where is" in query:
            query = query.replace("where is", "")
            location = query
            speak("User asked to Locate")
            speak(location)
            webbrowser.open(
                "https://www.google.nl/maps/place/" + location.replace(" ", "+")
            )

        elif "log off" in query or "sign out" in query:
            speak(
                "Ok , your pc will log off in 10 sec make sure you exit from all applications"
            )
            subprocess.call(["shutdown", "/l"])

        elif "exit" in query:
            speak("thanks for giving your time")
            stop_voice_assistant()
            break
    conn.close()


def start_voice_assistant():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
        wish_time()
        perform_task()



def stop_voice_assistant():
    speak("Stopping the Voice Assistant.")


tasks = [
    "Task Performed By G-one",
    "Provide general assistance and perform various other tasks based on user queries",
    "Recognize and greet users based on their input",
    "Who Are You",
    "Who Made You",
    "Search Wikipedia",
    "Open YouTube",
    "Open Prime Video",
    "Open notepad",
    "open Netflix",
    "Open Google",
    "Check Weather",
    "Open Valorant",
    "Open Gmail",
    "Search",
    "Get the Time" "Read News",
    "Take a Photo",
    "Ask Question",
    "Check Weather",
    "Get the current time",
    "Open Stack Overflow",
    "Open Google to locate a place",
    "Log off",
    "sign out",
    "Copy, rename, move, or delete files based on voice commands",
]

def perform_selected_task(selected_task):
    conn = create_connection("assistant.db")
    create_table(conn)
    
    if selected_task == "Search Wikipedia":
        speak("What would you like to search on Wikipedia?")
        query = take_command().lower()  # Capture user's query
        try:
            results = wikipedia.summary(query, sentences=2)
            speak("According to Wikipedia")
            print(results)
            speak(results)
            insert_command(conn, query, results)  # Insert command-response pair into the database
        except wikipedia.exceptions.DisambiguationError:
            speak(
                f"There are multiple meanings for '{query}'. Please be more specific."
            )
        except wikipedia.exceptions.PageError:
            speak(f"'{query}' does not match any Wikipedia page. Please try again.")
        except Exception as e:
            speak("An error occurred while searching Wikipedia.")
            print("Error:", e)

    elif selected_task == "Open YouTube":
        webbrowser.open_new_tab("https://www.youtube.com")
        speak("YouTube is now open.")
        insert_command(conn, selected_task, "YouTube opened")

    elif selected_task == "Open Prime Video":
        webbrowser.open_new_tab("https://www.primevideo.com")
        speak("Amazon Prime Video is now open.")
        insert_command(conn, selected_task, "Amazon Prime Video opened")
        time.sleep(5)

    elif selected_task == "Open Netflix":
        webbrowser.open_new_tab("https://www.netflix.com/browse")
        speak("Netflix is now open.")
        insert_command(conn, selected_task, "Netflix opened")
        time.sleep(5)

    elif selected_task == "Make a Note":
        speak("What would you like to make a note of?")
        note_content = take_command()
        note(note_content)
        speak("Note made successfully.")
        insert_command(conn, selected_task, "Note made successfully")

    elif selected_task == "Note This":
        speak("What would you like to note?")
        note_content = take_command()
        speak(note_content)
        insert_command(conn, selected_task, note_content)

    elif selected_task == "Open Google":
        webbrowser.open_new_tab("https://www.google.com")
        speak("Google Chrome is now open.")
        insert_command(conn, selected_task, "Google Chrome opened")
        time.sleep(5)

    elif selected_task == "Open Valorant":
        application_path = r"C:\\Riot Games\\Riot Client\\RiotClientServices.exe"
        open_application(application_path)
        insert_command(conn, selected_task, "Valorant opened")

    elif selected_task == "Open Gmail":
        webbrowser.open_new_tab("https://mail.google.com")
        speak("Google Mail is now open.")
        insert_command(conn, selected_task, "Google Mail opened")
        time.sleep(5)

    elif selected_task == "Search":
        speak("What would you like to search for?")
        search_query = take_command()
        webbrowser.open_new_tab(search_query)
        insert_command(conn, selected_task, f"Search '{search_query}' performed")

    elif selected_task == "Get the Time":
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        speak(f"The current time is {current_time}.")
        insert_command(conn, selected_task, f"Current time is {current_time}")

    elif selected_task == "Read News":
        webbrowser.open_new_tab("https://timesofindia.indiatimes.com/home/headlines")
        speak("Here are some headlines from the Times of India. Happy reading.")
        insert_command(conn, selected_task, "Headlines from Times of India displayed")
        time.sleep(6)

    elif selected_task == "Take a Photo":
        try:
            ec.capture(0, "robo camera", "img.jpg")
            speak("Photo captured successfully.")
            insert_command(conn, selected_task, "Photo captured")
        except Exception as e:
            print("An error occurred while capturing the photo:", str(e))
            speak("Sorry, I encountered an error while capturing the photo.")

    elif selected_task == "Ask Question":
        speak(
            "I can answer computational and geographical questions. What would you like to ask?"
        )
        question = take_command()
        client = wolframalpha.Client("R2K75H-7ELALHR35X")
        res = client.query(question)
        answer = next(res.results).text
        speak(answer)
        insert_command(conn, selected_task, f"Question: {question}, Answer: {answer}")

    elif selected_task == "Check Weather":
        speak("Which city's weather would you like to check?")
        city_name = take_command()
        api_key = "8ef61edcf1c576d65d836254e11ea420"
        base_url = "https://api.openweathermap.org/data/2.5/weather?"
        complete_url = f"{base_url}q={city_name}&appid={api_key}"
        response = requests.get(complete_url)
        if response.status_code == 200:
            weather_data = response.json()
            temperature = weather_data["main"]["temp"]
            humidity = weather_data["main"]["humidity"]
            description = weather_data["weather"][0]["description"]
            weather_info = (
                f"The temperature in {city_name} is {temperature} Kelvin with {humidity}% humidity. The weather is {description}."
            )
            speak(weather_info)
            insert_command(conn, selected_task, weather_info)
        else:
            speak("Sorry, I couldn't fetch the weather information for that city.")

    elif selected_task == "Who Are You":
        speak(
            "I am G-one version 1.0, your personal assistant. I am programmed to perform various tasks such as opening applications, searching the web, and providing information."
        )
        insert_command(conn, selected_task, "Introduction given")

    elif selected_task == "Who Made You":
        speak("I was built by Zuhair Khan.")
        insert_command(conn, selected_task, "Creator mentioned")

    elif selected_task == "Open Stack Overflow":
        webbrowser.open_new_tab("https://stackoverflow.com")
        speak("Stack Overflow is now open.")
        insert_command(conn, selected_task, "Stack Overflow opened")

    elif "Open Google to locate a place" in selected_task:
        location = selected_task.replace("Where Is", "")
        speak(f"Locating {location}.")
        webbrowser.open(f"https://www.google.com/maps/place/{location}")
        insert_command(conn, selected_task, f"Location: {location} opened in Google Maps")

    elif selected_task == "Log Off" or selected_task == "Shutdown":
        speak("Okay. Logging off now. Goodbye!")
        insert_command(conn, selected_task, "Assistant logged off")
        os.system("shutdown /s /t 1")

    else:
        speak("Sorry, I didn't catch that. Please try again.")
        insert_command(conn, selected_task, "Unknown command")
    
    conn.close()



def main():
    # Create the main GUI window
    root = tk.Tk()
    root.title("Voice Assistant")
    # root.geometry("1800x1800")
    root.configure(bg=BG_COLOR)

    frame1 = tk.Frame(root)
    frame1.pack(side=tk.TOP, fill=tk.Y)

    # def on_button_click(event):
    #     global stop_flag
    #     if not stop_flag:
    #         stop_flag = (
    #             False  # Reset the flag to False when starting the voice assistant
    #         )
    #         Thread(target=start_voice_assistant).start()
    #     else:
    #         stop_voice_assistant()
    
    def on_button_click(event):
        Thread(target=start_voice_assistant).start()

    # card1 = create_card(root, "Card 1", "This is the first card.")

    # card1.pack(fill=tk.BOTH)

    # Load and set the background image
    background_image = Image.open("8.jpg")
    resized_image = background_image.resize(
        (1950, 1250)
    )  # Replace "path/to/your/background_image.jpg" with the actual image file path
    background_photo = ImageTk.PhotoImage(resized_image)

    background_label = ttk.Label(root, image=background_photo)
    background_label.place(x=0, y=0)

    # f1 = ttk.Frame(root)
    # f1.pack(pady=100)  # Add some padding to the frame to center it vertically

    image2 = Image.open(
        "istockphoto-1290061049-612x612-removebg-preview.png"
    )  # Replace "path_to_image2.jpg" with the actual path to your image
    resized_image = image2.resize((120, 120))
    p2 = ImageTk.PhotoImage(resized_image)
    l2 = ttk.Label(root, image=p2, relief=SUNKEN, cursor="hand2")
    l2.pack(expand=True)
    l2.place(relx=0.5, rely=0.8, anchor=tk.CENTER)
    l2.bind("<Button-1>", on_button_click)
    # Heading
    heading_label = ttk.Label(
        root, text=" Desktop Voice Assistant", font=HEADING_FONT, background=BG_COLOR
    )
    heading_label.pack(anchor="nw")

    # Create and place a dropdown menu for tasks
    selected_task = tk.StringVar(root)
    selected_task.set(tasks[0])
    # Create and configure the style

    # Create the OptionMenu with the configured style
    task_dropdown = tk.OptionMenu(
        root, selected_task, *tasks, command=perform_selected_task
    )

    task_dropdown.config(width=40, font=("Helvetica", 14))
    task_dropdown.place(
        relx=1.0, rely=0, anchor="ne"
    )  # Place the dropdown at the top right corner
    # task_dropdown = tk.OptionMenu(
    #     root, selected_task, *tasks, command=perform_selected_task
    # )

    task_dropdown.pack(pady=10)

    label3 = tk.Label(frame1, text="Label 3", font=("Helvetica", 12), foreground="red")
    label3.pack()

    global entry
    f1 = ttk.Frame(root)
    f1.pack()
    l1 = ttk.Label(
        f1, text="Enter Your Name", font=INSTRUCTION_FONT, background=BG_COLOR
    )
    l1.pack(side=LEFT, fill=BOTH)
    entry = ttk.Entry(f1, width=30)
    entry.pack(pady=10)

    style = ttk.Style(root)
    style.configure(
        "VoiceAssistant.TButton",
        font=BUTTON_FONT,
        background=BUTTON_COLOR,
        foreground=BUTTON_FOREGROUND,
    )
    root.mainloop()


if __name__ == "__main__":
    main()
