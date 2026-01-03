import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

from groq import Groq
import logging
from typing import List, Dict, Optional
import random
import base64

logger = logging.getLogger(__name__)

class AICompanion:
    # Emotion keywords for detection
    EMOTION_PATTERNS = {
        'happy': ['happy', 'great', 'awesome', 'amazing', 'love', 'excited', 'wonderful', 'fantastic', 'yay', 'thanks', 'thank you', '😊', '😄', '❤️', 'haha', 'lol'],
        'sad': ['sad', 'upset', 'depressed', 'unhappy', 'crying', 'terrible', 'awful', 'miss', 'lonely', 'hurt', '😢', '😭', 'unfortunately'],
        'angry': ['angry', 'mad', 'furious', 'annoyed', 'frustrated', 'hate', 'stupid', 'damn', 'ugh', '😠', '😡'],
        'curious': ['what', 'how', 'why', 'when', 'where', 'who', 'tell me', 'explain', 'wondering', '?', 'curious'],
        'stressed': ['stressed', 'overwhelmed', 'anxious', 'worried', 'panic', 'busy', 'tired', 'exhausted']
    }
    
    def __init__(self, memory=None):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY environment variable is required")
        
        self.client = Groq(api_key=self.api_key)
        self.model = "llama-3.1-8b-instant"
        self.vision_model = "meta-llama/llama-4-scout-17b-16e-instruct"
        
        self.conversation_history: List[Dict[str, str]] = []
        self.memory = memory
        self.current_emotion = "neutral"
        
        # Akira personality - concise for speed
        self.base_system_prompt = """You are Akira, a friendly AI voice assistant.
- Keep responses SHORT (1-2 sentences max)
- Be conversational and helpful
- Use the user's name when you know it"""

    def detect_emotion(self, text: str) -> str:
        """Detect emotion from user input using keyword matching"""
        text_lower = text.lower()
        
        emotion_scores = {emotion: 0 for emotion in self.EMOTION_PATTERNS}
        
        for emotion, keywords in self.EMOTION_PATTERNS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    emotion_scores[emotion] += 1
        
        # Get highest scoring emotion
        max_emotion = max(emotion_scores, key=emotion_scores.get)
        if emotion_scores[max_emotion] > 0:
            self.current_emotion = max_emotion
            return max_emotion
        
        self.current_emotion = "neutral"
        return "neutral"

    def _get_system_prompt(self) -> str:
        """Build system prompt with memory context and emotion awareness"""
        prompt = self.base_system_prompt
        
        # Add emotion-aware instructions
        emotion_prompts = {
            'happy': "\n- The user seems happy! Match their positive energy.",
            'sad': "\n- The user seems down. Be extra gentle and supportive.",
            'angry': "\n- The user seems frustrated. Stay calm and helpful.",
            'curious': "\n- The user is curious. Be informative but concise.",
            'stressed': "\n- The user seems stressed. Be calming and reassuring.",
            'neutral': ""
        }
        prompt += emotion_prompts.get(self.current_emotion, "")
        
        if self.memory:
            context = self.memory.get_context_for_ai()
            if context:
                prompt += f"\n\n{context}"
        
        return prompt

    def get_response(self, user_message: str) -> str:
        try:
            # Detect emotion before generating response
            self.detect_emotion(user_message)
            
            messages = [{"role": "system", "content": self._get_system_prompt()}]
            messages.extend(self.conversation_history[-20:])
            messages.append({"role": "user", "content": user_message})
            
            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                temperature=0.7,
                max_tokens=80,  # Reduced for faster response
                top_p=0.9
            )
            
            response = chat_completion.choices[0].message.content
            
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": response})
            
            if len(self.conversation_history) > 30:
                self.conversation_history = self.conversation_history[-30:]
            
            return response
            
        except Exception as e:
            logger.error(f"Error: {e}")
            return self._get_fallback_response()
    
    def tell_joke(self) -> str:
        try:
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": "Tell me a short funny joke!"}
            ]
            
            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                temperature=0.9,
                max_tokens=100
            )
            
            return chat_completion.choices[0].message.content
            
        except Exception:
            return "Why don't scientists trust atoms? Because they make up everything!"
    
    def _get_fallback_response(self) -> str:
        return random.choice([
            "Sorry, I had trouble with that. Could you try again?",
            "Something went wrong. Let's try that again!",
        ])
    
    def get_vision_response(self, user_message: str, image_path: str) -> str:
        try:
            with open(image_path, "rb") as f:
                image_base64 = base64.b64encode(f.read()).decode('utf-8')
            
            messages = [
                {"role": "system", "content": "You are Akira. Describe what you see briefly (1-2 sentences)."},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_message},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                    ]
                }
            ]
            
            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model=self.vision_model,
                temperature=0.7,
                max_tokens=100
            )
            
            response = chat_completion.choices[0].message.content
            self.conversation_history.append({"role": "user", "content": f"[Vision]: {user_message}"})
            self.conversation_history.append({"role": "assistant", "content": response})
            
            return response
            
        except Exception as e:
            logger.error(f"Vision error: {e}")
            return "I couldn't analyze the image. Please try again."
    
    def reset_conversation(self):
        self.conversation_history = []
