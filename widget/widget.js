(function () {
  const host = document.createElement("div");
  document.body.appendChild(host);
  const shadow = host.attachShadow({ mode: "open" });

  const style = document.createElement("style");
  style.textContent = `
    .bubble {
      position: fixed;
      bottom: 20px;
      right: 20px;
      width: 60px;
      height: 60px;
      border-radius: 50%;
      background: #111827;
      color: white;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      font-family: sans-serif;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
      z-index: 999999;
      font-size: 24px;
      transition: transform 0.2s ease;
    }
    .bubble:hover {
      transform: scale(1.05);
    }
    .chat-container {
      position: fixed;
      bottom: 90px;
      right: 20px;
      width: 350px;
      height: 480px;
      background: white;
      border-radius: 12px;
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
      display: flex;
      flex-direction: column;
      overflow: hidden;
      font-family: sans-serif;
      z-index: 999999;
      border: 1px solid #e5e7eb;
      opacity: 0;
      transform: translateY(10px) scale(0.95);
      pointer-events: none;
      transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .chat-container.open {
      opacity: 1;
      transform: translateY(0) scale(1);
      pointer-events: auto;
    }
    .chat-header {
      background: #111827;
      color: white;
      padding: 16px;
      font-weight: 600;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .close-btn {
      background: none;
      border: none;
      color: white;
      font-size: 18px;
      cursor: pointer;
    }
    .chat-messages {
      flex: 1;
      padding: 16px;
      overflow-y: auto;
      background: #f9fafb;
      font-size: 14px;
      color: #374151;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    .message {
      max-width: 80%;
      padding: 10px 14px;
      border-radius: 10px;
      line-height: 1.4;
      word-break: break-word;
    }
    .message.user {
      background: #111827;
      color: white;
      align-self: flex-end;
      border-bottom-right-radius: 2px;
    }
    .message.assistant {
      background: #e5e7eb;
      color: #1f2937;
      align-self: flex-start;
      border-bottom-left-radius: 2px;
    }
    .chat-input-area {
      padding: 12px;
      border-top: 1px solid #e5e7eb;
      background: white;
      display: flex;
      gap: 8px;
    }
    .chat-input {
      flex: 1;
      padding: 8px 12px;
      border: 1px solid #d1d5db;
      border-radius: 6px;
      outline: none;
      font-size: 14px;
    }
    .chat-input:focus {
      border-color: #111827;
    }
    .send-btn {
      background: #111827;
      color: white;
      border: none;
      padding: 8px 16px;
      border-radius: 6px;
      cursor: pointer;
      font-weight: 500;
    }
    .send-btn:hover {
      background: #1f2937;
    }
  `;
  shadow.appendChild(style);

  // Chat Container Structure
  const container = document.createElement("div");
  container.className = "chat-container";
  container.innerHTML = `
    <div class="chat-header">
      <span>Ask AI Support</span>
      <button class="close-btn">&times;</button>
    </div>
    <div class="chat-messages" id="chat-messages">
      <div class="message assistant">Hello! How can I help you today?</div>
    </div>
    <div class="chat-input-area">
      <input type="text" class="chat-input" id="chat-input" placeholder="Type your message..." />
      <button class="send-btn" id="send-btn">Send</button>
    </div>
  `;
  shadow.appendChild(container);

  // Floating Bubble Button
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = "💬";
  shadow.appendChild(bubble);

  // Toggle Logic
  let isOpen = false;
  bubble.addEventListener("click", () => {
    isOpen = !isOpen;
    if (isOpen) {
      container.classList.add("open");
      bubble.textContent = "✕";
      shadow.getElementById("chat-input").focus();
    } else {
      container.classList.remove("open");
      bubble.textContent = "💬";
    }
  });

  const closeBtn = container.querySelector(".close-btn");
  closeBtn.addEventListener("click", () => {
    isOpen = false;
    container.classList.remove("open");
    bubble.textContent = "💬";
  });

  // API Integration Logic
  const inputField = shadow.getElementById("chat-input");
  const sendButton = shadow.getElementById("send-btn");
  const messagesContainer = shadow.getElementById("chat-messages");

  async function handleSendMessage() {
    const text = inputField.value.trim();
    if (!text) return;

    // Append user message to UI
    const userMsgDiv = document.createElement("div");
    userMsgDiv.className = "message user";
    userMsgDiv.textContent = text;
    messagesContainer.appendChild(userMsgDiv);

    inputField.value = "";
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    // Append loading placeholder
    const loadingDiv = document.createElement("div");
    loadingDiv.className = "message assistant";
    loadingDiv.textContent = "Thinking...";
    messagesContainer.appendChild(loadingDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    try {
      const response = await fetch("http://localhost:8000/chat/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question: text }),
      });

      if (!response.ok) {
        throw new Error("Failed to fetch response from server.");
      }

      const data = await response.json();
      loadingDiv.textContent = data.answer || "No response received.";
    } catch (error) {
      loadingDiv.textContent = "Error connecting to AI service. Please try again.";
      console.error(error);
    }

    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  sendButton.addEventListener("click", handleSendMessage);
  inputField.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
      handleSendMessage();
    }
  });
})();