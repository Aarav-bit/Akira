/**
 * AKIRA AI Companion Interface
 * Futuristic, Cinematic, Emotionally Warm
 */

class AkiraCompanion {
    constructor() {
        // DOM Elements
        this.avatarContainer = document.getElementById('avatarContainer');
        this.statusText = document.getElementById('statusText');
        this.statusLabel = this.statusText.querySelector('.status-label');
        this.chatContainer = document.getElementById('chatContainer');
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.micBtn = document.getElementById('micBtn');
        this.timeElement = document.getElementById('currentTime');
        this.particlesContainer = document.getElementById('particles');

        // State
        this.state = 'ready'; // ready, listening, speaking, thinking
        this.isRecording = false;

        // Initialize
        this.init();
    }

    init() {
        this.bindEvents();
        this.updateTime();
        this.createParticles();
        this.startAmbientAnimations();

        // Update time every minute
        setInterval(() => this.updateTime(), 60000);
    }

    bindEvents() {
        // Send message
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Microphone
        this.micBtn.addEventListener('click', () => this.toggleRecording());

        // Input focus effects
        this.messageInput.addEventListener('focus', () => {
            this.messageInput.parentElement.classList.add('focused');
        });

        this.messageInput.addEventListener('blur', () => {
            this.messageInput.parentElement.classList.remove('focused');
        });
    }

    updateTime() {
        const now = new Date();
        const hours = now.getHours();
        const minutes = now.getMinutes().toString().padStart(2, '0');
        const period = hours >= 12 ? 'PM' : 'AM';
        const displayHours = hours % 12 || 12;
        this.timeElement.textContent = `${displayHours}:${minutes} ${period}`;
    }

    createParticles() {
        const particleCount = 12;

        for (let i = 0; i < particleCount; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';

            // Random position around the avatar
            const angle = (i / particleCount) * Math.PI * 2;
            const radius = 100 + Math.random() * 40;
            const x = Math.cos(angle) * radius + 140;
            const y = Math.sin(angle) * radius + 140;

            particle.style.left = `${x}px`;
            particle.style.top = `${y}px`;
            particle.style.animationDelay = `${Math.random() * 3}s`;
            particle.style.animationDuration = `${2 + Math.random() * 2}s`;

            this.particlesContainer.appendChild(particle);
        }
    }

    startAmbientAnimations() {
        // Subtle parallax on mouse move
        document.addEventListener('mousemove', (e) => {
            const { clientX, clientY } = e;
            const centerX = window.innerWidth / 2;
            const centerY = window.innerHeight / 2;

            const moveX = (clientX - centerX) / 50;
            const moveY = (clientY - centerY) / 50;

            this.avatarContainer.style.transform = `translate(${moveX}px, ${moveY}px)`;
        });
    }

    setState(newState) {
        // Remove previous state classes
        this.avatarContainer.classList.remove('ready', 'listening', 'speaking', 'thinking');

        // Add new state
        this.state = newState;
        this.avatarContainer.classList.add(newState);

        // Update status text with animation
        this.statusLabel.style.opacity = '0';

        setTimeout(() => {
            const statusTexts = {
                ready: 'Ready',
                listening: 'Listening...',
                speaking: 'Speaking...',
                thinking: 'Thinking...'
            };

            this.statusLabel.textContent = statusTexts[newState];
            this.statusLabel.style.opacity = '1';
        }, 150);
    }

    toggleRecording() {
        if (this.isRecording) {
            this.stopRecording();
        } else {
            this.startRecording();
        }
    }

    startRecording() {
        this.isRecording = true;
        this.micBtn.classList.add('active');
        this.setState('listening');

        // Simulate voice input
        // In real implementation, integrate with Web Speech API
        console.log('Recording started...');
    }

    stopRecording() {
        this.isRecording = false;
        this.micBtn.classList.remove('active');
        this.setState('thinking');

        // Simulate processing delay
        setTimeout(() => {
            this.setState('ready');
        }, 1500);

        console.log('Recording stopped...');
    }

    sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message) return;

        // Add user message
        this.addMessage(message, 'user');
        this.messageInput.value = '';

        // Set thinking state
        this.setState('thinking');

        // Simulate AI response
        setTimeout(() => {
            this.setState('speaking');

            // Add AI response
            setTimeout(() => {
                const responses = [
                    "I understand. Let me help you with that.",
                    "Of course! I'm happy to assist.",
                    "That's a great question. Here's what I think...",
                    "I'm on it! Give me just a moment.",
                    "Absolutely! Let me take care of that for you."
                ];

                const randomResponse = responses[Math.floor(Math.random() * responses.length)];
                this.addMessage(randomResponse, 'ai');

                setTimeout(() => {
                    this.setState('ready');
                }, 500);
            }, 800);
        }, 1000);
    }

    addMessage(text, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;

        if (type === 'user') {
            messageDiv.innerHTML = `
                <div class="message-avatar">
                    <svg viewBox="0 0 24 24" fill="none">
                        <circle cx="12" cy="8" r="4" stroke="currentColor" stroke-width="1.5"/>
                        <path d="M4 20C4 16.6863 7.13401 14 11 14H13C16.866 14 20 16.6863 20 20" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                    </svg>
                </div>
                <div class="message-bubble">
                    <p>${this.escapeHtml(text)}</p>
                </div>
            `;
        } else {
            messageDiv.innerHTML = `
                <div class="message-avatar ai">
                    <span class="heart-icon">💗</span>
                </div>
                <div class="message-bubble">
                    <span class="ai-name">Akira:</span>
                    <p>${this.escapeHtml(text)}</p>
                </div>
            `;
        }

        this.chatContainer.appendChild(messageDiv);

        // Scroll to bottom smoothly
        this.chatContainer.scrollTo({
            top: this.chatContainer.scrollHeight,
            behavior: 'smooth'
        });
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Demo Mode - Cycle through states
class DemoController {
    constructor(companion) {
        this.companion = companion;
        this.states = ['ready', 'listening', 'thinking', 'speaking'];
        this.currentIndex = 0;
    }

    startDemo() {
        setInterval(() => {
            this.currentIndex = (this.currentIndex + 1) % this.states.length;
            this.companion.setState(this.states[this.currentIndex]);
        }, 3000);
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    const akira = new AkiraCompanion();

    // Optional: Start demo mode to showcase animations
    // const demo = new DemoController(akira);
    // demo.startDemo();

    console.log('🌟 AKIRA AI Companion initialized');
});
