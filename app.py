import tkinter as tk
import sounddevice as sd
import soundfile as sf
import speech_recognition as sr
import atexit
import os
import openai
import pyttsx3
import threading

class VoiceAssistantApp:
    def __init__(self):
        # Create a window using Tkinter
        self.window = tk.Tk()
        self.window.title("Voice Assistant")
        self.window.geometry("800x600") # Set the initial size of the window

        # Create a record button
        self.record_button = tk.Button(
            self.window, text="Record", command=self.toggle_recording, height=3, width=20 # Enable word wrapping
        )
        self.record_button.pack(pady=10)  # Make the text box read-only

        # Create a text box for displaying transcriptions
        self.transcription_text = tk.Text(
            self.window, height=10, width=60, wrap=tk.WORD
        )
        self.transcription_text.pack(pady=10)
        self.transcription_text.configure(state="disabled")

        # Create a send button
        self.send_button = tk.Button(
            self.window, text="Send", command=self.send_message
        )
        self.send_button.pack(pady=10)

        # Create a text box for displaying responses
        self.response_text = tk.Text(
            self.window, height=10, width=60, wrap=tk.WORD
        )
        self.response_text.pack(pady=10)
        self.response_text.configure(state="disabled")

        # Add regenerate button
        self.regenerate_button = tk.Button(
            self.window, text="Regenerate Response", command=self.regenerate_response
        )
        self.regenerate_button.pack(pady=10)

        # Initialize variables
        self.is_recording = False
        self.filename = "recording.wav"
        self.data = []
        self.flash_interval = 1000 # Flashing interval in milliseconds

        # Set up OpenAI API credentials
        self.api_key = "key" # Replace with your OpenAI API key
        self.chat_model = "gpt-3.5-turbo"

        self.tts_engine = pyttsx3.init()

        atexit.register(self.cleanup) # Register cleanup function

    
    def toggle_recording(self):
        # Toggle the recording state when the record button is clicked
        if not self.is_recording:
            self.record_button.configure(text="Stop Recording")
            self.start_recording()
            self.flash_button()
        else:
            self.record_button.configure(text="Record")
            self.stop_recording()
            self.record_button.configure(bg="SystemButtonFace") # Restore the button's original background color

    def start_recording(self):
        # Start recording audio
        self.is_recording = True
        self.data = []
        self.stream = sd.InputStream(callback=self.record_callback)
        self.stream.start()

    def stop_recording(self):
        # Stop recording audio, save it to a file, perform speech recognition, and display the transcription
        self.is_recording = False
        self.stream.stop()
        sf.write(self.filename, self.data, samplerate=44100)
        print("Recording saved.")

        transcription = self.perform_speech_recognition()
        self.display_transcription(transcription)

    def record_callback(self, indata, frames, time, status):
        # Callback function for recording audio
        if status:
            print(status)
        self.data.extend(indata[:, 0])

    def perform_speech_recognition(self):
        # Perform speech recognition on the recorded audio file
        r = sr.Recognizer()
        with sr.AudioFile(self.filename) as source:
            audio_data = r.record(source)
            transcription = r.recognize_google(audio_data)
        return transcription

    def display_transcription(self, transcription):
        # Display the transcription in the transcription text box
        self.transcription_text.configure(state="normal") # Enable the text box temporarily
        self.transcription_text.delete(1.0, tk.END)
        self.transcription_text.insert(tk.END, transcription)
        self.transcription_text.configure(state="disabled") # Disable the text box again

    def send_message(self):
        # Send the user input to the chatbot and display the response
        self.regenerate_response()

    def regenerate_response(self):
        # Regenerates the response when button is pressed
        user_input = self.transcription_text.get(1.0, tk.END).strip()

        if user_input:
            response = self.get_chatbot_response(user_input)
            self.display_response(response)
            self.speak_response(response)

    def get_chatbot_response(self, user_input):
        # Get a response from the OpenAI chatbot model
        openai.api_key = self.api_key
        response = openai.ChatCompletion.create(
            model=self.chat_model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_input},
            ],
            max_tokens=100,
            n=1,
            stop=None,
            temperature=0.7,
        )

        return response.choices[0].message["content"].strip()

    def speak_response(self, response):
        threading.Thread(target=self._speak_response, args=(response,), daemon=True).start()

    def _speak_response(self, response):
        self.tts_engine.say(response)
        self.tts_engine.runAndWait()

    def display_response(self, response):
        # Display the response in the response text box
        self.response_text.configure(state="normal") # Enable the text box temporarily
        self.response_text.delete(1.0, tk.END)
        self.response_text.insert(tk.END, response)
        self.response_text.configure(state="disabled") # Disable the text box again

    def cleanup(self):
        # Clean up by deleting the audio file
        if os.path.exists(self.filename):
            os.remove(self.filename)
            print("Deleted audio file: {}".format(self.filename))

    def flash_button(self):
        # Flash the record button while recording is in progress
        if self.is_recording:
            current_bg = self.record_button.cget("bg")
            new_bg = "red" if current_bg != "red" else "SystemButtonFace"
            self.record_button.configure(bg=new_bg)
            self.window.after(self.flash_interval, self.flash_button)

    def run(self):
         # Run the Tkinter event loop
        self.window.mainloop()

# Create an instance of the VoiceAssistantApp class and run it
if __name__ == "__main__":
    app = VoiceAssistantApp()
    app.run()