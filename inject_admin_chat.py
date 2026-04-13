import os
from pathlib import Path

CHATBOT_HTML = """
    <!-- AI Chat Widget for Admin -->
    <div id="aiChatWidget" style="position: fixed; bottom: 20px; right: 20px; z-index: 1000;">
        <button id="aiChatBtn" style="background: var(--primary); color: white; border: none; border-radius: 50%; width: 60px; height: 60px; font-size: 24px; cursor: pointer; box-shadow: var(--primary-glow); transition: var(--transition-bounce);">
            <i class="fas fa-robot"></i>
        </button>
        <div id="aiChatBox" style="display: none; position: absolute; bottom: 80px; right: 0; width: 340px; background: var(--glass-bg); backdrop-filter: blur(25px); border-radius: 15px; box-shadow: var(--glass-shadow); border: 1px solid var(--glass-border); overflow: hidden; flex-direction: column; height: 420px; z-index: 2000;">
            <div style="background: var(--primary); color: white; padding: 15px; font-weight: bold; display: flex; justify-content: space-between;">
                <span>AI Administrator Engine</span>
                <i class="fas fa-times" id="closeChatBtn" style="cursor: pointer;"></i>
            </div>
            <div id="chatMessages" style="flex: 1; padding: 15px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px;">
                <div style="background: rgba(255,255,255,0.05); border: 1px solid var(--glass-border); color: var(--text-primary); padding: 10px; border-radius: 10px; max-width: 85%; align-self: flex-start; font-size: 14px;">Hi! I'm your AI Admin Assistant. I can securely query the entire company's database for you. Ask me about total payroll, staff numbers, or pending workflows.</div>
            </div>
            <div style="padding: 10px; border-top: 1px solid var(--glass-border); display: flex;">
                <input type="text" id="chatInput" placeholder="Type a message..." style="flex: 1; border: 1px solid var(--input-border); background: var(--input-bg); color: var(--text-primary); border-radius: 5px; padding: 8px; outline: none;">
                <button id="sendChatBtn" style="background: var(--primary); color: white; border: none; padding: 8px 15px; border-radius: 5px; margin-left: 5px; cursor: pointer;"><i class="fas fa-paper-plane"></i></button>
            </div>
        </div>
    </div>
    
    <script>
        // AI Chat Logic
        if (document.getElementById('aiChatBtn')) {
            document.getElementById('aiChatBtn').addEventListener('click', () => {
                const box = document.getElementById('aiChatBox');
                box.style.display = box.style.display === 'none' ? 'flex' : 'none';
            });

            document.getElementById('closeChatBtn').addEventListener('click', () => {
                document.getElementById('aiChatBox').style.display = 'none';
            });

            document.getElementById('sendChatBtn').addEventListener('click', sendChatMessage);
            document.getElementById('chatInput').addEventListener('keypress', (e) => {
                if (e.key === 'Enter') sendChatMessage();
            });
        }

        async function sendChatMessage() {
            const input = document.getElementById('chatInput');
            const messages = document.getElementById('chatMessages');
            const text = input.value.trim();
            if (!text) return;

            const userMsg = document.createElement('div');
            userMsg.style.cssText = 'background: var(--primary); color: white; padding: 10px; border-radius: 10px; max-width: 80%; align-self: flex-end; font-size: 14px;';
            userMsg.textContent = text;
            messages.appendChild(userMsg);
            input.value = '';

            const typingDiv = document.createElement('div');
            typingDiv.style.cssText = 'color: var(--text-secondary); font-size: 12px; margin-top: -5px; margin-left: 5px;';
            typingDiv.textContent = 'AI is fetching data...';
            messages.appendChild(typingDiv);
            messages.scrollTop = messages.scrollHeight;

            try {
                const token = localStorage.getItem('token');
                const response = await fetch('http://localhost:8000/api/admin/ai/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                    body: JSON.stringify({ message: text })
                });
                const data = await response.json();
                
                typingDiv.remove();
                
                const aiMsg = document.createElement('div');
                aiMsg.style.cssText = 'background: rgba(255,255,255,0.05); border: 1px solid var(--glass-border); color: var(--text-primary); padding: 10px; border-radius: 10px; max-width: 85%; align-self: flex-start; font-size: 14px; margin-top: 5px;';
                aiMsg.textContent = data.response;
                messages.appendChild(aiMsg);
            } catch (err) {
                typingDiv.remove();
                const errorMsg = document.createElement('div');
                errorMsg.style.cssText = 'color: var(--danger); font-size: 12px;';
                errorMsg.textContent = 'Error connecting to AI Analytics Engine.';
                messages.appendChild(errorMsg);
            }
            messages.scrollTop = messages.scrollHeight;
        }
    </script>
"""

admin_dir = Path("frontend/admin")

for f in admin_dir.glob("*.html"):
    with open(f, "r", encoding="utf-8") as file:
        content = file.read()
        
    if "id=\"aiChatWidget\"" in content:
        continue # skip
        
    # Inject it before closing body tag
    content = content.replace("</body>", f"{CHATBOT_HTML}\n</body>")
    
    with open(f, "w", encoding="utf-8") as file:
        file.write(content)

print("Injected UI Widgets.")
