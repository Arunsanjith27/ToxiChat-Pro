import asyncio
import os
import sys
import traceback

sys.path.insert(0, os.path.dirname(__file__))

from ai.manager import analyze_message
import models

async def main():
    try:
        print("Running analyze_message...")
        res = await analyze_message('idiot')
        print("Result keys:", res.keys())
        
        print("Validating with ToxicityResult...")
        models.ToxicityResult(text='idiot', **res)
        print("SUCCESS!")
    except Exception as e:
        print("EXCEPTION CAUGHT:")
        traceback.print_exc()

asyncio.run(main())
