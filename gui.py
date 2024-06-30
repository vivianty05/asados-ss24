from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.core.audio import SoundLoader
from kivy.uix.spinner import Spinner
import functionality

class Synthesizer(App):
    def build(self):
        self.window = GridLayout()
        self.window.cols = 1
        self.window.size_hint = (0.6,0.7)
        self.window.pos_hint = {"center_x": 0.5,"center_y": 0.5}
        # Add widgets to window
        
        # Base frequency label widget
        self.frequency = Label(
            text="Insert Frequency",
            font_size=50,
            )
        self.window.add_widget(self.frequency)
        
        # Text input widget
        self.user = TextInput(
            multiline=False,        # Restricts to input to a single line only not multiple
            padding_y=(10,10),
            size_hint=(1, None),    # Set width to 100% and height to fixed size
            height=55               # Adjust height as needed to accommodate the text
            )
        self.window.add_widget(self.user)
        
        # Button widget
        self.button = Button(
            text="START",
            size_hint=(1, 0.25),
            background_color=(0, 1, 0, 1) # Green color
            )
        self.button.bind(on_press=self.callback)
        self.window.add_widget(self.button)

        # Keynote Buttons Grid
        self.keynote_grid = GridLayout()
        self.keynote_grid.cols = 4

        # Keynote C4
        self.button1 = Button (
            text = "C4", 
            background_color = (0, 1, 0, 1) # Green color
            )
        self.button1.bind(on_press=self.chordC4)                  
        self.keynote_grid.add_widget(self.button1)

        # Keynote C#4/Db4
        self.button2 = Button (
            text = "C#4/Db4", 
            background_color = (0, 1, 0, 1) # Green color
            )
        self.button2.bind(on_press=self.chordDb4)                  
        self.keynote_grid.add_widget(self.button2)

        # Keynote D4
        self.button3 = Button (
            text = "D4", 
            background_color = (0, 1, 0, 1) # Green color
            )
        self.button3.bind(on_press=self.chordD4)                  
        self.keynote_grid.add_widget(self.button3)

        # Keynote D#4/Eb4	
        self.button4 = Button (
            text = "D#4/Eb4", 
            background_color = (0, 1, 0, 1) # Green color
            )
        self.button4.bind(on_press=self.chordEb4)                  
        self.keynote_grid.add_widget(self.button4)

        # Keynote E4
        self.button5 = Button (
            text = "E4", 
            background_color = (0, 1, 0, 1) # Green color
            )
        self.button5.bind(on_press=self.chordE4)   
        self.keynote_grid.add_widget(self.button5)
        
        # Keynote F4
        self.button6 = Button (
            text = "F4", 
            background_color = (0, 1, 0, 1) # Green color
            )
        self.button6.bind(on_press=self.chordF4)
        self.keynote_grid.add_widget(self.button6)
      
        # Keynote F#4/Gb4	
        self.button7 = Button (
            text = "F#4/Gb4", 
            background_color = (0, 1, 0, 1) # Green color
            )
        self.button7.bind(on_press=self.chordGb4)
        self.keynote_grid.add_widget(self.button7)

        # Keynote G4	
        self.button8 = Button (
            text = "G4", 
            background_color = (0, 1, 0, 1) # Green color
            )
        self.button8.bind(on_press=self.chordG4)
        self.keynote_grid.add_widget(self.button8)

        # Keynote G#4/Ab4	
        self.button9 = Button (
            text = "G#4/Ab4", 
            background_color = (0, 1, 0, 1) # Green color
            )
        self.button9.bind(on_press=self.chordAb4)
        self.keynote_grid.add_widget(self.button9)

        # Keynote A4	
        self.button10 = Button (
            text = "A4", 
            background_color = (0, 1, 0, 1) # Green color
            )
        self.button10.bind(on_press=self.chordA4)
        self.keynote_grid.add_widget(self.button10)

        # Keynote A#4/Bb4		
        self.button11 = Button (
            text = "A#4/Bb4", 
            background_color = (0, 1, 0, 1) # Green color
            )
        self.button11.bind(on_press=self.chordBb4)
        self.keynote_grid.add_widget(self.button11)

        # Keynote B4		
        self.button12 = Button (
            text = "B4", 
            background_color = (0, 1, 0, 1) # Green color
            )
        self.button12.bind(on_press=self.chordB4)
        self.keynote_grid.add_widget(self.button12)

        self.window.add_widget(self.keynote_grid)

        # LFO frequency label widget
        self.lfo_frequency_label = Label(
            text="LFO Frequency",
            font_size=50,
        )
        self.window.add_widget(self.lfo_frequency_label)

        # LFO Frequency input widget
        self.lfo_frequency_input = TextInput(
            multiline=False,
            padding_y=(10, 10),
            size_hint=(1, None),
            height=55
        )
        self.window.add_widget(self.lfo_frequency_input)

        # LFO Amplitude label
        self.lfo_amplitude_label = Label(
            text="LFO Amplitude",
            font_size=50,
        )
        self.window.add_widget(self.lfo_amplitude_label)

        # LFO Amplitude input widget
        self.lfo_amplitude_input = TextInput(
            multiline=False,
            padding_y=(10, 10),
            size_hint=(1, None),
            height=55
        )
        self.window.add_widget(self.lfo_amplitude_input)

        # LFO Waveform label
        self.lfo_waveform_label = Label(
            text="LFO Waveform",
            font_size=50,
        )
        self.window.add_widget(self.lfo_waveform_label)

        # LFO Waveform selection widget
        self.lfo_waveform_spinner = Spinner(
            text='Pick a waveform',
            size_hint=(1, None),
            height=55,
            font_size=40,
            values=('Sine', 'Square', 'Triangle', 'Sawtooth'),
        )
        self.window.add_widget(self.lfo_waveform_spinner)

        return self.window
    
    def callback(self, instance):   
        if self.button.text == "START":
            duration = 1
            if not self.user.text:
                self.frequency.text = "Please input a valid frequency!"
                return
            try:
                freq = float(self.user.text)
                lfo_freq = float(self.lfo_frequency_input.text) if self.lfo_frequency_input.text else 0.0
                lfo_amp = float(self.lfo_amplitude_input.text) if self.lfo_amplitude_input.text else 0.0
                lfo_waveform = self.lfo_waveform_spinner.text
                modulated_freq = LFO.apply_lfo(freq, lfo_freq, lfo_amp, duration, lfo_waveform, sample_rate)
                self.sound_instance = Tone.sine(modulated_freq)
                self.button.text = "STOP"
                self.button.background_color = (1, 0, 0, 1)  # Red color
            except ValueError:
                self.frequency.text = "Invalid input! Please enter valid numbers."
        else:
            self.button.text = "START"
            Tone.stop(self.sound_instance)
            self.button.background_color = (0, 1, 0, 1)  # Green color

    def chordC4(self, instance):
        if self.button1.text == "C4":
            freq = Keynote.note_to_frequency(self.button1.text)
            self.C4_sound_instance = Tone.sine(freq)
            self.button1.text = "STOP"
            self.button1.background_color = (1, 0, 0, 1) # Red color
        else:
            self.button1.text = "C4"
            Tone.stop(self.C4_sound_instance)
            self.button1.background_color = (0, 1, 0, 1) # Green color
    
    def chordDb4(self, instance):
        if self.button2.text == "C#4/Db4":
            freq = Keynote.note_to_frequency("Db4")
            self.Db4_sound_instance = Tone.sine(freq)
            self.button2.text = "STOP"
            self.button2.background_color = (1, 0, 0, 1) # Red color
        else:
            self.button2.text = "C#4/Db4"
            Tone.stop(self.Db4_sound_instance)
            self.button2.background_color = (0, 1, 0, 1) # Green color

    def chordD4(self, instance):
        if self.button3.text == "D4":
            freq = Keynote.note_to_frequency(self.button3.text)
            self.D4_sound_instance = Tone.sine(freq)
            self.button3.text = "STOP"
            self.button3.background_color = (1, 0, 0, 1) # Red color
        else:
            self.button3.text = "D4"
            Tone.stop(self.D4_sound_instance)
            self.button3.background_color = (0, 1, 0, 1) # Green color

    def chordEb4(self, instance):
        if self.button4.text == "D#4/Eb4":
            freq = Keynote.note_to_frequency("Eb4")
            self.Eb4_sound_instance = Tone.sine(freq)
            self.button4.text = "STOP"
            self.button4.background_color = (1, 0, 0, 1) # Red color
        else:
            self.button4.text = "D#4/Eb4"
            Tone.stop(self.Eb4_sound_instance)
            self.button4.background_color = (0, 1, 0, 1) # Green color

    def chordE4(self, instance):
        if self.button5.text == "E4":
            freq = Keynote.note_to_frequency(self.button5.text)
            self.E4_sound_instance = Tone.sine(freq)
            self.button5.text = "STOP"
            self.button5.background_color = (1, 0, 0, 1) # Red color
        else:
            self.button5.text = "E4"
            Tone.stop(self.E4_sound_instance)
            self.button5.background_color = (0, 1, 0, 1) # Green color

    def chordF4(self, instance):
        if self.button6.text == "F4":
            freq = Keynote.note_to_frequency(self.button6.text)
            self.F4_sound_instance = Tone.sine(freq)
            self.button6.text = "STOP"
            self.button6.background_color = (1, 0, 0, 1) # Red color
        else:
            self.button6.text = "F4"
            Tone.stop(self.F4_sound_instance)
            self.button6.background_color = (0, 1, 0, 1) # Green color

    def chordGb4(self, instance):
        if self.button7.text == "F#4/Gb4":
            freq = Keynote.note_to_frequency("Gb4")
            self.Gb4_sound_instance = Tone.sine(freq)
            self.button7.text = "STOP"
            self.button7.background_color = (1, 0, 0, 1) # Red color
        else:
            self.button7.text = "F#4/Gb4"
            Tone.stop(self.Gb4_sound_instance)
            self.button7.background_color = (0, 1, 0, 1) # Green color
            
    def chordG4(self, instance):
        if self.button8.text == "G4":
            freq = Keynote.note_to_frequency(self.button8.text)
            self.G4_sound_instance = Tone.sine(freq)
            self.button8.text = "STOP"
            self.button8.background_color = (1, 0, 0, 1) # Red color
        else:
            self.button8.text = "G4"
            Tone.stop(self.G4_sound_instance)
            self.button8.background_color = (0, 1, 0, 1) # Green color

    def chordAb4(self, instance):
        if self.button9.text == "G#4/Ab4":
            freq = Keynote.note_to_frequency("Ab4")
            self.Ab4_sound_instance = Tone.sine(freq)
            self.button9.text = "STOP"
            self.button9.background_color = (1, 0, 0, 1) # Red color
        else:
            self.button9.text = "G#4/Ab4"
            Tone.stop(self.Ab4_sound_instance)
            self.button9.background_color = (0, 1, 0, 1) # Green color

    def chordA4(self, instance):
        if self.button10.text == "A4":
            freq = Keynote.note_to_frequency(self.button10.text)
            self.A4_sound_instance = Tone.sine(freq)
            self.button10.text = "STOP"
            self.button10.background_color = (1, 0, 0, 1) # Red color
        else:
            self.button10.text = "A4"
            Tone.stop(self.A4_sound_instance)
            self.button10.background_color = (0, 1, 0, 1) # Green color

    def chordBb4(self, instance):
        if self.button11.text == "A#4/Bb4":
            freq = Keynote.note_to_frequency("Bb4")
            self.Bb4_sound_instance = Tone.sine(freq)
            self.button11.text = "STOP"
            self.button11.background_color = (1, 0, 0, 1) # Red color
        else:
            self.button11.text = "A#4/Bb4"
            Tone.stop(self.Bb4_sound_instance)
            self.button11.background_color = (0, 1, 0, 1) # Green color

    def chordB4(self, instance):
        if self.button12.text == "B4":
            freq = Keynote.note_to_frequency(self.button12.text)
            self.B4_sound_instance = Tone.sine(freq)
            self.button12.text = "STOP"
            self.button12.background_color = (1, 0, 0, 1) # Red color
        else:
            self.button12.text = "B4"
            Tone.stop(self.B4_sound_instance)
            self.button12.background_color = (0, 1, 0, 1) # Green color
            
        
if __name__ == "__main__":
    Synthesizer().run()