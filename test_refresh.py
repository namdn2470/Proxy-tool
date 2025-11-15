#!/usr/bin/env python3
"""
Test script for "Làm mới list" button functionality
"""

from services.storage import Storage

def main():
    print("=" * 60)
    print("TEST: Nút 'Làm mới list'")
    print("=" * 60)
    
    # Initialize storage
    storage = Storage()
    
    # Load initial proxies
    print("\n📋 Initial load:")
    proxies = storage.get_proxies()
    print(f"   Loaded: {len(proxies)} proxy(ies)")
    for idx, p in enumerate(proxies, 1):
        if isinstance(p, dict):
            print(f"   {idx}. {p['proxy'][:30]}...")
        else:
            print(f"   {idx}. {p[:30]}...")
    
    print("\n" + "-" * 60)
    print("💡 Simulation: User adds new proxy to proxies.txt")
    print("-" * 60)
    
    # Simulate refresh - reload from file
    print("\n🔄 Refreshing list (reload from files)...")
    storage.proxies = storage.load_proxies()
    
    # Get updated list
    print("\n📋 After refresh:")
    proxies = storage.get_proxies()
    print(f"   Loaded: {len(proxies)} proxy(ies)")
    for idx, p in enumerate(proxies, 1):
        if isinstance(p, dict):
            print(f"   {idx}. {p['proxy'][:30]}...")
        else:
            print(f"   {idx}. {p[:30]}...")
    
    print("\n" + "=" * 60)
    print("✅ How 'Làm mới list' works:")
    print("=" * 60)
    print("""
1. User clicks "Làm mới list" button
2. App calls refresh_proxy_list()
3. Storage reloads data from:
   - proxies.txt (text file)
   - proxies.json (JSON file)
4. UI table updates with new data
5. Console shows: "✅ Refreshed proxy list: X proxies loaded"

🎯 Use cases:
- After manually editing proxies.txt
- After downloading new proxy list
- After API fetch to refresh display
- To reset status/type columns
    """)
    
    print("=" * 60)

if __name__ == "__main__":
    main()

