import tkinter
import customtkinter
import Tone

def generateTone():
    global sound_instance
    freq = frequency_var.get()
    sound_instance = Tone.sine(freq)

def stopTone():
    Tone.stop(sound_instance)

# System Settings
customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

# App Frame
app = customtkinter.CTk()
app.geometry("720x480")
app.title("Sinus Wave Generator")

# UI Element
title = customtkinter.CTkLabel(app, text = "Insert Frequency(Hz)")
title.pack(padx=10, pady=10)

# Frequency Input
frequency_var = tkinter.IntVar()
frequency = customtkinter.CTkEntry(app, width=350, height=40, textvariable=frequency_var)
frequency.pack(padx=10, pady=10)

# Start Button
play = customtkinter.CTkButton(app, text="Start", command=generateTone)
play.pack()

# Stop Button
stop = customtkinter.CTkButton(app, text="Stop", command=stopTone)
stop.pack()

# Run app
app.mainloop()