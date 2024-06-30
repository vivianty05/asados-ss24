import pyaudio
import pygame
import numpy
import math
import time
import threading

class Tone(App):
    pygame.init()

bits = 16
sample_rate = 44100

pygame.mixer.pre_init(sample_rate, bits)

# Calculates the amplitude of a sine wave at a given frequency and time
def sine_x(amp, freq, time):
    return int(round(amp * math.sin(2 * math.pi * freq * time)))

class Tone:        
    # Generates and plays sine wave
    def sine(freq_input, speaker=None):
        if isinstance(freq_input, (int, float)):
            freq_array = numpy.full((sample_rate,), freq_input)
        else:
            freq_array = freq_input

        num_samples = len(freq_array)

        sound_buffer = numpy.zeros((num_samples, 2), dtype=numpy.int16)
        amplitude = 2 ** (bits - 1) - 1

        for sample_num in range(num_samples):
            t = float(sample_num) / sample_rate

            sine = sine_x(amplitude, freq_array[sample_num], t)

            if speaker == 'r':
                sound_buffer[sample_num][1] = sine
            elif speaker == 'l':
                sound_buffer[sample_num][0] = sine
            else:
                sound_buffer[sample_num][1] = sine
                sound_buffer[sample_num][0] = sine

        sound = pygame.sndarray.make_sound(sound_buffer)
        sound.play(loops=-1)    # Makes the sound play infinitely
        return sound
    
    def stop(sound):
        sound.stop()


class LFO:
    # Generates LFO waveform 
    def lfo_waveform(freq, duration, waveform, sample_rate=44100):
        t = numpy.arange(int(duration * sample_rate)) / sample_rate
        # Square waveform
        if waveform == "square":
            return numpy.sign(numpy.sin(2 * numpy.pi * freq * t))
        # Triangle waveform
        elif waveform == "triangle":
            return 2 * numpy.abs(2 * (t * freq - numpy.floor(t * freq + 0.5))) - 1
        # Sawtooth waveform
        elif waveform == "sawtooth":
            return 2 * (t * freq - numpy.floor(t * freq + 0.5))
        else:
            # Default to sine wave
            return numpy.sin(2 * numpy.pi * freq * t)  
        
    # Applies LFO to modulate the frequency of the sine wave
    def apply_lfo(base_freq, lfo_freq, lfo_amp, duration, waveform, sample_rate=44100):
        lfo_wave = LFO.lfo_waveform(lfo_freq, duration, waveform, sample_rate)
        modulated_freq = base_freq + lfo_amp * lfo_wave
        return modulated_freq


class Keynote():
    # Dictionary to map note names to key numbers
    note_to_key = {
        "C4" : 40, "C#4" : 41, "Db4" : 41, "D4": 42,
        "D#4": 43, "Eb4": 43, "E4": 44, "F4": 45, 
        "F#4": 46, "Gb4": 46, "G4": 47, "G#4": 48, 
        "Ab4": 48, "A4": 49, "A#4": 50, "Bb4": 50, "B4": 51
    }

    # Convert the chosen keynote into frequency
    def note_to_frequency(note):
        if note in Keynote.note_to_key:
            key_number = Keynote.note_to_key[note]
            A4_key_number = 49  # Key number of A4
            A4_frequency = 440  # Frequency of A4 in Hz

            # Formula to determine the frequency of the chosen keynote
            frequency = 2 ** ((key_number - A4_key_number) / 12) * A4_frequency
            return frequency
        else:
            raise ValueError("Invalid note name")