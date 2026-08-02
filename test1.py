import torch
from sarvamai import SarvamAI
import json
import os
client = SarvamAI(
    api_subscription_key=""
)
api_key = os.getenv("SARVAM_API_KEY")
print(api_key)

