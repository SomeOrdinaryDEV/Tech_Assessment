"""
Multi-lingual keyword rules and domain prototypes for Medtronics_Project
Supports native Indic scripts (Devanagari, Tamil, Telugu, Malayalam, Kannada) and Hinglish/Latin scripts.
"""

DOMAIN_KEYWORDS = {
    "adherence": [
        # Hindi / Hinglish / Devanagari
        "dawa", "dawai", "tablet", "miss", "choot", "timing", "khana", "khaya", "dose", "nikshay", "tb", "pill",
        "दवा", "दवाई", "टैबलेट", "छूट", "खुराक", "निक्षय", "टीबी", "medicine"
        # Tamil
        "marundhu", "saapida", "மருந்து", "மாத்திரை",
        # Telugu
        "mandhu", "vesuko", "మందు", "మాత్ర",
        # Malayalam
        "marrunnu", "kazhichilla", "മരുന്ന്",
        # Kannada
        "mathirai", "owshadha", "ಔಷಧ"
    ],
    "schemes": [
        # Hindi / Hinglish / Devanagari
        "ayushman", "card", "yojana", "sarkari", "free", "pmjay", "pm-jay", "paisa", "bima", "pension", "janani", "bharat",
        "आयुष्मान", "कार्ड", "योजना", "सरकारी", "फ्री", "मुफ्त", "पैसा", "बीमा", "भारत",
        # Tamil / Telugu / Malayalam / Kannada
        "scheme", "arogya", "ஆயுஷ்மான்", "பாரத்", "திட்டம்", "ఉచితం", "పథకం"
    ],
    "facility_linkage": [
        # Hindi / Hinglish / Devanagari
        "hospital", "aspatal", "phc", "chc", "clinic", "lab", "kahan", "paas", "address", "doctor", "kendra", "center",
        "अस्पताल", "पीएचसी", "क्लिनिक", "लैब", "कहाँ", "पास", "डॉक्टर", "केंद्र",
        # Tamil / Telugu / Malayalam / Kannada
        "maruthuvamanai", "enge", "ekkada", "evide", "yelli", "மருத்துவமனை", "ஆசுపత్రి"
    ],
    "triage": [
        # Hindi / Hinglish / Devanagari
        "bukhar", "khansi", "dard", "saans", "ulti", "chakkar", "sirdard", "pet", "bimar", "cheenk", "fever", "cough", "pain",
        "बुखार", "खांसी", "दर्द", "सांस", "उल्टी", "चक्कर", "सिरदर्द", "पेट", "बीमार",
        # Tamil / Telugu / Malayalam / Kannada
        "kaichal", "jwaram", "paniyund", "jwara", "vali", "noppi", "காய்ச்சல்", "இருமல்", "வலி", "జ్వరం", "నొప్పి"
    ]
}

OUT_OF_SCOPE_KEYWORDS = [
    "cricket", "weather", "mausam", "politics", "narendra modi", "election", "movie", "film", "song", "money transfer", "game",
    "मौसम", "राजनीति", "चुनाव", "फिल्म", "गाने"
]
