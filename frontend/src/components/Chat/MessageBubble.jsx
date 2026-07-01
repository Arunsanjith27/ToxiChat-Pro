import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Check, CheckCheck, Pencil, X, Trash2 } from 'lucide-react';

const QUICK_REACTIONS = ['👍', '❤️', '😂', '😮', '😢', '😡'];

function HighlightedText({ text, toxicWords }) {
  if (!toxicWords || toxicWords.length === 0) {
    return <span>{text}</span>;
  }
  const pattern = new RegExp(`(${toxicWords.map(w => w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|')})`, 'gi');
  const parts = text.split(pattern);
  return (
    <>
      {parts.map((part, i) =>
        toxicWords.some(w => w.toLowerCase() === part.toLowerCase()) ? (
          <span key={i} className="bg-red-500/30 text-red-200 px-0.5 rounded font-semibold">{part}</span>
        ) : (
          <span key={i}>{part}</span>
        )
      )}
    </>
  );
}

function StatusTicks({ status, isOwn }) {
  if (!isOwn) return null;
  if (status === 'read') {
    return <span className="flex items-center gap-0.5 text-[10px] text-blue-400"><CheckCheck className="w-3.5 h-3.5" /> Read</span>;
  }
  if (status === 'delivered') {
    return <span className="flex items-center gap-0.5 text-[10px] text-gray-300"><CheckCheck className="w-3.5 h-3.5" /> Delivered</span>;
  }
  return <span className="flex items-center gap-0.5 text-[10px] text-gray-400"><Check className="w-3.5 h-3.5" /> Sent</span>;
}

function ReactionBar({ reactions, onReaction, msgId, target, currentUsername }) {
  if (!reactions) return null;
  
  let normalized = [];
  if (Array.isArray(reactions)) {
    normalized = reactions;
  } else if (typeof reactions === 'object') {
    Object.entries(reactions).forEach(([emoji, users]) => {
      users.forEach(username => {
        normalized.push({ username, emoji });
      });
    });
  }
  
  if (normalized.length === 0) return null;

  const grouped = {};
  normalized.forEach(r => {
    if (!grouped[r.emoji]) grouped[r.emoji] = [];
    grouped[r.emoji].push(r.username);
  });

  return (
    <div className="flex flex-wrap gap-1 mt-1">
      {Object.entries(grouped).map(([emoji, users]) => {
        const hasReacted = users.includes(currentUsername);
        return (
          <button
            key={emoji}
            onClick={() => onReaction(msgId, emoji, target)}
            className={`flex items-center gap-0.5 rounded-full px-1.5 py-0.5 text-xs transition-colors ${
              hasReacted ? 'bg-emerald-500/20 border border-emerald-500/30 text-emerald-400' : 'bg-white/10 hover:bg-white/20 border border-white/10'
            }`}
            title={users.join(', ')}
          >
            <span>{emoji}</span>
            <span className={hasReacted ? 'text-emerald-400 text-[10px]' : 'text-gray-400 text-[10px]'}>{users.length}</span>
          </button>
        );
      })}
    </div>
  );
}

