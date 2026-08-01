from sarvamai import SarvamAI

client = SarvamAI(
    api_subscription_key="sk_6azugix3_iP2Ao5iLVqoneOcvhr0bHvey"
)

response = client.speech_to_text.transcribe(
    file=open("audio.wav", "rb"),
    model="saaras:v3",
    mode="transcribe"  # default mode
)

print(response)
# Output: मेरा फोन नंबर है 9840950950
