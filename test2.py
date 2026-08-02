import asyncio
from engines.tts.sarvam_tts import SarvamTTSEngine

API_KEY = "sk_mempi2aj_p1SWKIL9XGaFOJ91nLgqM41X"

async def main():
    engine = SarvamTTSEngine(api_key=API_KEY)
    b64 = await engine.synthesize_speech("Hello, this is a test.", "hi-IN")
    if b64:
        # Decode and save to check
        import base64
        with open("test_output.mp3", "wb") as f:
            f.write(base64.b64decode(b64))
        print("Saved test_output.mp3")
    else:
        print("No audio generated.")

asyncio.run(main())