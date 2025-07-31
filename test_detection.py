#!/usr/bin/env python3
# Test script for category detection

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("Testing category detection...")

# Test the local mapping first
local_mappings = {
    'şarj aleti': 'Charger',
    'sarj aleti': 'Charger', 
    'şarj cihazı': 'Charger',
    'sarj cihazi': 'Charger',
    'charger': 'Charger',
    'kulaklık': 'Headphones',
    'kulaklik': 'Headphones',
    'headphones': 'Headphones',
    'telefon': 'Phone',
    'phone': 'Phone',
    'klima': 'Klima',
    'ac': 'Klima',
    'air conditioner': 'Klima',
    'bilgisayar': 'Bilgisayar',
    'computer': 'Bilgisayar',
    'pc': 'Bilgisayar'
}

test_queries = ['şarj aleti', 'charger', 'kulaklık', 'pc', 'klima']

print("Testing local mappings:")
for query in test_queries:
    query_lower = query.strip().lower()
    if query_lower in local_mappings:
        mapped_category = local_mappings[query_lower]
        print(f"✅ '{query}' → '{mapped_category}'")
    else:
        print(f"❌ '{query}' → Not found")

# Test if categories exist
try:
    import json
    with open('categories.json', 'r', encoding='utf-8') as f:
        categories = json.load(f)
    
    print(f"\nAvailable categories: {list(categories.keys())}")
    
    print("\nChecking if mapped categories exist:")
    for mapped_cat in set(local_mappings.values()):
        if mapped_cat in categories:
            print(f"✅ '{mapped_cat}' exists in categories.json")
        else:
            print(f"❌ '{mapped_cat}' NOT found in categories.json")
            
except Exception as e:
    print(f"Error loading categories: {e}")
