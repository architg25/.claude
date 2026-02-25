---
name: interactive-code-map
description: >
  Generate an interactive HTML code map for a codebase component. Creates a self-contained
  playground with pipeline visualization, step-by-step flow tracer, output format comparison,
  change impact analysis, and FAQ. Use when user asks to "create a code map", "visualize the
  pipeline", "interactive flow diagram", "debug flow visualization", or wants to understand
  how data flows through a component.
argument-hint: [component-path]
---

# Interactive Code Map

Generate a self-contained HTML playground that visualizes how data flows through a codebase component. The output is a single HTML file with 5 interactive tabs for learning, debugging, and change impact analysis.

## When to Use

- Exploring a new pipeline, projection, or data flow component
- Onboarding to an unfamiliar codebase area
- Debugging "if I change X, what breaks?"
- Understanding how entity types route through processing steps
- Comparing output formats (e.g., V4 vs V5, REST vs gRPC, old vs new)

## Skill Resources

| Resource         | Path                         | Use when                  |
| ---------------- | ---------------------------- | ------------------------- |
| Tab patterns ref | `references/tab-patterns.md` | Building the 5 tab panels |

---

## Input

The user provides a **component path** (e.g., `statements-audiobooks/statements-critical-path-audiobook/projections/audiobook`). If not provided, ask for it.

Determine the **output location** — write the HTML file at the component root (next to `src/`), named `code-map.html`.

---

## Phase 1: Explore

Create a team named `codemap-explore` with 3 specialized agents running in parallel. Each agent writes a structured markdown deliverable to `.claude/codemap-work/`.

### Agent: `architect`

**Role:** Pipeline structure

**Instructions:** Explore the component and extract:

- Ordered list of processing steps with input/output types
- PubSub topics / message queues between steps
- Side projections or branching flows
- Class file paths for each step
- Main.java (or equivalent entry point) wiring — how steps are composed
- Entity types that flow through the pipeline
- Step composition pattern (sequential, parallel, fan-out)

**Write to:** `.claude/codemap-work/architecture.md`

### Agent: `data-analyst`

**Role:** Entity and field mapping

**Instructions:** Explore the component and extract:

- All entity types flowing through the component
- Subscribed fields per entity type (what triggers processing)
- Field routing logic (which fields cascade to child entities)
- Converter field mappings: source field → output field per output format
- Data model record shapes with field types (input models, intermediate models, output models)
- Validation rules and what makes an entity valid/invalid

**Write to:** `.claude/codemap-work/data-analysis.md`

### Agent: `gotcha-hunter`

**Role:** Edge cases and risks

**Instructions:** Explore the component and extract:

- Non-obvious behaviors (silent failures, unexpected field sources, deliberate discrepancies)
- Test coverage gaps (behaviors that exist in code but have no tests)
- Validation and fallback flows (what happens when things fail)
- Concurrency control patterns (optimistic locking, version checks)
- Error paths (what gets dropped, what gets retried, what fails loudly vs silently)
- "If I change X, what breaks?" dependency chains
- Fields or behaviors where output format variants diverge intentionally

**Write to:** `.claude/codemap-work/gotchas.md`

### Team Lead Synthesis

After all 3 agents complete, read all 3 deliverables and synthesize into a unified data spec at `.claude/codemap-work/unified-spec.md`. This spec feeds Phase 2.

The unified spec should contain:

1. **Entity list** with color assignments (use the palette: blue, green, purple, orange — extend with cyan, red, yellow if needed)
2. **Pipeline steps** in order with entity participation per step
3. **Field index** — every field mapped to its converters and output locations
4. **Gotcha list** with severity ratings (high/medium/low)
5. **Dependency chains** — fields that trigger cascading re-processing
6. **Data models** — input, intermediate, and output record shapes

---

## Phase 2: Build

Create a team named `codemap-build` with 4 agents. The `assembler` is blocked by the other 3.

Read `references/tab-patterns.md` before starting this phase — it contains the HTML structure, CSS conventions, JS data shapes, and rendering patterns for each tab.

### Agent: `css-html`

**Uses:** All 3 explore outputs + unified spec

**Instructions:** Build the CSS and HTML skeleton:

- CSS custom properties for the dark theme color palette (see tab-patterns.md)
- Toolbar with entity type toggle buttons (pill-shaped, color-coded)
- Tab bar with 5 tabs: Pipeline, Tracer, Comparison, Impact, FAQ
- HTML panel containers for each tab
- Responsive layout using CSS grid/flexbox
- All CSS inline in a `<style>` block

