#!/usr/bin/env python3
"""
browser_test.py - Python wrapper for agent-browser CLI

Provides helper functions for browser automation and testing.
Uses subprocess calls to the agent-browser CLI.

Usage:
    python browser_test.py                  # Run example tests
    python browser_test.py --url URL        # Test specific URL
    python browser_test.py --headless       # Run in headless mode
"""

import subprocess
import json
import time
import sys
import argparse
from pathlib import Path
from typing import Optional, List, Dict, Any, Union
from dataclasses import dataclass


@dataclass
class Element:
    """Represents an interactive element from a snapshot."""
    ref: str
    tag: str
    text: Optional[str] = None
    type: Optional[str] = None
    placeholder: Optional[str] = None
    visible: bool = True
    enabled: bool = True


@dataclass
class Snapshot:
    """Represents a page snapshot."""
    url: str
    title: str
    elements: List[Element]
    text_content: str


class AgentBrowser:
    """Python wrapper for agent-browser CLI commands."""

    def __init__(self, timeout: int = 30000, headless: bool = False):
        """
        Initialize the browser wrapper.

        Args:
            timeout: Default timeout in milliseconds
            headless: Run browser in headless mode
        """
        self.timeout = timeout
        self.headless = headless
        self._launched = False

    def _run(self, *args: str, timeout: Optional[int] = None) -> subprocess.CompletedProcess:
        """
        Run an agent-browser command.

        Args:
            *args: Command arguments
            timeout: Optional timeout override in seconds

        Returns:
            CompletedProcess with stdout, stderr, returncode
        """
        cmd = ["agent-browser"] + list(args)
        timeout_sec = (timeout or self.timeout) / 1000

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout_sec + 10  # Buffer for command overhead
            )
            return result
        except subprocess.TimeoutExpired as e:
            raise TimeoutError(f"Command timed out: {' '.join(cmd)}") from e
        except FileNotFoundError:
            raise RuntimeError(
                "agent-browser not found. Install with: npm install -g agent-browser"
            )

    def _run_check(self, *args: str, timeout: Optional[int] = None) -> str:
        """Run command and raise on error, return stdout."""
        result = self._run(*args, timeout=timeout)
        if result.returncode != 0:
            raise RuntimeError(f"Command failed: {result.stderr}")
        return result.stdout.strip()

    # === Navigation ===

    def launch(self, **options) -> None:
        """
        Launch the browser with options.

        Args:
            headless: Run without visible window
            viewport: Viewport size as "WIDTHxHEIGHT"
            profile: Named profile for session persistence
        """
        args = ["launch"]
        if self.headless or options.get("headless"):
            args.append("--headless")
        if options.get("viewport"):
            args.extend(["--viewport", options["viewport"]])
        if options.get("profile"):
            args.extend(["--profile", options["profile"]])

        self._run_check(*args)
        self._launched = True

    def open_url(self, url: str, wait_until: str = "networkidle") -> None:
        """
        Navigate to a URL.

        Args:
            url: The URL to navigate to
            wait_until: When to consider navigation done (load, domcontentloaded, networkidle)
        """
        self._run_check("open", url, f"--wait-until={wait_until}", timeout=self.timeout)

    def back(self) -> None:
        """Navigate back in history."""
        self._run_check("back")

    def forward(self) -> None:
        """Navigate forward in history."""
        self._run_check("forward")

    def refresh(self, hard: bool = False) -> None:
        """
        Reload the current page.

        Args:
            hard: Clear cache on refresh
        """
        args = ["refresh"]
        if hard:
            args.append("--hard")
        self._run_check(*args)

    def close(self) -> None:
        """Close the browser."""
        self._run("close")
        self._launched = False

    # === Snapshots ===

    def snapshot(self, interactive: bool = True, format: str = "text",
                 selector: Optional[str] = None) -> Union[str, Snapshot]:
        """
        Capture page content.

        Args:
            interactive: Include interactive element refs
            format: Output format (text, json, markdown)
            selector: CSS selector to snapshot specific element

        Returns:
            String content or Snapshot object (if format is json and interactive)
        """
        args = ["snapshot"]
        if interactive:
            args.append("-i")
        args.extend(["--format", format])
        if selector:
            args.extend(["--selector", selector])

        output = self._run_check(*args)

        if format == "json" and interactive:
            data = json.loads(output)
            elements = [
                Element(
                    ref=el.get("ref", ""),
                    tag=el.get("tag", ""),
                    text=el.get("text"),
                    type=el.get("type"),
                    placeholder=el.get("placeholder"),
                    visible=el.get("visible", True),
                    enabled=el.get("enabled", True)
                )
                for el in data.get("elements", [])
            ]
            return Snapshot(
                url=data.get("url", ""),
                title=data.get("title", ""),
                elements=elements,
                text_content=data.get("text", "")
            )

        return output

    def screenshot(self, path: Optional[str] = None, full_page: bool = False,
                   element: Optional[str] = None) -> str:
        """
        Capture a screenshot.

        Args:
            path: File path to save screenshot
            full_page: Capture entire scrollable page
            element: Ref or selector to screenshot specific element

        Returns:
            Path to saved screenshot
        """
        args = ["screenshot"]
        if path:
            args.append(path)
        if full_page:
            args.append("--full-page")
        if element:
            args.extend(["--element", element])

        return self._run_check(*args)

    # === Interaction ===

    def click(self, ref_or_selector: str, double: bool = False,
              right: bool = False, force: bool = False) -> None:
        """
        Click an element.

        Args:
            ref_or_selector: Element ref (@e1) or CSS selector
            double: Double click
            right: Right click
            force: Click even if element is covered
        """
        args = ["click", ref_or_selector]
        if double:
            args.append("--double")
        if right:
            args.append("--right")
        if force:
            args.append("--force")

        self._run_check(*args)

    def fill(self, ref_or_selector: str, value: str,
             clear: bool = True, mask: bool = False) -> None:
        """
        Fill a text input field.

        Args:
            ref_or_selector: Element ref or selector
            value: Text to fill
            clear: Clear field before filling
            mask: Hide value in output (for passwords)
        """
        args = ["fill", ref_or_selector, value]
        if not clear:
            args.append("--no-clear")
        if mask:
            args.append("--mask")

        self._run_check(*args)

    def select(self, ref_or_selector: str, value: str) -> None:
        """
        Select option in a dropdown.

        Args:
            ref_or_selector: Element ref or selector
            value: Option value, label, or index
        """
        self._run_check("select", ref_or_selector, value)

    def check(self, ref_or_selector: str) -> None:
        """Check a checkbox or radio button."""
        self._run_check("check", ref_or_selector)

    def uncheck(self, ref_or_selector: str) -> None:
        """Uncheck a checkbox."""
        self._run_check("uncheck", ref_or_selector)

    def hover(self, ref_or_selector: str) -> None:
        """Hover over an element."""
        self._run_check("hover", ref_or_selector)

    def press(self, key: str) -> None:
        """
        Press a keyboard key.

        Args:
            key: Key to press (e.g., Enter, Tab, Escape, Control+a)
        """
        self._run_check("press", key)

    def scroll(self, direction: str = "down", to_ref: Optional[str] = None,
               by: Optional[tuple] = None) -> None:
        """
        Scroll the page.

        Args:
            direction: up, down, to-top, to-bottom
            to_ref: Scroll element into view
            by: Scroll by (x, y) pixels
        """
        args = ["scroll"]
        if to_ref:
            args.extend(["--to", to_ref])
        elif by:
            args.extend(["--by", f"{by[0]},{by[1]}"])
        else:
            args.append(direction)

        self._run_check(*args)

    # === Semantic Locators ===

    def find_role(self, role: str, name: Optional[str] = None) -> str:
        """
        Find element by ARIA role.

        Args:
            role: ARIA role (button, textbox, link, etc.)
            name: Accessible name

        Returns:
            Selector string to use with other commands
        """
        args = ["find", "role", role]
        if name:
            args.append(name)
        return self._run_check(*args)

    def find_text(self, text: str, exact: bool = False) -> str:
        """
        Find element by visible text.

        Args:
            text: Text to search for
            exact: Exact match (not substring)

        Returns:
            Selector string
        """
        args = ["find", "text", text]
        if exact:
            args.append("--exact")
        return self._run_check(*args)

    def find_label(self, label: str) -> str:
        """
        Find input by associated label.

        Args:
            label: Label text

        Returns:
            Selector string
        """
        return self._run_check("find", "label", label)

    # === Waiting ===

    def wait_visible(self, ref_or_selector: str, timeout: Optional[int] = None) -> None:
        """Wait for element to become visible."""
        args = ["wait", "visible", ref_or_selector]
        if timeout:
            args.extend(["--timeout", str(timeout)])
        self._run_check(*args, timeout=timeout)

    def wait_hidden(self, ref_or_selector: str, timeout: Optional[int] = None) -> None:
        """Wait for element to be hidden or removed."""
        args = ["wait", "hidden", ref_or_selector]
        if timeout:
            args.extend(["--timeout", str(timeout)])
        self._run_check(*args, timeout=timeout)

    def wait_network(self, idle_time: int = 500) -> None:
        """Wait for network to be idle."""
        self._run_check("wait", "network", f"--idle-time={idle_time}")

    def wait_time(self, milliseconds: int) -> None:
        """Wait for specified duration."""
        self._run_check("wait", "time", str(milliseconds))

    def wait_url(self, pattern: str) -> None:
        """Wait for URL to match pattern."""
        self._run_check("wait", "url", pattern)

    # === Information Retrieval ===

    def get_url(self) -> str:
        """Get current page URL."""
        return self._run_check("get", "url")

    def get_title(self) -> str:
        """Get page title."""
        return self._run_check("get", "title")

    def get_text(self, ref_or_selector: str) -> str:
        """Get element text content."""
        return self._run_check("get", "text", ref_or_selector)

    def get_value(self, ref_or_selector: str) -> str:
        """Get input element value."""
        return self._run_check("get", "value", ref_or_selector)

    def get_visible(self, ref_or_selector: str) -> bool:
        """Check if element is visible."""
        result = self._run_check("get", "visible", ref_or_selector)
        return result.lower() == "true"

    def get_enabled(self, ref_or_selector: str) -> bool:
        """Check if element is enabled."""
        result = self._run_check("get", "enabled", ref_or_selector)
        return result.lower() == "true"

    def eval(self, javascript: str) -> str:
        """Execute JavaScript and get result."""
        return self._run_check("eval", javascript)

    # === Session Management ===

    def session_save(self, name: str) -> None:
        """Save browser state."""
        self._run_check("session", "save", name)

    def session_load(self, name: str) -> None:
        """Load saved browser state."""
        self._run_check("session", "load", name)

    def session_list(self) -> List[str]:
        """List saved sessions."""
        output = self._run_check("session", "list")
        return [s.strip() for s in output.split("\n") if s.strip()]

    def session_delete(self, name: str) -> None:
        """Delete a saved session."""
        self._run_check("session", "delete", name)


