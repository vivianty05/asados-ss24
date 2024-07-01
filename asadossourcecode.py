# ASADOS

import time
import math
import pyaudio
# import librosa
import itertools
import numpy as np
# import seaborn as sns
import sounddevice as sd
# import IPython.display as ipd

from scipy.signal import square, sawtooth
# from abc import ABC, abstractmethod
# from scipy.io import wavfile

from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivymd.app import MDApp
from kivy.uix.image import Image
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.slider import MDSlider
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.screen import MDScreen
from threading import Thread, Event

# GUI Code
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

        BoxLayout:
            orientation: 'horizontal'
            padding: dp(20)
            spacing: dp(20)

            # Collect user input for base pitch
            MDTextField:
                id: A4frequency_value
                hint_text: "Enter frequency for A4"
                helper_text: "Only numbers are allowed"
                helper_text_mode: "on_focus"
                input_filter: 'float'   # Restrict input to float numbers
                halign: 'center'
                font_style: 'Subtitle1'

            MDRaisedButton:
                text: "Enter"
                pos_hint: {'center_x': 0.5}
                on_release: app.update_A4frequency()
                size_hint_x: None
                width: dp(100)

        # Slider for choosing the root frequency
        MDSlider:
            id: rootfrequency_slider
            min: 0
            max: 8000
            value: 440
            hint: False     # Doesn't show the value at which the slider is at
            on_value: app.update_rootfrequency(self.value)
            value_track: True
            value_track_color: app.theme_cls.primary_color

        # Show the value of the root frequency as well as its chord
        BoxLayout:
            orientation: 'horizontal'
            padding: dp(20)     # Between the children and the edge of the app
            spacing: dp(20)     # Between each children

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

        BoxLayout:
            padding: dp(10)
            spacing: dp(10)

            MDLabel:
                text: "Destination"
                halign: 'center'
                font_style: 'H6'

            MDCheckbox:
                id: amp_mod
                group: 'lfodestination'
                on_active: app.set_lfodestination('amp_mod', self.active)
            MDLabel:
                text: "AM"
                
            MDCheckbox:
                id: freq_mod
                group: 'lfodestination'
                on_active: app.set_lfodestination('freq_mod', self.active)
            MDLabel:
                text: "FM"
            
        # To select LFO waveform
        BoxLayout:
            padding: dp(10)
            spacing: dp(0)

            MDLabel:
                text: "Wave"
                halign: 'center'
                font_style: 'H6'

            MDCheckbox:
                id: sine
                group: 'lfowaveform'
                on_active: app.set_lfowaveform('sine', self.active)
            MDLabel:
                text: "Sine"

            MDCheckbox:
                id: squares
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
                on_active: app.set_lfowaveform('triangle', self.active)
            MDLabel:
                text: "Triangle"

        BoxLayout: 
            padding: dp(10)
            spacing: dp(10)

            MDLabel:
                text: "LFO Frequency"
                halign: 'center'
                font_style: 'H6'

            # Slider for LFO frequency 
            MDSlider:
                id: lfofrequency_slider
                min: 0.0
                max: 20.0
                value: 0.0 # Default LFO frequency value is set to 0
                on_value: app.update_lfofrequency(self.value)
                # value_track: True
                # value_track_color: app.theme_cls.primary_color

        BoxLayout: 
            padding: dp(10)
            spacing: dp(10)

            MDLabel:
                text: "LFO Amplitude"
                halign: 'center'
                font_style: 'H6'

            # Slider for LFO amplitude
            MDSlider:
                id: lfoamplitude_slider
                min: 0.0
                max: 1.0
                value: 0.0
                on_value: app.update_lfoamplitude(self.value)
                # value_track: True
                # value_track_color: app.theme_cls.primary_color

        BoxLayout:
            size_hint_y: None
            height: dp(50)
            spacing: dp(20)
            padding: dp(20)

            MDRaisedButton:
                id: startstop_button
                text: "Start"
                pos_hint: {'center_x': 0.5}
                on_release: app.toggle_button()
                size_hint_x: None
                width: dp(100)
