#!/usr/bin/env python3
"""
Tests for PurpleAir client using a mock requests implementation.
"""

import sys
import os

# Add the code directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'code'))

import purpleair


class MockResponse:
    """Mock HTTP response object."""
    
    def __init__(self, json_data, status_code=200, text=""):
        self._json_data = json_data
        self.status_code = status_code
        self.text = text
    
    def json(self):
        return self._json_data


class MockRequests:
    """Mock requests library that doesn't make actual HTTP calls."""
    
    def __init__(self, response_data=None, status_code=200, should_fail=False):
        self.response_data = response_data or {}
        self.status_code = status_code
        self.should_fail = should_fail
        self.last_url = None
        self.last_headers = None
    
    def get(self, url, headers=None):
        """Mock GET request that returns predefined data."""
        self.last_url = url
        self.last_headers = headers
        
        if self.should_fail:
            raise OSError("Network error")
        
        return MockResponse(
            self.response_data,
            self.status_code,
            text=str(self.response_data)
        )


def test_fetch_sensor_data_success():
    """Test successful sensor data fetch."""
    print("Test: fetch_sensor_data_success")
    
    # Create mock response data
    mock_data = {
        "sensor": {
            "sensor_index": 12345,
            "name": "Test Sensor",
            "pm2.5": 15.3,
            "last_seen": 1702483200
        }
    }
    
    # Create mock requests and client
    mock_requests = MockRequests(response_data=mock_data, status_code=200)
    client = purpleair.PurpleAirClient(mock_requests, api_key="test_api_key")
    
    # Fetch data
    result = client.fetch_sensor_data(
        sensor_id=12345,
        field_list=["name", "pm2.5", "last_seen"]
    )
    
    # Verify the result
    assert result == mock_data, f"Expected {mock_data}, got {result}"
    
    # Verify the request was made correctly
    assert "12345" in mock_requests.last_url, "Sensor ID not in URL"
    assert mock_requests.last_headers["X-API-Key"] == "test_api_key", "API key not set correctly"
    assert "fields=" in mock_requests.last_url, "Fields parameter not in URL"
    
    print("  ✓ Successfully fetched sensor data")
    print("  ✓ Request URL and headers correct")


def test_fetch_sensor_data_with_list():
    """Test sensor data fetch with field list as list."""
    print("\nTest: fetch_sensor_data_with_list")
    
    mock_data = {"sensor": {"name": "Test"}}
    mock_requests = MockRequests(response_data=mock_data)
    client = purpleair.PurpleAirClient(mock_requests, api_key="key")
    
    # Pass fields as a list
    result = client.fetch_sensor_data(
        sensor_id=123,
        field_list=["name", "pm2.5", "temperature"]
    )
    
    # Verify URL encoding worked
    assert "name" in mock_requests.last_url, "Field 'name' not in URL"
    assert "pm2.5" in mock_requests.last_url or "pm2%2e5" in mock_requests.last_url, "Field 'pm2.5' not encoded in URL"
    
    print("  ✓ Field list properly converted and encoded")


def test_fetch_sensor_data_with_string():
    """Test sensor data fetch with field list as string."""
    print("\nTest: fetch_sensor_data_with_string")
    
    mock_data = {"sensor": {"name": "Test"}}
    mock_requests = MockRequests(response_data=mock_data)
    client = purpleair.PurpleAirClient(mock_requests, api_key="key")
    
    # Pass fields as a string
    result = client.fetch_sensor_data(
        sensor_id=123,
        field_list="name,pm2.5"
    )
    
    assert "name" in mock_requests.last_url, "Field 'name' not in URL"
    print("  ✓ Field string properly encoded")


def test_fetch_sensor_data_api_error():
    """Test handling of API error responses."""
    print("\nTest: fetch_sensor_data_api_error")
    
    mock_requests = MockRequests(
        response_data={"error": "Invalid API key"},
        status_code=403
    )
    client = purpleair.PurpleAirClient(mock_requests, api_key="bad_key")
    
    try:
        result = client.fetch_sensor_data(
            sensor_id=123,
            field_list="name"
        )
        assert False, "Expected exception but none was raised"
    except Exception as e:
        assert "403" in str(e), f"Expected 403 in error message, got: {e}"
        print("  ✓ API error properly raised")


def test_fetch_sensor_data_network_error():
    """Test handling of network errors."""
    print("\nTest: fetch_sensor_data_network_error")
    
    mock_requests = MockRequests(should_fail=True)
    client = purpleair.PurpleAirClient(mock_requests, api_key="key")
    
    try:
        result = client.fetch_sensor_data(
            sensor_id=123,
            field_list="name"
        )
        assert False, "Expected exception but none was raised"
    except Exception as e:
        assert "Network error" in str(e) or "error" in str(e).lower(), f"Expected network error, got: {e}"
        print("  ✓ Network error properly handled")


def test_fetch_sensor_data_invalid_field_list():
    """Test handling of invalid field_list type."""
    print("\nTest: fetch_sensor_data_invalid_field_list")
    
    mock_requests = MockRequests(response_data={})
    client = purpleair.PurpleAirClient(mock_requests, api_key="key")
    
    try:
        result = client.fetch_sensor_data(
            sensor_id=123,
            field_list=12345  # Invalid type
        )
        assert False, "Expected ValueError but none was raised"
    except ValueError as e:
        assert "must be a list or a string" in str(e), f"Expected validation error, got: {e}"
        print("  ✓ Invalid field_list type properly rejected")


def test_stateless_functions():
    """Test that stateless utility functions work correctly."""
    print("\nTest: stateless_functions")
    
    # Test url_encode
    encoded = purpleair.url_encode("pm2.5")
    assert "pm2" in encoded and "5" in encoded, f"URL encoding failed: {encoded}"
    print("  ✓ url_encode works correctly")
    
    # Test aqiFromPM
    aqi = purpleair.aqiFromPM(25.0)  # Should be in "Moderate" range (51-100)
    assert 51 <= aqi <= 100, f"Expected AQI between 51-100, got {aqi}"
    print(f"  ✓ aqiFromPM(25.0) = {aqi}")
    
    # Test aqiColor
    color = purpleair.aqiColor(75)  # Moderate = YELLOW
    assert color == purpleair.YELLOW, f"Expected YELLOW for AQI 75, got {color}"
    print("  ✓ aqiColor returns correct color")
    
    # Test calcAQI
    calc = purpleair.calcAQI(25.0, 100, 51, 35.4, 12.1)
    assert calc > 0, "calcAQI should return positive value"
    print(f"  ✓ calcAQI works correctly: {calc}")


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("Running PurpleAir Client Tests (No HTTP Traffic)")
    print("=" * 60)
    
    test_fetch_sensor_data_success()
    test_fetch_sensor_data_with_list()
    test_fetch_sensor_data_with_string()
    test_fetch_sensor_data_api_error()
    test_fetch_sensor_data_network_error()
    test_fetch_sensor_data_invalid_field_list()
    test_stateless_functions()
    
    print("\n" + "=" * 60)
    print("All tests passed! ✓")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