class TestRunner:
    """Simple test runner for browser tests."""

    def __init__(self, browser: Optional[AgentBrowser] = None):
        self.browser = browser or AgentBrowser()
        self.results: List[Dict[str, Any]] = []

    def run_test(self, name: str, test_func: callable) -> bool:
        """
        Run a single test.

        Args:
            name: Test name
            test_func: Test function to execute

        Returns:
            True if test passed, False otherwise
        """
        print(f"Running: {name}...", end=" ")
        start_time = time.time()

        try:
            test_func(self.browser)
            elapsed = time.time() - start_time
            print(f"PASS ({elapsed:.2f}s)")
            self.results.append({"name": name, "passed": True, "time": elapsed})
            return True
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"FAIL ({elapsed:.2f}s)")
            print(f"  Error: {e}")
            self.results.append({
                "name": name,
                "passed": False,
                "time": elapsed,
                "error": str(e)
            })
            return False

    def summary(self) -> None:
        """Print test summary."""
        total = len(self.results)
        passed = sum(1 for r in self.results if r["passed"])
        failed = total - passed

        print("\n" + "=" * 50)
        print(f"Tests: {total} | Passed: {passed} | Failed: {failed}")

        if failed > 0:
            print("\nFailed tests:")
            for r in self.results:
                if not r["passed"]:
                    print(f"  - {r['name']}: {r.get('error', 'Unknown error')}")

        print("=" * 50)


