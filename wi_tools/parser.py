import pandas as pd
import requests
import logging
from pathlib import Path
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def download_images(df: pd.DataFrame, label: str, email: str, password: str) -> None:
    output_path = Path('./download') / label
    output_path.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=USER_AGENT,
            viewport={"width": 1280, "height": 800},
            java_script_enabled=True,
            ignore_https_errors=False,
        )
        page = context.new_page()

        # Login
        logger.debug("Performing login...")
        page.goto("https://app.wildlifeinsights.org/login", wait_until="networkidle", timeout=30000)

        # Fill form using your exact IDs
        page.fill('#sign-in-email', email)
        page.fill('#sign-in-password', password)

        # Click submit
        page.click('button.btn.btn-primary[type="submit"]')  # matches button class + type

        # Wait for navigation / dashboard / redirect after login
        page.wait_for_load_state("networkidle", timeout=60000)

        # Now process each row using the logged-in context
        success = failed = 0
        with logging_redirect_tqdm():
            for idx, row in tqdm(df.iterrows(), total=len(df), desc="Downloading"):
                page_url = row['location']
                image_id = row['image_id']
                target_path = output_path / f"{image_id}.jpg"

                logger.debug(f"-> {page_url}")

                try:
                    page.goto(page_url, wait_until="networkidle", timeout=45000)

                    # Give extra time for dynamic content
                    try:
                        page.wait_for_selector("div.c-public-image img", timeout=20000)
                    except PlaywrightTimeoutError:
                        pass  # proceed anyway

                    html = page.content()
                    soup = BeautifulSoup(html, "html.parser")

                    # Early exit if still login wall
                    if "Please sign in to view this page" in html or soup.find("div", class_="alert-danger"):
                        logger.warning("Login wall still present — check credentials / 2FA")
                        failed += 1
                        continue

                    img_src = soup.find("div", class_="c-public-image").find("img").get("src")

                    # Download with requests
                    img_resp = requests.get(img_src, headers={'User-Agent': USER_AGENT}, timeout=15, allow_redirects=True)
                    img_resp.raise_for_status()

                    with open(target_path, "wb") as f:
                        f.write(img_resp.content)

                    logger.debug(f"SUCCESS -> {target_path}")
                    success += 1

                except Exception as e:
                    logger.error(f"Error: {e}")
                    failed += 1

        browser.close()

    logger.info(f"Success: {success} | Failed: {failed} | Total: {len(df)}")
