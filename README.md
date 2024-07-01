# ASADOS-SS24

## An Android synthesizer app for drone and overtone singing

This project aims to develop an innovative and user-friendly mobile application that provides a dynamic and enriching drone experience for practicing drone and overtone singers. This app will harness the rich, pitch-stable tones of the Indian Tanpura and the advanced harmonic capabilities of modular synthesizers to support and enhance vocal practice.


## Table of Content:
1. Features
2. Installation
3. Deployment
4. Usage
5. Challenges and Solutions
6. Authors


## Features


## Installation 
1. Clone this repository. To do so, execute this command below on a bash window.
```
git clone https://mygit.th-deg.de/mmayer/asados-ss24.git
```
2. Navigate to the project directory.
```
cd asados-ss24
```
3. Create a virtual environment.
```
python -m venv venv
```
4. Activate the virtual environment.
- On Windows:
```
venv\Scripts\activate
```
- On Unix/MacOS:
```
source venv/bin/activate
```
5. Install dependencies 
```
pip install -r requirements.txt
```
5. Run the app using this command.


## Deployment 
The method we use to deploy Python Project to Android is by using Window Subsystem for Linux. The reason is that Windows operating system is not compatible to convert a Python project into an Android apk. By using a subsystem, we can use an operating system such as Ubuntu to help convert the Python project to Android with Android Debug Bridge.

### Deployment Steps
1. Install Window Subsystem for Linux
   - By using Windows Powershell, follow the steps from https://learn.microsoft.com/en-us/windows/wsl/install to install the subsystem.
2. Install Ubuntu from the Microsoft Store and run.
   - When Ubuntu is installed and first time setup is done, change the directory in the Ubuntu to the folder that you are working with the Python project (e.g: cd /mnt/c/Users/Documents/Project)
3. Install Buildozer and dependencies
   - To install Buildozer and the dependencies, follow the step from https://buildozer.readthedocs.io/en/latest/installation.html 
4. Setup Android Debug Bridge (adb)
   - Firstly install apt adb in Ubuntu by typing in `sudo apt install adb` to install the Android Debug Bridge in Ubuntu.
   - Then download Android SDK Platform Tools for Android from https://developer.android.com/tools/releases/platform-tools#downloads, then copy the first three files from the zip. (adb, AdbWinApi.dll, AdbWinUsbApi.dll) into the folder that you are working on.
5. Make sure to have the same version of Android Debug Bridge
   - The adb files that you have downloaded, it must have the same version as in Ubuntu.
   - In Ubuntu, simply type `./adb --version` to check which version of ADB that is installed.
   - From the folder that you are working on, simply press 'Shift' and 'Right Click', and choose 'Open Window Powershell here'. In the Powershell, type `./adb --version`.
   - If both have the same version, you are good to go.
6. Enable developer option in Android device
   - In your Android device setting, head to 'About phone' and keep pressing 'Build number' until developer mode is enabled.
   - Once developer mode is enabled, in the setting now will have developer option. Press developer option and enable USB debugging.(with your device connected to PC)
7. Create buildozer.spec file
   - In Ubuntu, type `buildozer init` and it will create a buildozer.spec file in the folder of your project.
   - Configure the buildozer.spec file and make sure that all requirements needed by your projects is included.
8. Start Window adb server
   - Open Windows Powershell from the project folder and type `./adb start-server`
   - To make sure that your device is connected to the bridge, type `./adb devices`
9. Start debug
   - In Ubuntu, type `buildozer -v android debug` to start the debugging process. The process can take quite some time (45-90 minutes) depending on how complex your project is.
   - If during your **first** debug process encounter a failure such as 'Buildozer failed to execute the last command' right after you debug, simply type `sudo mount -t C: /mnt/c/ -o metadata`. This is to ensure that all necessary files and resources are accessible from your Ubuntu environment.

### Additional
In the case of the steps being unclear to some, here is a link to a Youtube video that explain the same steps clearly.
 - https://youtu.be/VsTaM057rdc?si=tGtEpw-M5N5SPEgh


## Usage
**1. Base Frequency Input**

![Entering the base frequency](/uploads/5251251bd37fbfba93b22349d14294e1/Screen_Recording_2024-07-01_at_22.14.07.MOV)

Users can enter a base frequency for A4 using the text field. This sets the fundamental frequency for the synthesizer.

**2. Key Notes Adjustment**

![Using sliders to pick key notes](/uploads/ab6ec061ccb4fca56c9377198db41414/Screen_Recording_2024-07-01_at_22.14.07_2.MOV)

This slider allows users to adjust the key notes they want to play continuously.

**3. Start/Stop Button**

![Start or stop button](/uploads/798712f6c28448931deeaaaa3f21ca8d/Screen_Recording_2024-07-01_at_22.14.07_6.MOV)

The button labeled "Start" starts the playback of the synthesized sound when pressed. This action initializes the sound generation and enables continuous playback. Upon pressing the button, it changes its text to "Stop". Pressing it again stops the playback, halting the sound generation process.

**4. LFO (Low Frequency Oscillator) Settings**

Users can configure LFO settings for modulation: 
- Destination: Users can select either Amplitude Modulation (AM) or Frequency Modulation (FM) using checkboxes.

![Checking which destination for LFO](/uploads/aeb99aaefa6db3202de32911979d3a0f/Screen_Recording_2024-07-01_at_22.14.07_3.MOV)

- Waveform: Users can choose from different waveforms (Sine, Square, Sawtooth, Triangle) for the LFO modulation using checkboxes.

![Checking which waveform to use](/uploads/7f2e04bcd14d6592a7ebac3456ca765b/Screen_Recording_2024-07-01_at_22.14.07_4.MOV)

- Frequency and Amplitude: Sliders allow users to set the frequency and amplitude of the LFO.

![Adjusting frequency and amplitude modulation](/uploads/eeaee735a3fec14c8491ad5399e2a7ee/Screen_Recording_2024-07-01_at_22.14.07_5.MOV)


## Challenges and Solutions
During this project, we have encountered a few problems with the development and this is how we fixed the problem: 
### Challenge 1  
**Problem:**  
Finding the most suitable audio module that is compatible with android environment.
**Solution:**  
After tons of researches, we decided to use pyjnius as the sound module since it is the most Android-friendly module.
### Challenge 2
**Problem:**  
When using pyjnius, it can only be tested in an Android environment which you either have to deploy after every change or have an Android emulator.  
**Solution:**  
There is no solution at the moment other than deploying the project after every major changes.
### Challenge 3
**Problem:**  
Numpy works when running the project through the terminal, but unfortunately it does not compatible with Android so there are some functions that works best with numpy that cannot be implemented using only pyjnius.  
**Solution:**  
Using the basic Python libraries to create the same functionality as numpy.  
### Challenge 4  
**Problem:**  
Project that has been deployed using only pyjnius as audio module have some trouble generating LFO waveforms.  
**Solution:**  
There is no solution at the moment, as the function works best by using numpy.
## Authors
- Aiman Bin Hassim [@ab23568](https://mygit.th-deg.de/ab23568)
- Isabella Yang [@isabella.yang](https://mygit.th-deg.de/isabella.yang)
- Vivian Yang [@vy16417](https://mygit.th-deg.de/vy16417)

