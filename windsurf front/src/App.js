import React, { useState } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import './App.css';
import Settings from './components/Settings';

function App() {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [activeView, setActiveView] = useState('chat'); // 'chat' or 'settings'
  const [settings, setSettings] = useState({
    target_audience: 'PhD student',
    answer_tone: 'Professional and Clear',
    answer_length: '4 paragraphs',
    system_template_RouterAgent: '',
    system_template_OuterAgent: '',
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim()) return;

    // Add user message to chat
    const userMessage = { content: inputMessage, sender: 'user' };
    setMessages(prev => [...prev, userMessage]);

    try {
      // Send message to FastAPI backend with settings
      const response = await axios.post('http://localhost:8000/ask', {
        question: inputMessage,
        settings: settings  // Include settings in the request
      });

      // Add AI response to chat
      const aiMessage = { content: response.data.response, sender: 'ai' };
      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error:', error);
      const errorMessage = { content: 'Error sending message', sender: 'system' };
      setMessages(prev => [...prev, errorMessage]);
    }

    setInputMessage('');
  };

  const handleSettingsSave = (newSettings) => {
    setSettings(newSettings);
    // You might want to send these settings to the backend to update them there
    try {
      axios.post('http://localhost:8000/update_settings', newSettings);
    } catch (error) {
      console.error('Error updating settings:', error);
    }
  };

  return (
    <div className="App">
      <div className="layout-container">
        <div className="navigation-panel">
          <div className="nav-header">
            <h1>AI Assistant</h1>
          </div>
          <nav className="nav-menu">
            <button 
              className={`nav-item ${activeView === 'chat' ? 'active' : ''}`}
              onClick={() => setActiveView('chat')}
            >
              💬 AI Chat
            </button>
            <button 
              className={`nav-item ${activeView === 'settings' ? 'active' : ''}`}
              onClick={() => setActiveView('settings')}
            >
              ⚙️ Settings
            </button>
          </nav>
        </div>

        <div className="main-content">
          {activeView === 'chat' ? (
            <div className="chat-container">
              <div className="chat-header">
                <h2>Chat</h2>
              </div>
              <div className="messages">
                {messages.map((message, index) => (
                  <div key={index} className={`message ${message.sender}`}>
                    <div className="message-content">
                      <ReactMarkdown>{message.content}</ReactMarkdown>
                    </div>
                  </div>
                ))}
              </div>
              <form onSubmit={handleSubmit} className="input-form">
                <input
                  type="text"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  placeholder="Type your message..."
                  className="message-input"
                />
                <button type="submit" className="send-button">Send</button>
              </form>
            </div>
          ) : (
            <Settings
              onSave={handleSettingsSave}
              settings={settings}
              onBack={() => setActiveView('chat')}
            />
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
