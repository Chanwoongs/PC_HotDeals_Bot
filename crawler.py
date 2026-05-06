import json
import os
import time
import requests
from playwright.sync_api import sync_playwright

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
SEEN_FILE = "seen_deals.json"
TARGET_URL = "https://hotdeal.zip/PC"

# ── 텔레그램 메시지 전송 ──────────────────────────────────────────────────────
def send_telegram(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }
    try:
        r = requests.post(url, json=payload, timeout=10)
        r.raise_for_status()
        print(f"[텔레그램 전송 완료] {message[:60]}...")
    except Exception as e:
        print(f"[텔레그램 오류] {e}")

# ── 이전에 본 딜 ID 불러오기 ─────────────────────────────────────────────────
def load_seen() -> set:
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()

# ── 본 딜 ID 저장 ─────────────────────────────────────────────────────────────
def save_seen(seen: set):
    # 최대 500개만 유지 (오래된 것 제거)
    seen_list = list(seen)[-500:]
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(seen_list, f, ensure_ascii=False)

# ── 핫딜 크롤링 ───────────────────────────────────────────────────────────────
def fetch_deals() -> list[dict]:
    deals = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page.goto(TARGET_URL, wait_until="networkidle", timeout=30000)

        # 페이지 제목 확인
        print(f"[페이지 제목] {page.title()}")

        # JS 렌더링 대기
        try:
            page.wait_for_selector("a[href*='/deal/'], .deal-card, article", timeout=15000)
        except Exception:
            print("[경고] 딜 셀렉터 타임아웃 - 페이지 소스 확인 필요")
            # 페이지 HTML 저장
            with open("page_source.html", "w", encoding="utf-8") as f:
                f.write(page.content())
            print("[디버그] page_source.html에 저장됨")

        # 딜 카드 파싱 (사이트 구조에 맞게 유연하게)
        cards = page.query_selector_all("a[href*='/deal/']")
        print(f"[디버그] a[href*='/deal/'] 찾음: {len(cards)}개")

        # 다른 셀렉터들도 확인
        if len(cards) == 0:
            print(f"[디버그] .deal-card 찾음: {len(page.query_selector_all('.deal-card'))}개")
            print(f"[디버그] article 찾음: {len(page.query_selector_all('article'))}개")
            print(f"[디버그] 전체 a 태그: {len(page.query_selector_all('a'))}개")
            all_links = page.query_selector_all('a')
            for i, link in enumerate(all_links[:5]):
                href = link.get_attribute("href")
                text = (link.inner_text() or "")[:50]
                print(f"  a태그#{i}: href={href} | text={text}")

        seen_links = set()
        for card in cards:
            href = card.get_attribute("href") or ""
            if not href or href in seen_links:
                continue
            seen_links.add(href)

            # 링크를 절대경로로
            if href.startswith("/"):
                href = "https://hotdeal.zip" + href

            # 제목 추출 (텍스트 전체에서 짧게)
            title = (card.inner_text() or "").strip()
            title = " ".join(title.split())[:80]  # 80자 제한

            if title:
                deal_id = href  # URL을 고유 ID로 사용
                deals.append({"id": deal_id, "title": title, "url": href})

        browser.close()

    print(f"[크롤링] {len(deals)}개 딜 발견")
    return deals

# ── 메인 ─────────────────────────────────────────────────────────────────────
def main():
    seen = load_seen()
    print(f"[기존 캐시] {len(seen)}개 딜 ID 저장됨")

    deals = fetch_deals()

    new_deals = [d for d in deals if d["id"] not in seen]
    print(f"[신규 딜] {len(new_deals)}개")

    for deal in new_deals:
        msg = (
            f"🔥 <b>PC 핫딜 알림!</b>\n\n"
            f"📌 {deal['title']}\n\n"
            f"🔗 <a href='{deal['url']}'>핫딜 보러가기</a>"
        )
        send_telegram(msg)
        seen.add(deal["id"])
        time.sleep(1)  # 텔레그램 rate limit 방지

    save_seen(seen)
    print("[완료]")

if __name__ == "__main__":
    main()
