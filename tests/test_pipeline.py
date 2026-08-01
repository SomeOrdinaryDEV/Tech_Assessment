import asyncio
from core.pipeline import MedtronicsCorePipeline
from core.models import DomainType

async def run_tests():
    print("==================================================")
    print("   Medtronics_Project Core Pipeline Verification   ")
    print("==================================================")

    pipeline = MedtronicsCorePipeline()

    # Test 1: Adherence Query
    print("\n[Test 1] Testing Medication Adherence Query...")
    res1 = await pipeline.process_voice_input(b"TB ki dawa miss ho gayi, kya karu?")
    print(f"Transcript: {res1.transcript}")
    print(f"Domain: {res1.domain.value}")
    print(f"Response: {res1.text_response}")
    assert res1.domain == DomainType.ADHERENCE

    # Test 2: Native Devanagari Script Scheme Query ("आयुष्मान भारत")
    print("\n[Test 2] Testing Native Devanagari Script Scheme Query ('आयुष्मान भारत')...")
    res2 = await pipeline.process_voice_input("आयुष्मान भारत कार्ड से कौन सा अस्पताल फ्री है?".encode("utf-8"))
    print(f"Native Transcript: {res2.transcript}")
    print(f"Domain: {res2.domain.value}")
    print(f"Response: {res2.text_response}")
    assert res2.domain == DomainType.SCHEMES
    assert "Ayushman" in res2.text_response or "5 Lakh" in res2.text_response or "आयुष्मान" in res2.text_response

    # Test 3: Emergency Red Flag Interception
    print("\n[Test 3] Testing Cardiac Emergency Red Flag Interception...")
    res3 = await pipeline.process_voice_input(b"Mera seene me bahut tej dard ho raha hai aur saans nahi aa rahi")
    print(f"Transcript: {res3.transcript}")
    print(f"Emergency Triggered: {res3.is_emergency}")
    print(f"Escalation Triggered: {res3.escalation_triggered}")
    print(f"Emergency Response: {res3.text_response}")
    assert res3.is_emergency == True
    assert res3.escalation_triggered == True

    # Test 4: Out of Scope Query Rejection
    print("\n[Test 4] Testing Out-of-Scope Query Rejection...")
    oos_res = pipeline.intent_classifier.classify_intent("Cricket match me kaun jeeta?")
    print(f"Out of scope domain: {oos_res.domain.value}")
    assert oos_res.domain == DomainType.OUT_OF_SCOPE

    print("\n==================================================")
    print("   ✅ ALL CORE PIPELINE TESTS PASSED SUCCESSFULLY!  ")
    print("==================================================")

if __name__ == "__main__":
    asyncio.run(run_tests())
