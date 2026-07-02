import asyncio
import os
import sys

# Change dir to backend so imports work
sys.path.insert(0, os.path.dirname(__file__))

from main import app
from ai.manager import analyze_message
import models

async def main():
    res = await analyze_message('idiot')
    print("RES:")
    print(res)
    print("\nAttempting ToxicityResult:")
    try:
        models.ToxicityResult(text='idiot', **res)
        print("Success!")
    except Exception as e:
        print("Validation Error:")
        print(e)

asyncio.run(main())
