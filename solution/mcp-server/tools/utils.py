from bs4 import BeautifulSoup


def remove_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(" ").strip()
