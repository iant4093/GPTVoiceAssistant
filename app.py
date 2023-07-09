import tkinter as tk
import sounddevice as sd
import soundfile as sf

class VoiceRecorderApp:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Voice Recorder")
        
        self.record_button = tk.Button(self.window, text="Record", command=self.toggle_recording)
        self.record_button.pack(pady=10)
        
        self.is_recording = False
        self.filename = "recording.wav"
        self.data = []
        
    def toggle_recording(self):
        if not self.is_recording:
            self.record_button.configure(text="Stop Recording")
            self.start_recording()
        else:
            self.record_button.configure(text="Record")
            self.stop_recording()
        
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
        
    def record_callback(self, indata, frames, time, status):
        if status:
            print(status)
        self.data.extend(indata[:, 0])
        
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = VoiceRecorderApp()
    app.run()
