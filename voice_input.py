import speech_recognition as sr
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class VoiceInput:
    # Sensitivity presets: (energy_threshold, pause_threshold)
    SENSITIVITY_LEVELS = {
        'low': (500, 0.8),      # Less sensitive - needs louder voice
        'medium': (300, 0.6),   # Default - balanced
        'high': (150, 0.4)      # More sensitive - picks up quieter voices
    }
    
    def __init__(self, sensitivity: str = 'medium'):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.sensitivity = sensitivity
        
        # Quick calibration
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
        
        # Apply sensitivity settings
        self.set_sensitivity(sensitivity)
        self.recognizer.dynamic_energy_threshold = True
    
    def set_sensitivity(self, level: str):
        """Set sensitivity level: 'low', 'medium', or 'high'"""
        if level not in self.SENSITIVITY_LEVELS:
            level = 'medium'
        
        self.sensitivity = level
        energy, pause = self.SENSITIVITY_LEVELS[level]
        self.recognizer.energy_threshold = energy
        self.recognizer.pause_threshold = pause
        logger.info(f"Voice sensitivity set to {level}: energy={energy}, pause={pause}")
    
    def get_sensitivity(self) -> str:
        """Get current sensitivity level"""
        return self.sensitivity
    
    def listen(self, timeout=5, phrase_time_limit=10) -> Optional[str]:
        try:
            with self.microphone as source:
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout, 
                    phrase_time_limit=phrase_time_limit
                )
            
            try:
                text = self.recognizer.recognize_google(audio)
                return text
            except sr.UnknownValueError:
                return None
            except sr.RequestError:
                return None
                
        except sr.WaitTimeoutError:
            return None
        except Exception:
            return None
