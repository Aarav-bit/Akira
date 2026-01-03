"""
Media Control Module - System media playback control
"""
import os
import subprocess
import webbrowser
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class MediaControl:
    def __init__(self):
        self.platform = os.name
    
    def play_pause(self) -> str:
        """Toggle play/pause for media"""
        try:
            if self.platform == 'nt':  # Windows
                import ctypes
                VK_MEDIA_PLAY_PAUSE = 0xB3
                ctypes.windll.user32.keybd_event(VK_MEDIA_PLAY_PAUSE, 0, 0, 0)
                ctypes.windll.user32.keybd_event(VK_MEDIA_PLAY_PAUSE, 0, 2, 0)
                return "Toggled play/pause."
        except Exception as e:
            logger.error(f"Play/pause error: {e}")
        return "Couldn't control media playback."
    
    def next_track(self) -> str:
        """Skip to next track"""
        try:
            if self.platform == 'nt':
                import ctypes
                VK_MEDIA_NEXT = 0xB0
                ctypes.windll.user32.keybd_event(VK_MEDIA_NEXT, 0, 0, 0)
                ctypes.windll.user32.keybd_event(VK_MEDIA_NEXT, 0, 2, 0)
                return "Skipped to next track."
        except Exception as e:
            logger.error(f"Next track error: {e}")
        return "Couldn't skip track."
    
    def prev_track(self) -> str:
        """Go to previous track"""
        try:
            if self.platform == 'nt':
                import ctypes
                VK_MEDIA_PREV = 0xB1
                ctypes.windll.user32.keybd_event(VK_MEDIA_PREV, 0, 0, 0)
                ctypes.windll.user32.keybd_event(VK_MEDIA_PREV, 0, 2, 0)
                return "Going to previous track."
        except Exception as e:
            logger.error(f"Prev track error: {e}")
        return "Couldn't go to previous track."
    
    def play_on_youtube(self, query: str) -> str:
        """Open YouTube, search and auto-play first result"""
        try:
            import pyautogui
            import time
            
            # Open YouTube search
            search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
            webbrowser.open(search_url)
            
            # Wait for page to load
            time.sleep(3)
            
            # Press Tab to get to first video, then Enter to play
            # Or use keyboard shortcut
            pyautogui.press('tab')
            time.sleep(0.3)
            pyautogui.press('tab')
            time.sleep(0.3)
            pyautogui.press('enter')
            
            return f"Playing {query} on YouTube."
        except Exception as e:
            logger.error(f"YouTube error: {e}")
            return "Couldn't play on YouTube."
    
    def play_on_spotify(self, query: str) -> str:
        """Open Spotify, search and auto-play first song"""
        try:
            import pyautogui
            import time
            
            if self.platform == 'nt':
                # Try Spotify URI first (opens app directly with search)
                search_uri = f"spotify:search:{query.replace(' ', '%20')}"
                try:
                    os.startfile(search_uri)
                    time.sleep(3)  # Wait for Spotify to load search
                    
                    # Navigate to first song and play
                    # Tab to get to first result in songs section
                    for _ in range(3):
                        pyautogui.press('tab')
                        time.sleep(0.2)
                    
                    # Enter to select/play
                    pyautogui.press('enter')
                    time.sleep(0.5)
                    
                    return f"Playing {query} on Spotify."
                except:
                    pass
            
            # Fallback to web player
            search_url = f"https://open.spotify.com/search/{query.replace(' ', '%20')}"
            webbrowser.open(search_url)
            
            time.sleep(4)  # Web takes longer
            
            # Navigate to songs section and play
            for _ in range(5):
                pyautogui.press('tab')
                time.sleep(0.15)
            
            pyautogui.press('enter')
            
            return f"Playing {query} on Spotify."
            
        except Exception as e:
            logger.error(f"Spotify error: {e}")
            return "Couldn't play on Spotify."
    
    def volume_up(self, amount: int = 10) -> str:
        """Increase system volume"""
        try:
            if self.platform == 'nt':
                from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                from ctypes import cast, POINTER
                from comtypes import CLSCTX_ALL
                
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume = cast(interface, POINTER(IAudioEndpointVolume))
                
                current = volume.GetMasterVolumeLevelScalar()
                new_vol = min(1.0, current + (amount / 100))
                volume.SetMasterVolumeLevelScalar(new_vol, None)
                return f"Volume set to {int(new_vol * 100)}%."
        except Exception as e:
            logger.error(f"Volume up error: {e}")
        return "Couldn't change volume."
    
    def volume_down(self, amount: int = 10) -> str:
        """Decrease system volume"""
        try:
            if self.platform == 'nt':
                from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                from ctypes import cast, POINTER
                from comtypes import CLSCTX_ALL
                
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume = cast(interface, POINTER(IAudioEndpointVolume))
                
                current = volume.GetMasterVolumeLevelScalar()
                new_vol = max(0.0, current - (amount / 100))
                volume.SetMasterVolumeLevelScalar(new_vol, None)
                return f"Volume set to {int(new_vol * 100)}%."
        except Exception as e:
            logger.error(f"Volume down error: {e}")
        return "Couldn't change volume."
    
    def mute(self) -> str:
        """Toggle mute"""
        try:
            if self.platform == 'nt':
                from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                from ctypes import cast, POINTER
                from comtypes import CLSCTX_ALL
                
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume = cast(interface, POINTER(IAudioEndpointVolume))
                
                current_mute = volume.GetMute()
                volume.SetMute(not current_mute, None)
                return "Muted." if not current_mute else "Unmuted."
        except Exception as e:
            logger.error(f"Mute error: {e}")
        return "Couldn't toggle mute."
