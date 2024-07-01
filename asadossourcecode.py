# ASADOS - Android Synthesizer App for Drone and Overtone Singing
# File      : asadossourcecode.py
# Subject   : Wahlpflichtfach Projekt ASADOS, Sommersemester 2024
# Authors   : Aiman Bin Hassim, Isabella Yang, Vivian Yang
# Date      : 01/07/2024
# This file contains the source code for the ASADOS app. This code implements a sound synthesizer using KivyMD  
# for the GUI and Android audio classes for sound generation. Users can set a base frequency, adjust the root frequency,  
# and apply LFO to modulate amplitude or frequency with various waveforms. The app supports continuous sound playback  
# with real-time parameter adjustments.
import kivy
kivy.require('2.3.0')
import time
import math
from jnius import autoclass, cast
import array
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

# Android Audio Classes
AudioFormat = autoclass('android.media.AudioFormat')
AudioManager = autoclass('android.media.AudioManager')
AudioTrack = autoclass('android.media.AudioTrack')

# GUI Code
KV = '''
MDScreen:
    BoxLayout:
        orientation: 'vertical'
        padding: dp(20)
        spacing: dp(20)

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

            MDTextField:
                id: A4frequency_value
                hint_text: "Enter frequency for A4"
                helper_text: "Only numbers are allowed"
                helper_text_mode: "on_focus"
                input_filter: 'float'
                halign: 'center'
                font_style: 'Subtitle1'

            MDRaisedButton:
                text: "Enter"
                pos_hint: {'center_x': 0.5}
                on_release: app.update_A4frequency()
                size_hint_x: None
                width: dp(100)

        MDSlider:
            id: rootfrequency_slider
            min: 0
            max: 8000
            value: 440
            hint: False
            on_value: app.update_rootfrequency(self.value)
            value_track: True
            value_track_color: app.theme_cls.primary_color

        BoxLayout:
            orientation: 'horizontal'
            padding: dp(20)
            spacing: dp(20)

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

            MDSlider:
                id: lfofrequency_slider
                min: 0.0
                max: 20.0
                value: 0.0
                on_value: app.update_lfofrequency(self.value)

        BoxLayout: 
            padding: dp(10)
            spacing: dp(10)

            MDLabel:
                text: "LFO Amplitude"
                halign: 'center'
                font_style: 'H6'

            MDSlider:
                id: lfoamplitude_slider
                min: 0.0
                max: 1.0
                value: 0.0
                on_value: app.update_lfoamplitude(self.value)

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

class ToneGeneratorApp(MDApp):
    def build(self):
        self.rootwaveform = 'sine'
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
        self.buffer_size = 1024
        self.stop_event = Event()
        self.thread = None

        self.audio_track = AudioTrack(
            AudioManager.STREAM_MUSIC,
            self.sample_rate,
            AudioFormat.CHANNEL_OUT_MONO,
            AudioFormat.ENCODING_PCM_16BIT,
            self.buffer_size,
            AudioTrack.MODE_STREAM
        )

        self.screen = Builder.load_string(KV)
        return self.screen

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

    def set_lfowaveform(self, waveform, active):
        if active: 
            self.lfowaveform = waveform

    def update_A4frequency(self):
        self.A4frequency = float(self.screen.ids.A4frequency_value.text)

    def update_rootfrequency(self, value):
        self.rootfrequency = value
        self.screen.ids.rootfrequency_value.text = f"{value:.0f} Hz"
        self.screen.ids.chord_value.text = self.get_chord(value)

    def update_lfofrequency(self, value):
        self.lfofrequency = value

    def update_lfoamplitude(self, value):
        self.lfoamplitude = value

    def generate_chord_library(self):
        note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        chord_library = {}
        
        for midi_number in range(0, 128):
            frequency = self.A4frequency * 2 ** ((midi_number - 69) / 12)
            octave = (midi_number // 12) - 1
            note = note_names[midi_number % 12]
            note_name = f"{note}{octave}"
            chord_library[note_name] = frequency
        
        return chord_library

    def get_chord(self, frequency):
        chord_library = self.generate_chord_library()
        min_distance = float('inf')
        closest_note = 'A4'

        for note, freq in chord_library.items():
            distance = abs(frequency - freq)
            if distance < min_distance:
                min_distance = distance
                closest_note = note

        return closest_note

    def generate_wave(self, amplitude, waveform_type, frequency):
        wave = []
        increment = (2 * math.pi * frequency) / self.sample_rate
        angle = 0

        for _ in range(self.buffer_size):
            if waveform_type == 'sine':
                sample = amplitude * math.sin(angle)
            elif waveform_type == 'square':
                sample = amplitude * (1 if math.sin(angle) >= 0 else -1)
            elif waveform_type == 'sawtooth':
                sample = amplitude * (2 * (angle / (2 * math.pi)) - 1)
            elif waveform_type == 'triangle':
                sample = amplitude * (2 * abs(2 * (angle / (2 * math.pi)) - 1) - 1)

            wave.append(sample)
            angle += increment
            if angle > 2 * math.pi:
                angle -= 2 * math.pi

        return wave

    def modulate(self):
        self.rootsound = self.generate_wave(self.rootamplitude, self.rootwaveform, self.rootfrequency)
        lfowave = self.generate_wave(self.lfoamplitude, self.lfowaveform, self.lfofrequency)

        if self.freq_mod:
            self.amp_mod = False
            modulated_wave = []
            for i in range(self.buffer_size):
                modulated_frequency = self.rootfrequency + lfowave[i]
                modulated_wave.append(math.sin(2 * math.pi * modulated_frequency * (i / self.sample_rate)))
            return modulated_wave

        if self.amp_mod:
            self.freq_mod = False
            return [self.rootsound[i] * (1 + lfowave[i]) for i in range(self.buffer_size)]
        
        if not self.amp_mod and not self.freq_mod:
            return self.rootsound

    def play_tone(self):
        self.audio_track.play()
        while not self.stop_event.is_set(): 
            self.modulatedsound = self.modulate()
            buffer = array.array('h', [int(sample * 32767) for sample in self.modulatedsound]).tobytes()
            self.audio_track.write(buffer, 0, len(buffer))

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
        self.audio_track.stop()
        self.audio_track.release()

if __name__ == '__main__':
    ToneGeneratorApp().run()
