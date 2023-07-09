import tkinter as tk
import sounddevice as sd
import soundfile as sf
import speech_recognition as sr
import atexit
import os
import openai

class VoiceRecorderApp:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Voice Recorder")
        self.window.geometry("800x600")  # Set the initial size of the window
        
        self.record_button = tk.Button(self.window, text="Record", command=self.toggle_recording, height=3, width=20)
        self.record_button.pack(pady=10)
        
        self.transcription_text = tk.Text(self.window, height=10, width=60, wrap=tk.WORD)  # Enable word wrapping
        self.transcription_text.pack(pady=10)
        
        self.transcription_text.configure(state="disabled")  # Make the text box read-only
        
        self.send_button = tk.Button(self.window, text="Send", command=self.send_message)
        self.send_button.pack(pady=10)
        
        self.response_text = tk.Text(self.window, height=10, width=60, wrap=tk.WORD)  # Enable word wrapping
        self.response_text.pack(pady=10)
        
        self.response_text.configure(state="disabled")  # Make the text box read-only
        
        self.is_recording = False
        self.filename = "recording.wav"
        self.data = []
        self.flash_interval = 1000  # Flashing interval in milliseconds
        
        self.api_key = "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"  # Replace with your OpenAI API key
        self.chat_model = "gpt-3.5-turbo"
        
        atexit.register(self.cleanup)
 
        
    def toggle_recording(self):
        if not self.is_recording:
            self.record_button.configure(text="Stop Recording")
            self.start_recording()
            self.flash_button()
        else:
            self.record_button.configure(text="Record")
            self.stop_recording()
            self.record_button.configure(bg="SystemButtonFace")  # Restore the button's original background color
        
    def start_recording(self):
        self.is_recording = True
        self.data = []
        self.stream = sd.InputStream(callback=self.record_callback)
        self.stream.start()
        
    def stop_recording(self):
        self.is_recording = False
        self.stream.stop()
        sf.write(self.filename, self.data, samplerate=44100)
        print("Recording saved.")
        
        transcription = self.perform_speech_recognition()
        self.display_transcription(transcription)
        
    def record_callback(self, indata, frames, time, status):
        if status:
            print(status)
        self.data.extend(indata[:, 0])
        
    def perform_speech_recognition(self):
        r = sr.Recognizer()
        with sr.AudioFile(self.filename) as source:
            audio_data = r.record(source)
            transcription = r.recognize_google(audio_data)
        return transcription
        
    def display_transcription(self, transcription):
        self.transcription_text.configure(state="normal")  # Enable the text box temporarily
        self.transcription_text.delete(1.0, tk.END)
        self.transcription_text.insert(tk.END, transcription)
        self.transcription_text.configure(state="disabled")  # Disable the text box again
        
    def send_message(self):
        user_input = self.transcription_text.get(1.0, tk.END).strip()
        
        if user_input:
            response = self.get_chatbot_response(user_input)
            self.display_response(response)
        
    def get_chatbot_response(self, user_input):
        openai.api_key = self.api_key
        response = openai.ChatCompletion.create(
            model=self.chat_model,
            messages=[{"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": user_input}],
            max_tokens=50,
            n=1,
            stop=None,
            temperature=0.7
        )
        
        return response.choices[0].message['content'].strip()

        
    def display_response(self, response):
        self.response_text.configure(state="normal")  # Enable the text box temporarily
        self.response_text.delete(1.0, tk.END)
        self.response_text.insert(tk.END, response)
        self.response_text.configure(state="disabled")  # Disable the text box again
        
    def cleanup(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)
            print("Deleted audio file: {}".format(self.filename))
        
    def flash_button(self):
        if self.is_recording:
            current_bg = self.record_button.cget("bg")
            new_bg = "red" if current_bg != "red" else "SystemButtonFace"
            self.record_button.configure(bg=new_bg)
            self.window.after(self.flash_interval, self.flash_button)
        
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = VoiceRecorderApp()
    app.run()
