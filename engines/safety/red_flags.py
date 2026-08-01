"""
Hardcoded clinical emergency rules & multi-lingual keywords for Medtronics_Project
Evaluates cardiac, respiratory, stroke, hemorrhage, and suicide/self-harm red flags.
"""

RED_FLAG_RULES = {
    "CARDIAC_EMERGENCY": [
        "seene me dard", "chest pain", "chhathee me dard", "heart attack", "marundhu dard",
        "nenju vali", "gunde noppi", "nenju vedhana", "edeyalli novu"
    ],
    "RESPIRATORY_DISTRESS": [
        "saans nahi", "breathless", "saans lene me takleef", "saans phool",
        "moochu thindral", "voopiri aadadam ledhu", "shwaasa thondare"
    ],
    "STROKE_NEUROLOGICAL": [
        "pakshaghat", "paralysis", "mukha tedi", "chehra tedha", "ek taraf sunn",
        "kai kaal seeyal", "kaalu cheyyi padipoyindi"
    ],
    "SEVERE_BLEEDING": [
        "khoon beh raha", "heavy bleeding", "khoon ki ulti", "blood loss",
        "ratham varugiradhu", "raktham osthondhi"
    ],
    "SUICIDE_SELF_HARM": [
        "suicide", "marne ka mann", "jeena nahi", "aatmahatya", "khudkhushi",
        "tharkolai", "athmahatya"
    ]
}

EMERGENCY_OVERRIDE_MESSAGES = {
    "hi-IN": "DHYAN DEIN: Yeh ek aapatkalin chikitsa sthiti ho sakti hai. Hum aapko turant doctor aur teleconsultation team se jodh rahe hain. Kripya shant rahein.",
    "ta-IN": "HECHARIKKAI: Idhu oru அவசர மருத்துவ நிலைமை. Ungalai udanadiyaga maruthuvaridam inaikkirom.",
    "te-IN": "HECHARRIKA: Idhi oka apathkaleena vaidhya paristhithi. Mimmalni ventane doctor thoni kaluputhunnam.",
    "ml-IN": "SRADDHIKKUKA: Idh oru aapatkaala chikitsa avastha aanu. Doctor-umaay bandhappaduthunnu.",
    "kn-IN": "ECHARIKE: Idhu apathkaalina vaidhya paristhithi. Nimmanukodale doctor ge kaluhisuthive.",
    "en-IN": "EMERGENCY ALERT: This appears to be a medical emergency. We are connecting you immediately to a teleconsultation doctor."
}
