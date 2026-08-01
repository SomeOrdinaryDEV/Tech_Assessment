# Product Requirement Document (PRD)

**Project Name:** Medtronics_Project  
**Feature Name:** Voice-First Healthcare & Government Scheme Assistant  
**Target Audience:** Junior Developers, AI Engineers, Frontend & Backend Implementers  
**Document Version:** 1.0.0  
**Date:** August 1, 2026  
**Status:** Approved for Implementation  

---

## 1. Introduction / Overview

### 1.1 Problem Statement
Millions of patients in rural and low-literacy regions across India face severe barriers when trying to access basic health information, government healthcare benefits (such as Ayushman Bharat PM-JAY and TB Nikshay), medication adherence guidelines, and nearby facility details. Existing applications rely heavily on text-based UI, English/Hindi-only forms, and complex navigation menus, making them unusable for illiterate or semi-literate individuals.

### 1.2 Solution Overview
**Medtronics_Project** is a voice-first, mini-application system that removes all literacy and technical barriers. The patient simply taps a large microphone button and speaks their question in their native language or dialect (Hindi, Hinglish, Tamil, Telugu, Malayalam, Kannada). 

The system transcribes the speech, automatically detects the language, routes the question to a deterministic intent classifier, queries isolated domain vector databases (RAG), passes through a strict deterministic clinical safety gate, and plays back a natural voice answer in the patient's language. If a clinical emergency (red flag) is detected, the system immediately halts LLM response generation and escalates the patient to a real-time teleconsultation portal for human clinicians.

---

## 2. Goals

1. **Zero-Literacy Accessibility**: Enable 100% of patient interactions (questioning, navigation, answer reception) to happen entirely via voice in 6 target languages/dialects.
2. **Sub-Second Voice Response Latency**: Deliver audio response playback within **1.5 seconds** of the patient finishing their spoken input on standard 3G/4G networks.
3. **Zero Medical Hallucinations**: Ensure 100% of AI-generated responses are synthesized strictly from retrieved official government healthcare documents, never from LLM inherent memory.
4. **Deterministic Safety Escalation**: Guarantee 100% interception of critical emergency red flags (e.g., chest pain, severe dyspnea, stroke, self-harm) via non-ML rule checks, immediately routing the alert to human clinicians via a WebSocket Teleconsultation Portal.
5. **Zero Cross-Contamination of Knowledge**: Ensure 4 strictly partitioned vector databases (`adherence`, `schemes`, `facility_linkage`, `triage`) so information from one domain never leaks into another.

---

## 3. User Stories

### Story 1: Rural Patient asking about Government Scheme (Ayushman Bharat)
> **As a** low-literacy patient in rural Uttar Pradesh,  
> **I want to** tap a single button and ask in Hinglish *"Mera Ayushman card se konsa hospital free hai?"*,  
> **So that** I can hear a clear audio answer listing nearby empaneled hospitals without having to read or write text.

### Story 2: Patient Checking Medication Adherence Rule (TB Treatment)
> **As a** patient undergoing TB treatment in Tamil Nadu,  
> **I want to** speak in Tamil *"Naan innaikku tablet miss pannitten, enna seiyyanum?"*,  
> **So that** I can receive official Nikshay adherence guidance on what steps to take when a dose is missed.

### Story 3: Emergency Red-Flag Interception & Teleconsultation Alert
> **As a** patient experiencing sudden severe chest pain,  
> **I want to** speak *"Mere seene me bahut tej dard ho raha hai aur saans nahi aa rahi"*,  
> **So that** the system immediately recognizes a medical emergency, halts standard AI text generation, reassures me via voice, and instantly notifies a doctor on duty through the teleconsultation portal.

### Story 4: Duty Clinician Receiving Emergency Alerts
> **As a** duty medical officer on the teleconsultation dashboard,  
> **I want to** receive an immediate visual and audible alert with the patient's transcript, detected language, and matched emergency flag,  
> **So that** I can join a priority call and assist the patient without delay.

---

## 4. Functional Requirements

### 4.1 Voice-First Frontend Mini-App
- **FR-1.1**: The system must provide a mobile-responsive web UI containing a central, large glowing microphone button with real-time audio waveform animations.
- **FR-1.2**: The system must capture raw browser audio via the Web Audio API and stream binary audio frames (`audio/webm` / PCM) over a persistent WebSocket connection.
- **FR-1.3**: The system must support single-tap "Barge-In" functionality, allowing the patient to interrupt active audio playback at any time to re-open microphone recording.
- **FR-1.4**: The system must display zero mandatory text input fields or text-heavy menus on the primary patient screen.

### 4.2 Speech-to-Text (STT) & Language Detection Engine
- **FR-2.1**: The system must interface with Google Cloud Speech-to-Text API behind an abstract Python driver (`BaseSTTEngine`).
- **FR-2.2**: The engine must supply multi-language detection hints (`hi-IN`, `ta-IN`, `te-IN`, `ml-IN`, `kn-IN`, `en-IN`) to automatically detect the spoken language and return transcript text with language code.
- **FR-2.3**: The engine must evaluate transcription confidence scores. If confidence is below `0.65`, the engine must trigger a polite audio re-ask response (*"Aapki aawaz saaf nahi aayi, kripya dubara bolein"*) without forwarding to intent classification.

