import requests
import csv
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Content-Type": "application/json",
    "Origin": "https://bina.az",
    "Referer": "https://bina.az/baki/kiraye/menziller",
}

def fetch_page(cursor=None):
    variables = {
        "first": 16,
        "filter": {"cityId": "1", "categoryId": "1", "leased": True},
        "sort": "BUMPED_AT_DESC",
    }
    if cursor:
        variables["cursor"] = cursor

    payload = {
        "operationName": "SearchItems",
        "variables": variables,
        "extensions": {
            "persistedQuery": {
                "version": 1,
                "sha256Hash": "a2b7bef96bc42110dd00da3fdc558d26a60fdb9b91e3802dd124c3091ce43f0b"
            }
        }
    }
    resp = requests.post("https://bina.az/graphql", json=payload, headers=HEADERS)
    return resp.json()

all_listings = {}
cursor = None
page = 1
skipped = 0

while True:
    print(f"Səifə {page}...", end=" ")
    data = fetch_page(cursor)

    connection = data["data"]["itemsConnection"]
    edges = connection["edges"]
    page_info = connection["pageInfo"]

    for e in edges:
        n = e["node"]

        # Gündəlik icarəni ləqv edirik
        if n["paidDaily"]:
            skipped += 1
            continue

        all_listings[n["id"]] = {
            "id":        n["id"],
            "rooms":     n["rooms"],
            "area_m2":   n["area"]["value"],
            "floor":     n["floor"],
            "floors":    n["floors"],
            "price_azn": n["price"]["total"],
            "district":  n["location"]["fullName"],
            "repair":    n["hasRepair"],
            "updated":   n["updatedAt"],
            "link":      "https://bina.az" + n["path"],
        }

    print(f"Aylıq: {len(all_listings)} | gündəlik buraxıldı: {skipped}")

    if not page_info["hasNextPage"]:
        print("Axırıncı səifə.")
        break

    cursor = page_info["endCursor"]
    page += 1
    time.sleep(0.3)

rows = list(all_listings.values())
filename = "baku_rent_monthly.csv"
with open(filename, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print(f"\nHazırdır! Aylıq kirayə elanları: {len(rows)} → {filename}")
print(f"Günlük icarə filtr-ləndi: {skipped}")