from config import load_env_config, get_api_headers
import httpx
import sys

def test():
    try:
        config = load_env_config()
        print(f"Loaded config: base_url={config.base_url}")
        print(f"Token length: {len(config.api_token)}")
        print(f"Token starts with: {config.api_token[:3]}")
        print(f"Token ends with: {config.api_token[-3:]}")
        headers = get_api_headers(config.api_token)
        with httpx.Client(base_url=config.base_url, headers=headers) as client:
            response = client.get("/api/v1/users/self/profile")
            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                print(f"Success! Authenticated as: {response.json().get('name')}")
            else:
                print(f"Failed! {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    test()
