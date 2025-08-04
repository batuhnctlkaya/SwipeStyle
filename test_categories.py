#!/usr/bin/env python3
"""
Test script to verify category matching works correctly
"""

import requests
import json

def test_category_matching():
    """Test that phones and headphones are correctly distinguished"""
    
    base_url = "http://localhost:8082"
    
    test_cases = [
        # Phone tests
        ("phone", "phones"),
        ("smartphone", "phones"),
        ("iphone", "phones"), 
        ("android phone", "phones"),
        ("akıllı telefon", "phones"),
        ("cep telefonu", "phones"),
        
        # Headphone tests
        ("headphones", "headphones"),
        ("wireless headphones", "headphones"),
        ("bluetooth headphones", "headphones"),
        ("airpods", "headphones"),
        ("kulaklık", "headphones"),
        ("kablosuz kulaklık", "headphones"),
        
        # Other categories
        ("laptop", "laptops"),
        ("gaming laptop", "laptops"),
        ("tablet", "tablets"),
        ("smartwatch", "smartwatches"),
    ]
    
    print("🧪 Testing Category Matching Logic")
    print("=" * 50)
    
    for query, expected_category in test_cases:
        try:
            response = requests.post(f"{base_url}/api/search-category", 
                                   json={"query": query, "language": "en"})
            
            if response.status_code == 200:
                data = response.json()
                if data["success"]:
                    actual_category = data["category"]["name"].lower()
                    status = "✅" if expected_category in actual_category else "❌"
                    print(f"{status} '{query}' -> {actual_category} (expected: {expected_category})")
                else:
                    print(f"❌ '{query}' -> Error: {data.get('error', 'Unknown error')}")
            else:
                print(f"❌ '{query}' -> HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ '{query}' -> Exception: {e}")
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    test_category_matching()
