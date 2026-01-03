#!/usr/bin/env python3
"""
Akira - AI Voice Assistant with High Impact Features
"""

import os
import sys

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import logging
import asyncio
import re
from pathlib import Path

# Load environment variables
try:
    from dotenv import load_dotenv
    env_file = Path(__file__).parent / ".env"
    load_dotenv(dotenv_path=env_file)
except ImportError:
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        with open(env_file, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

from ai_companion import AICompanion
from voice_input import VoiceInput
from voice_output import VoiceOutput
from camera_vision import CameraVision
from web_search import WebSearch
from media_control import MediaControl
from system_control import SystemControl
from reminders import Reminders

# Suppress all logging
logging.disable(logging.CRITICAL)

class VoiceChatbot:
    def __init__(self):
        if not os.getenv("GROQ_API_KEY"):
            print("Error: GROQ_API_KEY not found. Set it in .env file.")
            sys.exit(1)
        
        self.ai = AICompanion()
        self.voice_input = VoiceInput()
        self.voice_output = VoiceOutput()
        self.camera = CameraVision()
        self.web_search = WebSearch()
        self.media = MediaControl()
        self.system = SystemControl()
        self.reminders = Reminders()
    
    def _detect_command(self, text: str) -> tuple:
        """Detect command type and extract parameters"""
        text_lower = text.lower()
        
        # Web Search
        if any(kw in text_lower for kw in ['search for', 'search', 'google', 'look up']):
            query = re.sub(r'(search for|search|google|look up)\s*', '', text_lower).strip()
            return ('search', query)
        
        if 'weather' in text_lower:
            # Extract location
            match = re.search(r'weather\s+(?:in|at|for)?\s*(.+)', text_lower)
            location = match.group(1).strip() if match else 'current location'
            return ('weather', location)
        
        if 'news' in text_lower:
            topic = re.sub(r'(latest|news|headlines|about)\s*', '', text_lower).strip() or 'latest'
            return ('news', topic)
        
        # Media Control
        if any(kw in text_lower for kw in ['play music', 'resume music', 'pause music', 'pause']):
            if 'pause' in text_lower:
                return ('media_pause', None)
            return ('media_play', None)
        
        if 'next song' in text_lower or 'next track' in text_lower or 'skip' in text_lower:
            return ('media_next', None)
        
        if 'previous song' in text_lower or 'previous track' in text_lower:
            return ('media_prev', None)
        
        if 'play' in text_lower and 'youtube' in text_lower:
            query = re.sub(r'(play|on youtube|youtube)\s*', '', text_lower).strip()
            return ('youtube', query)
        
        if 'play' in text_lower and 'spotify' in text_lower:
            query = re.sub(r'(play|on spotify|spotify)\s*', '', text_lower).strip()
            return ('spotify', query)
        
        # Also handle "play [song name]" without platform - default to Spotify
        if text_lower.startswith('play ') and 'youtube' not in text_lower:
            query = text_lower.replace('play ', '').strip()
            if query and len(query) > 2:
                return ('spotify', query)
        
        if 'volume up' in text_lower or 'increase volume' in text_lower:
            return ('volume_up', None)
        
        if 'volume down' in text_lower or 'decrease volume' in text_lower:
            return ('volume_down', None)
        
        if 'mute' in text_lower or 'unmute' in text_lower:
            return ('mute', None)
        
        # System Control
        if 'open' in text_lower:
            app = re.sub(r'open\s*', '', text_lower).strip()
            return ('open_app', app)
        
        if 'screenshot' in text_lower or 'screen shot' in text_lower:
            return ('screenshot', None)
        
        if 'battery' in text_lower:
            return ('battery', None)
        
        if 'what time' in text_lower or 'current time' in text_lower:
            return ('time', None)
        
        if 'lock' in text_lower and ('screen' in text_lower or 'computer' in text_lower):
            return ('lock', None)
        
        if 'shutdown' in text_lower or 'shut down' in text_lower:
            return ('shutdown', False)
        
        if 'restart' in text_lower:
            return ('shutdown', True)
        
        if 'cancel shutdown' in text_lower:
            return ('cancel_shutdown', None)
        
        # Reminders
        if 'remind' in text_lower:
            return ('reminder', text)
        
        if 'list reminder' in text_lower or 'my reminder' in text_lower:
            return ('list_reminders', None)
        
        if 'clear reminder' in text_lower:
            return ('clear_reminders', None)
        
        # Vision
        vision_keywords = ["what do you see", "what's in front", "describe", "what is this", 
                          "look at", "show me", "see", "camera", "picture", "image",
                          "around me", "surrounding", "in front of", "what's here",
                          "what am i", "what is in", "room", "desk", "table", "holding"]
        if any(kw in text_lower for kw in vision_keywords):
            return ('vision', text)
        
        # Joke
        if any(kw in text_lower for kw in ['joke', 'funny', 'humor', 'laugh']):
            return ('joke', None)
        
        # Default - AI conversation
        return ('chat', text)
    
    async def process_message(self, text: str):
        """Process user message and respond"""
        if not text or not text.strip():
            return
        
        print(f"You: {text}")
        
        command, param = self._detect_command(text)
        response = None
        
        # Handle commands
        if command == 'search':
            response = self.web_search.search(param)
        
        elif command == 'weather':
            response = self.web_search.get_weather(param)
        
        elif command == 'news':
            response = self.web_search.get_news(param)
        
        elif command == 'media_play' or command == 'media_pause':
            response = self.media.play_pause()
        
        elif command == 'media_next':
            response = self.media.next_track()
        
        elif command == 'media_prev':
            response = self.media.prev_track()
        
        elif command == 'youtube':
            response = self.media.play_on_youtube(param)
        
        elif command == 'spotify':
            response = self.media.play_on_spotify(param)
        
        elif command == 'volume_up':
            response = self.media.volume_up()
        
        elif command == 'volume_down':
            response = self.media.volume_down()
        
        elif command == 'mute':
            response = self.media.mute()
        
        elif command == 'open_app':
            response = self.system.open_app(param)
        
        elif command == 'screenshot':
            response = self.system.take_screenshot()
        
        elif command == 'battery':
            response = self.system.get_battery()
        
        elif command == 'time':
            response = self.system.get_time()
        
        elif command == 'lock':
            response = self.system.lock_screen()
        
        elif command == 'shutdown':
            response = self.system.shutdown(restart=param)
        
        elif command == 'cancel_shutdown':
            response = self.system.cancel_shutdown()
        
        elif command == 'reminder':
            response = self.reminders.set_reminder(param)
        
        elif command == 'list_reminders':
            response = self.reminders.list_reminders()
        
        elif command == 'clear_reminders':
            response = self.reminders.clear_reminders()
        
        elif command == 'vision':
            if self.camera.is_available():
                image_path = None
                for _ in range(3):
                    image_path = self.camera.capture_image()
                    if image_path and os.path.exists(image_path) and os.path.getsize(image_path) > 1000:
                        break
                    await asyncio.sleep(0.1)
                
                if image_path and os.path.exists(image_path):
                    response = self.ai.get_vision_response(param, image_path)
                    try:
                        os.unlink(image_path)
                    except:
                        pass
                else:
                    response = "I couldn't capture an image."
            else:
                response = "Camera not available."
        
        elif command == 'joke':
            response = self.ai.tell_joke()
        
        else:  # chat
            response = self.ai.get_response(text)
        
        # Speak and print response
        if response:
            await self.voice_output.speak(response)
            print(f"Akira: {response}\n")
    
    async def run_voice_mode(self):
        """Run in voice mode with wake word"""
        print("\n🎙️ Akira Voice Assistant")
        print("Say 'Akira' to activate, 'stop' to exit\n")
        
        try:
            while True:
                text = self.voice_input.listen(timeout=10, phrase_time_limit=15)
                
                if text:
                    text_lower = text.lower()
                    
                    if any(word in text_lower for word in ["stop", "exit", "quit", "goodbye"]):
                        print("Akira: Goodbye!\n")
                        await self.voice_output.speak("Goodbye!")
                        break
                    
                    if "akira" in text_lower:
                        text = text_lower.replace("akira", "").strip()
                        if not text:
                            print("Akira: Yes?\n")
                            await self.voice_output.speak("Yes?")
                            text = self.voice_input.listen(timeout=10, phrase_time_limit=15)
                            if not text:
                                continue
                    
                    await self.process_message(text)
                    
        except KeyboardInterrupt:
            print("\nAkira: Goodbye!\n")
        finally:
            if self.camera:
                self.camera.release()
            self.reminders.stop()
    
    async def run_text_mode(self):
        """Run in text mode"""
        print("\n💬 Akira Text Mode")
        print("Type 'exit' to quit\n")
        
        try:
            while True:
                text = input("You: ").strip()
                
                if not text:
                    continue
                
                if text.lower() in ["exit", "quit", "stop"]:
                    print("Akira: Goodbye!\n")
                    break
                
                await self.process_message(text)
                
        except KeyboardInterrupt:
            print("\nAkira: Goodbye!\n")
        finally:
            self.reminders.stop()

async def main():
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except:
            pass
    
    print("Select mode: (1) Voice  (2) Text")
    choice = input("Choice [1]: ").strip()
    
    chatbot = VoiceChatbot()
    
    if choice == "2":
        await chatbot.run_text_mode()
    else:
        await chatbot.run_voice_mode()

if __name__ == "__main__":
    asyncio.run(main())
