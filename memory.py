"""
Akira Long-term Memory Module
Persistent storage for user preferences, facts, and habits
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class Memory:
    def __init__(self, memory_file: str = None):
        """Initialize memory with persistent JSON storage"""
        if memory_file is None:
            memory_file = Path(__file__).parent / "akira_memory.json"
        
        self.memory_file = Path(memory_file)
        self.data = self._load()
    
    def _load(self) -> Dict[str, Any]:
        """Load memory from file"""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading memory: {e}")
        
        # Default memory structure
        return {
            "user": {
                "name": None,
                "birthday": None,
                "location": None
            },
            "preferences": {
                "music": [],
                "topics": [],
                "greeting_style": "friendly"
            },
            "facts": [],  # Things user asked to remember
            "habits": {
                "frequent_commands": {},
                "last_interaction": None
            },
            "conversation_history": [],  # Store recent conversations
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    
    def _save(self):
        """Save memory to file"""
        try:
            self.data["updated_at"] = datetime.now().isoformat()
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving memory: {e}")
    
    # User info methods
    def set_user_name(self, name: str):
        """Remember user's name"""
        self.data["user"]["name"] = name
        self._save()
    
    def get_user_name(self) -> Optional[str]:
        """Get user's name"""
        return self.data["user"].get("name")
    
    def set_user_info(self, key: str, value: str):
        """Set user info (birthday, location, etc.)"""
        self.data["user"][key] = value
        self._save()
    
    def get_user_info(self, key: str) -> Optional[str]:
        """Get user info"""
        return self.data["user"].get(key)
    
    # Preferences methods
    def add_preference(self, category: str, value: str):
        """Add a preference (music, topic, etc.)"""
        if category not in self.data["preferences"]:
            self.data["preferences"][category] = []
        
        if isinstance(self.data["preferences"][category], list):
            if value not in self.data["preferences"][category]:
                self.data["preferences"][category].append(value)
        else:
            self.data["preferences"][category] = value
        
        self._save()
    
    def get_preferences(self, category: str = None) -> Any:
        """Get preferences"""
        if category:
            return self.data["preferences"].get(category, [])
        return self.data["preferences"]
    
    # Facts methods (explicit remember requests)
    def remember_fact(self, fact: str):
        """Remember a fact the user told"""
        fact_entry = {
            "content": fact,
            "timestamp": datetime.now().isoformat()
        }
        self.data["facts"].append(fact_entry)
        self._save()
    
    def get_facts(self) -> List[Dict]:
        """Get all remembered facts"""
        return self.data.get("facts", [])
    
    def forget_fact(self, keyword: str) -> bool:
        """Forget facts containing keyword"""
        original_count = len(self.data["facts"])
        self.data["facts"] = [
            f for f in self.data["facts"] 
            if keyword.lower() not in f["content"].lower()
        ]
        
        if len(self.data["facts"]) < original_count:
            self._save()
            return True
        return False
    
    # Habits tracking
    def track_command(self, command: str):
        """Track frequently used commands"""
        if command not in self.data["habits"]["frequent_commands"]:
            self.data["habits"]["frequent_commands"][command] = 0
        
        self.data["habits"]["frequent_commands"][command] += 1
        self.data["habits"]["last_interaction"] = datetime.now().isoformat()
        self._save()
    
    def get_frequent_commands(self, limit: int = 5) -> List[str]:
        """Get most frequently used commands"""
        commands = self.data["habits"]["frequent_commands"]
        sorted_commands = sorted(commands.items(), key=lambda x: x[1], reverse=True)
        return [cmd for cmd, count in sorted_commands[:limit]]
    
    # Memory context for AI
    def get_context_for_ai(self) -> str:
        """Get memory context to inject into AI prompt"""
        context_parts = []
        
        # User info
        if self.data["user"]["name"]:
            context_parts.append(f"User's name is {self.data['user']['name']}.")
        
        if self.data["user"].get("birthday"):
            context_parts.append(f"User's birthday is {self.data['user']['birthday']}.")
        
        if self.data["user"].get("location"):
            context_parts.append(f"User lives in {self.data['user']['location']}.")
        
        # Preferences
        prefs = self.data["preferences"]
        if prefs.get("music"):
            context_parts.append(f"User likes music: {', '.join(prefs['music'][:3])}.")
        
        if prefs.get("topics"):
            context_parts.append(f"User is interested in: {', '.join(prefs['topics'][:3])}.")
        
        # Recent facts
        facts = self.data.get("facts", [])[-5:]  # Last 5 facts
        for fact in facts:
            context_parts.append(f"Remember: {fact['content']}")
        
        if context_parts:
            return "What you know about the user: " + " ".join(context_parts)
        return ""
    
    # Conversation history methods
    def store_conversation(self, user_msg: str, ai_response: str):
        """Store a conversation exchange with timestamp"""
        if "conversation_history" not in self.data:
            self.data["conversation_history"] = []
        
        exchange = {
            "user": user_msg,
            "ai": ai_response,
            "timestamp": datetime.now().isoformat()
        }
        self.data["conversation_history"].append(exchange)
        
        # Keep only last 50 conversations
        if len(self.data["conversation_history"]) > 50:
            self.data["conversation_history"] = self.data["conversation_history"][-50:]
        
        self._save()
    
    def get_conversation_summary(self) -> str:
        """Generate a summary of recent conversations"""
        history = self.data.get("conversation_history", [])
        
        if not history:
            return "We haven't chatted much yet! Say something to get started. 💬"
        
        # Get last 10 conversations
        recent = history[-10:]
        
        # Build summary
        topics = []
        for conv in recent:
            user_msg = conv.get("user", "")[:50]  # First 50 chars
            if user_msg:
                topics.append(user_msg)
        
        if len(history) == 1:
            return f"We've had 1 conversation. You asked about: {topics[0]}..."
        else:
            summary = f"We've had {len(history)} conversations. "
            if topics:
                summary += f"Recently we discussed: {', '.join(topics[:3])}..."
            return summary
    
    def parse_summary_command(self, text: str) -> Optional[str]:
        """Check if user is asking for conversation summary"""
        text_lower = text.lower()
        summary_triggers = [
            "what did we discuss",
            "what did we talk about",
            "summarize our chat",
            "conversation summary",
            "what have we talked about",
            "recap our chat"
        ]
        
        for trigger in summary_triggers:
            if trigger in text_lower:
                return self.get_conversation_summary()
        
        return None
    
    # Parse and handle memory commands
    def parse_remember_command(self, text: str) -> Optional[str]:
        """Parse 'remember' commands and store info"""
        text_lower = text.lower()
        
        # "Remember my name is X"
        if "my name is" in text_lower:
            name = text.split("my name is")[-1].strip().strip(".!").title()
            self.set_user_name(name)
            return f"Got it! I'll remember your name is {name}. 💕"
        
        # "Remember my birthday is X"
        if "my birthday" in text_lower:
            birthday = text.split("birthday")[-1].strip().strip(".!")
            birthday = birthday.replace("is", "").strip()
            self.set_user_info("birthday", birthday)
            return f"I'll remember your birthday is {birthday}! 🎂"
        
        # "Remember I live in X"
        if "i live in" in text_lower or "i'm from" in text_lower:
            if "i live in" in text_lower:
                location = text.split("i live in")[-1].strip().strip(".!")
            else:
                location = text.split("i'm from")[-1].strip().strip(".!")
            self.set_user_info("location", location.title())
            return f"Noted! You're from {location.title()}. 🏠"
        
        # "Remember I like X music"
        if "i like" in text_lower and "music" in text_lower:
            music = text_lower.split("i like")[-1].replace("music", "").strip().strip(".!")
            self.add_preference("music", music)
            return f"I'll remember you like {music} music! 🎵"
        
        # Generic "Remember that X"
        if "remember that" in text_lower or "remember " in text_lower:
            fact = text.lower().replace("remember that", "").replace("remember ", "").strip()
            if len(fact) > 3:
                self.remember_fact(fact)
                return f"I'll remember that! ✨"
        
        return None
    
    def parse_recall_command(self, text: str) -> Optional[str]:
        """Parse 'what is my' type commands"""
        text_lower = text.lower()
        
        if "my name" in text_lower:
            name = self.get_user_name()
            if name:
                return f"Your name is {name}! 😊"
            return "I don't know your name yet. Tell me by saying 'My name is...'!"
        
        if "my birthday" in text_lower:
            bday = self.get_user_info("birthday")
            if bday:
                return f"Your birthday is {bday}! 🎂"
            return "I don't know your birthday yet. Tell me!"
        
        if "about me" in text_lower or "what do you know" in text_lower:
            context = self.get_context_for_ai()
            if context:
                return context.replace("What you know about the user: ", "Here's what I know about you: ")
            return "I don't know much about you yet! Tell me about yourself. 💕"
        
        return None
    
    def parse_forget_command(self, text: str) -> Optional[str]:
        """Parse 'forget' commands"""
        text_lower = text.lower()
        
        if "forget my name" in text_lower:
            self.data["user"]["name"] = None
            self._save()
            return "I've forgotten your name."
        
        if "forget" in text_lower:
            # Try to forget facts with keyword
            keyword = text_lower.replace("forget", "").replace("about", "").strip()
            if keyword and self.forget_fact(keyword):
                return f"I've forgotten about {keyword}."
        
        return None
