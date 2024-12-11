# Gesture and Voice-Based Calculator

This project introduces a calculator that allows users to perform mathematical operations using hand gestures and voice commands. It leverages Mediapipe for gesture detection and Google Web Speech API for voice recognition, combined with a PySide6 GUI for an interactive user interface.

## Prerequisites
- **Python Version:** Python 3.10.13
- **Operating System:** Cross-platform (Windows/Linux/MacOS)

Ensure you have Python installed. If not, download and install Python from [python.org](https://www.python.org/downloads/).

## Installation Guide

### 1. Clone the Repository
```bash
$ git clone https://github.com/anikaduskar/GestureVoiceCalculator.git
$ cd GestureVoiceCalculator
```

### 2. Create and Activate a Virtual Environment
It is recommended to use a virtual environment to manage dependencies.

#### Windows
```bash
$ python -m venv venv
$ venv\Scripts\activate
```

#### macOS/Linux
```bash
$ python3 -m venv venv
$ source venv/bin/activate
```

### 3. Install Required Libraries
Manually install the following libraries:

```bash
$ pip install PySide6 mediapipe opencv-python numpy SpeechRecognition
```

### 4. Additional Dependencies
#### For Voice Recognition:
Ensure you have a microphone set up and accessible for the `speech_recognition` library to function properly.

#### For Mediapipe:
Mediapipe works with OpenCV. Ensure your system's webcam is functional for gesture detection.

### 5. Running the Application
Execute the application by running the `main.py` file:

```bash
$ python main.py
```

### 6. Directory Structure
Ensure the following structure is maintained:
```
GestureVoiceCalculator/
├── main.py
├── voice_module.py
├── gui.py
```

### 7. Troubleshooting
- **Webcam Issues:** Ensure your webcam is not being used by another application.
- **Microphone Issues:** Test the microphone setup using basic voice recording tools to ensure it is functional.
- **Missing Libraries:** Run `$ pip install` for any missing library errors.
- **Permission Errors:** Run the application with appropriate permissions (e.g., `sudo` on Linux).

## Features
- Gesture recognition for selecting numbers and operators.
- Voice commands for performing mathematical calculations.
- Real-time feedback through a modern GUI.
- Handles invalid expressions (e.g., division by zero) gracefully.

## Dependencies
- **PySide6:** For building the graphical user interface.
- **Mediapipe:** For gesture detection using a webcam.
- **OpenCV:** For processing webcam input.
- **SpeechRecognition:** For interpreting voice commands.



