"""Run against an already started server; optionally include a live Yahoo request."""

import argparse
import csv
import io
import os
from pathlib import Path

from playwright.sync_api import expect, sync_playwright


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--url", default="http://127.0.0.1:8766")
    args = parser.parse_args()
    output = Path("artifacts")
    output.mkdir(exist_ok=True)
    errors = []
    with sync_playwright() as playwright:
        browser_path = os.environ.get("STOCKLAB_BROWSER_PATH")
        options = {"headless": True}
        if browser_path:
            options["executable_path"] = browser_path
        browser = playwright.chromium.launch(**options)
        context = browser.new_context(
            viewport={"width": 1440, "height": 1100},
            color_scheme="light",
            timezone_id="Pacific/Kiritimati",
        )
        page = context.new_page()
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(args.url)
        expect(page.locator("#subtitle")).to_contain_text("MSFT vs SPY", timeout=90000)
        assert page.locator("#provenance").inner_text() == "SYNTHETIC DATA"
        page.screenshot(path=str(output / "overview.png"), full_page=True)
        page.click("#tab-forecast")
        assert page.locator("#model option").count() == 4
        page.select_option("#model", "Random Forest")
        page.select_option("#horizon", "5")
        page.select_option("#band", "80")
        assert page.locator("#forecastRows tr").count() == 5
        expect(page.locator("#forecastSummary")).to_contain_text("Random Forest")
        page.locator("#forecastChart").focus()
        page.keyboard.press("ArrowLeft")
        assert page.locator("#forecastChart").locator("..").locator(".tip").is_visible()
        with page.expect_download() as download:
            page.click("#export")
        rows = list(csv.reader(io.StringIO(Path(download.value.path()).read_text())))
        assert len(rows) == 6 and rows[1][2] == "Random Forest"
        assert rows[0][4] == "lower_80"
        with page.expect_download() as download:
            page.click("#png")
        assert Path(download.value.path()).read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
        page.select_option("#band", "none")
        assert page.locator("#forecastRows tr").first.locator("td").nth(2).inner_text() == "--"
        page.select_option("#model", "auto")
        page.select_option("#horizon", "20")
        page.select_option("#band", "95")
        page.mouse.move(0, 0)
        page.screenshot(path=str(output / "forecast.png"), full_page=True)
        page.click("#tab-signals")
        expect(page.locator("#rule")).to_contain_text("next open")
        assert page.locator("#tradeRows tr").count() > 0
        before = page.evaluate("report.signals.return_pct")
        page.fill("#cost", "50")
        page.click("#run")
        expect(page.locator("#tradeNote")).to_contain_text("50 bps", timeout=90000)
        assert page.evaluate("report.signals.return_pct") <= before
        page.click("#tab-macro")
        assert page.locator("#vintage").input_value() == page.evaluate(
            "report.macro_default_vintage"
        )
        page.click("#loadMacro")
        expect(page.locator("#macroTable")).to_be_visible(timeout=30000)
        assert page.locator("#macroRows tr").count() == 4
        expect(page.locator("#macroNote")).to_contain_text("Synthetic")
        page.fill("#ticker", "../bad")
        page.click("#run")
        expect(page.locator("#error")).to_be_visible(timeout=30000)
        expect(page.locator("#error")).to_contain_text("Previous analysis remains displayed")
        page.fill("#ticker", "MSFT")
        page.click("#theme")
        assert page.locator("html").get_attribute("data-theme") == "dark"
        page.click("#theme")
        response = context.request.post(args.url + "/api/analyze", data={"ticker": "MSFT"})
        assert response.status == 403
        if args.live:
            page.select_option("#source", "live")
            page.click("#run")
            expect(page.locator("#provenance")).to_have_text("LIVE SOURCE", timeout=90000)
            expect(page.locator("#sourceNote")).to_contain_text("Yahoo Finance")
            assert page.evaluate("report.mode") == "live"
            page.click("#tab-overview")
            page.screenshot(path=str(output / "live-overview.png"), full_page=True)
        assert not errors, errors
        mobile = browser.new_context(viewport={"width": 390, "height": 844}, color_scheme="light")
        mobile_page = mobile.new_page()
        mobile_page.goto(args.url)
        expect(mobile_page.locator("#subtitle")).to_contain_text("MSFT vs SPY", timeout=90000)
        assert mobile_page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
        mobile_page.screenshot(path=str(output / "mobile.png"), full_page=True)
        mobile.close()
        context.close()
        browser.close()
    print("PASS: four panels, models, horizons, costs, macro, exports, errors and mobile layout.")


if __name__ == "__main__":
    main()