### 4.3 Deterministic Intent Classifier
- **FR-3.1**: The system must route every transcribed query into exactly one of four approved domain tags: `adherence`, `schemes`, `facility_linkage`, or `triage`.
- **FR-3.2**: The classifier must first execute multi-lingual keyword rule matching. If keyword rules are inconclusive, it must compute cosine similarity against domain prototype embeddings.
- **FR-3.3**: If the highest domain similarity score is below `0.72` or the query is out-of-scope, the classifier must immediately trigger a deterministic rejection node returning a standardized localized boundary response (*"Main srif dawaiyan, sarkari yojana, aspatal, aur swasthya jaanch me madad kar sakta hoon"*).

### 4.4 Isolated Retrieval-Augmented Generation (RAG) Engine
- **FR-4.1**: The system must store domain knowledge in 4 physically separate ChromaDB collections (`adherence_col`, `schemes_col`, `facility_col`, `triage_col`).
- **FR-4.2**: The retriever must ONLY query the single ChromaDB collection specified by the Intent Classifier.
- **FR-4.3**: The LLM response synthesizer must operate under a strict context-only prompt. It must NEVER generate medical diagnoses, prescribe drugs, or use inherent memory outside the retrieved context chunks. If no relevant context is found, it must return `NO_CONTEXT_FOUND`.

### 4.5 Deterministic Safety & Escalation Gate
- **FR-5.1**: The system must pass both the user transcript AND the generated response through a non-ML hardcoded keyword and regex safety filter.
- **FR-5.2**: The safety rules must evaluate clinical emergency keywords across all 6 target languages for: cardiac symptoms, severe respiratory distress, stroke signs, heavy trauma/bleeding, and self-harm.
- **FR-5.3**: If a red flag is detected, the safety gate MUST override any LLM output, generate an emergency voice instruction for the patient, log the audit telemetry, and broadcast a real-time WebSocket event to the clinician portal.

### 4.6 Low-Latency Text-to-Speech (TTS) & Teleconsultation Portal
- **FR-6.1**: The system must interface with Google Cloud TTS API behind an abstract Python driver (`BaseTTSEngine`) to synthesize audio in the patient's detected language.
- **FR-6.2**: The system must serve a dedicated clinician dashboard (`/clinician.html`) that listens for WebSocket red-flag escalation events and renders visual alert cards with audio chimes.

---

## 5. Non-Goals (Out of Scope)

1. **Automated Medical Diagnosis & Prescription**: The system will NEVER diagnose medical conditions or issue prescriptions.
2. **Video Streaming Teleconsultation**: The portal handles alert notifications and triage logs; full video calling infrastructure is out of scope for initial core pipeline.
3. **User Authentication & Passwords**: Illiterate patients will interact in anonymous session mode; no password entry or account creation required for patient app.
4. **Third-Party Hospital Booking API Integration**: The facility module provides nearby PHC/hospital details from static government registries, not live appointment booking.

---

## 6. Design Considerations

- **Color Palette**: Dark slate blue background (`#0b132b`), vibrant emerald pulse indicator (`#10b981`), emergency alert crimson (`#ef4444`).
- **Typography**: Clean, readable sans-serif fonts (Inter / Noto Sans Devanagari / Noto Sans Tamil / Noto Sans Telugu / Noto Sans Malayalam / Noto Sans Kannada).
- **Micro-Animations**: Ripple wave effect around the microphone button during speech recording; audio equalizer bars during playback.

---

## 7. Technical Considerations & Architecture

- **Backend Stack**: Python 3.10+, FastAPI, AsyncIO, Pydantic v2, ChromaDB, Google Cloud STT & TTS SDKs.
- **Frontend Stack**: Vanilla HTML5, CSS3 Glassmorphism, Web Audio API, WebSockets.
- **Modular Directory Layout**:
  ```
  Medtronics_Project/
  ├── app.py
  ├── config.py
  ├── core/ (models.py, pipeline.py)
  ├── engines/ (stt/, intent/, rag/, safety/, tts/)
  ├── portal/ (teleconsult.py)
  ├── data/ (adherence/, schemes/, facility/, triage/)
  └── static/ (index.html, styles.css, app.js, clinician.html)
  ```

---

## 8. Success Metrics

1. **Intent Classification Accuracy**: > 95% correct routing across 4 domains for clear speech.
2. **Safety Red Flag Recall**: 100% recall on emergency queries (0 missed red-flag escalations).
3. **End-to-End Latency**: < 1.5 seconds average time from silence detection to audio response playback.
4. **Zero Cross-Domain Contamination**: 0 instances of RAG retriever fetching context outside assigned collection.

---

## 9. Open Questions

- *None currently open.* All 10 architectural decisions across Branches 1–5 have been confirmed and locked. Ready for modular code implementation.
