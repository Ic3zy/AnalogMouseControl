# Gamepad Mouse Controller

![License](https://img.shields.io/badge/license-MIT-green)
![Made By](https://img.shields.io/badge/Coded%20By-Ic3zy-blue)

This Python script allows you to control your mouse cursor using a gamepad.

Use the left and right bumpers (L1 and R1) to simulate **left** and **right mouse clicks**.  
Use the triggers (L2 and R2) to control the **middle mouse button (scroll wheel)** for zooming in and out.

---

## ⚙️ Features

- Control mouse cursor movement using joystick axes  
- Left bumper (L1) triggers left click  
- Right bumper (R1) triggers right click  
- Left trigger (L2) and right trigger (R2) control middle mouse button (scroll wheel)  
- Smooth and responsive input with deadzone and acceleration  
- Runs in the background with threading

---

## 🧠 How It Works

The script reads the gamepad’s analog stick positions, applies deadzone filtering and acceleration, then moves the mouse cursor accordingly.  
Button presses on L1 and R1 simulate left and right mouse clicks.  
Triggers L2 and R2 activate scrolling up and down via the middle mouse button.  
All mouse input is sent using Windows API calls for accurate control.

---

## 🛠 Requirements

- Python 3.8 or higher  
- `pygame` module  

Install dependencies with:

```
pip install -r req.txt
```

---

## 🚀 Usage

1. Connect your gamepad to your PC.  
2. Run the script:

```
python main.py
```

3. Use your gamepad to move the mouse cursor and perform clicks/scrolls.

---

## ⚠️ Notes

- This script is designed for Windows and uses Windows-specific APIs.  
- Make sure you run the script with necessary permissions if you encounter issues.  
- Use responsibly and avoid interfering with other applications.

---

## 📄 License

This project is licensed under the **MIT License**.

---

## 👨‍💻 Author

**CodedBy:** Ic3zy
