import numpy as np
import sounddevice as sd
from scipy.signal import square, sawtooth
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.slider import MDSlider
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.screen import MDScreen
from threading import Thread, Event

KV = '''
MDScreen:
    BoxLayout: # Widgets are arranged sequentially (either horizontally or vertically)
        orientation: 'vertical'
        padding: dp(20) # Between the children and the edge of the app
        spacing: dp(20) # Between each children

        MDLabel:
            text: "ASADOS"
            halign: 'center'
            font_style: 'H4'

        MDLabel:
            text: "Base Note"
            halign: 'center'
            font_style: 'H5'

        # Slider for choosing the root frequency
        MDSlider:
            id: rootfrequency_slider
            min: 440
            max: 8000
            value: 440
            hint: False # Doesn't show the value at which the slider is at
            on_value: app.update_rootfrequency(self.value)
            value_track: True
            value_track_color: app.theme_cls.primary_color

        # Show the value of the root frequency as well as its chord
        BoxLayout:
            orientation: 'horizontal'
            adding: dp(20) # Between the children and the edge of the app
            spacing: dp(20) # Between each children

            MDLabel:
                id: rootfrequency_value
                text: "440 Hz"
                halign: 'center'
                font_style: 'Subtitle1'

            MDLabel:
                id: chord_value
                text: "A4"
                halign: 'center'
                font_style: 'Subtitle1'

        MDLabel:
            text: "LFO Settings"
            halign: 'center'
            font_style: 'H5'

        MDLabel:
            text: "LFO Waveform"
            halign: 'center'
            font_style: 'H6'

        # To select LFO waveform
        BoxLayout:
            padding: dp(10)
            spacing: dp(10)

            MDCheckbox:
                id: sine
                group: 'lfowaveform'
                on_active: app.set_lfowaveform('sine', self.active)
            MDLabel:
                text: "Sine"
                
            MDCheckbox:
                id: square
                group: 'lfowaveform'
                on_active: app.set_lfowaveform('square', self.active)
            MDLabel:
                text: "Square"
                    
            MDCheckbox:
                id: sawtooth
                group: 'lfowaveform'
                on_active: app.set_lfowaveform('sawtooth', self.active)
            MDLabel:
                text: "Sawtooth"
                
            MDCheckbox:
                id: triangle
                group: 'lfowaveform'
                # on_active: app.set_triangle(*args)
                on_active: app.set_lfowaveform('triangle', self.active)
            MDLabel:
                text: "Triangle"

        MDLabel:
            text: "LFO Frequency"
            halign: 'center'
            font_style: 'H6'

        # Slider for LFO frequency 
        MDSlider:
            id: lfofrequency_slider
            min: 0
            max: 20
            value: 0.0 # Default LFO frequency value is set to 0
            on_value: app.update_lfofrequency(self.value)
            # value_track: True
            # value_track_color: app.theme_cls.primary_color

        MDLabel:
            text: "LFO Amplitude"
            halign: 'center'
            font_style: 'H6'

        # Slider for LFO amplitude
        MDSlider:
            id: lfoamplitude_slider
            min: 0
            max: 1
            value: 0.0
            on_value: app.update_lfoamplitude(self.value)
            # value_track: True
            # value_track_color: app.theme_cls.primary_color

        BoxLayout:
            size_hint_y: None
            height: dp(50)
            spacing: dp(20)
            padding: dp(10)

            MDRaisedButton:
                id: startstop_button
                text: "Start"
                pos_hint: {'center_x': 0.5}
                on_release: app.toggle_button()
                size_hint_x: None
                width: dp(100)
'''