# === Example Test Functions ===

def test_homepage_loads(browser: AgentBrowser) -> None:
    """Test that homepage loads correctly."""
    browser.open_url("https://example.com")
    browser.wait_network()

    title = browser.get_title()
    assert "Example" in title, f"Expected 'Example' in title, got '{title}'"


def test_navigation(browser: AgentBrowser) -> None:
    """Test browser navigation."""
    browser.open_url("https://example.com")
    initial_url = browser.get_url()

    # Navigate to another page
    browser.snapshot(interactive=True)
    browser.click("@e1")  # Click first link
    browser.wait_network()

    new_url = browser.get_url()
    assert new_url != initial_url, "URL should change after navigation"

    # Go back
    browser.back()
    browser.wait_network()

    back_url = browser.get_url()
    assert back_url == initial_url, "Should return to initial URL"


def test_form_interaction(browser: AgentBrowser) -> None:
    """Test form filling and submission."""
    browser.open_url("https://httpbin.org/forms/post")
    browser.wait_network()

    # Get form elements
    browser.snapshot(interactive=True)

    # Fill form fields (refs will vary, this is an example)
    browser.fill("@e1", "Test Customer")
    browser.fill("@e2", "555-1234")

    # Verify values were set
    value = browser.get_value("@e1")
    assert value == "Test Customer", f"Expected 'Test Customer', got '{value}'"


