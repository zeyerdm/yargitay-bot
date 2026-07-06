from playwright.sync_api import sync_playwright
try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://karararama.yargitay.gov.tr/")
        page.get_by_text("DETAYLI ARAMA").click(timeout=3000)
        page.fill("#esasNoYil", "2003")
        page.fill("#esasNoSira1", "3003")
        page.click("#detaylýAramaG")
        print("Search submitted")
        page.wait_for_selector("table", timeout=5000)
        print("Table loaded")
        browser.close()
except Exception as e:
    print("Error:", e)
