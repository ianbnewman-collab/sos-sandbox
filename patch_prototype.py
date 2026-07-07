"""
Stanley's Own Scouts — Prototype Wiring Script
Patches all 9 Claude Design HTML exports for multi-page navigation.

Changes applied (logged in patch_log.md):
  1. Replace the flat <nav> with a dropdown-capable nav on every page
  2. Fix Contact.dc.html broken links → # (placeholder, no contact page in this set)
  3. Ensure Sections dropdown links: Beavers → beavers-hub.html, Cubs → cubs-hub.html,
     Scouts → scouts-hub.html; Squirrels/Explorers → # (stubs)
  4. Scout Hub body already has correct king-troop.html / everett-troop.html links — no change needed

The nav replacement is a string replace of the entire <nav>…</nav> block.
This preserves the logo src UUID (Claude Design image reference) on each page.
"""

import json, re, shutil, os, sys
from pathlib import Path

SRC = Path('/mnt/user-data/uploads')
OUT = Path('/home/claude/prototype')
OUT.mkdir(exist_ok=True)

FILES = [
    'homepage.html',
    'about-us.html',
    'beavers-hub.html',
    'cubs-hub.html',
    'scouts-hub.html',
    'king-troop.html',
    'everett-troop.html',
    'magazine.html',
    'hall-hire.html',
]

# Active-page indicator: which file gets the highlighted nav item
ACTIVE_MAP = {
    'homepage.html':      'Home',
    'about-us.html':      'About Us',
    'beavers-hub.html':   'Sections',
    'cubs-hub.html':      'Sections',
    'scouts-hub.html':    'Sections',
    'king-troop.html':    'Sections',
    'everett-troop.html': 'Sections',
    'magazine.html':      'Magazine',
    'hall-hire.html':     'Hall Hire',
}

# --- NEW NAV TEMPLATE ---
# Uses the same logo src UUID extracted from each page individually.
# The dropdown is CSS-only (hover), works without JS, and degrades cleanly.
# Inline <style> block is injected once per nav.

NAV_STYLE = """<style>
  .sos-nav-dropdown { position: relative; }
  .sos-nav-dropdown-menu {
    display: none; position: absolute; top: 100%; left: 0;
    background: #5a0db8; border-radius: 0 0 6px 6px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.32); min-width: 220px;
    padding: 8px 0; z-index: 200;
  }
  .sos-nav-dropdown:hover .sos-nav-dropdown-menu,
  .sos-nav-dropdown:focus-within .sos-nav-dropdown-menu { display: block; }
  .sos-nav-dropdown-menu a {
    display: block; padding: 10px 20px; color: rgba(255,255,255,0.88);
    font-size: 14px; font-weight: 700; text-decoration: none;
    transition: background 0.12s;
  }
  .sos-nav-dropdown-menu a:hover { background: rgba(255,255,255,0.12); color: #fff; }
  .sos-nav-dropdown-menu .sos-sub-indent {
    padding-left: 32px; font-size: 13px; font-weight: 400; color: rgba(255,255,255,0.68);
  }
  .sos-nav-dropdown-menu .sos-sub-indent:hover { color: #fff; }
  .sos-nav-sep { height: 1px; background: rgba(255,255,255,0.12); margin: 6px 0; }
</style>"""

