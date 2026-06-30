import React from 'react';
import { avatarUrl } from '../../services/api';

const SIZES = {
  sm: 'w-8 h-8 text-xs rounded-lg',
  md: 'w-10 h-10 text-sm rounded-xl',
  lg: 'w-11 h-11 text-lg rounded-xl',
  xl: 'w-24 h-24 text-3xl rounded-2xl',
};

export default function Avatar({ user, size = 'md', className = '' }) {
  const url = avatarUrl(user?.avatar_url);
  const initial = user?.display_name?.[0]?.toUpperCase() || user?.username?.[0]?.toUpperCase() || '?';

  if (url) {
    return (
      <img
        src={url}
        alt={user?.display_name || user?.username || 'Avatar'}
        className={`${SIZES[size]} object-cover border border-emerald-500/20 ${className}`}
      />
    );
  }

  return (
    <div className={`${SIZES[size]} bg-gradient-to-br from-emerald-500/30 to-cyan-500/30 border border-emerald-500/20 flex items-center justify-center font-bold theme-text ${className}`}>
      {initial}
    </div>
  );
}
