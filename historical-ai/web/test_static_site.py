"""Dependency-free regression checks for the static Historical AI website."""
from pathlib import Path
import re
import unittest

WEB_DIR = Path(__file__).resolve().parent
PAGES = (
    "index.html",
    "about.html",
    "how-it-works.html",
    "archive.html",
    "library.html",
    "login.html",
)


class StaticSiteTests(unittest.TestCase):
    def test_pages_have_shared_assets_and_navigation(self):
        for page in PAGES:
            with self.subTest(page=page):
                html = (WEB_DIR / page).read_text(encoding="utf-8")
                self.assertIn('lang="en"', html)
                self.assertIn('name="viewport"', html)
                self.assertIn('href="styles.css"', html)
                self.assertIn("<nav>", html)

    def test_internal_html_links_resolve(self):
        for page in PAGES:
            html = (WEB_DIR / page).read_text(encoding="utf-8")
            for href in re.findall(r'href="([^"]+\.html)"', html):
                with self.subTest(page=page, href=href):
                    self.assertTrue(
                        (WEB_DIR / href).is_file(),
                        f"{page} links to missing page: {href}",
                    )

    def test_mobile_navigation_remains_visible_and_wraps(self):
        css = (WEB_DIR / "styles.css").read_text(encoding="utf-8")
        media = re.search(
            r"@media\(max-width:800px\)\{(.*)\}\s*$", css
        )
        self.assertIsNotNone(media, "Expected the mobile breakpoint.")
        mobile_rules = media.group(1)
        self.assertIn(
            "nav{display:flex;flex-wrap:wrap;width:100%;gap:4px}",
            mobile_rules,
        )
        self.assertNotIn("nav{display:none}", mobile_rules)


if __name__ == "__main__":
    unittest.main()
