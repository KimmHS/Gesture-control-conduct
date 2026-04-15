I want to start from this repository as a reference:

https://github.com/SongxiangT/Conductor-Simulator

Use it as inspiration and partial structural reference, but do NOT preserve outdated design choices just because they already exist.
Modernize the project where appropriate.

Project goal:
Build a demo-first webcam-based conducting system for a class project.
The goal is not research-grade conducting recognition.
The goal is a stable, visually convincing live demo.

Important context:
The reference repo already uses hand gestures to control tempo and volume, with MediaPipe-based hand tracking, a GUI flow, and VLC-based music playback.
It appears to rely on both hands, uses gesture-like cues for pause/continue, and has some known fragility around initialization and cue detection.
I want a cleaner and more modern version of this idea.

What to preserve conceptually:
- webcam-based conducting interaction
- real-time control of music playback
- tempo control
- dynamics/volume control
- live visual feedback

What to improve:
- reduce fragile hand-pose-only logic
- shift toward trajectory-based conducting interpretation where useful
- simplify the demo flow
- make the system presentation-safe
- modernize the code structure
- avoid brittle initialization assumptions
- avoid over-sensitive cue logic
- make thresholds configurable
- add fallback keyboard controls
- prefer modular architecture over a monolithic script flow

Preferred stack:
- Python
- OpenCV
- MediaPipe
- lightweight playback backend
- configurable modules
- easy local execution on one laptop

Behavioral design:
- Treat static hand shape recognition as optional
- Treat wrist / hand motion over time as the main signal
- Tempo should come from conducting speed / periodicity
- Dynamics should come from motion size / amplitude
- Start/stop can use either a simple gesture or a manual fallback key
- Optimize for demo stability, not generality

Do not start coding immediately.

First:
1. inspect the repository structure
2. summarize what parts are worth reusing conceptually
3. identify outdated or fragile design choices
4. propose a modernized MVP architecture
5. propose a folder structure
6. list the minimum viable implementation order

Then implement incrementally:
1. project skeleton
2. webcam + landmark tracking
3. wrist trajectory buffer
4. tempo estimation from motion
5. dynamics estimation from motion size
6. playback backend integration
7. on-screen overlay
8. calibration
9. keyboard fallback controls
10. concise README

While implementing:
- avoid overengineering
- keep dependencies light
- keep interfaces clean
- make demo-critical paths robust
- prefer the simplest working version first