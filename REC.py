import soundcard as sc
import soundfile as sf
import numpy as np
import tkinter as tk
from tkinter import filedialog, ttk
import threading

class AudioRecorder:
    def __init__(self):
        self.is_recording = False
        self.audio_data = []
        self.sample_rate = 48000
        self.setup_gui()

    def setup_gui(self):
        self.window = tk.Tk()
        self.window.title("Audio Recorder")
        self.window.geometry("450x100")
        self.window.configure(bg='#f0f0f0')
        self.window.resizable(False, False)  # Disable window resizing

        top_frame = tk.Frame(self.window, bg='#f0f0f0')
        top_frame.pack(fill=tk.X, padx=20, pady=10)

        self.device_label = tk.Label(top_frame, text="Select Output Device:", bg='#f0f0f0')
        self.device_label.pack(side=tk.LEFT)

        self.device_var = tk.StringVar()
        self.device_dropdown = ttk.Combobox(top_frame, textvariable=self.device_var, width=45)
        self.device_dropdown['values'] = [speaker.name for speaker in sc.all_speakers()]
        self.device_dropdown.set(sc.default_speaker().name)
        self.device_dropdown.pack(side=tk.LEFT, padx=(10, 0))

        button_frame = tk.Frame(self.window, bg='#f0f0f0')
        button_frame.pack(pady=10)

        self.record_indicator = tk.Label(button_frame, text="🔴", fg="gray", bg='#f0f0f0', font=("Arial", 16))
        self.record_indicator.pack(side=tk.LEFT, padx=(0, 10))

        self.record_button = tk.Button(button_frame, text="Record", command=self.toggle_recording, width=10)
        self.record_button.pack(side=tk.LEFT, padx=5)

        save_frame = tk.Frame(button_frame, bg='#f0f0f0')
        save_frame.pack(side=tk.LEFT, padx=5)

        self.save_button = tk.Button(save_frame, text="Save", command=self.save_audio, width=10)
        self.save_button.pack(side=tk.LEFT)

        self.save_indicator = tk.Label(save_frame, text="🟢", fg="gray", bg='#f0f0f0', font=("Arial", 16))
        self.save_indicator.pack(side=tk.LEFT, padx=(5, 0))

    def toggle_recording(self):
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        self.is_recording = True
        self.record_button.config(text="Stop")
        self.audio_data = []
        self.save_indicator.config(fg="gray")  # Reset save indicator
        threading.Thread(target=self.record_audio, daemon=True).start()
        self.blink_indicator()

    def stop_recording(self):
        self.is_recording = False
        self.record_button.config(text="Record")
        self.record_indicator.config(fg="gray")
        if self.audio_data:
            self.save_indicator.config(fg="green")  # Set save indicator to green

    def record_audio(self):
        selected_device = self.device_var.get()
        with sc.get_microphone(id=str(selected_device), include_loopback=True).recorder(samplerate=self.sample_rate) as mic:
            while self.is_recording:
                data = mic.record(numframes=self.sample_rate // 10)
                self.audio_data.append(data)

    def blink_indicator(self):
        if self.is_recording:
            current_color = self.record_indicator.cget("fg")
            new_color = "red" if current_color == "gray" else "gray"
            self.record_indicator.config(fg=new_color)
            self.window.after(500, self.blink_indicator)

    def save_audio(self):
        if not self.audio_data:
            print("No audio to save")
            return

        filename = filedialog.asksaveasfilename(defaultextension=".wav", 
                                                filetypes=[("WAV files", "*.wav")])
        if filename:
            full_audio = np.concatenate(self.audio_data, axis=0)
            sf.write(file=filename, data=full_audio[:, 0], samplerate=self.sample_rate)
            print(f"Audio saved as {filename}")
            self.save_indicator.config(fg="gray")  # Reset save indicator after saving

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    recorder = AudioRecorder()
    recorder.run()