"""
Akira Companion GUI - Anime character visual interface
"""

import os
import sys
import threading
import asyncio
import math
from pathlib import Path

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import customtkinter as ctk
from PIL import Image, ImageTk, ImageDraw
from typing import Optional, Callable

# Load environment variables
try:
    from dotenv import load_dotenv
    env_file = Path(__file__).parent / ".env"
    load_dotenv(dotenv_path=env_file)
except ImportError:
    pass

# Heavy imports deferred to background thread for instant UI
# from memory import Memory
# from ai_companion import AICompanion

import logging
logging.disable(logging.CRITICAL)

class AkiraCompanionGUI:
    # Design System - Futuristic Sci-Fi Theme
    COLORS = {
        'bg_primary': '#000000',
        'bg_secondary': '#0a0a0f',
        'bg_tertiary': '#12121a',
        'bg_glass': '#16213e',
        'accent_cyan': '#00d4ff',
        'accent_glow': '#38bdf8',
        'accent_pink': '#f472b6',
        'text_primary': '#f8fafc',
        'text_secondary': '#94a3b8',
        'text_muted': '#64748b',
        'success': '#22c55e',
        'danger': '#ef4444',
        # Emotion colors
        'emotion_happy': '#f472b6',    # Pink
        'emotion_sad': '#60a5fa',      # Blue
        'emotion_angry': '#f87171',    # Red
        'emotion_curious': '#fbbf24',  # Amber/Orange
        'emotion_stressed': '#a78bfa', # Purple
        'emotion_neutral': '#00d4ff',  # Cyan (default)
    }
    
    def __init__(self):
        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create window FIRST - show UI instantly
        self.root = ctk.CTk()
        self.root.title("AKIRA")
        self.root.geometry("420x780")
        self.root.resizable(False, False)
        self.root.attributes('-topmost', True)
        self.root.configure(fg_color=self.COLORS['bg_primary'])
        
        # Defer ALL heavy components
        self._memory = None
        self._ai = None
        self._voice_input = None
        self._voice_output = None
        self._camera = None
        self._web_search = None
        self._media = None
        self._system = None
        self._reminders = None
        
        # State
        self.is_listening = False
        self.voice_mode = False
        self.status = "idle"
        self.components_loaded = False
        self.ring_phase = 0
        
        # Show UI immediately (before any imports)
        self._show_mode_selection()
        
        # Load ALL components in background
        threading.Thread(target=self._load_components, daemon=True).start()
        
        self.loop = asyncio.new_event_loop()
    
    @property
    def memory(self):
        while self._memory is None:
            import time
            time.sleep(0.01)
        return self._memory
    
    @property
    def ai(self):
        while self._ai is None:
            import time
            time.sleep(0.01)
        return self._ai
    
    def _load_components(self):
        """Lazy load ALL heavy components in background"""
        # Load core AI components first (needed for responses)
        from memory import Memory
        from ai_companion import AICompanion
        self._memory = Memory()
        self._ai = AICompanion(memory=self._memory)
        
        # Then load other modules
        from voice_input import VoiceInput
        from voice_output import VoiceOutput
        from camera_vision import CameraVision
        from web_search import WebSearch
        from media_control import MediaControl
        from system_control import SystemControl
        from reminders import Reminders
        
        self._voice_input = VoiceInput()
        self._voice_output = VoiceOutput()
        self._camera = CameraVision()
        self._web_search = WebSearch()
        self._media = MediaControl()
        self._system = SystemControl()
        self._reminders = Reminders()
        self.components_loaded = True
    
    # Property accessors for lazy components
    @property
    def voice_input(self):
        while self._voice_input is None:
            pass  # Wait for loading
        return self._voice_input
    
    @property
    def voice_output(self):
        while self._voice_output is None:
            pass
        return self._voice_output
    
    @property
    def camera(self):
        while self._camera is None:
            pass
        return self._camera
    
    @property
    def web_search(self):
        while self._web_search is None:
            pass
        return self._web_search
    
    @property
    def media(self):
        while self._media is None:
            pass
        return self._media
    
    @property
    def system(self):
        while self._system is None:
            pass
        return self._system
    
    @property
    def reminders(self):
        while self._reminders is None:
            pass
        return self._reminders
    
    def _show_mode_selection(self):
        """Show mode selection dialog with futuristic styling"""
        # Mode selection frame - cosmic dark background
        self.mode_frame = ctk.CTkFrame(self.root, fg_color=self.COLORS['bg_primary'], corner_radius=0)
        self.mode_frame.pack(fill="both", expand=True)
        
        # Inner container with glass effect
        inner = ctk.CTkFrame(
            self.mode_frame, 
            fg_color=self.COLORS['bg_secondary'], 
            corner_radius=20,
            border_width=1,
            border_color=self.COLORS['bg_tertiary']
        )
        inner.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Logo icon
        logo_icon = ctk.CTkLabel(
            inner,
            text="◇",
            font=("Arial", 32),
            text_color=self.COLORS['accent_cyan']
        )
        logo_icon.pack(pady=(80, 5))
        
        # Title
        title = ctk.CTkLabel(
            inner,
            text="AKIRA",
            font=("Arial", 44, "bold"),
            text_color=self.COLORS['text_primary']
        )
        title.pack(pady=(0, 5))
        
        subtitle = ctk.CTkLabel(
            inner,
            text="AI Companion",
            font=("Arial", 14),
            text_color=self.COLORS['text_muted']
        )
        subtitle.pack(pady=(0, 60))
        
        # Mode selection label
        mode_label = ctk.CTkLabel(
            inner,
            text="Select Input Mode",
            font=("Arial", 15),
            text_color=self.COLORS['text_secondary']
        )
        mode_label.pack(pady=(0, 25))
        
        # Voice mode button - cyan glow
        voice_btn = ctk.CTkButton(
            inner,
            text="🎤  Voice Mode",
            font=("Arial", 15, "bold"),
            height=55,
            width=260,
            corner_radius=28,
            fg_color=self.COLORS['accent_cyan'],
            hover_color=self.COLORS['accent_glow'],
            text_color=self.COLORS['bg_primary'],
            command=lambda: self._select_mode(True)
        )
        voice_btn.pack(pady=8)
        
        # Text mode button - glass style
        text_btn = ctk.CTkButton(
            inner,
            text="💬  Text Mode",
            font=("Arial", 15, "bold"),
            height=55,
            width=260,
            corner_radius=28,
            fg_color=self.COLORS['bg_glass'],
            hover_color=self.COLORS['bg_tertiary'],
            border_width=1,
            border_color=self.COLORS['text_muted'],
            text_color=self.COLORS['text_primary'],
            command=lambda: self._select_mode(False)
        )
        text_btn.pack(pady=8)
        
        # Keyboard hint
        hint = ctk.CTkLabel(
            inner,
            text="Press 1 or 2 to select",
            font=("Arial", 11),
            text_color=self.COLORS['text_muted']
        )
        hint.pack(pady=(40, 0))
        
        # Keyboard shortcuts
        self.root.bind("1", lambda e: self._select_mode(True))
        self.root.bind("2", lambda e: self._select_mode(False))
    
    def _select_mode(self, voice_mode: bool):
        """Handle mode selection"""
        self.voice_mode = voice_mode
        
        # Remove mode selection frame
        self.mode_frame.destroy()
        
        # Unbind keyboard shortcuts
        self.root.unbind("1")
        self.root.unbind("2")
        
        # Build main UI
        self._build_ui()
        
        # If voice mode, start listening automatically
        if self.voice_mode:
            self.is_listening = True
            self.input_frame.pack_forget()  # Hide text input in voice mode
            self.mic_btn.configure(
                text="⏹  Stop Listening", 
                fg_color=self.COLORS['success'],
                hover_color="#16a34a"
            )
            self._add_message("Akira", "Voice mode activated! 🎤 I'm listening...")
            threading.Thread(target=self._voice_loop, daemon=True).start()
        else:
            self.mic_btn.pack_forget()  # Hide mic button in text mode
            self._add_message("Akira", "Text mode activated! 💬 Type your messages below.")
    
    def _build_ui(self):
        """Build the GUI layout with futuristic styling"""
        # Main container - deep space black
        self.main_frame = ctk.CTkFrame(self.root, fg_color=self.COLORS['bg_primary'], corner_radius=0)
        self.main_frame.pack(fill="both", expand=True)
        
        # Inner container with subtle border
        self.inner_frame = ctk.CTkFrame(
            self.main_frame, 
            fg_color=self.COLORS['bg_secondary'],
            corner_radius=20,
            border_width=1,
            border_color=self.COLORS['bg_tertiary']
        )
        self.inner_frame.pack(fill="both", expand=True, padx=12, pady=12)
        
        # Header with settings
        header = ctk.CTkFrame(self.inner_frame, fg_color="transparent", height=35)
        header.pack(fill="x", padx=15, pady=(10, 0))
        header.pack_propagate(False)
        
        logo_label = ctk.CTkLabel(
            header,
            text="◇ AKIRA",
            font=("Arial", 13, "bold"),
            text_color=self.COLORS['accent_cyan']
        )
        logo_label.pack(side="left")
        
        # Settings button
        settings_btn = ctk.CTkButton(
            header,
            text="⚙",
            width=30,
            height=25,
            corner_radius=12,
            fg_color="transparent",
            hover_color=self.COLORS['bg_glass'],
            text_color=self.COLORS['text_muted'],
            font=("Arial", 14),
            command=self._show_settings
        )
        settings_btn.pack(side="right")
        
        # Quick Actions Panel
        quick_actions = ctk.CTkFrame(self.inner_frame, fg_color="transparent", height=45)
        quick_actions.pack(fill="x", padx=15, pady=(5, 0))
        quick_actions.pack_propagate(False)
        
        actions = [
            ("🎵", "Play music", lambda: self._quick_action("play music")),
            ("🌤️", "Weather", lambda: self._quick_action("what's the weather")),
            ("📰", "News", lambda: self._quick_action("latest news")),
            ("⏰", "Timer", lambda: self._quick_action("set a timer for 5 minutes")),
        ]
        
        for emoji, tooltip, cmd in actions:
            btn = ctk.CTkButton(
                quick_actions,
                text=emoji,
                width=50,
                height=35,
                corner_radius=10,
                fg_color=self.COLORS['bg_glass'],
                hover_color=self.COLORS['bg_tertiary'],
                font=("Arial", 16),
                command=cmd
            )
            btn.pack(side="left", padx=4)
        
        # Avatar section with holographic ring - compact height
        self.avatar_frame = ctk.CTkFrame(self.inner_frame, fg_color="transparent", height=280)
        self.avatar_frame.pack(fill="x", pady=(5, 0))
        self.avatar_frame.pack_propagate(False)
        
        # Create canvas for holographic ring animation - adjusted size
        self.ring_canvas = ctk.CTkCanvas(
            self.avatar_frame,
            width=280,
            height=280,
            bg=self.COLORS['bg_secondary'],
            highlightthickness=0
        )
        self.ring_canvas.pack()
        
        # Load and display avatar with circular mask - balanced size 230x230
        avatar_path = Path(__file__).parent / "assets" / "akira_avatar.png"
        if avatar_path.exists():
            img = Image.open(avatar_path)
            size = (230, 230)
            img = img.resize(size, Image.Resampling.LANCZOS)
            # Create circular mask
            mask = Image.new('L', size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, size[0], size[1]), fill=255)
            img.putalpha(mask)
            self.avatar_photo = ImageTk.PhotoImage(img)
            self.ring_canvas.create_image(140, 140, image=self.avatar_photo)
        else:
            self.ring_canvas.create_text(
                140, 140,
                text="🎀",
                font=("Arial", 55),
                fill=self.COLORS['accent_pink']
            )
        
        # Start ring animation
        self._animate_ring()
        
        # Status indicator
        self.status_frame = ctk.CTkFrame(self.inner_frame, fg_color="transparent")
        self.status_frame.pack(pady=(0, 8))
        
        self.status_dot = ctk.CTkLabel(
            self.status_frame,
            text="●",
            font=("Arial", 10),
            text_color=self.COLORS['accent_cyan']
        )
        self.status_dot.pack(side="left", padx=(0, 5))
        
        self.status_label = ctk.CTkLabel(
            self.status_frame, 
            text="Ready", 
            font=("Arial", 13),
            text_color=self.COLORS['text_secondary']
        )
        self.status_label.pack(side="left")
        
        # Chat display with glass effect
        self.chat_frame = ctk.CTkFrame(
            self.inner_frame,
            fg_color=self.COLORS['bg_glass'],
            corner_radius=16,
            border_width=1,
            border_color=self.COLORS['bg_tertiary']
        )
        self.chat_frame.pack(fill="both", expand=True, padx=15, pady=5)
        
        self.chat_text = ctk.CTkTextbox(
            self.chat_frame, 
            font=("Arial", 13),
            fg_color="transparent",
            text_color=self.COLORS['text_primary'],
            wrap="word",
            state="disabled",
            scrollbar_button_color=self.COLORS['bg_tertiary'],
            scrollbar_button_hover_color=self.COLORS['text_muted']
        )
        self.chat_text.pack(fill="both", expand=True, padx=12, pady=12)
        
        # Input section
        self.input_frame = ctk.CTkFrame(self.inner_frame, fg_color="transparent")
        self.input_frame.pack(fill="x", padx=15, pady=10)
        
        self.input_entry = ctk.CTkEntry(
            self.input_frame,
            placeholder_text="Send a message...",
            placeholder_text_color=self.COLORS['text_muted'],
            font=("Arial", 13),
            height=45,
            corner_radius=22,
            fg_color=self.COLORS['bg_glass'],
            border_width=1,
            border_color=self.COLORS['bg_tertiary'],
            text_color=self.COLORS['text_primary']
        )
        self.input_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.input_entry.bind("<Return>", self._on_text_submit)
        self.input_entry.bind("<FocusIn>", lambda e: self.input_entry.configure(border_color=self.COLORS['accent_cyan']))
        self.input_entry.bind("<FocusOut>", lambda e: self.input_entry.configure(border_color=self.COLORS['bg_tertiary']))
        
        self.send_btn = ctk.CTkButton(
            self.input_frame,
            text="➤",
            width=45,
            height=45,
            corner_radius=22,
            fg_color=self.COLORS['accent_cyan'],
            hover_color=self.COLORS['accent_glow'],
            text_color=self.COLORS['bg_primary'],
            font=("Arial", 16),
            command=self._on_send_click
        )
        self.send_btn.pack(side="right")
        
        # Voice control button
        self.btn_frame = ctk.CTkFrame(self.inner_frame, fg_color="transparent")
        self.btn_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        self.mic_btn = ctk.CTkButton(
            self.btn_frame,
            text="🎤  Start Listening",
            font=("Arial", 14, "bold"),
            height=50,
            corner_radius=25,
            fg_color=self.COLORS['danger'],
            hover_color="#dc2626",
            text_color=self.COLORS['text_primary'],
            command=self._toggle_listening
        )
        self.mic_btn.pack(fill="x")
        
        # Add welcome message
        self._add_message("Akira", "Hi! I'm Akira, your AI companion. 💕 How can I help you?")
        
        # Start status animation
        self._animate_status()
    
    def _animate_ring(self):
        """Animate holographic ring around avatar with emotion-based colors"""
        if not hasattr(self, 'ring_canvas'):
            return
        
        self.ring_canvas.delete("ring")
        center_x, center_y = 140, 140
        
        # Get emotion color from AI if available
        emotion_color = self.COLORS['emotion_neutral']
        if hasattr(self, '_ai') and self._ai is not None:
            emotion = getattr(self._ai, 'current_emotion', 'neutral')
            emotion_color = self.COLORS.get(f'emotion_{emotion}', self.COLORS['emotion_neutral'])
        
        if self.status == "listening":
            # Pulsing rings when listening
            pulse = abs(math.sin(self.ring_phase * 0.15)) * 10
            base_radius = 120
            for i, r_off in enumerate([0, 8, 16]):
                radius = base_radius + r_off + pulse
                self.ring_canvas.create_oval(
                    center_x - radius, center_y - radius,
                    center_x + radius, center_y + radius,
                    outline=self.COLORS['accent_cyan'], width=2, tags="ring"
                )
        elif self.status == "speaking":
            # Ripple effect when speaking - use emotion color
            base_radius = 120
            for i in range(3):
                offset = (self.ring_phase * 2 + i * 15) % 40
                radius = base_radius + offset
                self.ring_canvas.create_oval(
                    center_x - radius, center_y - radius,
                    center_x + radius, center_y + radius,
                    outline=emotion_color, width=2, tags="ring"
                )
        else:
            # Gentle breathing glow when idle - use emotion color
            glow = abs(math.sin(self.ring_phase * 0.04)) * 5
            radius = 122 + glow
            self.ring_canvas.create_oval(
                center_x - radius, center_y - radius,
                center_x + radius, center_y + radius,
                outline=emotion_color, width=2, tags="ring"
            )
        
        self.ring_phase += 1
        self.root.after(50, self._animate_ring)
    
    def _animate_status(self):
        """Animate status dots"""
        if hasattr(self, 'status_label'):
            current = self.status_label.cget("text")
            if "..." in current and self.status != "idle":
                dots = current.count(".")
                base = current.rstrip(".")
                new_dots = "." * ((dots % 3) + 1)
                self.status_label.configure(text=base + new_dots)
        
        self.root.after(400, self._animate_status)
    
    def _set_status(self, status: str):
        """Update status indicator with animation"""
        self.status = status
        
        if hasattr(self, 'status_dot') and hasattr(self, 'status_label'):
            if status == "listening":
                self.status_dot.configure(text_color="#f59e0b")
                self.status_label.configure(text="Listening...", text_color="#f59e0b")
            elif status == "speaking":
                self.status_dot.configure(text_color=self.COLORS['accent_pink'])
                self.status_label.configure(text="Speaking...", text_color=self.COLORS['accent_pink'])
            elif status == "thinking":
                self.status_dot.configure(text_color=self.COLORS['accent_cyan'])
                self.status_label.configure(text="Thinking...", text_color=self.COLORS['accent_cyan'])
            else:
                self.status_dot.configure(text_color=self.COLORS['accent_cyan'])
                self.status_label.configure(text="Ready", text_color=self.COLORS['text_secondary'])
        
        self.root.update()
    
    def _add_message(self, sender: str, message: str):
        """Add message to chat display with styling"""
        self.chat_text.configure(state="normal")
        
        # Add spacing
        self.chat_text.insert("end", "\n")
        
        if sender == "You":
            # User message - right aligned feel with different color
            self.chat_text.insert("end", f"You ➤ ", "user_name")
            self.chat_text.insert("end", f"{message}\n", "user_msg")
        else:
            # Akira message - with pink accent
            self.chat_text.insert("end", f"💕 Akira: ", "akira_name")
            self.chat_text.insert("end", f"{message}\n", "akira_msg")
        
        # Configure text tags for colors
        self.chat_text.tag_config("user_name", foreground="#60a5fa")
        self.chat_text.tag_config("user_msg", foreground="#cbd5e1")
        self.chat_text.tag_config("akira_name", foreground="#f472b6")
        self.chat_text.tag_config("akira_msg", foreground="#e2e8f0")
        
        self.chat_text.configure(state="disabled")
        self.chat_text.see("end")
    
    def _on_text_submit(self, event):
        """Handle text input submission"""
        self._on_send_click()
    
    def _on_send_click(self):
        """Process text input"""
        text = self.input_entry.get().strip()
        if not text:
            return
        
        self.input_entry.delete(0, "end")
        self._add_message("You", text)
        
        # Process in thread
        threading.Thread(target=self._process_message_sync, args=(text,), daemon=True).start()
    
    def _show_settings(self):
        """Show settings popup for voice sensitivity"""
        settings_window = ctk.CTkToplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("300x200")
        settings_window.attributes('-topmost', True)
        settings_window.configure(fg_color=self.COLORS['bg_secondary'])
        
        # Center on parent
        x = self.root.winfo_x() + 60
        y = self.root.winfo_y() + 200
        settings_window.geometry(f"+{x}+{y}")
        
        # Title
        title = ctk.CTkLabel(settings_window, text="Voice Sensitivity", font=("Arial", 16, "bold"))
        title.pack(pady=(20, 10))
        
        # Current sensitivity
        current = self.voice_input.get_sensitivity() if hasattr(self.voice_input, 'get_sensitivity') else 'medium'
        
        sensitivity_var = ctk.StringVar(value=current)
        
        for level, desc in [('low', 'Low - Needs louder voice'), ('medium', 'Medium - Balanced'), ('high', 'High - Picks up quiet voices')]:
            rb = ctk.CTkRadioButton(
                settings_window,
                text=desc,
                variable=sensitivity_var,
                value=level,
                command=lambda l=level: self._set_voice_sensitivity(l)
            )
            rb.pack(pady=5, padx=20, anchor="w")
        
        # Close button
        close_btn = ctk.CTkButton(
            settings_window,
            text="Close",
            width=100,
            command=settings_window.destroy
        )
        close_btn.pack(pady=20)
    
    def _set_voice_sensitivity(self, level: str):
        """Set voice input sensitivity level"""
        if hasattr(self.voice_input, 'set_sensitivity'):
            self.voice_input.set_sensitivity(level)
            self._add_message("Akira", f"Voice sensitivity set to {level}! 🎤")
    
    def _quick_action(self, command: str):
        """Execute a quick action command"""
        self._add_message("You", command)
        threading.Thread(target=self._process_message_sync, args=(command,), daemon=True).start()
    
    def _toggle_listening(self):
        """Toggle voice listening"""
        if self.is_listening:
            self.is_listening = False
            self.mic_btn.configure(text="🎤 Start Listening", fg_color="#ef4444")
            self._set_status("idle")
        else:
            self.is_listening = True
            self.mic_btn.configure(text="⏹️ Stop Listening", fg_color="#22c55e")
            threading.Thread(target=self._voice_loop, daemon=True).start()
    
    def _voice_loop(self):
        """Voice listening loop"""
        while self.is_listening:
            self._set_status("listening")
            text = self.voice_input.listen(timeout=10, phrase_time_limit=15)
            
            if text:
                text_lower = text.lower()
                
                if any(word in text_lower for word in ["stop listening", "stop", "exit"]):
                    self.is_listening = False
                    self.root.after(0, lambda: self.mic_btn.configure(text="🎤 Start Listening", fg_color="#ef4444"))
                    self._set_status("idle")
                    break
                
                # Check for wake word "Akira" - interrupt if speaking
                if "akira" in text_lower:
                    # Stop any current speech
                    self.voice_output.stop()
                    
                    text = text_lower.replace("akira", "").strip()
                    if not text:
                        self.root.after(0, lambda: self._add_message("Akira", "Yes? 💕"))
                        asyncio.run(self.voice_output.speak("Yes?"))
                        continue
                
                self.root.after(0, lambda t=text: self._add_message("You", t))
                self._process_message_sync(text)
        
        self._set_status("idle")
    
    def _process_message_sync(self, text: str):
        """Process message synchronously"""
        self._set_status("thinking")
        
        response = self._get_response(text)
        
        if response:
            # Store conversation for summary feature
            self.memory.store_conversation(text, response)
            
            self._set_status("speaking")
            self.root.after(0, lambda: self._add_message("Akira", response))
            
            # Speak with interruption support
            asyncio.run(self.voice_output.speak(response))
        
        self._set_status("idle")
    
    def _get_response(self, text: str) -> str:
        """Get response based on command detection"""
        import re
        text_lower = text.lower()
        
        # Memory commands - check first
        if 'remember' in text_lower:
            response = self.memory.parse_remember_command(text)
            if response:
                return response
        
        if 'forget' in text_lower:
            response = self.memory.parse_forget_command(text)
            if response:
                return response
        
        if any(kw in text_lower for kw in ['what is my', 'what\'s my', 'my name', 'about me', 'what do you know']):
            response = self.memory.parse_recall_command(text)
            if response:
                return response
        
        # Conversation summary commands
        summary = self.memory.parse_summary_command(text)
        if summary:
            return summary
        
        # Web Search
        if any(kw in text_lower for kw in ['search for', 'search', 'google', 'look up']):
            query = re.sub(r'(search for|search|google|look up)\s*', '', text_lower).strip()
            return self.web_search.search(query)
        
        if 'weather' in text_lower:
            match = re.search(r'weather\s+(?:in|at|for)?\s*(.+)', text_lower)
            location = match.group(1).strip() if match else 'current location'
            return self.web_search.get_weather(location)
        
        if 'news' in text_lower:
            return self.web_search.get_news()
        
        # Media
        if any(kw in text_lower for kw in ['play music', 'pause music', 'pause']):
            return self.media.play_pause()
        
        if 'next song' in text_lower or 'skip' in text_lower:
            return self.media.next_track()
        
        if 'play' in text_lower and 'youtube' in text_lower:
            query = re.sub(r'(play|on youtube|youtube)\s*', '', text_lower).strip()
            return self.media.play_on_youtube(query)
        
        if 'play' in text_lower:
            query = re.sub(r'(play|on spotify|spotify)\s*', '', text_lower).strip()
            if query:
                return self.media.play_on_spotify(query)
        
        if 'volume up' in text_lower:
            return self.media.volume_up()
        
        if 'volume down' in text_lower:
            return self.media.volume_down()
        
        # System
        if 'open' in text_lower:
            app = re.sub(r'open\s*', '', text_lower).strip()
            return self.system.open_app(app)
        
        # AI-powered writing - "write about X", "write a message about Y"
        if any(kw in text_lower for kw in ['write about', 'write a ', 'type about', 'compose', 'draft']):
            # Get AI to generate the content
            prompt = text.replace("type", "write").replace("and type it", "").strip()
            generated = self.ai.get_response(f"Write this for the user (just the content, no explanation): {prompt}")
            self.system.type_text(generated)
            return f"Wrote: {generated[:50]}..."
        
        # Direct typing - "type: exact text" or "write: exact text"
        if 'type:' in text_lower or 'write:' in text_lower:
            for kw in ['type:', 'write:']:
                if kw in text_lower:
                    to_type = text.split(kw, 1)[-1].strip().strip('"\'')
                    self.system.type_text(to_type)
                    return f"Typed: {to_type[:50]}..."
        
        # Send message with AI-generated content - "send a thank you message"
        if any(kw in text_lower for kw in ['send a ', 'send message about', 'reply with a ']):
            prompt = text_lower.replace("send a ", "").replace("send message about ", "").replace("reply with a ", "").strip()
            generated = self.ai.get_response(f"Write a short message: {prompt}")
            self.system.type_text(generated)
            self.system.press_enter()
            return f"Sent: {generated[:50]}..."
        
        # Direct send - "send: exact message"
        if 'send:' in text_lower or 'reply:' in text_lower:
            for kw in ['send:', 'reply:']:
                if kw in text_lower:
                    msg = text.split(kw, 1)[-1].strip().strip('"\'')
                    if msg:
                        self.system.type_text(msg)
                        self.system.press_enter()
                        return f"Sent: {msg[:50]}..."
        
        # Generate and type AI reply
        if 'reply to' in text_lower or 'respond to' in text_lower:
            # Capture screen to see the message
            screen_path = self.system.capture_screen()
            if screen_path and os.path.exists(screen_path):
                # Ask AI to generate reply
                reply = self.ai.get_vision_response(
                    "Look at this screen. There's a message the user wants to reply to. Generate a brief, friendly reply.",
                    screen_path
                )
                try:
                    os.unlink(screen_path)
                except:
                    pass
                # Type the reply
                self.system.type_text(reply)
                return f"Generated and typed reply: {reply[:50]}..."
            return "Couldn't see the screen to generate reply."
        
        # Keyboard shortcuts
        if 'press enter' in text_lower or 'hit enter' in text_lower:
            return self.system.press_enter()
        
        if 'select all' in text_lower:
            return self.system.select_all()
        
        if 'copy' in text_lower and 'that' not in text_lower:
            return self.system.copy()
        
        if 'paste' in text_lower:
            return self.system.paste()
        
        if 'save' in text_lower and 'file' in text_lower:
            return self.system.save()
        
        if 'undo' in text_lower:
            return self.system.undo()
        
        if 'switch window' in text_lower or 'next window' in text_lower:
            return self.system.switch_window()
        
        if 'close window' in text_lower or 'close this' in text_lower:
            return self.system.close_window()
        
        if 'screenshot' in text_lower:
            return self.system.take_screenshot()
        
        if 'battery' in text_lower:
            return self.system.get_battery()
        
        if 'time' in text_lower:
            return self.system.get_time()
        
        # Reminders
        if 'remind' in text_lower:
            return self.reminders.set_reminder(text)
        
        # Screen reading - analyze what's on screen
        screen_keywords = ["my screen", "on screen", "on my screen", "read screen", "see screen",
                          "what's on screen", "look at screen", "screen shows", "this page",
                          "this window", "what app", "help me with this", "click on", "where is",
                          "find the button"]
        if any(kw in text_lower for kw in screen_keywords):
            screen_path = self.system.capture_screen()
            if screen_path and os.path.exists(screen_path):
                response = self.ai.get_vision_response(
                    f"Look at this screenshot and help the user. User says: {text}", 
                    screen_path
                )
                try:
                    os.unlink(screen_path)
                except:
                    pass
                return response
            return "I couldn't capture your screen."
        
        # Vision - expanded keywords
        vision_keywords = ["what do you see", "what am i", "holding", "around me", "describe",
                          "look at", "what is this", "what's this", "in front", "surrounding",
                          "can you see", "what's here", "room", "desk", "table", "my hand"]
        if any(kw in text_lower for kw in vision_keywords):
            if self.camera.is_available():
                image_path = self.camera.capture_image()
                if image_path and os.path.exists(image_path):
                    response = self.ai.get_vision_response(text, image_path)
                    try:
                        os.unlink(image_path)
                    except:
                        pass
                    return response
                return "I couldn't capture an image. Let me try again."
            return "Camera is not available. Please check your camera connection."
        
        # Joke
        if any(kw in text_lower for kw in ['joke', 'funny']):
            return self.ai.tell_joke()
        
        # Default - AI chat
        return self.ai.get_response(text)
    
    def run(self):
        """Run the GUI"""
        self.root.mainloop()
        
        # Cleanup
        if self.camera:
            self.camera.release()
        self.reminders.stop()

def main():
    app = AkiraCompanionGUI()
    app.run()

if __name__ == "__main__":
    main()
