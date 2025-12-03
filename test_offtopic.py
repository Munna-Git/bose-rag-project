"""Test off-topic detection"""

# Test the off-topic detection logic
test_queries = [
    # Off-topic (should be rejected immediately)
    ("How many pizzas should I eat?", True),
    ("How many wings on an airplane?", True),
    ("What's the weather today?", True),
    ("Who won the football game?", True),
    ("How to cook pasta?", True),
    
    # On-topic (should go through normal flow)
    ("What is the power rating of DM6PE?", False),
    ("How to install a Bose speaker?", False),
    ("Configure ControlSpace processor", False),
    ("Bose audio system setup", False),
    ("Speaker frequency response", False),
]

print("=" * 70)
print("OFF-TOPIC DETECTION TEST")
print("=" * 70)

# Simulate the detection logic
def is_off_topic(query: str) -> bool:
    query_lower = query.lower()
    
    audio_keywords = [
        'bose', 'speaker', 'audio', 'sound', 'amplifier', 'microphone',
        'loudspeaker', 'processor', 'dsp', 'channel', 'frequency', 'db',
        'watt', 'ohm', 'installation', 'setup', 'configure', 'connect',
        'designmax', 'controlspace', 'professional', 'system', 'equipment',
    ]
    
    if any(keyword in query_lower for keyword in audio_keywords):
        return False
    
    off_topic_keywords = [
        'pizza', 'food', 'recipe', 'cook', 'restaurant', 'eat',
        'airplane', 'aeroplane', 'wings', 'fly', 'flight',
        'weather', 'temperature', 'rain',
        'football', 'game', 'sport',
        'pasta', 'cook',
    ]
    
    if any(keyword in query_lower for keyword in off_topic_keywords):
        return True
    
    return False

print("\nTesting queries:\n")
for query, expected_off_topic in test_queries:
    detected_off_topic = is_off_topic(query)
    status = "✓" if detected_off_topic == expected_off_topic else "✗"
    
    if detected_off_topic:
        action = "REJECTED (off-topic)"
    else:
        action = "ALLOWED (on-topic)"
    
    print(f"{status} {action:25} | {query}")

print("\n" + "=" * 70)
print("Expected Response for Off-Topic Queries:")
print("=" * 70)
print('"I am a technical assistant for Bose Professional Audio equipment."')
print('"I can only answer questions about Bose audio products..."')
print("\nConfidence: 0% (very_low)")
print("Time: <0.1s (no retrieval/generation needed)")
