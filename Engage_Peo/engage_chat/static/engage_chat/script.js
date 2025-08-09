document.addEventListener("DOMContentLoaded", () => {
    const chatForm = document.getElementById("chat-form");
    const userInput = document.getElementById("user-input");
    const chatBox = document.getElementById("chat-box");
    const typingIndicator = document.getElementById("typing-indicator");
    const welcomeScreen = document.getElementById("welcome-screen");
    const themeButtons = document.querySelectorAll(".theme-btn");
    const newChatBtn = document.getElementById("new-chat");
    const clearChatBtn = document.getElementById("clear-chat");

    // Theme handling
    function setTheme(theme) {
        document.body.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        
        // Update active state of theme buttons
        themeButtons.forEach(btn => {
            btn.classList.toggle('active', btn.dataset.theme === theme);
        });
    }

    // Handle welcome screen visibility
    function updateWelcomeScreen() {
        const hasMessages = chatBox.children.length > 0;
        welcomeScreen.classList.toggle('hidden', hasMessages);
    }

    // Initialize theme and welcome screen
    const savedTheme = localStorage.getItem('theme') || 'system';
    setTheme(savedTheme);
    updateWelcomeScreen();

    // Theme buttons click listener
    themeButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            setTheme(btn.dataset.theme);
        });
    });

    // New chat button click listener
    newChatBtn.addEventListener('click', () => {
        chatBox.innerHTML = '';
        updateWelcomeScreen();
    });

    // Clear chat button click listener
    clearChatBtn.addEventListener('click', () => {
        if (confirm('Are you sure you want to clear the chat history?')) {
            chatBox.innerHTML = '';
            updateWelcomeScreen();
        }
    });

    // Suggestion chips click listener
    document.querySelectorAll('.suggestion-chip').forEach(chip => {
        chip.addEventListener('click', () => {
            userInput.value = chip.textContent;
            chatForm.dispatchEvent(new Event('submit'));
        });
    });

    function appendMessage(text, className, avatar) {
        const message = document.createElement("div");
        message.classList.add("message", className);

        const avatarEl = document.createElement("div");
        avatarEl.classList.add("avatar");
        
        // Use Font Awesome icons instead of emojis
        const icon = document.createElement("i");
        icon.className = className === "user-message" ? "fas fa-user" : "fas fa-robot";
        avatarEl.appendChild(icon);

        const bubble = document.createElement("div");
        bubble.classList.add("bubble");
        bubble.textContent = text;

        message.appendChild(avatarEl);
        message.appendChild(bubble);
        chatBox.appendChild(message);
        chatBox.scrollTop = chatBox.scrollHeight;

        return bubble;
    }

    async function typeMessage(messageElement, text) {
        messageElement.textContent = "";
        for (let i = 0; i < text.length; i++) {
            messageElement.textContent += text.charAt(i);
            chatBox.scrollTop = chatBox.scrollHeight;
            await new Promise(res => setTimeout(res, 15));
        }
    }

    async function fetchBotResponse(query) {
        if (typingIndicator) {
            typingIndicator.classList.remove("hidden");
            // Scroll to show typing indicator
            setTimeout(() => {
                chatBox.scrollTop = chatBox.scrollHeight;
            }, 100);
        }

        try {
            const res = await fetch(`/ask/?q=${encodeURIComponent(query)}`);
            const data = await res.json();
            
            if (typingIndicator) {
                typingIndicator.classList.add("hidden");
            }

            const botBubble = appendMessage("", "bot-message", "bot");
            await typeMessage(botBubble, data.answer || "I couldn't understand that.");
        } catch (error) {
            console.error("Error fetching response:", error);
            
            if (typingIndicator) {
                typingIndicator.classList.add("hidden");
            }

            const errorBubble = appendMessage("", "bot-message", "bot");
            await typeMessage(errorBubble, "⚠️ Error fetching response. Please try again.");
        }
    }

    chatForm.addEventListener("submit", e => {
        e.preventDefault();
        const message = userInput.value.trim();
        if (!message) return;

        appendMessage(message, "user-message", "👤");
        userInput.value = "";
        welcomeScreen.classList.add('hidden');
        fetchBotResponse(message);
    });
});
