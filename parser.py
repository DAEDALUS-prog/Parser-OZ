from bs4 import BeautifulSoup
import requests
import csv
import multiprocessing

URL = "https://oz.by/entertainment"
HOST = "https://oz.by"
HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36 OPR/69.0.3686.49"
}
FILE = "oz_entertainment_02.csv"


def get_html(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params)
    return r


def get_pages_count(html):
    soup = BeautifulSoup(html, "html.parser")
    pagination = soup.find_all("li", class_="g-pagination__list__li")
    if pagination:
        return int(pagination[-1].get_text())
    else:
        return 1


def get_content(html):
    soup = BeautifulSoup(html, "html.parser")
    items = soup.find_all("li", class_="viewer-type-card__li")
    products = []

    for item in items:
        try:
            products.append(
                {
                    "name": item.find("p", class_="item-type-card__title").get_text(),
                    "brand": item.find("p", class_="item-type-card__info").get_text(),
                    "price": item.find("span", class_="item-type-card__btn").get_text().strip().replace("\xa0", " ").replace(".", ""),
                    "link": HOST + item.find("a", class_="needsclick item-type-card__link item-type-card__link--main").get("href")
                }
            )
        except:
            continue

    return products


def save_file(items, path):
    with open(path, "w", newline="",  encoding="utf-8") as file:

        writer = csv.writer(file, delimiter=";")
        writer.writerow(["Имя", "Бренд", "Цена", "Ссылка"])

        for item in items:
            writer.writerow([item["name"], item["brand"], item["price"], item["link"]])


def parse():
    html = get_html(URL)
    if html.status_code == 200:
        products = []

        pages_count = get_pages_count(html.text)
        for page in range(1, pages_count+1):
            print(f"Парсинг {page} страницы из {pages_count}...")
            html = get_html(URL, params={"page": page})
            products.extend(get_content(html.text))

        print(products)
        print(f"Получено {len(products)} продуктов")
        save_file(products, FILE)
    else:
        print("ERROR")


parse()