✋ Hand Gesture Volume Control

A Computer Vision project that allows users to control the system volume using hand gestures through a webcam. The system detects hand landmarks and adjusts the volume based on the distance between fingers.

This project demonstrates touchless human-computer interaction using real-time hand tracking.

🚀 Features

🎥 Real-time hand detection using webcam

✋ Thumb + Index finger distance controls system volume

🔇 Thumb + Pinky pinch gesture mutes the volume

📊 Smooth volume transition to avoid sudden jumps

🧠 Uses hand landmark detection for accurate gesture tracking

🛠 Technologies Used

Python

OpenCV – video processing

MediaPipe – hand landmark detection

PyCaw – system audio control (Windows)

NumPy

Math / Time modules

⚙️ How It Works

The webcam captures live video.

The system detects the hand using MediaPipe Hand Tracking.

Key finger landmarks are extracted:

Thumb tip

Index finger tip

Pinky tip

The distance between fingers is calculated.

Gesture Actions
Gesture	Action
Thumb + Index distance	Controls volume level
Thumb + Pinky pinch	Mute volume

The volume is adjusted smoothly using a smoothing algorithm to prevent sudden changes.