class ToneGeneratorApp(MDApp):
    def build(self):
        self.rootwaveform = 'sine'  # The root waveform is set to sine, it's unchangeable
        self.lfowaveform = 'sine'
        self.rootfrequency = 440
        self.lfofrequency = 0
        self.rootamplitude = 0.5
        self.lfoamplitude = 0
        self.sample_rate = 44100
        self.duration = 1  # Duration per sample chunk, not relevant for continuous playback
        self.stop_event = Event()
        self.thread = None

        self.screen = Builder.load_string(KV)
        return self.screen

    # Set the LFO waveform based on the ticked checkbox
    def set_lfowaveform(self, waveform, active):
        if active: 
            self.lfowaveform = waveform

    # To update the root frequency
    def update_rootfrequency(self, value):
        self.rootfrequency = value
        # Display the root frequency and chord on the screen
        self.screen.ids.rootfrequency_value.text = f"{value:.0f} Hz"
        self.screen.ids.chord_value.text = self.get_chord(value)        

    # To update the LFO frequency
    def update_lfofrequency(self, value):
        self.lfofrequency = value

    # To update the LFO amplitude
    def update_lfoamplitude(self, value):
        self.lfoamplitude = value

    def get_chord(self, frequency):
        # Define the frequencies for musical notes (A4 = 440Hz as reference)
        notes = [
            ('C0', 16.35), ('C#0/Db0', 17.32), ('D0', 18.35), ('D#0/Eb0', 19.45), ('E0', 20.60), ('F0', 21.83), ('F#0/Gb0', 23.12), ('G0', 24.50), ('G#0/Ab0', 25.96), ('A0', 27.50), ('A#0/Bb0', 29.14), ('B0', 30.87),
            ('C1', 32.70), ('C#1/Db1', 34.65), ('D1', 36.71), ('D#1/Eb1', 38.89), ('E1', 41.20), ('F1', 43.65), ('F#1/Gb1', 46.25), ('G1', 49.00), ('G#1/Ab1', 51.91), ('A1', 55.00), ('A#1/Bb1', 58.27), ('B1', 61.74),
            ('C2', 65.41), ('C#2/Db2', 69.30), ('D2', 73.42), ('D#2/Eb2', 77.78), ('E2', 82.41), ('F2', 87.31), ('F#2/Gb2', 92.50), ('G2', 98.00), ('G#2/Ab2', 103.83), ('A2', 110.00), ('A#2/Bb2', 116.54), ('B2', 123.47),
            ('C3', 130.81), ('C#3/Db3', 138.59), ('D3', 146.83), ('D#3/Eb3', 155.56), ('E3', 164.81), ('F3', 174.61), ('F#3/Gb3', 185.00), ('G3', 196.00), ('G#3/Ab3', 207.65), ('A3', 220.00), ('A#3/Bb3', 233.08), ('B3', 246.94),
            ('C4', 261.63), ('C#4/Db4', 277.18), ('D4', 293.66), ('D#4/Eb4', 311.13), ('E4', 329.63), ('F4', 349.23), ('F#4/Gb4', 369.99), ('G4', 392.00), ('G#4/Ab4', 415.30), ('A4', 440.00), ('A#4/Bb4', 466.16), ('B4', 493.88),
            ('C5', 523.25), ('C#5/Db5', 554.37), ('D5', 587.33), ('D#5/Eb5', 622.25), ('E5', 659.25), ('F5', 698.46), ('F#5/Gb5', 739.99), ('G5', 783.99), ('G#5/Ab5', 830.61), ('A5', 880.00), ('A#5/Bb5', 932.33), ('B5', 987.77),
            ('C6', 1046.50), ('C#6/Db6', 1108.73), ('D6', 1174.66), ('D#6/Eb6', 1244.51), ('E6', 1318.51), ('F6', 1396.91), ('F#6/Gb6', 1479.98), ('G6', 1567.98), ('G#6/Ab6', 1661.22), ('A6', 1760.00), ('A#6/Bb6', 1864.66), ('B6', 1975.53),
            ('C7', 2093.00), ('C#7/Db7', 2217.46), ('D7', 2349.32), ('D#7/Eb7', 2489.02), ('E7', 2637.02), ('F7', 2793.83), ('F#7/Gb7', 2959.96), ('G7', 3135.96), ('G#7/Ab7', 3322.44), ('A7', 3520.00), ('A#7/Bb7', 3729.31), ('B7', 3951.07),
            ('C8', 4186.01), ('C#8/Db8', 4434.92), ('D8', 4698.63), ('D#8/Eb8', 4978.03), ('E8', 5274.04), ('F8', 5587.65), ('F#8/Gb8', 5919.91), ('G8', 6271.93), ('G#8/Ab8', 6644.88), ('A8', 7040.00), ('A#8/Bb8', 7458.62), ('B8', 7902.13)
        ]
        min_distance = float('inf')
        closest_note = 'A4'
        for note, freq in notes:
            distance = abs(frequency - freq)
            if distance < min_distance:
                min_distance = distance
                closest_note = note
        return closest_note

    # Generate a wave according to the waveform type and frequency
    def generate_wave(self, amplitude, waveform_type, frequency):
        # t = Time array
        t = np.linspace(0, self.duration, int(self.sample_rate * self.duration), endpoint=False)
        if waveform_type == 'sine':
            return amplitude * np.sin(2 * np.pi * frequency * t)
        elif waveform_type == 'square':
            return amplitude * square(2 * np.pi * frequency * t)
        elif waveform_type == 'sawtooth':
            return amplitude * sawtooth(2 * np.pi * frequency * t)
        elif waveform_type == 'triangle':
            return amplitude * sawtooth(2 * np.pi * frequency * t, 0.5)

    # Play the generated wave
    def play_tone(self):
        while not self.stop_event.is_set(): 
            # Generate the root sound and LFO sound
            root_sound = self.generate_wave(self.rootamplitude, self.rootwaveform, self.rootfrequency)
            lfo_sound = self.generate_wave(self.lfoamplitude, self.lfowaveform, self.lfofrequency)

            # Blend both waveforms (the root waveform and the LFO waveform)
            # Multiplying both waveforms results in a smoother waveforms than adding them
            modulated_sound = root_sound * lfo_sound if np.any(lfo_sound != 0) else root_sound

            # Play the current sound with an overlap
            sd.play(modulated_sound, self.sample_rate, blocking=True)

    # When pressed, the Start button will change into a Stop button and vice versa
    def toggle_button(self):
        button = self.screen.ids.startstop_button

        if button.text == "Start":
            self.start_tone()
            button.text = "Stop"
        else:
            self.stop_tone()
            button.text = "Start"
    
    def start_tone(self):
        if self.thread is None or not self.thread.is_alive():
            self.stop_event.clear()
            self.thread = Thread(target=self.play_tone)
            self.thread.start()

    def stop_tone(self):
        self.stop_event.set()
        if self.thread is not None:
            self.thread.join()

    def on_stop(self):
        self.stop_tone() 

if __name__ == '__main__':
    ToneGeneratorApp().run()