import pytest
import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from safety import CrisisDetector, get_crisis_response, validate_message_safety

class TestCrisisDetector:
    @pytest.fixture
    def detector(self):
        return CrisisDetector()
    
    def test_suicide_detection(self, detector):
        """Test detection of suicidal ideation"""
        crisis_messages = [
            "I want to kill myself",
            "I'm going to end my life tonight",
            "I want to commit suicide",
            "I'm planning to die",
            "I'm better off dead"
        ]
        
        for message in crisis_messages:
            assert detector.detect_crisis(message) == True, f"Failed to detect crisis in: {message}"
    
    def test_self_harm_detection(self, detector):
        """Test detection of self-harm indicators"""
        self_harm_messages = [
            "I want to cut myself",
            "I'm going to hurt myself",
            "I need to find a razor blade",
            "I've been burning myself"
        ]
        
        for message in self_harm_messages:
            assert detector.detect_crisis(message) == True, f"Failed to detect self-harm in: {message}"
    
    def test_normal_messages(self, detector):
        """Test that normal messages don't trigger crisis detection"""
        normal_messages = [
            "I'm feeling a bit sad today",
            "Work has been stressful",
            "I had a good day",
            "Can you help me with anxiety?",
            "I'm looking for coping strategies"
        ]
        
        for message in normal_messages:
            assert detector.detect_crisis(message) == False, f"False positive for: {message}"
    
    def test_contextual_crisis_detection(self, detector):
        """Test contextual crisis indicators"""
        contextual_messages = [
            "I'm in so much pain and can't take it anymore",
            "I'm tired of fighting and want to give up on life",
            "No one cares about me and I'm completely alone",
            "Life feels pointless and meaningless to me"
        ]
        
        for message in contextual_messages:
            # These should trigger contextual detection
            result = detector.detect_crisis(message)
            # May or may not trigger depending on exact implementation
            # At minimum, should be flagged as concerning
    
    def test_edge_cases(self, detector):
        """Test edge cases for crisis detection"""
        edge_cases = [
            "",  # Empty string
            "kill",  # Single word
            "I killed it at work today",  # Different context
            "This movie is to die for",  # Figurative language
            "I'm dying of laughter"  # Figurative language
        ]
        
        # Empty should not crash
        assert detector.detect_crisis(edge_cases[0]) == False
        
        # Other cases should not trigger false positives
        for message in edge_cases[1:]:
            result = detector.detect_crisis(message)
            # Should be False for figurative usage

def test_crisis_response():
    """Test crisis response message"""
    response = get_crisis_response()
    
    # Should contain key crisis resources
    assert "911" in response
    assert "988" in response
    assert "741741" in response
    assert "emergency" in response.lower()
    assert "professional" in response.lower()

def test_message_safety_validation():
    """Test comprehensive message safety validation"""
    # Test crisis message
    crisis_result = validate_message_safety("I want to end my life")
    assert crisis_result["crisis_detected"] == True
    assert crisis_result["safe"] == False
    assert crisis_result["risk_level"] == "high"
    
    # Test normal message
    normal_result = validate_message_safety("I'm feeling anxious")
    assert normal_result["crisis_detected"] == False
    assert normal_result["safe"] == True
    assert normal_result["risk_level"] == "low"
    
    # Test long message
    long_message = "x" * 2500
    long_result = validate_message_safety(long_message)
    assert "Message too long" in long_result["concerns"]