**Write to:** `.claude/codemap-work/skeleton.html`

### Agent: `core-js`

**Uses:** architecture.md + data-analysis.md + unified spec

**Instructions:** Build the core JavaScript:

- `pipelineSteps[]` and `pipelineConnections[]` data arrays from the architecture
- `buildPipelineSVG()` function rendering clickable step nodes with entity highlighting
- `selectPipelineStep()` for detail sidebar population
- `classInfo{}` object mapping class names to file paths, methods, responsibility
- `tracerData{}` per entity type with step-by-step trace entries
- `dataModels{}` with field types for the data model sidebar
- `sharedSteps[]` for steps common across entity types
- Tracer rendering with prev/next/play controls and timeline dots
- Entity toggle function affecting pipeline highlighting and tracer content
- Tab switching function

**Write to:** `.claude/codemap-work/core.js`

### Agent: `analysis-js`

**Uses:** data-analysis.md + gotchas.md + unified spec

**Instructions:** Build the analysis JavaScript:

- Comparison tab: `buildComparisonTab()` with side-by-side field mapping tables, inline warning badges for gotchas, key differences callout section
- Impact tab: `fieldIndex{}` object for field reverse lookup (field → converters → output locations), `gotchas[]` array with severity/title/location/detail/impact/tested, `dependencyChains[]` array, `buildImpactTab()` with dropdown field selector and result rendering
- FAQ tab: `buildFAQ()` with interactive decision tree ("why didn't X happen?") and accordion Q&A, entity-aware highlighting
- All highlight/filter functions for entity toggling on these tabs

**Write to:** `.claude/codemap-work/analysis.js`

### Agent: `assembler` (blocked by above 3)

**Uses:** All 3 builder outputs

**Instructions:** Assemble the final HTML file:

1. Read `skeleton.html`, `core.js`, and `analysis.js`
2. Combine into a single self-contained HTML file
3. Place all JS in a single `<script>` block after the HTML
4. Add initialization: `document.addEventListener('DOMContentLoaded', init)` that builds all tabs and sets up event listeners
5. Verify no external dependencies (no CDN links, no imports)
6. Write to the output location determined in the Input step

---

## Phase 3: Review

Spawn a single review agent to evaluate the assembled HTML file. The reviewer should read the file and evaluate against these criteria:

1. **Learning:** Can I understand how data flows through this component by using the Pipeline and Tracer tabs?
2. **Debugging:** Can I spot where bugs might hide using the Impact tab's gotcha cards?
3. **Change impact:** Can I answer "if I change field X, what breaks?" using the Impact tab's field lookup?
4. **Completeness:** Are all entity types represented? Are all processing steps covered?
5. **Navigation:** Do class names link to file paths? Do entity buttons filter all tabs?

Return a prioritized list of gaps (critical → nice-to-have).

---

## Phase 4: Enhance

Apply the review findings via targeted edits to the assembled HTML file. Focus on critical gaps first. Skip nice-to-haves unless they're trivial to add.

---

## Cleanup

Delete the `.claude/codemap-work/` directory after the final file is assembled and reviewed.

---

## Technical Conventions

These are non-negotiable for the output HTML:

- **Single self-contained HTML file** — zero external dependencies
- **Dark theme** using CSS custom properties (see tab-patterns.md for the palette)
- **Vanilla JS** — no frameworks, no build tools
- **CSS grid/flexbox** for layout, **SVG** for diagrams
- **Data-driven rendering** — all content lives in JS objects, rendering functions consume them
- **Navigable class names** — clicking a class name shows a popup with file path, methods, and responsibility
- **Entity type buttons** — toggle buttons in the toolbar that affect ALL tabs (highlighting, filtering, auto-expanding relevant sections)

## Adapting to Different Domains

This skill works beyond pipelines. The 5-tab pattern adapts to:

| Domain           | Pipeline tab becomes  | Tracer becomes              | Comparison becomes         | Impact becomes       |
| ---------------- | --------------------- | --------------------------- | -------------------------- | -------------------- |
| Request handler  | Request flow diagram  | Request lifecycle trace     | Response format comparison | Field/header impact  |
| ETL flow         | Transform pipeline    | Record transformation trace | Schema version comparison  | Column lineage       |
| Event processor  | Event routing diagram | Event processing trace      | Output event comparison    | Field propagation    |
| Data transformer | Transform chain       | Data shape evolution        | Before/after comparison    | Transform dependency |

The core principle stays the same: visualize the flow, trace individual paths, compare outputs, and analyze change impact.