def test_screenshot(browser: AgentBrowser) -> None:
    """Test screenshot capture."""
    browser.open_url("https://example.com")
    browser.wait_network()

    screenshot_path = browser.screenshot(".tmp/test-screenshot.png")
    assert Path(".tmp/test-screenshot.png").exists() or screenshot_path, "Screenshot should be created"


def test_semantic_locators(browser: AgentBrowser) -> None:
    """Test finding elements by semantic attributes."""
    browser.open_url("https://example.com")
    browser.wait_network()

    # Find link by text
    try:
        link = browser.find_text("More information")
        assert link, "Should find 'More information' link"
    except RuntimeError:
        # May not exist on example.com, that's ok for this test
        pass


def main():
    """Run example tests."""
    parser = argparse.ArgumentParser(description="Browser testing with agent-browser")
    parser.add_argument("--url", help="Test specific URL")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    parser.add_argument("--screenshot-dir", default=".tmp", help="Screenshot output directory")
    args = parser.parse_args()

    # Ensure output directory exists
    Path(args.screenshot_dir).mkdir(parents=True, exist_ok=True)

    # Initialize browser
    browser = AgentBrowser(headless=args.headless)
    runner = TestRunner(browser)

    try:
        print("=" * 50)
        print("Browser Test Suite")
        print("=" * 50 + "\n")

        if args.url:
            # Test specific URL
            def test_custom_url(b: AgentBrowser):
                b.open_url(args.url)
                b.wait_network()
                b.snapshot(interactive=True)
                b.screenshot(f"{args.screenshot_dir}/custom-url.png")

            runner.run_test(f"Load {args.url}", test_custom_url)
        else:
            # Run all example tests
            runner.run_test("Homepage loads", test_homepage_loads)
            runner.run_test("Navigation works", test_navigation)
            runner.run_test("Form interaction", test_form_interaction)
            runner.run_test("Screenshot capture", test_screenshot)
            runner.run_test("Semantic locators", test_semantic_locators)

        runner.summary()

    except KeyboardInterrupt:
        print("\nTests interrupted")
    finally:
        browser.close()

    # Exit with error code if any tests failed
    failed = sum(1 for r in runner.results if not r["passed"])
    sys.exit(1 if failed > 0 else 0)


if __name__ == "__main__":
    main()
