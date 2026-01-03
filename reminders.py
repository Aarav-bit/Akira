"""
Reminders Module - Timed reminders with notifications
"""
import threading
import time
import logging
import re
from datetime import datetime, timedelta
from typing import Optional, Callable

logger = logging.getLogger(__name__)

class Reminders:
    def __init__(self):
        self.reminders = []
        self._running = True
        self._thread = threading.Thread(target=self._reminder_loop, daemon=True)
        self._thread.start()
        
        try:
            from winotify import Notification
            self.notification_available = True
        except ImportError:
            self.notification_available = False
    
    def _reminder_loop(self):
        """Background loop to check reminders"""
        while self._running:
            now = datetime.now()
            
            for reminder in self.reminders[:]:
                if now >= reminder['time']:
                    self._show_notification(reminder['message'])
                    self.reminders.remove(reminder)
            
            time.sleep(1)
    
    def _show_notification(self, message: str):
        """Show Windows notification"""
        try:
            if self.notification_available:
                from winotify import Notification, audio
                
                toast = Notification(
                    app_id="Akira",
                    title="Reminder",
                    msg=message,
                    duration="long"
                )
                toast.set_audio(audio.Default, loop=False)
                toast.show()
            else:
                # Fallback - just print
                print(f"\n⏰ REMINDER: {message}\n")
        except Exception as e:
            logger.error(f"Notification error: {e}")
            print(f"\n⏰ REMINDER: {message}\n")
    
    def parse_time(self, text: str) -> Optional[timedelta]:
        """Parse time from text like '5 minutes', '1 hour', '30 seconds'"""
        text = text.lower()
        
        # Match patterns like "5 minutes", "1 hour", "30 seconds"
        patterns = [
            (r'(\d+)\s*(?:second|sec|s)', 'seconds'),
            (r'(\d+)\s*(?:minute|min|m)', 'minutes'),
            (r'(\d+)\s*(?:hour|hr|h)', 'hours'),
        ]
        
        total_seconds = 0
        
        for pattern, unit in patterns:
            match = re.search(pattern, text)
            if match:
                value = int(match.group(1))
                if unit == 'seconds':
                    total_seconds += value
                elif unit == 'minutes':
                    total_seconds += value * 60
                elif unit == 'hours':
                    total_seconds += value * 3600
        
        if total_seconds > 0:
            return timedelta(seconds=total_seconds)
        
        return None
    
    def set_reminder(self, text: str) -> str:
        """Set a reminder from natural language"""
        try:
            # Parse the time
            duration = self.parse_time(text)
            
            if not duration:
                return "I couldn't understand the time. Try saying 'remind me in 5 minutes to stretch'."
            
            # Extract the reminder message
            # Remove common phrases
            message = text
            for phrase in ['remind me in', 'remind me', 'set a reminder', 'set reminder', 
                          'in', 'to', 'that', 'about']:
                message = re.sub(rf'\b{phrase}\b', '', message, flags=re.IGNORECASE)
            
            # Remove time patterns
            message = re.sub(r'\d+\s*(?:second|sec|s|minute|min|m|hour|hr|h)s?', '', message, flags=re.IGNORECASE)
            message = message.strip(' .,!?')
            
            if not message:
                message = "Time's up!"
            
            # Set the reminder
            reminder_time = datetime.now() + duration
            self.reminders.append({
                'time': reminder_time,
                'message': message
            })
            
            # Format response
            if duration.total_seconds() < 60:
                time_str = f"{int(duration.total_seconds())} seconds"
            elif duration.total_seconds() < 3600:
                time_str = f"{int(duration.total_seconds() / 60)} minutes"
            else:
                time_str = f"{duration.total_seconds() / 3600:.1f} hours"
            
            return f"I'll remind you in {time_str}: {message}"
            
        except Exception as e:
            logger.error(f"Reminder error: {e}")
            return "Sorry, I couldn't set that reminder."
    
    def list_reminders(self) -> str:
        """List all active reminders"""
        if not self.reminders:
            return "You have no active reminders."
        
        lines = []
        for i, r in enumerate(self.reminders, 1):
            time_left = r['time'] - datetime.now()
            minutes = int(time_left.total_seconds() / 60)
            lines.append(f"{i}. {r['message']} - in {minutes} minutes")
        
        return "Active reminders: " + ". ".join(lines)
    
    def clear_reminders(self) -> str:
        """Clear all reminders"""
        count = len(self.reminders)
        self.reminders.clear()
        return f"Cleared {count} reminder(s)."
    
    def stop(self):
        """Stop the reminder thread"""
        self._running = False
