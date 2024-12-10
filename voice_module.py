import speech_recognition as sr

class VoiceRecognizer:
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def recognize_voice(self): #Captures and recognizes voice input using Google Speech API
        try:
            with sr.Microphone() as source:
                # Calibrate for ambient noise
                print("Calibrating for ambient noise... Please wait.")
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
                
                print("Listening for command...")
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=8)

            # Recognize speech using Google Web Speech API
            print("Recognizing...")
            command = self.recognizer.recognize_google(audio, show_all=False)
            print(f"Recognized command: {command}")
            return command

        except sr.UnknownValueError:
            print("Error: Could not understand the audio.")
            return None
        except sr.RequestError as e:
            print(f"Error: Could not request results from Google Speech Recognition service; {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None
