from fastapi import WebSocket
from typing import Dict, Set

# In-memory store: username -> Set[WebSocket]
# This cleanly handles multiple tabs/devices per user.
_active_connections: Dict[str, Set[WebSocket]] = {}

def add_connection(username: str, ws: WebSocket) -> bool:
    """
    Adds a connection for the user.
    Returns True if this is the user's FIRST active connection (i.e. they just came online).
    """
    if username not in _active_connections:
        _active_connections[username] = set()
    
    was_offline = len(_active_connections[username]) == 0
    _active_connections[username].add(ws)
    return was_offline

def remove_connection(username: str, ws: WebSocket) -> bool:
    """
    Removes a connection for the user.
    Returns True if this was the user's LAST active connection (i.e. they just went offline).
    """
    if username not in _active_connections:
        return False
        
    if ws in _active_connections[username]:
        _active_connections[username].remove(ws)
        
    is_offline = len(_active_connections[username]) == 0
    if is_offline:
        # Clean up the key to prevent memory leaks
        del _active_connections[username]
        
    return is_offline

def is_user_online(username: str) -> bool:
    """
    Checks if a user currently has any active connections.
    """
    return username in _active_connections and len(_active_connections[username]) > 0

def get_online_users() -> Set[str]:
    """
    Returns a set of all currently online usernames.
    """
    return {username for username, conns in _active_connections.items() if len(conns) > 0}
