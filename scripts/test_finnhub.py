"""Quick test of Finnhub API key and news fetch."""
import httpx

key = "d770tr9r01qtg3nf7j5gd770tr9r01qtg3nf7j60"
print(f"Full key length: {len(key)}")

# Looks like two keys concatenated - try each half
half1 = key[:20]   # d770tr9r01qtg3nf7j5g
half2 = key[20:]   # d770tr9r01qtg3nf7j60
print(f"Half 1: {half1}")
print(f"Half 2: {half2}")

# Test half 1
r1 = httpx.get("https://finnhub.io/api/v1/news", params={"category": "general", "token": half1}, timeout=10)
items1 = r1.json() if r1.status_code == 200 else []
print(f"Half1 status: {r1.status_code}, items: {len(items1)}")

# Test half 2
r2 = httpx.get("https://finnhub.io/api/v1/news", params={"category": "general", "token": half2}, timeout=10)
items2 = r2.json() if r2.status_code == 200 else []
print(f"Half2 status: {r2.status_code}, items: {len(items2)}")

# Test full key
r3 = httpx.get("https://finnhub.io/api/v1/news", params={"category": "general", "token": key}, timeout=10)
items3 = r3.json() if r3.status_code == 200 else []
print(f"Full  status: {r3.status_code}, items: {len(items3)}")

# If any returned data, print first headline
for label, items in [("Half1", items1), ("Half2", items2), ("Full", items3)]:
    if items:
        print(f"  {label} first headline: {items[0].get('headline', '')[:80]}")