'''

# Functionality Code
class ToneGeneratorApp(MDApp):
    def build(self):
        self.rootwaveform = 'sine'  # The root waveform is set to sine, it's unchangeable
        self.rootfrequency = 440
        self.rootamplitude = 1
        self.rootsound = None

        self.lfowaveform = None
        self.lfofrequency = 0
        self.lfoamplitude = 0
        self.lfodestination = None
        self.amp_mod = False
        self.freq_mod = False
        self.modulatedsound = None

        self.A4frequency = 440
        self.sample_rate = 44100
        self.duration = 1  # Duration per sample chunk, not relevant for continuous playback
        self.stop_event = Event()
        self.thread = None

        self.screen = Builder.load_string(KV)
        return self.screen

    # Set LFO destination as Amplitude Modulation (AM) or Frequency Modulation (FM)
    def set_lfodestination(self, destination, active):
        if active: 
            self.lfodestination = destination
            if self.lfodestination == "amp_mod":
                self.amp_mod = True
            elif self.lfodestination == "freq_mod":
                self.freq_mod = True            
        else:
            self.lfodestination = None   
            self.amp_mod = False
            self.freq_mod = False  
        print(self.lfodestination)

    # Set the LFO waveform based on the ticked checkbox
    def set_lfowaveform(self, waveform, active):
        if active: 
            self.lfowaveform = waveform

    # To update the A4 frequency
    # The A4 frequency is used here because the formula to generate the frequency of each keynote is based on the A4 frequency
    def update_A4frequency(self):
        self.A4frequency = float(self.screen.ids.A4frequency_value.text)

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
    
    # To generate a chord library based on the inputted A4 frequency
    # The chord library will be consist of the keynote and its frequency, i.e. A4 = 440Hz, etc.
    def generate_chord_library(self):
        note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        chord_library = {}
        
        for midi_number in range(0, 128):  # MIDI numbers range from 0 to 127
            frequency = self.A4frequency * 2 ** ((midi_number - 69) / 12)   # Calulates the frequency of each MIDI note; A4 MIDI note number = 69
            octave = (midi_number // 12) - 1    # Calculate the octave for each midi number
            note = note_names[midi_number % 12] # Retrieve the note name
            note_name = f"{note}{octave}"
            chord_library[note_name] = frequency
        
        return chord_library

    #  To get the chord name, i.e. C4, etc,
    def get_chord(self, frequency):
        chord_library = self.generate_chord_library()
        min_distance = float('inf')
        closest_note = 'A4'

        # Iterates over chord library, calculate distance, and update the closest note
        for note, freq in chord_library.items():
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

    def modulate(self):
        self.rootsound = self.generate_wave(amplitude=self.rootamplitude, waveform_type=self.rootwaveform, frequency=self.rootfrequency)
        lfowave = self.generate_wave(amplitude=self.lfoamplitude, waveform_type=self.lfowaveform, frequency=self.lfofrequency)

        # Frequency modulation
        if self.freq_mod is True:
            self.amp_mod = False
            modulation_index = 1
            t = np.linspace(0, self.duration, int(self.sample_rate * self.duration), endpoint=False)
            modulated_frequency = self.rootfrequency + modulation_index * lfowave
            return np.sin(2 * np.pi * modulated_frequency * t)  # Generate the modulated wave directly

        # Amplitude modulation
        if self.amp_mod is True:
            self.freq_mod = False
            return self.rootsound * (1 + lfowave)
        
        # No LFO applied
        if self.amp_mod is False and self.freq_mod is False:
            return self.rootsound

    # Play the generated wave
    def play_tone(self):
        while not self.stop_event.is_set(): 
            # Play the current sound with an overlap
            self.modulatedsound = self.modulate()
            sd.play(self.modulatedsound, self.sample_rate, blocking=True)

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