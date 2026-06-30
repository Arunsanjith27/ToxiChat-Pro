import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Link } from 'react-router-dom';
import Sidebar from './Sidebar';
import ChatWindow from './ChatWindow';
import Dashboard from '../Dashboard/Dashboard';
import ToxicityAlert from './ToxicityAlert';
import ToxicityPreSendModal from './ToxicityPreSendModal';
import ThemeToggle from '../Layout/ThemeToggle';
import { useAuth } from '../../context/AuthContext';
import { API_URL, chatApi, dashboardApi } from '../../services/api';

const WS_URL = API_URL.replace('http', 'ws');

function playNotifSound() {
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.frequency.setValueAtTime(880, ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(440, ctx.currentTime + 0.15);
    gain.gain.setValueAtTime(0.12, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.25);
    osc.start();
    osc.stop(ctx.currentTime + 0.25);
  } catch (_) {}
}

export default function ChatLayout() {
  const { user, logout, isAdmin } = useAuth();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [contacts, setContacts] = useState([]);
  const [activeChat, setActiveChat] = useState(null);
  const [showDashboard, setShowDashboard] = useState(false);
  const [alert, setAlert] = useState(null);
  const [dashboardStats, setDashboardStats] = useState(null);
  const [receiverWarning, setReceiverWarning] = useState(null);
  const [typingUsers, setTypingUsers] = useState({});
  const [isMuted, setIsMuted] = useState(false);
  const [muteMessage, setMuteMessage] = useState('');
  const [muteUntil, setMuteUntil] = useState(null);
  const [unreadCounts, setUnreadCounts] = useState({});
  const [preSendWarning, setPreSendWarning] = useState(null);
  const [conversationHealth, setConversationHealth] = useState(null);

  const wsRef = useRef(null);
  const typingTimeoutRef = useRef({});
  const activeChatRef = useRef(activeChat);

  useEffect(() => { activeChatRef.current = activeChat; }, [activeChat]);

  useEffect(() => {
    if (!showDashboard || !user?.access_token) return;
    dashboardApi.stats(user.access_token)
      .then(setDashboardStats)
      .catch(console.error);
  }, [showDashboard, messages, user?.access_token]);

  useEffect(() => {
    if (!activeChat || !user?.access_token) {
      setConversationHealth(null);
      return;
    }
    chatApi.conversationHealth(activeChat.username, user.access_token)
      .then(setConversationHealth)
      .catch(() => setConversationHealth(null));
  }, [activeChat, messages.length, user?.access_token]);

  useEffect(() => {
    if (!user?.access_token) return;
    const ws = new WebSocket(`${WS_URL}/ws/${user.access_token}`);
    wsRef.current = ws;

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === 'users_list') {
        setContacts(data.users.filter(u => u.username !== user.username));
      } else if (data.type === 'message') {
        setMessages(prev => {
          const exists = prev.some(m => m.id === data.id);
          return exists ? prev : [...prev, data];
        });
        if (data.sender !== user.username) {
          playNotifSound();
          if ('Notification' in window && Notification.permission === 'granted') {
            new Notification(data.sender, { body: data.text || '[message]' });
          }
          if (data.sender === activeChatRef.current?.username) {
            ws.send(JSON.stringify({ type: 'seen', id: data.id, sender: data.sender }));
          } else {
            setUnreadCounts(prev => ({
              ...prev,
              [data.sender]: (prev[data.sender] || 0) + 1
            }));
          }
        }
      } else if (data.type === 'toxicity_pre_send') {
        setPreSendWarning(data);
      } else if (data.type === 'toxicity_alert') {
        setAlert(data);
      } else if (data.type === 'toxicity_warning') {
        setReceiverWarning(data);
        setTimeout(() => setReceiverWarning(null), 5000);
      } else if (data.type === 'typing') {
        const sender = data.sender;
        setTypingUsers(prev => ({ ...prev, [sender]: true }));
        if (typingTimeoutRef.current[sender]) clearTimeout(typingTimeoutRef.current[sender]);
        typingTimeoutRef.current[sender] = setTimeout(() => {
          setTypingUsers(prev => ({ ...prev, [sender]: false }));
        }, 3000);
      } else if (data.type === 'status_update') {
        setMessages(prev => prev.map(m =>
          m.id === data.id ? { ...m, status: data.status } : m
        ));
      } else if (data.type === 'reaction_update') {
        setMessages(prev => prev.map(m =>
          m.id === data.msg_id ? { ...m, reactions: data.reactions } : m
        ));
      } else if (data.type === 'message_edited') {
        setMessages(prev => prev.map(m =>
          m.id === data.msg_id ? { ...m, text: data.text, edited: true } : m
        ));
      } else if (data.type === 'muted') {
        setIsMuted(true);
        setMuteMessage(data.message);
        if (data.until) {
          setMuteUntil(data.until);
          const ms = new Date(data.until) - Date.now();
          if (ms > 0) setTimeout(() => setIsMuted(false), ms);
        } else {
          setTimeout(() => setIsMuted(false), 1800000);
        }
      } else if (data.type === 'system') {
        ws.send(JSON.stringify({ type: 'get_users' }));
      }
    };

    return () => ws.close();
  }, [user]);

  useEffect(() => {
    if (!activeChat || !user?.access_token) return;
    chatApi.messages(user.username, activeChat.username, user.access_token)
      .then(data => setMessages(Array.isArray(data) ? data : []))
      .catch(() => setMessages([]));
    setUnreadCounts(prev => ({ ...prev, [activeChat.username]: 0 }));
    wsRef.current?.send(JSON.stringify({ type: 'active_chat', partner: activeChat.username }));
  }, [activeChat, user?.username, user?.access_token]);

  useEffect(() => {
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission();
    }
  }, []);

  const sendWsMessage = useCallback((text, receiver, forceSend = false) => {
    if (!wsRef.current) return;
    wsRef.current.send(JSON.stringify({
      type: 'message',
      text: text.trim(),
      receiver,
      is_group: false,
      force_send: forceSend,
    }));
  }, []);

  const sendMessage = useCallback((e) => {
    e.preventDefault();
    if (!input.trim() || !activeChat || !wsRef.current || isMuted) return;
    sendWsMessage(input, activeChat.username, false);
    setInput('');
  }, [input, activeChat, isMuted, sendWsMessage]);

  const handleSendAnyway = () => {
    if (!preSendWarning) return;
    sendWsMessage(preSendWarning.pending_text, preSendWarning.receiver, true);
    setPreSendWarning(null);
  };

  const handleUseRewrite = () => {
    if (!preSendWarning?.rewrite) return;
    sendWsMessage(preSendWarning.rewrite, preSendWarning.receiver, true);
    setInput('');
    setPreSendWarning(null);
  };

  const sendTyping = useCallback(() => {
    if (!activeChat || !wsRef.current) return;
    wsRef.current.send(JSON.stringify({ type: 'typing', receiver: activeChat.username }));
  }, [activeChat]);

  const sendReaction = useCallback((msgId, emoji, target) => {
    if (!wsRef.current) return;
    wsRef.current.send(JSON.stringify({ type: 'reaction', msg_id: msgId, emoji, target }));
  }, []);

  const sendEdit = useCallback((msgId, newText, target) => {
    if (!wsRef.current) return;
    wsRef.current.send(JSON.stringify({ type: 'edit_message', msg_id: msgId, text: newText, target }));
  }, []);

  const chatMessages = messages.filter(m =>
    (m.sender === user.username && m.receiver === activeChat?.username) ||
    (m.sender === activeChat?.username && m.receiver === user.username)
  );

  const typingUser = activeChat && typingUsers[activeChat.username] ? activeChat.username : null;

  return (
    <>
      <ToxicityAlert alert={alert} onClose={() => setAlert(null)} />
      <ToxicityPreSendModal
        warning={preSendWarning}
        onSendAnyway={handleSendAnyway}
        onUseRewrite={handleUseRewrite}
        onCancel={() => setPreSendWarning(null)}
      />

      <div className="h-screen w-full flex flex-col p-4 md:p-6 max-w-7xl mx-auto pb-6 md:pb-10">
        <div className="flex flex-wrap justify-end items-center gap-2 mb-4 w-full z-50 shrink-0">
          <ThemeToggle />
          <Link to="/profile" className="btn-secondary text-sm px-4 py-2 rounded-xl">Profile</Link>
          {isAdmin && (
            <Link to="/admin" className="btn-secondary text-sm px-4 py-2 rounded-xl border-violet-500/30 text-violet-300">
              Admin
            </Link>
          )}
          <button
            onClick={() => setShowDashboard(!showDashboard)}
            className={`px-4 py-2 rounded-xl text-sm font-medium border backdrop-blur-md transition-all ${
              showDashboard
                ? 'bg-emerald-500 text-white border-emerald-400'
                : 'btn-secondary'
            }`}
          >
            {showDashboard ? 'Close Dashboard' : '📊 Analytics'}
          </button>
        </div>

        <div className="flex-1 flex w-full min-h-0 relative">
          <Sidebar
          user={user}
          contacts={contacts}
          activeChat={activeChat}
          setActiveChat={(c) => { setActiveChat(c); setShowDashboard(false); }}
          onLogout={logout}
          unreadCounts={unreadCounts}
        />

        {showDashboard ? (
          <Dashboard stats={dashboardStats} />
        ) : (
          <ChatWindow
            user={user}
            activeChat={activeChat}
            messages={chatMessages}
            input={input}
            setInput={setInput}
            sendMessage={sendMessage}
            receiverWarning={receiverWarning}
            typingUser={typingUser}
            isMuted={isMuted}
            muteMessage={muteMessage}
            onTyping={sendTyping}
            onReaction={sendReaction}
            onEdit={sendEdit}
            conversationHealth={conversationHealth}
          />
        )}
      </div>
    </div>
    </>
  );
}
