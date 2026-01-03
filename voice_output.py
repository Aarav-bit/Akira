import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import edge_tts
import asyncio
import logging
import tempfile
import re
from typing import Optional

try:
    import pygame
    pygame.mixer.init()
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

logger = logging.getLogger(__name__)

class VoiceOutput:
    def __init__(self):
        """
        Dual voice TTS - English (Aria) and Hindi (Swara)
        Optimized for low latency with streaming playback
        """
        self.english_voice = "en-US-AriaNeural"
        self.hindi_voice = "hi-IN-SwaraNeural"
        self.rate = "+35%"  # Slightly faster speech
        self.pitch = "+0Hz"
        self.volume = "+0%"
        self._stop_speaking = False
        self._audio_queue = []
        self._is_playing = False
    
    def _detect_hindi(self, text: str) -> bool:
        """Detect if text contains Hindi (Devanagari) characters"""
        hindi_pattern = re.compile(r'[\u0900-\u097F]')
        return bool(hindi_pattern.search(text))
    
    def stop(self):
        self._stop_speaking = True
        self._audio_queue.clear()
        if PYGAME_AVAILABLE:
            pygame.mixer.music.stop()
    
    async def speak(self, text: str) -> bool:
        """TTS with edge_tts - optimized for speed"""
        self._stop_speaking = False
        
        try:
            # Detect language and select voice
            is_hindi = self._detect_hindi(text)
            voice = self.hindi_voice if is_hindi else self.english_voice
            
            # Clean text - keep Hindi characters
            text_clean = re.sub(r'[^\w\s\.,!?;:\-\'\"\u0900-\u097F]', '', text)
            if not text_clean.strip():
                text_clean = text
            
            communicate = edge_tts.Communicate(
                text=text_clean,
                voice=voice,
                rate=self.rate,
                pitch=self.pitch,
                volume=self.volume
            )
            
            # Collect all audio chunks
            audio_data = b""
            async for chunk in communicate.stream():
                if self._stop_speaking:
                    return False
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
            
            if self._stop_speaking or not audio_data:
                return False
            
            # Save and play
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                tmp.write(audio_data)
                tmp_path = tmp.name
            
            if not self._stop_speaking:
                await self._play_audio(tmp_path)
            
            try:
                os.unlink(tmp_path)
            except:
                pass
            
            return not self._stop_speaking
            
        except Exception as e:
            logger.error(f"TTS error: {e}")
            return False
    
    async def _play_audio(self, file_path: str):
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.music.load(file_path)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    if self._stop_speaking:
                        pygame.mixer.music.stop()
                        return
                    await asyncio.sleep(0.03)  # Faster polling
                return
            except Exception:
                pass
        
        # Fallback for Windows
        import platform
        import subprocess
        system = platform.system()
        
        if system == "Windows":
            try:
                abs_path = os.path.abspath(file_path).replace("\\", "\\\\")
                ps_cmd = f'''
                Add-Type -AssemblyName presentationCore
                $p = New-Object system.windows.media.mediaplayer
                $p.open((New-Object System.Uri("{abs_path}")))
                $p.Play()
                Start-Sleep -Milliseconds 300
                while ($p.Position.TotalSeconds -lt $p.NaturalDuration.TimeSpan.TotalSeconds) {{ Start-Sleep -Milliseconds 30 }}
                $p.Stop(); $p.Close()
                '''
                subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True, timeout=60)
            except:
                pass
        elif system == "Darwin":
            subprocess.run(["afplay", file_path], check=False, timeout=30)
    
    def set_voice(self, voice: str):
        self.voice = voice
    
    def set_rate(self, rate: str):
        self.rate = rate
