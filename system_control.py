"""
System Control Module - Apps, screenshot, battery, etc.
"""
import os
import subprocess
import logging
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class SystemControl:
    def __init__(self):
        self.platform = os.name
        
        # Common Windows apps
        self.apps = {
            'chrome': 'chrome',
            'google chrome': 'chrome',
            'browser': 'chrome',
            'notepad': 'notepad',
            'calculator': 'calc',
            'calc': 'calc',
            'explorer': 'explorer',
            'file explorer': 'explorer',
            'files': 'explorer',
            'cmd': 'cmd',
            'command prompt': 'cmd',
            'terminal': 'wt',
            'settings': 'ms-settings:',
            'spotify': 'spotify',
            'vs code': 'code',
            'vscode': 'code',
            'word': 'winword',
            'excel': 'excel',
            'powerpoint': 'powerpnt',
            'paint': 'mspaint',
            'snipping tool': 'snippingtool',
        }
    
    def open_app(self, app_name: str) -> str:
        """Open an application"""
        try:
            app_lower = app_name.lower().strip()
            
            # Check if it's a known app
            if app_lower in self.apps:
                cmd = self.apps[app_lower]
                if cmd.startswith('ms-'):
                    os.system(f'start {cmd}')
                else:
                    subprocess.Popen(cmd, shell=True)
                return f"Opening {app_name}."
            
            # Try to open directly
            subprocess.Popen(app_lower, shell=True)
            return f"Trying to open {app_name}."
            
        except Exception as e:
            logger.error(f"Open app error: {e}")
            return f"Couldn't open {app_name}."
    
    def type_text(self, text: str) -> str:
        """Type text into the currently focused application"""
        try:
            import pyautogui
            import time
            
            # Small delay to ensure app is focused
            time.sleep(0.3)
            
            # Type the text
            pyautogui.typewrite(text, interval=0.02) if text.isascii() else self._type_unicode(text)
            
            return f"Typed the text."
            
        except Exception as e:
            logger.error(f"Type error: {e}")
            return "Couldn't type the text."
    
    def _type_unicode(self, text: str):
        """Type unicode text (for non-ASCII characters)"""
        import pyautogui
        import pyperclip
        
        # Copy to clipboard and paste
        pyperclip.copy(text)
        pyautogui.hotkey('ctrl', 'v')
    
    def press_enter(self) -> str:
        """Press Enter key"""
        try:
            import pyautogui
            pyautogui.press('enter')
            return "Pressed Enter."
        except:
            return "Couldn't press Enter."
    
    def press_key(self, key: str) -> str:
        """Press a specific key"""
        try:
            import pyautogui
            pyautogui.press(key)
            return f"Pressed {key}."
        except:
            return f"Couldn't press {key}."
    
    def hotkey(self, *keys) -> str:
        """Press keyboard shortcut"""
        try:
            import pyautogui
            pyautogui.hotkey(*keys)
            return f"Pressed {'+'.join(keys)}."
        except:
            return "Couldn't press hotkey."
    
    def copy(self) -> str:
        """Copy selected text (Ctrl+C)"""
        return self.hotkey('ctrl', 'c')
    
    def paste(self) -> str:
        """Paste from clipboard (Ctrl+V)"""
        return self.hotkey('ctrl', 'v')
    
    def select_all(self) -> str:
        """Select all (Ctrl+A)"""
        return self.hotkey('ctrl', 'a')
    
    def undo(self) -> str:
        """Undo (Ctrl+Z)"""
        return self.hotkey('ctrl', 'z')
    
    def save(self) -> str:
        """Save (Ctrl+S)"""
        return self.hotkey('ctrl', 's')
    
    def new_line(self) -> str:
        """Press Enter for new line"""
        return self.press_enter()
    
    def switch_window(self) -> str:
        """Switch to next window (Alt+Tab)"""
        try:
            import pyautogui
            pyautogui.hotkey('alt', 'tab')
            return "Switched window."
        except:
            return "Couldn't switch window."
    
    def close_window(self) -> str:
        """Close current window (Alt+F4)"""
        try:
            import pyautogui
            pyautogui.hotkey('alt', 'F4')
            return "Closing window."
        except:
            return "Couldn't close window."
    
    def click_at(self, x: int, y: int) -> str:
        """Click at specific coordinates"""
        try:
            import pyautogui
            pyautogui.click(x, y)
            return f"Clicked at ({x}, {y})."
        except:
            return "Couldn't click."
    
    def take_screenshot(self) -> str:
        """Take a screenshot and save it"""
        try:
            import pyautogui
            
            # Create screenshots folder
            screenshots_dir = os.path.join(os.path.expanduser('~'), 'Pictures', 'Screenshots')
            os.makedirs(screenshots_dir, exist_ok=True)
            
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filepath = os.path.join(screenshots_dir, f'screenshot_{timestamp}.png')
            
            # Take screenshot
            screenshot = pyautogui.screenshot()
            screenshot.save(filepath)
            
            return f"Screenshot saved to {filepath}."
            
        except Exception as e:
            logger.error(f"Screenshot error: {e}")
            return "Couldn't take screenshot."
    
    def capture_screen(self) -> Optional[str]:
        """Capture screen and return temp file path for AI analysis"""
        try:
            import pyautogui
            import tempfile
            
            # Take screenshot
            screenshot = pyautogui.screenshot()
            
            # Save to temp file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            temp_path = temp_file.name
            temp_file.close()
            
            screenshot.save(temp_path)
            return temp_path
            
        except Exception as e:
            logger.error(f"Screen capture error: {e}")
            return None
    
    def get_battery(self) -> str:
        """Get battery status"""
        try:
            import ctypes
            
            class SYSTEM_POWER_STATUS(ctypes.Structure):
                _fields_ = [
                    ('ACLineStatus', ctypes.c_byte),
                    ('BatteryFlag', ctypes.c_byte),
                    ('BatteryLifePercent', ctypes.c_byte),
                    ('SystemStatusFlag', ctypes.c_byte),
                    ('BatteryLifeTime', ctypes.c_ulong),
                    ('BatteryFullLifeTime', ctypes.c_ulong),
                ]
            
            status = SYSTEM_POWER_STATUS()
            ctypes.windll.kernel32.GetSystemPowerStatus(ctypes.byref(status))
            
            percent = status.BatteryLifePercent
            charging = "charging" if status.ACLineStatus == 1 else "not charging"
            
            if percent == 255:
                return "No battery detected. You're on desktop power."
            
            return f"Battery is at {percent}%, {charging}."
            
        except Exception as e:
            logger.error(f"Battery error: {e}")
            return "Couldn't get battery status."
    
    def get_time(self) -> str:
        """Get current time"""
        now = datetime.now()
        return f"It's {now.strftime('%I:%M %p')} on {now.strftime('%A, %B %d')}."
    
    def lock_screen(self) -> str:
        """Lock the computer"""
        try:
            if self.platform == 'nt':
                import ctypes
                ctypes.windll.user32.LockWorkStation()
                return "Locking screen."
        except Exception as e:
            logger.error(f"Lock error: {e}")
        return "Couldn't lock screen."
    
    def shutdown(self, restart: bool = False) -> str:
        """Shutdown or restart computer"""
        try:
            if self.platform == 'nt':
                cmd = 'shutdown /r /t 60' if restart else 'shutdown /s /t 60'
                os.system(cmd)
                action = "restart" if restart else "shutdown"
                return f"Computer will {action} in 60 seconds. Say 'cancel shutdown' to stop."
        except Exception as e:
            logger.error(f"Shutdown error: {e}")
        return "Couldn't initiate shutdown."
    
    def cancel_shutdown(self) -> str:
        """Cancel scheduled shutdown"""
        try:
            if self.platform == 'nt':
                os.system('shutdown /a')
                return "Shutdown cancelled."
        except:
            pass
        return "Couldn't cancel shutdown."
