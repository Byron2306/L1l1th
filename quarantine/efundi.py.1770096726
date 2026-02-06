"""
Efundi (Sakai) Web UI integration using Playwright.

Design: persistent session via storage state to avoid re-login.
"""
from __future__ import annotations
from pathlib import Path
from typing import Optional

from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page


class EfundiClient:
    def __init__(
        self,
        base_url: str,
        storage_state_path: Path,
        headless: bool = True,
        slow_mo_ms: int = 0,
    ):
        self.base_url = base_url.rstrip("/")
        self.storage_state_path = Path(storage_state_path)
        self.headless = headless
        self.slow_mo_ms = slow_mo_ms

    def _launch(self):
        return sync_playwright()

    def _new_context(self, p):
        browser = p.chromium.launch(headless=self.headless, slow_mo=self.slow_mo_ms)
        if self.storage_state_path.exists():
            ctx = browser.new_context(storage_state=str(self.storage_state_path))
        else:
            ctx = browser.new_context()
        return browser, ctx

    def interactive_login_and_save(self, start_url: Optional[str] = None):
        """
        Open efundi login page and let user sign in manually.
        Then save storage state to storage_state_path.
        """
        start_url = start_url or self.base_url
        with self._launch() as p:
            browser, ctx = self._new_context(p)
            page = ctx.new_page()
            page.goto(start_url, wait_until="domcontentloaded")
            print("[Efundi] Please complete login in the opened browser.")
            input("[Efundi] Press ENTER here once logged in...")
            ctx.storage_state(path=str(self.storage_state_path))
            print(f"[Efundi] Saved session to {self.storage_state_path}")
            ctx.close()
            browser.close()

    def _with_page(self, fn):
        with self._launch() as p:
            browser, ctx = self._new_context(p)
            page = ctx.new_page()
            try:
                return fn(page)
            finally:
                ctx.close()
                browser.close()

    # --- The functions below need site-specific selectors/flows ---
    def list_courses(self):
        def _run(page: Page):
            page.goto(self.base_url, wait_until="domcontentloaded")
            # TODO: implement site-specific navigation to course list
            raise NotImplementedError("Course listing not implemented yet")
        return self._with_page(_run)

    def download_assignment_zip(self, course_id: str, assignment_id: str, dest_zip: Path):
        def _run(page: Page):
            dest_zip.parent.mkdir(parents=True, exist_ok=True)
            assignment_url = assignment_id
            if not assignment_url.startswith("http"):
                # Fallback: build a Sakai-style URL if given course/tool ids
                assignment_url = f"{self.base_url}/portal/site/{course_id}/tool/{assignment_id}?panel=Main"

            page.goto(assignment_url, wait_until="domcontentloaded")
            page.get_by_role("link", name="Download All").click()

            # Download All options
            page.get_by_label("All").check()
            # Ensure CSV grade file
            if page.get_by_label("CSV format, file grades.csv").count() > 0:
                page.get_by_label("CSV format, file grades.csv").check()
            # Include non-submitters
            if page.get_by_label("Include students who have not yet submitted").count() > 0:
                page.get_by_label("Include students who have not yet submitted").check()

            with page.expect_download() as dl_info:
                page.get_by_role("button", name="Download").click()
            download = dl_info.value
            download.save_as(str(dest_zip))
        return self._with_page(_run)

    def upload_feedback_zip(self, course_id: str, assignment_id: str, zip_path: Path):
        def _run(page: Page):
            zip_path = Path(zip_path)
            assignment_url = assignment_id
            if not assignment_url.startswith("http"):
                assignment_url = f"{self.base_url}/portal/site/{course_id}/tool/{assignment_id}?panel=Main"

            page.goto(assignment_url, wait_until="domcontentloaded")
            page.get_by_role("link", name="Upload All").click()

            file_input = page.locator("input[type=file]").first
            file_input.set_input_files(str(zip_path))
            page.get_by_role("button", name="Upload").click()
        return self._with_page(_run)

    def update_gradebook(self, course_id: str, grades_csv: Path):
        def _run(page: Page):
            # TODO: implement gradebook update
            raise NotImplementedError("Gradebook update not implemented yet")
        return self._with_page(_run)
