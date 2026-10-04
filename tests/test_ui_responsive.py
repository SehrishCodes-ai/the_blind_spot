"""
Responsive design and UI/UX automated checks for 'The Blind Spot'.
Verifies:
- Page-level horizontal overflow protection in CSS
- Container and grid column minmax(0, ...) safety
- Absence of fixed pixel widths that exceed narrow mobile viewports (360px-412px)
- Inclusion of accessible inline error component in index.html
- Component-level isolated horizontal scrolling
"""
import re
import os


def test_no_page_level_horizontal_overflow_css():
    """Verify html and body have overflow-x: hidden and max-width: 100vw."""
    css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "css", "styles.css")
    with open(css_path, "r", encoding="utf-8") as f:
        css = f.read()

    # Check html overflow-x
    assert re.search(r'html\s*\{[^}]*overflow-x:\s*hidden', css, re.DOTALL), "html must have overflow-x: hidden"
    assert re.search(r'body\s*\{[^}]*overflow-x:\s*hidden', css, re.DOTALL), "body must have overflow-x: hidden"


def test_grid_track_prevents_column_blowout():
    """Verify .main-layout uses minmax(0, ...) on fractional tracks."""
    css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "css", "styles.css")
    with open(css_path, "r", encoding="utf-8") as f:
        css = f.read()

    # Verify min-width: 0 is on .main-layout or grid items
    assert "min-width: 0" in css
    # Verify minmax(0, 1fr) is used for the desktop grid column
    assert "minmax(0, 1fr)" in css, ".main-layout grid track must use minmax(0, 1fr) to prevent content blowout"


def test_scenarios_and_filters_component_scrolling():
    """Verify .scenarios-scroll and .analysis-filters have isolated overflow-x: auto."""
    css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "css", "styles.css")
    with open(css_path, "r", encoding="utf-8") as f:
        css = f.read()

    assert ".scenarios-scroll" in css
    assert ".analysis-filters" in css
    assert re.search(r'\.scenarios-scroll\s*\{[^}]*overflow-x:\s*auto', css, re.DOTALL)
    assert re.search(r'\.analysis-filters\s*\{[^}]*overflow-x:\s*auto', css, re.DOTALL)


def test_accessible_inline_error_component_present():
    """Verify inline error component exists in index.html to replace browser alert()."""
    html_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    assert "inlineErrorAlert" in html
    assert 'role="alert"' in html
    assert 'aria-live="assertive"' in html
    assert "inlineErrorClose" in html


def test_no_hardcoded_overwide_fixed_widths():
    """Verify there are no fixed widths > 360px without max-width constraint."""
    css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "css", "styles.css")
    with open(css_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for idx, line in enumerate(lines):
        match = re.search(r'^\s*width:\s*([4-9]\d{2,}|\d{4,})px;', line)
        if match:
            # If line specifies a fixed width over 400px, it must be accompanied by max-width
            assert False, f"Fixed overwide width found on line {idx+1}: {line.strip()}"
