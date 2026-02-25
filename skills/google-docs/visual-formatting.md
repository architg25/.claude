# Visual Formatting Validation

Automated visual comparison and formatting correction for Google Docs based on rendered markdown screenshots. Uses Playwright for screenshots, odiff for pixel comparison, Claude Code Read tool for LLM vision analysis, and Google Docs API for batch formatting fixes. Validates with SSIM metric.

## Features

- **Screenshot Automation** - Playwright-based rendering and capture
- **Fast Pixel Comparison** - odiff pre-screening (6x faster than alternatives)
- **SSIM Validation** - Quantitative similarity measurement
- **Reusable Utilities** - Permanent scripts that subagents can execute

## Dependencies

**Python Packages:**

```bash
pip install playwright scikit-image
playwright install chromium
```

**CLI Tools:**

```bash
npm install -g odiff-bin
```

## Scripts

### capture_screenshots.py

Renders markdown as HTML and captures screenshots of both markdown and Google Docs.

**Usage**:

```bash
python3 ~/.claude/skills/google-docs/scripts/visual-formatting/capture_screenshots.py \
  --markdown rfcs/example.md \
  --gdoc-url "https://docs.google.com/document/d/DOCUMENT_ID/edit" \
  --output-dir /tmp/screenshots
```

**Output**:

- `/tmp/screenshots/markdown.png` - Rendered markdown screenshot
- `/tmp/screenshots/gdoc.png` - Google Doc screenshot

### compare_pixel.py

Fast pixel-level comparison using odiff.

**Usage**:

```bash
python3 ~/.claude/skills/google-docs/scripts/visual-formatting/compare_pixel.py \
  --image1 /tmp/screenshots/markdown.png \
  --image2 /tmp/screenshots/gdoc.png \
  --output /tmp/screenshots/diff.png
```

**Output**: JSON with diff percentage: `{"diff_percent": 5.2}`

### measure_similarity.py

SSIM (Structural Similarity Index) calculation.

**Usage**:

```bash
python3 ~/.claude/skills/google-docs/scripts/visual-formatting/measure_similarity.py \
  --image1 /tmp/screenshots/markdown.png \
  --image2 /tmp/screenshots/gdoc.png
```

**Output**: JSON with SSIM score: `{"ssim": 0.92, "quality": "good"}`

## Workflow

These scripts are designed to be called by a subagent that orchestrates the full visual formatting validation workflow:

1. **Capture** - Screenshot both the rendered markdown and the Google Doc
2. **Compare** - Run pixel-level diff with odiff for fast pre-screening
3. **Analyze** - If diff > 1%, use LLM vision analysis (Claude Code Read tool) to identify formatting discrepancies
4. **Fix** - Generate Google Docs API batchUpdate requests to correct formatting
5. **Validate** - Re-capture and measure SSIM to confirm fixes (target >= 0.95)
