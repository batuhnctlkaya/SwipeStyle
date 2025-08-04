#!/usr/bin/env python3
"""
Focused test for phone vs headphone distinction
"""

import requests
import json

def test_phone_headphone_distinction():
    """Test that phones and headphones are correctly distinguished"""
    
    base_url = "http://localhost:8082"
    
    test_cases = [
        # Critical phone tests
        ("phone", "should match phone category, not headphones"),
        ("iphone", "should match phone category, not headphones"),
        ("android phone", "should match phone category, not headphones"),
        
        # Critical headphone tests  
        ("headphones", "should match headphones"),
        ("bluetooth headphones", "should match headphones"),
        ("airpods", "should match headphones"),
    ]
    
    print("🔍 Testing Phone vs Headphone Distinction")
    print("=" * 60)
    
    for query, expected_behavior in test_cases:
        try:
            response = requests.post(f"{base_url}/api/search-category", 
                                   json={"query": query, "language": "en"})
            
            if response.status_code == 200:
                data = response.json()
                if data["success"]:
                    actual_category = data["category"]["name"]
                    
                    # Check if it's phone-related query
                    is_phone_query = any(word in query.lower() for word in ['phone', 'iphone', 'android'])
                    # Check if result is headphone category
                    is_headphone_result = 'headphone' in actual_category.lower()
                    
                    # This is the critical test: phone queries should NOT return headphone categories
                    if is_phone_query and is_headphone_result:
                        status = "❌ CRITICAL BUG"
                    elif not is_phone_query and not is_headphone_result and 'headphone' not in query:
                        status = "⚠️  Unexpected"
                    else:
                        status = "✅"
                    
                    print(f"{status} '{query}' -> {actual_category}")
                    print(f"     Expected: {expected_behavior}")
                else:
                    print(f"❌ '{query}' -> Error: {data.get('error', 'Unknown error')}")
            else:
                print(f"❌ '{query}' -> HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ '{query}' -> Exception: {e}")
        
        print()  # Empty line for readability
    
    print("=" * 60)
    print("Test completed!")

if __name__ == "__main__":
    test_phone_headphone_distinction()
