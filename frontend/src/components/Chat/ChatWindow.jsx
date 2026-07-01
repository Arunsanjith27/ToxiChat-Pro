import React, { useRef, useEffect, useCallback, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, ShieldAlert, Search, X, HeartPulse } from 'lucide-react';
import MessageBubble from './MessageBubble';
import Avatar from '../Common/Avatar';
import { chatApi } from '../../services/api';

function TypingIndicator({ sender }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 10 }}
      className="flex items-center gap-2 px-4 py-2"
    >
      <div className="bg-white/10 rounded-2xl rounded-bl-sm px-4 py-3 flex items-center gap-1.5 border border-white/5">
        <span className="text-xs text-gray-400 mr-1">{sender}</span>
        {[0, 1, 2].map(i => (
          <motion.div
            key={i}
            className="w-1.5 h-1.5 bg-emerald-400 rounded-full"
            animate={{ y: [0, -6, 0] }}
            transition={{ duration: 0.6, repeat: Infinity, delay: i * 0.15 }}
          />
        ))}
      </div>
    </motion.div>
  );
}

export default function ChatWindow({
  user,
  activeChat,
  messages,
  input,
  setInput,
  sendMessage,
  receiverWarning,
  typingUser,
  isMuted,
  muteMessage,
  onTypingStart,
  onTypingStop,
  onReaction,
  onEdit,
  onDelete,
  onReadReceipt,
  conversationHealth
}) {
  const token = user?.access_token;
  const messagesEndRef = useRef(null);
  const [showSearch, setShowSearch] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  useEffect(scrollToBottom, [messages, typingUser]);

  useEffect(() => {
    if (activeChat && messages) {
      messages.forEach(m => {
        // If we are the receiver and it's not read yet, mark it
        if (m.receiver === user.username && m.status !== 'read') {
          onReadReceipt?.(m.id, m.sender);
        }
      });
    }
  }, [activeChat, messages, user.username, onReadReceipt]);

  const handleInputChange = useCallback((e) => {
    setInput(e.target.value);
    onTypingStart?.();
  }, [setInput, onTypingStart]);

  const handleSendMessage = (e) => {
    e.preventDefault();
    onTypingStop?.();
    sendMessage(e);
  };

  const handleSearch = useCallback(async (q) => {
    setSearchQuery(q);
    if (!q.trim() || !token) { setSearchResults([]); return; }
    try {
      const data = await chatApi.search(q, token);
      setSearchResults(Array.isArray(data) ? data : []);
    } catch { setSearchResults([]); }
  }, [token]);

  if (!activeChat) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center relative z-10 glass-panel ml-4 rounded-r-3xl border-l-0">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center max-w-sm"
        >
          <div className="w-24 h-24 mx-auto bg-emerald-500/10 rounded-full flex items-center justify-center mb-6 shadow-[0_0_50px_rgba(16,185,129,0.2)]">
            <span className="text-5xl">🛡️</span>
          </div>
          <h2 className="text-2xl font-bold mb-2">ToxiChat Pro</h2>
          <p className="text-gray-400 text-sm leading-relaxed">
            Select a contact to start a secure, AI-monitored conversation.
          </p>
        </motion.div>
      </div>
    );
  }

  const displayMessages = showSearch && searchQuery.trim() ? searchResults : messages;

  return (
    <div className="flex-1 flex flex-col relative z-10 glass-panel ml-4 rounded-r-3xl overflow-hidden shadow-2xl">
      <div className="p-4 border-b border-space-border bg-white/5 backdrop-blur-md flex items-center gap-4 relative z-20">
        <Avatar user={activeChat} size="md" />
        <div className="flex-1">
          <h2 className="theme-text font-semibold flex items-center gap-2">
            {activeChat.display_name}
            {activeChat.is_online ? (
              <span className="text-emerald-400 text-xs font-medium flex items-center gap-1">🟢 Online</span>
            ) : activeChat.last_seen ? (
              <span className="text-gray-400 text-xs font-medium flex items-center gap-1">
                ⚫ Last seen {new Date(activeChat.last_seen).toLocaleDateString([], { month: 'short', day: 'numeric' })} at {new Date(activeChat.last_seen).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
            ) : null}
          </h2>
          <p className="text-xs theme-muted">
            {typingUser === activeChat.username ? (
              <span className="text-emerald-400">typing...</span>
            ) : conversationHealth ? (
              <span className="flex items-center gap-1">
                <HeartPulse className="w-3 h-3" />
                Health: {conversationHealth.health_score}% · {conversationHealth.escalation_level}
              </span>
            ) : (
              'AI-Protected · End-to-End Monitored'
            )}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => { setShowSearch(s => !s); setSearchQuery(''); setSearchResults([]); }}
            className={`p-2 rounded-lg transition-all ${showSearch ? 'bg-emerald-500/20 text-emerald-400' : 'text-gray-400 hover:text-white hover:bg-white/5'}`}
            title="Search messages"
          >
            <Search className="w-4 h-4" />
          </button>
          {activeChat.warnings_count > 0 && (
            <div className="flex items-center gap-1 bg-amber-500/10 border border-amber-500/20 px-2 py-1 rounded-lg">
              <ShieldAlert className="w-3.5 h-3.5 text-amber-400" />
              <span className="text-[10px] text-amber-400 font-bold">{activeChat.warnings_count} WARNINGS</span>
            </div>
          )}
        </div>
      </div>

      {/* Search bar */}
      <AnimatePresence>
        {showSearch && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="border-b border-white/5 bg-white/[0.02] overflow-hidden"
          >
            <div className="px-4 py-2 flex items-center gap-2">
              <Search className="w-4 h-4 text-gray-500 shrink-0" />
              <input
                value={searchQuery}
                onChange={e => handleSearch(e.target.value)}
                placeholder="Search messages..."
                className="flex-1 bg-transparent text-sm text-white placeholder-gray-500 focus:outline-none"
                autoFocus
              />
              {searchQuery && (
                <span className="text-[10px] text-gray-500">{searchResults.length} results</span>
              )}
              <button onClick={() => { setShowSearch(false); setSearchQuery(''); setSearchResults([]); }} className="text-gray-400 hover:text-white">
                <X className="w-4 h-4" />
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {receiverWarning && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          className="bg-red-500/10 border-b border-red-500/20 py-2 px-6 flex items-center gap-3 relative z-20"
        >
          <span className="text-red-500 animate-pulse">⚠️</span>
          <span className="text-red-200 text-sm">
            {receiverWarning.message} (score: {(receiverWarning.score * 100).toFixed(0)}%)
          </span>
        </motion.div>
      )}

      {isMuted && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="bg-red-900/30 border-b border-red-500/30 py-3 px-6 flex items-center gap-3 relative z-20"
        >
          <span className="text-xl">🔇</span>
          <span className="text-red-300 text-sm font-medium">{muteMessage}</span>
        </motion.div>
      )}

      <div className="flex-1 overflow-y-auto p-6 space-y-4 flex flex-col relative z-10">
        {displayMessages.length === 0 && (
          <div className="text-center py-10 text-gray-500 text-sm">
            {showSearch && searchQuery ? 'No results found' : 'No messages yet. Say hello! 👋'}
          </div>
        )}
        <AnimatePresence>
          {displayMessages.map((m, i) => (
            <MessageBubble
              key={m.id || i}
              message={m}
              isOwn={m.sender === user.username}
              currentUsername={user.username}
              onReaction={onReaction}
              onEdit={onEdit}
              onDelete={onDelete}
            />
          ))}
        </AnimatePresence>
        <AnimatePresence>
          {typingUser === activeChat.username && <TypingIndicator sender={activeChat.display_name} />}
        </AnimatePresence>
        <div ref={messagesEndRef} />
      </div>

      <div className="p-4 border-t border-space-border bg-black/40 backdrop-blur-md relative z-20">
        <form onSubmit={handleSendMessage} className="flex gap-2">
          <input
            value={input}
            onChange={handleInputChange}
            placeholder={isMuted ? "You are muted..." : "Type a message..."}
            disabled={isMuted}
            autoFocus
            className="flex-1 bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:bg-white/10 transition-all font-medium disabled:opacity-30"
          />
          <motion.button
            whileTap={{ scale: 0.95 }}
            type="submit"
            disabled={!input.trim() || isMuted}
            className="bg-emerald-500 hover:bg-emerald-400 text-white w-12 h-12 rounded-xl flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-lg shadow-emerald-500/20"
          >
            <Send className="w-5 h-5 -ml-1 mt-1" />
          </motion.button>
        </form>
      </div>
    </div>
  );
}
