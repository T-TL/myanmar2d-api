
import requests
import json

BASE_URL = "https://www.set.or.th"

ENDPOINTS = [
    "/api/set/index/info/list?type=index",
    "/api/set/market/SET/info",
    "/api/set/market/mai/info",
    "/api/set/index/SET/performance",
    "/api/set/index/mai/performance",
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/120 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Referer": (
        "https://www.set.or.th/en/market/"
        "product/stock/overview?market=SET"
    ),
    "x-channel": "WEB_SET",
}


def test_endpoint(path):
    url = BASE_URL + path

    print("\n" + "=" * 60)
    print("ENDPOINT:", path)

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=25
        )

        print("HTTP STATUS:", response.status_code)
        print("CONTENT TYPE:", response.headers.get("Content-Type"))
        print("RESPONSE SIZE:", len(response.text))

        try:
            data = response.json()

            print("JSON: YES")
            print(
                json.dumps(
                    data,
                    ensure_ascii=False,
                    indent=2
                )[:3500]
            )

        except ValueError:
            print("JSON: NO")
            print("RESPONSE PREVIEW:")
            print(response.text[:1000])

    except requests.RequestException as error:
        print("REQUEST ERROR:", error)


if __name__ == "__main__":
    for endpoint in ENDPOINTS:
        test_endpoint(endpoint)
