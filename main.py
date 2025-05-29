# CodedBy: Ic3zy
# License: MIT
# Description:
# Easily control your mouse pointer with a gamepad — move the cursor with analog sticks, click with L1/R1, and scroll with L2/R2. Perfect for gaming or hands-free navigation!

import ctypes
import pygame
import threading
import time
import math
from dataclasses import dataclass
import logging

# Configure logging format and level
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Define pointer type for INPUT structures
PUL = ctypes.POINTER(ctypes.c_ulong)

# Define MOUSEINPUT structure
class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.c_long),
        ("dy", ctypes.c_long),
        ("mouseData", ctypes.c_ulong),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", PUL)
    ]

# Define INPUT_I union with only mouse input
class INPUT_I(ctypes.Union):
    _fields_ = [("mi", MOUSEINPUT)]

# Define general INPUT structure
class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_ulong),
        ("ii", INPUT_I)
    ]

# Send relative mouse movement

def mouse_move(x, y):
    inp = INPUT(type=0, ii=INPUT_I(mi=MOUSEINPUT(x, y, 0, 0x0001, 0, None)))
    ctypes.windll.user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))

# Send mouse click events

def mouse_click(down=True, button='left'):
    flags = {'left': (0x0002, 0x0004), 'right': (0x0008, 0x0010)}
    flag = flags[button][0] if down else flags[button][1]
    inp = INPUT(type=0, ii=INPUT_I(mi=MOUSEINPUT(0, 0, 0, flag, 0, None)))
    ctypes.windll.user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))

# Simulate mouse scroll wheel

def mouse_scroll(amount):
    inp = INPUT(type=0, ii=INPUT_I(mi=MOUSEINPUT(0, 0, amount, 0x0800, 0, None)))
    ctypes.windll.user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))

# Configuration dataclass for gamepad behavior
@dataclass
class GamepadConfig:
    left_max_speed: int = 20
    left_acceleration: float = 0.4
    left_deadzone: float = 0
    right_max_speed: int = 5
    right_acceleration: float = 0.1
    right_deadzone: float = 0
    refresh_rate: float = 0.005
    left_click_button: int = 7
    right_click_button: int = 6
    scroll_up_button: int = 4
    scroll_down_button: int = 5
    left_x_axis: int = 0
    left_y_axis: int = 1
    right_x_axis: int = 2
    right_y_axis: int = 4
    restart_delay: float = 0.5

# Main controller class for gamepad to mouse mapping
class GamepadController:
    def __init__(self, config: GamepadConfig):
        self.config = config
        self.gamepad = None
        self.running = False
        self.left_motion = (0, 0)
        self.right_motion = (0, 0)
        self.left_speed = 0
        self.right_speed = 0
        self.button_states = {'left_click': False, 'right_click': False}
        self.scroll_thread_active = {'up': False, 'down': False}
        self._init_pygame()
        self._connect_gamepad()

    def _init_pygame(self):
        pygame.init()
        pygame.joystick.init()

    def _connect_gamepad(self):
        if pygame.joystick.get_count() == 0:
            raise ConnectionError("No gamepad found!")
        self.gamepad = pygame.joystick.Joystick(0)
        self.gamepad.init()

    def _apply_deadzone(self, value, deadzone):
        return 0 if abs(value) <= deadzone else math.copysign((abs(value) - deadzone) / (1 - deadzone), value)

    def _calculate_motion(self, x, y, max_speed, acceleration, current_speed):
        magnitude = math.sqrt(x * x + y * y)
        if magnitude > 0:
            norm_x, norm_y = x / magnitude, y / magnitude
            target_speed = min(magnitude * max_speed, max_speed)
            new_speed = (
                min(target_speed, current_speed + acceleration)
                if target_speed > current_speed
                else max(target_speed, current_speed - acceleration * 2)
            )
            return (norm_x * new_speed, norm_y * new_speed), new_speed
        return (0, 0), 0

    def _scroll_thread(self, direction):
        self.scroll_thread_active[direction] = True
        delay = 0.12
        while self.scroll_thread_active[direction]:
            mouse_scroll(120 if direction == 'up' else -120)
            time.sleep(delay)
            delay = max(0.02, delay * 0.9)

    def _handle_scroll(self):
        up = self.gamepad.get_button(self.config.scroll_up_button)
        down = self.gamepad.get_button(self.config.scroll_down_button)

        if up and not self.scroll_thread_active['up']:
            threading.Thread(target=self._scroll_thread, args=('up',), daemon=True).start()
        elif not up and self.scroll_thread_active['up']:
            self.scroll_thread_active['up'] = False

        if down and not self.scroll_thread_active['down']:
            threading.Thread(target=self._scroll_thread, args=('down',), daemon=True).start()
        elif not down and self.scroll_thread_active['down']:
            self.scroll_thread_active['down'] = False

    def _read_analog_inputs(self):
        lx = self._apply_deadzone(self.gamepad.get_axis(self.config.left_x_axis), self.config.left_deadzone)
        ly = self._apply_deadzone(self.gamepad.get_axis(self.config.left_y_axis), self.config.left_deadzone)
        self.left_motion, self.left_speed = self._calculate_motion(lx, ly, self.config.left_max_speed, self.config.left_acceleration, self.left_speed)

        rx = self._apply_deadzone(self.gamepad.get_axis(self.config.right_x_axis), self.config.right_deadzone)
        ry = self._apply_deadzone(self.gamepad.get_axis(self.config.right_y_axis), self.config.right_deadzone)
        self.right_motion, self.right_speed = self._calculate_motion(rx, ry, self.config.right_max_speed, self.config.right_acceleration, self.right_speed)

    def _handle_buttons(self):
        for key, button in [('left_click', self.config.left_click_button), ('right_click', self.config.right_click_button)]:
            current = self.gamepad.get_button(button)
            if current != self.button_states[key]:
                mouse_click(down=current, button='left' if key == 'left_click' else 'right')
                self.button_states[key] = current

    def _input_listener(self):
        while self.running:
            try:
                pygame.event.pump()
                self._read_analog_inputs()
                self._handle_buttons()
                self._handle_scroll()
                time.sleep(self.config.refresh_rate)
            except Exception as e:
                logging.error(f"Error in input listener: {e}")
                self.stop()
                break

    def _mouse_mover(self):
        while self.running:
            try:
                total_x = self.left_motion[0] + self.right_motion[0]
                total_y = self.left_motion[1] + self.right_motion[1]
                if total_x or total_y:
                    mouse_move(int(total_x), int(total_y))
                time.sleep(self.config.refresh_rate)
            except Exception as e:
                logging.error(f"Error in mouse mover: {e}")
                self.stop()
                break

    def start(self):
        if not self.running:
            self.running = True
            threading.Thread(target=self._input_listener, daemon=True).start()
            threading.Thread(target=self._mouse_mover, daemon=True).start()
            logging.info("Gamepad control started")

    def stop(self):
        self.running = False
        for direction in self.scroll_thread_active:
            self.scroll_thread_active[direction] = False
        logging.info("Gamepad control stopped")

# Entry point for the script

def main():
    config = GamepadConfig
    attempts = 0
    while attempts < 5:
        try:
            controller = GamepadController(config)
            controller.start()
            while controller.running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            break
        except Exception as e:
            logging.error(f"ERROR: {e}")
            attempts += 1
            time.sleep(config.restart_delay)
        finally:
            if 'controller' in locals():
                controller.stop()
            pygame.quit()

if __name__ == "__main__":
    main()