export default function MessageBubble({ message, isOwn, currentUsername, onReaction, onEdit, onDelete }) {
  const [showReactions, setShowReactions] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editText, setEditText] = useState(message.text);
  const isFlagged = message.is_flagged;

  const target = isOwn ? message.receiver : message.sender;

  const handleEdit = () => {
    if (editText.trim() && editText !== message.text) {
      onEdit?.(message.id, editText.trim(), target);
    }
    setIsEditing(false);
  };


  if (message.deleted) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 12, scale: 0.96 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        layout
        className={`flex w-full group ${isOwn ? 'justify-end' : 'justify-start'}`}
      >
        <div className={`relative max-w-[70%] sm:max-w-[60%] flex flex-col ${isOwn ? 'items-end' : 'items-start'}`}>
          <div className={`px-5 py-3 rounded-2xl shadow-lg relative overflow-hidden backdrop-blur-md bg-white/5 text-gray-500 italic border border-white/5 ${
            isOwn ? 'rounded-br-sm' : 'rounded-bl-sm'
          }`}>
            <p className="relative z-10 leading-relaxed text-[15px]">
              🚫 This message was deleted.
            </p>
          </div>
          <div className={`flex items-center gap-2 mt-1.5 px-1 ${isOwn ? 'flex-row-reverse' : 'flex-row'}`}>
            <div className="flex items-center gap-1">
              <span className="text-[10px] text-gray-600 font-medium">
                {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
            </div>
          </div>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 12, scale: 0.96 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      transition={{ type: "spring", stiffness: 400, damping: 30 }}
      layout
      className={`flex w-full group ${isOwn ? 'justify-end' : 'justify-start'}`}
      onDoubleClick={() => setShowReactions(s => !s)}
    >
      <div className={`relative max-w-[70%] sm:max-w-[60%] flex flex-col ${isOwn ? 'items-end' : 'items-start'}`}>

        {isFlagged && !isOwn && (
          <motion.div
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            className="flex items-center gap-1 mb-1 px-2"
          >
            <span className="text-red-500 text-xs">⚠️</span>
            <span className="text-red-400 text-[10px] uppercase font-bold tracking-wider">
              {message.toxicity_label === 'high' ? 'Highly toxic' : 'Potentially harmful'}
            </span>
          </motion.div>
        )}

        <div className={`px-5 py-3 rounded-2xl shadow-lg relative overflow-hidden backdrop-blur-md ${
          isOwn
            ? 'bg-gradient-to-br from-emerald-500 to-teal-600 text-white rounded-br-sm border border-emerald-400/30'
            : isFlagged
              ? 'bg-red-500/10 text-red-100 rounded-bl-sm border border-red-500/50'
              : 'bg-white/10 text-gray-100 rounded-bl-sm border border-white/5 shadow-black/50'
        }`}>
          {isOwn && <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent pointer-events-none" />}

          {isEditing ? (
            <div className="relative z-10 flex items-center gap-2">
              <input
                value={editText}
                onChange={e => setEditText(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleEdit()}
                className="flex-1 bg-black/20 border border-white/20 rounded-lg px-2 py-1 text-sm text-white focus:outline-none"
                autoFocus
              />
              <button onClick={handleEdit} className="text-emerald-300 hover:text-white text-xs font-bold">Save</button>
              <button onClick={() => setIsEditing(false)} className="text-gray-400 hover:text-white">
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
          ) : (
            <p className="relative z-10 leading-relaxed text-[15px]">
              {isFlagged && !isOwn ? (
                <HighlightedText text={message.text} toxicWords={message.toxic_words} />
              ) : (
                message.text
              )}
            </p>
          )}
        </div>

        {/* Reaction picker */}
        <AnimatePresence>
          {showReactions && (
            <motion.div
              initial={{ opacity: 0, scale: 0.8, y: -5 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.8 }}
              className={`flex gap-0.5 bg-gray-900/95 backdrop-blur-md border border-white/10 rounded-full px-1.5 py-1 shadow-xl mt-1 ${isOwn ? 'self-end' : 'self-start'}`}
            >
              {QUICK_REACTIONS.map(emoji => (
                <button
                  key={emoji}
                  onClick={() => { onReaction?.(message.id, emoji, target); setShowReactions(false); }}
                  className="w-7 h-7 flex items-center justify-center hover:bg-white/10 rounded-full transition-colors text-sm"
                >
                  {emoji}
                </button>
              ))}
            </motion.div>
          )}
        </AnimatePresence>

        <ReactionBar reactions={message.reactions} onReaction={onReaction} msgId={message.id} target={target} currentUsername={currentUsername} />

        <div className={`flex items-center gap-2 mt-1.5 px-1 ${isOwn ? 'flex-row-reverse' : 'flex-row'}`}>
          <div className="flex items-center gap-1">
            <span className="text-[10px] text-gray-500 font-medium">
              {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </span>
            <StatusTicks status={message.status} isOwn={isOwn} />
            {message.edited && <span className="text-[9px] text-gray-500 italic">(edited)</span>}
          </div>

          {/* Edit button for own messages */}
          {isOwn && !isEditing && (
            <div className="opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-1">
              <button
                onClick={() => { setEditText(message.text); setIsEditing(true); }}
                className="p-1 hover:bg-white/10 rounded"
                title="Edit message"
              >
                <Pencil className="w-3 h-3 text-gray-400" />
              </button>
              <button
                onClick={() => onDelete?.(message.id, target)}
                className="p-1 hover:bg-red-500/20 rounded group/del"
                title="Delete message"
              >
                <Trash2 className="w-3 h-3 text-gray-400 group-hover/del:text-red-400 transition-colors" />
              </button>
            </div>
          )}

          {message.emotion && message.emotion !== 'neutral' && (
            <span className="text-[9px] bg-white/5 border border-white/10 px-1.5 py-0.5 rounded text-gray-400 capitalize">
              {message.emotion === 'joy' ? '😊' : message.emotion === 'anger' ? '😤' : message.emotion === 'sadness' ? '😢' : message.emotion === 'fear' ? '😨' : '😮'} {message.emotion}
            </span>
          )}

          {message.toxicity_score > 0 && (
            <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded uppercase ${
              message.toxicity_label === 'high'
                ? 'bg-red-500/20 text-red-400 border border-red-500/30'
                : message.toxicity_label === 'medium'
                  ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                  : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
            }`}>
              {message.toxicity_label === 'high' ? '🔴' : message.toxicity_label === 'medium' ? '🟡' : '🟢'} {(message.toxicity_score * 100).toFixed(0)}%
            </span>
          )}
        </div>
      </div>
    </motion.div>
  );
}
