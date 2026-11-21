
import requests
from bs4 import BeautifulSoup

SOURCES = {
    "SET_OFFICIAL": (
        "https://www.set.or.th/en/market/"
        "product/stock/overview?market=SET"
    ),
    "SETLIVE_REFERENCE": (
        "https://setlive.myanmarnode.com/en"
    ),
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; Myanmar2DResearch/1.0)"
    ),
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9",
}


def inspect_source(name, url):
    print("\n" + "=" * 55)
    print(f"SOURCE: {name}")
    print(f"URL: {url}")

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=20
        )

        print("HTTP STATUS:", response.status_code)
        print("CONTENT TYPE:",
              response.headers.get("Content-Type"))

        if response.status_code != 200:
            print("SOURCE NOT ACCESSIBLE")
            return

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        title = soup.title.get_text(
            strip=True
        ) if soup.title else "No title"

        print("PAGE TITLE:", title)

        for tag in soup([
            "script", "style", "noscript",
            "svg"
        ]):
            tag.decompose()

        text = soup.get_text(
            separator=" ",
            strip=True
        )

        print("\nPAGE TEXT PREVIEW:")
        print(text[:3000])

        keywords = [
            "SET Index",
            "Index",
            "Value",
            "Market Value",
            "Last Update",
            "Market Status",
        ]

        print("\nKEYWORD CHECK:")

        for keyword in keywords:
            print(
                keyword,
                "FOUND" if keyword.lower()
                in text.lower() else "NOT FOUND"
            )

    except requests.RequestException as error:
        print("REQUEST ERROR:", str(error))


if __name__ == "__main__":
    for name, url in SOURCES.items():
        inspect_source(name, url)