def make_nav(logo_src, active_page):
    """Build the full <nav> block. logo_src is the UUID image reference."""
    
    def link(label, href, active_label, extra_style=''):
        is_active = (label == active_label)
        bg = "background: rgba(255,255,255,0.18);" if is_active else ""
        colour = "#fff" if is_active else "rgba(255,255,255,0.88)"
        return (f'<a href="{href}" style="color: {colour}; font-weight: 700; font-size: 14px; '
                f'text-decoration: none; padding: 8px 13px; border-radius: 4px; {bg}{extra_style}">{label}</a>')

    active_label = ACTIVE_MAP.get(active_page, '')

    sections_active = "background: rgba(255,255,255,0.18);" if active_label == 'Sections' else ""

    sections_dropdown = f"""<div class="sos-nav-dropdown" style="position:relative;">
      <button style="background: rgba(255,255,255,0.0); {sections_active} border: none; cursor: pointer;
        color: {'#fff' if active_label=='Sections' else 'rgba(255,255,255,0.88)'}; font-weight: 700;
        font-size: 14px; font-family: 'Nunito Sans', sans-serif;
        padding: 8px 13px; border-radius: 4px; display: flex; align-items: center; gap: 4px;">
        Sections ▾
      </button>
      <div class="sos-nav-dropdown-menu">
        <a href="#">Squirrels (4–6)</a>
        <a href="beavers-hub.html">Beavers (6–8)</a>
        <a href="cubs-hub.html">Cubs (8–10½)</a>
        <a href="scouts-hub.html">Scouts (10½–14)</a>
        <div class="sos-nav-sep"></div>
        <span style="display:block; padding: 4px 20px 2px; font-size:11px; font-weight:700;
          letter-spacing:0.1em; text-transform:uppercase; color:rgba(255,255,255,0.35);">Scout Troops</span>
        <a class="sos-sub-indent" href="scouts-hub.html#troops">King Troop</a>
        <a class="sos-sub-indent" href="scouts-hub.html#troops">Everett Troop</a>
        <div class="sos-nav-sep"></div>
        <a href="#">Explorers (14–18)</a>
      </div>
    </div>"""

    # Note: King/Everett are accessible from scouts-hub directly — no separate top-level nav items.
    # Clicking them from the dropdown sends you to scouts-hub#troops anchor (the troop cards section).

    nav = f"""<nav style="background: #7413dc; height: 72px; display: flex; align-items: center; justify-content: space-between; padding: 0 48px; position: sticky; top: 0; z-index: 100; box-shadow: 0 2px 16px rgba(0,0,0,0.26);">
  {NAV_STYLE}
  <a href="homepage.html" style="display: flex; align-items: center; gap: 14px; text-decoration: none; flex-shrink: 0;">
    <div style="display: inline-flex; background: #7413dc; isolation: isolate;">
      <img src="{logo_src}" alt="Scouts" style="height: 52px; width: auto; filter: invert(1); mix-blend-mode: screen; display: block;">
    </div>
    <div style="border-left: 1px solid rgba(255,255,255,0.28); padding-left: 14px; line-height: 1.3;">
      <div style="font-size: 16px; font-weight: 900; color: #fff; letter-spacing: -0.01em; white-space: nowrap;">2nd Copythorne</div>
      <div style="font-size: 12px; font-weight: 400; color: rgba(255,255,255,0.75); white-space: nowrap;">(Stanley's Own) Scouts</div>
    </div>
  </a>
  <div style="display: flex; align-items: center; gap: 2px;">
    {link('Home', 'homepage.html', active_label)}
    {link('About Us', 'about-us.html', active_label)}
    {sections_dropdown}
    {link('Band', '#', active_label)}
    {link('Volunteer', '#', active_label)}
    {link('Events', '#', active_label)}
    {link('Magazine', 'magazine.html', active_label)}
    {link('Hall Hire', 'hall-hire.html', active_label)}
    {link('Contact', '#', active_label)}
  </div>
  <a href="#" style="background: #fff; color: #7413dc; font-weight: 700; font-size: 14px; padding: 10px 22px; border-radius: 4px; text-decoration: none; white-space: nowrap; flex-shrink: 0;">Join Us →</a>
</nav>"""
    return nav


def patch_file(filename):
    src_path = SRC / filename
    out_path = OUT / filename
    
    with open(src_path, 'rb') as f:
        raw_bytes = f.read()
    raw = raw_bytes.decode('utf-8')
    
    # These are Claude Design standalone exports.
    # The page HTML is JSON-encoded inside <script type="__bundler/template">
    m = re.search(r'(<script type="__bundler/template">)(.*?)(</script>)', raw, re.DOTALL)
    if not m:
        print(f"  WARNING: {filename} — no bundler template found, skipping")
        return False, "no bundler template found"
    
    prefix = m.group(1)
    encoded = m.group(2)
    suffix = m.group(3)
    
    # Decode the JSON string to get the actual HTML
    try:
        page_html = json.loads(encoded)
    except json.JSONDecodeError as e:
        print(f"  ERROR: {filename} — JSON decode failed: {e}")
        return False, f"JSON decode error: {e}"
    
    changes = []
    
    # 1. Extract logo src UUID from existing nav
    logo_match = re.search(r'<nav [^>]*>.*?<img src="([^"]+)"', page_html, re.DOTALL)
    if not logo_match:
        print(f"  WARNING: {filename} — could not find logo src in nav")
        logo_src = "8510c064-bc1c-4f7c-a5fc-e677699e9996"  # fallback from homepage
    else:
        logo_src = logo_match.group(1)
    
    # 2. Replace the entire <nav> block
    old_nav_match = re.search(r'<nav [^>]*>.*?</nav>', page_html, re.DOTALL)
    if old_nav_match:
        new_nav = make_nav(logo_src, filename)
        page_html = page_html[:old_nav_match.start()] + new_nav + page_html[old_nav_match.end():]
        changes.append("nav replaced with dropdown-capable version")
    else:
        changes.append("WARNING: nav block not found")
    
    # 3. Fix Contact.dc.html broken links
    contact_count = page_html.count('Contact.dc.html')
    if contact_count > 0:
        page_html = page_html.replace('Contact.dc.html', '#')
        changes.append(f"fixed {contact_count}x Contact.dc.html → #")
    
    # 4. Re-encode and slot back in, escaping </script> inside the JSON string
    re_encoded = json.dumps(page_html, ensure_ascii=False)
    # Escape any </script> that might appear in the re-encoded string (safety)
    re_encoded = re_encoded.replace('</script>', '<\\/script>')
    
    # Rebuild the full file
    new_raw = raw[:m.start()] + prefix + re_encoded + suffix + raw[m.end():]
    
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(new_raw)
    
    print(f"  OK: {filename} — {'; '.join(changes)}")
    return True, changes


print("=== Stanley's Own Prototype Wiring Patcher ===\n")
results = {}
for fname in FILES:
    ok, info = patch_file(fname)
    results[fname] = {'ok': ok, 'changes': info}

print(f"\nDone. {sum(1 for r in results.values() if r['ok'])}/{len(FILES)} files patched.")
print(f"Output directory: {OUT}")

# Save results for the log
with open('/home/claude/patch_results.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)
