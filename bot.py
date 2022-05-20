import os
import webbrowser
import subprocess
from gtts import gTTS
from playsound import playsound
import speech_recognition as sr

# Default audio file name.
AUDIO_FILE = 'audio.mp3'

# Command prefix. You can define your function with this prefix and it will count as a command.
COMMAND_PREFIX = 'command_'

# Searching platform urls.
URLS = {
    'google': 'https://www.google.com/search?q={}',
    'github': 'https://github.com/search?q={}',
    'youtube': 'https://www.youtube.com/results?search_query={}'
}

# Bot speechs.
AVAILABLE_COMMANDS = 'Available commands are {}.'
EXAMPLE_COMMANDS = 'For example you can say the word "Search" for details, or "Search Amazon on Google" for a quick search.'
ASK_COMMAND = 'What is your command?'
INVALID_COMMAND = 'Invalid command received.'

AVAILABLE_PLATFORMS = 'Available platforms are {}.'
ASK_SEARCH = 'What would you like to search on which platform?'
INVALID_PLATFORM = 'Invalid platform received.'

ASK_OPEN = 'What would you like to open?'

class Bot:
    def _speak(self, text):
        # Converts text to speech.
        tts = gTTS(text)
        
        # Saves speech as mp3.
        tts.save(AUDIO_FILE)

        # Plays speech.
        playsound(AUDIO_FILE)

        # Deletes created mp3 file.
        os.remove(AUDIO_FILE)

    def speak(self, *args):
        # Supports multiple arguments.
        self._speak(' '.join(args))

    def listen(self) -> str:
        # Creates `Recognizer` object.
        rec = sr.Recognizer()

        # Listens microphone.
        with sr.Microphone() as mic:
            audio = rec.listen(mic)
        
        # Converts speech to text.
        return rec.recognize_google(audio).lower()
    
    def get_commands(self):
        # Looks for each attribute and yields if callable starts with `COMMAND_PREFIX`.
        for name, func in self.__class__.__dict__.items():
            if callable(func) and name.startswith(COMMAND_PREFIX):
                yield name.replace(COMMAND_PREFIX, '')
    
    def command_search(self, speech: list[str]):
        # If there is no speech, takes input from user.
        if not speech:
            # Gives information about search command.
            self.speak(
                AVAILABLE_PLATFORMS.format(', '.join(URLS.keys())),
                ASK_SEARCH
            )
        
            # Listens and splits given input to words.
            speech = self.listen().split()

        # Fetches platform from splitted words.
        platform = speech[-1]

        # Gets related url of platform.
        url = URLS.get(platform)

        # If there is no such a platform, returns invalid.
        if url is None:
            return self.speak(INVALID_PLATFORM)

        # Converts splitted speech to string.
        query = ' '.join(speech)

        # Removes "on platform_name" from string.
        query = query.replace(f'on {platform}', '')

        # Opens related url with given query.
        return webbrowser.open(url.format(query))

    def command_open(self, speech: list[str]):
        # If there is no speech, takes input from user.
        if not speech:
            # Asks what to open.
            self.speak(ASK_OPEN)

            # Listens what to open.
            speech = self.listen()
        
        # Tries to open what you asked for.
        return subprocess.Popen(speech)

    def take_command(self):
        # Says available commands.
        self.speak(
            AVAILABLE_COMMANDS.format(', '.join(self.get_commands())),
            EXAMPLE_COMMANDS,
            ASK_COMMAND
        )
        
        # Listens and splits given input to words.
        speech = self.listen().split()

        # Extracts command from speech.
        command = speech.pop(0)

        # Checks if command is valid.
        if not command in self.get_commands():
            return self.speak(INVALID_COMMAND)

        # Runs related function for command.
        func = getattr(self, COMMAND_PREFIX + command)
        return func(speech)
