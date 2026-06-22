import httpx
import sys

def test_api():
    print("Testing connection to running FastAPI application...")
    base_url = "http://localhost:8000"
    
    # 1. Test live endpoint
    try:
        r = httpx.get(f"{base_url}/live")
        print(f"GET /live: status_code={r.status_code}, response={r.json()}")
        if r.status_code != 200 or r.json().get("status") != "ok":
            print("Failed liveness check!")
            sys.exit(1)
    except Exception as e:
        print(f"Failed to connect to API on {base_url}: {e}")
        sys.exit(1)
        
    # 2. Test ready endpoint
    try:
        r = httpx.get(f"{base_url}/ready")
        print(f"GET /ready: status_code={r.status_code}, response={r.json()}")
        if r.status_code != 200 or r.json().get("status") != "ready":
            print("Failed readiness check!")
            sys.exit(1)
    except Exception as e:
        print(f"Failed to connect to API on {base_url}: {e}")
        sys.exit(1)

    # 3. Test auth endpoint (obtaining a token)
    try:
        data = {
            "username": "testuser",
            "password": "testpassword"
        }
        r = httpx.post(f"{base_url}/api/v1/auth/token", data=data)
        print(f"POST /api/v1/auth/token: status_code={r.status_code}")
        if r.status_code != 200:
            print("Failed to authenticate!")
            sys.exit(1)
        token_info = r.json()
        token = token_info.get("access_token")
        print("Token obtained successfully!")
    except Exception as e:
        print(f"Failed to connect to Auth API: {e}")
        sys.exit(1)

    # 4. Test flights search with the obtained token
    try:
        headers = {"Authorization": f"Bearer {token}"}
        params = {
            "origin": "FOR",
            "destination": "SCL",
            "departure_date": "2026-07-01",
            "adults": 1,
            "strategy": "cheapest"
        }
        r = httpx.get(f"{base_url}/api/v1/flights/search", params=params, headers=headers, timeout=15.0)
        print(f"GET /api/v1/flights/search: status_code={r.status_code}")
        if r.status_code == 200:
            results = r.json()
            print(f"Found {len(results)} flight search results!")
        else:
            print(f"Search failed: {r.text}")
            sys.exit(1)
    except Exception as e:
        print(f"Search API call failed: {e}")
        sys.exit(1)

    print("\nAPI connection and integration testing completed successfully!")

if __name__ == "__main__":
    test_api()
