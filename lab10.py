import json
import pyttsx3, pyaudio, vosk
import requests
import random
from PIL import Image
from io import BytesIO


API_URL = "https://rickandmortyapi.com/api/character"


def get_random_character():
    char_id = random.randint(1, 826)
    response = requests.get(f"{API_URL}/{char_id}")
    return response.json()


def show_image(url):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    img.show()


def get_first_episode(url):
    response = requests.get(url)
    data = response.json()
    return data["name"]


def get_species(url):
    response = requests.get(url)
    data = response.json()
    return data["species"]


class Speech:
    def __init__(self):
        self.speaker = 0
        self.tts = pyttsx3.init('sapi5')
        self.voices = self.tts.getProperty('voices')

    def set_voice(self, speaker):
        if 0 <= speaker < len(self.voices):
            return self.voices[speaker].id
        return self.voices[0].id

    def text2voice(self, speaker=0, text='Готов'):
        self.tts.setProperty('voice', self.set_voice(speaker))
        self.tts.say(text)
        self.tts.runAndWait()


class Recognize:
    def __init__(self):
        model = vosk.Model('model_small')
        self.record = vosk.KaldiRecognizer(model, 16000)
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            input_device_index=3,
            frames_per_buffer=8000
        )
        self.stream.start_stream()

    def listen(self):
        while True:
            data = self.stream.read(4000, exception_on_overflow=False)
            if self.record.AcceptWaveform(data):
                answer = json.loads(self.record.Result())
                text = answer.get('text', '').strip().lower()
                if text:
                    yield text

    def close(self):
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()


def speak(text):
    speech = Speech()
    speech.text2voice(speaker=1, text=text)

def main():
    rec = Recognize()
    text_gen = rec.listen()

    speak('Hello')
    speak('Please start speaking')

    character = None

    for text in text_gen:
        print("Распознано:", text)

        if 'случайный' in text:
            character = get_random_character()
            print("Персонаж:", character["name"])
            speak('Here is your character')

        elif character is None:
            speak("Snachala skazhi sluchaynyy personazh")

        elif 'картинка' in text:
            show_image(character["image"])
            speak('Here is your picture')

        elif 'природа' in text:
            print(f"Вид:", character["species"])

        elif 'эпизод' in text:
            episode_url = character["episode"][0]
            episode_name = get_first_episode(episode_url)
            print("Первый эпизод:", episode_name)

        elif 'стоп' in text:
            speak("I'll be back")
            break

        else:
            speak("Govori luchshe, ya ne slyshu")


if __name__ == "__main__":
    main()
