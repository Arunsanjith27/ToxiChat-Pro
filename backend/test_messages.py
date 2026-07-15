import requests
from database import _memory_store
import pprint

print([m["sender"] for m in _memory_store["messages"]])
