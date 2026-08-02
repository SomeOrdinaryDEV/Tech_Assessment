from sarvamai import SarvamAI

text="Hello, my name is Shrinivas, and I am a software engineer. I enjoy working on AI and machine learning projects."
client = SarvamAI(
    api_subscription_key="sk_mempi2aj_p1SWKIL9XGaFOJ91nLgqM41X",
)

response = client.text.translate(
    source_language_code="en-IN",
    input=text,
    target_language_code="hi-IN",
    model="mayura:v1",
    numerals_format="international",
    mode="formal",
)

print(response.translated_text)

audio_stream = client.text_to_speech.convert_stream(
    text=response.translated_text,
    target_language_code="hi-IN",
    speaker="shubh",
    model="bulbul:v3",
    pace=0.77,
    speech_sample_rate=22050,
)

with open("speech.mp3", "wb") as f:
    for chunk in audio_stream:
        if chunk:  # skip empty chunks if any
            f.write(chunk)
            f.flush()

print("Audio saved to speech.mp3")