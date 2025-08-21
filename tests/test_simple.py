"""
Simple test to verify pytest works.
"""

def test_simple_addition():
    """Test that 1 + 1 equals 2."""
    assert 1 + 1 == 2

def test_string_concatenation():
    """Test string concatenation."""
    result = "Hello" + " " + "World"
    assert result == "Hello World"
