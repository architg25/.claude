# Tab Patterns Reference

Reusable structure for the 5 interactive tabs in an HTML code map. Each section defines the HTML skeleton, CSS class conventions, JS data structures, and rendering approach.

---

## CSS Custom Property Contract

The following property **names** are referenced by JS and HTML throughout the code map. The `css-html` agent must define values for all of them based on the aesthetic direction from `/frontend-design`. The values below are placeholders — not defaults.

```css
:root {
  /* Backgrounds — 4 tiers from darkest/deepest to lightest/surface */
  --bg-primary: /* ... */;
  --bg-secondary: /* ... */;
  --bg-tertiary: /* ... */;
  --bg-card: /* ... */;

  /* Borders — 2 tiers */
  --border: /* ... */;
  --border-light: /* ... */;

  /* Text — 3 tiers */
  --text-primary: /* ... */;
  --text-secondary: /* ... */;
  --text-muted: /* ... */;

  /* Entity colors — assign to entity types in order.
     Names are semantic labels, NOT literal color requirements.
     --blue could be teal, --green could be lime, etc.
     Just need 4-7 distinct, accessible colors that fit the aesthetic. */
  --blue: /* ... */;
  --green: /* ... */;
  --purple: /* ... */;
  --orange: /* ... */;
  --red: /* ... */;
  --yellow: /* ... */;
  --cyan: /* ... */;

  /* Dimmed variants — typically 10-20% opacity of the entity color, for backgrounds */
  --blue-dim: /* ... */;
  --green-dim: /* ... */;
  --purple-dim: /* ... */;
  --orange-dim: /* ... */;
  --red-dim: /* ... */;
  --yellow-dim: /* ... */;
  --cyan-dim: /* ... */;

  /* Fonts — chosen by /frontend-design aesthetic direction.
     Load display/body fonts via @import from Google Fonts in styles.css. */
  --font-mono: /* ... */;
  --font-system: /* ... */;
}
```

**Important:** The property names are a contract — JS and HTML reference them directly (e.g., `var(--bg-primary)`, `var(--blue-dim)`). The `css-html` agent populates the values. Entity color names like `--blue` and `--green` are labels for the 1st, 2nd, etc. entity colors — they don't have to literally be blue or green.

## Common Layout Structure

```html
<!-- Toolbar: entity toggle buttons -->
<div class="toolbar">
  <span class="toolbar-title">Component Name</span>
  <!-- One button per entity type, colored by assignment -->
  <button
    class="entity-btn"
    data-entity="entityA"
    onclick="toggleEntity('entityA')"
  >
    EntityA
  </button>
  <button
    class="entity-btn"
    data-entity="entityB"
    onclick="toggleEntity('entityB')"
  >
    EntityB
  </button>
  <span class="toolbar-spacer"></span>
  <span class="toolbar-info">N entity types &middot; M pipeline steps</span>
</div>

<!-- Tab bar -->
<div class="tab-bar">
  <button class="tab-btn active" onclick="switchTab('pipeline')">
    Pipeline
  </button>
  <button class="tab-btn" onclick="switchTab('tracer')">Tracer</button>
  <button class="tab-btn" onclick="switchTab('comparison')">Comparison</button>
  <button class="tab-btn" onclick="switchTab('impact')">Impact</button>
  <button class="tab-btn" onclick="switchTab('faq')">FAQ</button>
</div>

<!-- Tab panels -->
<div class="main-content">
  <div id="tab-pipeline" class="tab-panel active">...</div>
  <div id="tab-tracer" class="tab-panel">...</div>
  <div id="tab-comparison" class="tab-panel">...</div>
  <div id="tab-impact" class="tab-panel">...</div>
  <div id="tab-faq" class="tab-panel">...</div>
</div>
```

### CSS Class Conventions

- `.entity-btn.active-{entityName}` — active entity button styling (background: `--{color}-dim`, border/text: `--{color}`)
- `.tab-btn.active` — active tab with bottom border
- `.tab-panel.active` — visible panel (`display: flex`)
- `.dimmed` — faded elements when entity filter is active (opacity 0.15)
- `.selected` — highlighted element (blue border glow)
- `.nav-link` — clickable class name reference (underline, cursor pointer)

### Core JS Functions (shared across all tabs)

```js
let activeEntity = null; // Currently toggled entity type, or null for "all"
let activeTab = "pipeline"; // Currently visible tab

function toggleEntity(entity) {
  // If already active, deactivate (show all). Otherwise activate.
  activeEntity = activeEntity === entity ? null : entity;
  // Update button styles
  // Call per-tab highlight updaters
  updatePipelineHighlights();
  updateTracerHighlights();
  updateComparisonHighlights();
  updateImpactHighlights();
  updateFaqHighlights();
}

function switchTab(tab) {
  activeTab = tab;
  // Hide all panels, show selected
  // Update tab button active states
}

// Class info popup — maps class names to metadata
const classInfo = {
  ClassName: {
    file: "path/to/ClassName.java",
    methods: ["method1()", "method2()"],
    responsibility: "One-line description of what this class does",
  },
};

function showClassInfo(name) {
  // Show a fixed-position popup with file path, methods, responsibility
  // Position near the cursor or centered
}
```

---

## Tab 1: Pipeline

SVG flow diagram with clickable steps, entity type highlighting, and a detail sidebar.

### HTML Skeleton

```html
<div id="tab-pipeline" class="tab-panel active" style="flex-direction: row;">
  <div class="pipeline-svg-container">
    <svg id="pipeline-svg" viewBox="0 0 1100 550"></svg>
  </div>
  <div class="pipeline-detail" id="pipeline-detail">
    <h3>Step Details</h3>
    <div class="detail-empty">Click a step to see details</div>
  </div>
</div>
```

### JS Data Structures

```js
const pipelineSteps = [
  {
    id: "step-id", // Unique identifier
    x: 20,
    y: 60, // SVG position
    w: 160,
    h: 52, // SVG dimensions
    title: "Step Name", // Display title
    desc: "Short description",
    entities: ["entityA", "entityB"], // Which entity types flow through
    detail: {
      input: "InputType",
      output: "OutputType",
      methods: ["perform()", "validate()"],
      file: "path/to/StepClass.java",
      description: "What this step does in detail.",
    },
  },
];

const pipelineConnections = [
  {
    from: "step-id-1",
    to: "step-id-2",
    entities: ["entityA", "entityB"], // Which entities flow along this edge
  },
];
```

### Rendering

- `buildPipelineSVG()` iterates `pipelineConnections` first (draw behind), then `pipelineSteps`
- Each step is an SVG `<g class="step-node">` with `<rect>` + `<text>` elements
- Connections are dashed animated lines (`stroke-dasharray: 8 4`, `@keyframes dashFlow`)
- Clicking a step calls `selectPipelineStep(stepId)` which populates the detail sidebar
- Entity toggling dims steps/connections that don't include the active entity

### Detail Sidebar Sections

```html
<div class="detail-section">
  <div class="detail-label">INPUT</div>
  <div class="detail-value">InputType</div>
</div>
<div class="detail-section">
  <div class="detail-label">OUTPUT</div>
  <div class="detail-value">OutputType</div>
</div>
<div class="detail-section">
  <div class="detail-label">METHODS</div>
  <div class="detail-value"><code>perform()</code></div>
</div>
<div class="detail-section">
  <div class="detail-label">FILE</div>
  <div class="detail-value">
    <span class="file-path">path/to/File.java</span>
  </div>
</div>
<div class="detail-section">
  <div class="detail-label">DESCRIPTION</div>
  <div class="detail-value">Detailed explanation of what this step does.</div>
</div>
```

---

## Tab 2: Tracer

Step-by-step trace through the pipeline per entity type. Vertical timeline on the left, detail area in the middle, data model sidebar on the right.

### HTML Skeleton

```html
<div id="tab-tracer" class="tab-panel" style="flex-direction: row;">
  <div class="tracer-timeline" id="tracer-timeline">
    <!-- Vertical dot timeline, built by JS -->
  </div>
  <div class="tracer-main" id="tracer-main">
    <div class="tracer-controls">
      <button class="tracer-ctrl-btn" onclick="tracerPrev()">Prev</button>
      <button
        class="tracer-ctrl-btn"
        id="tracer-play-btn"
        onclick="tracerPlay()"
      >
        Play
      </button>
      <button class="tracer-ctrl-btn" onclick="tracerNext()">Next</button>
      <span class="tracer-step-label" id="tracer-step-label">Step 1 of N</span>
    </div>
    <div id="tracer-content">
      <!-- Current step detail rendered here -->
    </div>
  </div>
  <div class="tracer-sidebar" id="tracer-sidebar">
    <!-- Data model view rendered here -->
  </div>
</div>
```

### JS Data Structures

```js
// Shared steps that appear in every entity's trace
const sharedSteps = [
  {
    title: "Step title",
    detail: "HTML description of what happens",
    outcome: "info", // 'info' | 'pass' | 'warn' | 'drop'
    outcomeText: "LABEL", // Short badge text
    modelKey: "modelName", // Key into dataModels{} for sidebar
    dataFlow: {
      // Optional — shown as input→output badge
      input: "InputType",
      output: "OutputType",
    },
  },
];

// Per-entity trace steps (entity-specific prefix + shared steps)
const tracerData = {
  entityA: [
    {
      title: "Entity A arrives",
      detail: "...",
      outcome: "info",
      outcomeText: "RECEIVED",
      modelKey: "inputEvent",
    },
    {
      title: "Field check",
      detail: "...",
      outcome: "pass",
      outcomeText: "PASS",
    },
    ...sharedSteps,
  ],
  entityB: [
    {
      title: "Entity B arrives",
      detail: "...",
      outcome: "info",
      outcomeText: "RECEIVED",
      modelKey: "inputEvent",
    },
    ...sharedSteps,
  ],
};

// Data models shown in the sidebar when a step references one
const dataModels = {
  inputEvent: {
    title: "InputEvent",
    proto: true, // Optional flag for proto-based models
    fields: [
      { name: "fieldName", type: "string" },
      {
        name: "nested",
        type: "NestedType",
        children: [{ name: "childField", type: "int32" }],
      },
    ],
  },
};
```

### Rendering

- Timeline dots: numbered circles with states `active` (blue glow), `completed` (green), `dropped` (red)
- `renderTracerStep()` populates the content area with:
  - Outcome badge (colored by outcome type)
  - Title and HTML detail
  - Optional fields list (subscribed fields for the current entity)
  - Optional data flow badge (input → output)
- `renderDataModel(modelKey)` populates the sidebar with a tree view of the model's fields
- Play button auto-advances with `setInterval` (1.5s per step), toggles to Pause

### Outcome Badge Colors

| Outcome | Color  | Use for                                  |
| ------- | ------ | ---------------------------------------- |
| `info`  | blue   | Informational steps (fetch, emit, build) |
| `pass`  | green  | Validation passed, check succeeded       |
| `warn`  | orange | Fallback triggered, discrepancy detected |
| `drop`  | red    | Event dropped, processing stopped        |

---

## Tab 3: Comparison

Side-by-side output format tables with field mappings. Useful when a component produces multiple output formats (V4/V5, REST/gRPC, old/new schema).

### HTML Skeleton

```html
<div
  id="tab-comparison"
  class="tab-panel"
  style="flex-direction: column; padding: 20px 30px;"
>
  <div class="comparison-header">
    <h3>Output Format Comparison</h3>
    <p class="comparison-subtitle">
      Side-by-side field mapping between output formats
    </p>
  </div>
  <div id="comparison-content">
    <!-- Built by buildComparisonTab() -->
  </div>
</div>
```

### JS Data Structures

The comparison tab reuses `fieldIndex{}` from the Impact tab. For each field, it shows how the field maps to each output format.

```js
// Built dynamically from fieldIndex
// Each row: source field | Format A output | Format B output | warnings
function buildComparisonTab() {
  // Group fields by entity type
  // For each entity, build a table:
  //   Source Field | Format A (converter, method, output, note) | Format B (same)
  // Add warning badges where gotchas exist
  // Add "Key Differences" callout section at the top
}
```

### Table Structure

```js
function buildMappingTable(headers, rows, entityTags) {
  // headers: ['Source Field', 'Format A', 'Format B']
  // rows: [{ field, formatA: {converter, method, output, note}, formatB: {...}, gotcha? }]
  // entityTags: which entity types are relevant to this table
  // Returns HTML string
}
```

### Key Differences Callout

At the top of the comparison content, show a highlighted box listing the most important divergences between formats. These come from fields in `fieldIndex` that have a `gotcha` property.

```html
<div class="key-differences">
  <h4>Key Differences</h4>
  <div class="diff-item">
    <span class="diff-badge warn">DIVERGENT</span>
    <strong>fieldName</strong> — explanation of the difference
  </div>
</div>
```

### Entity Highlighting

When an entity is toggled, tables for other entity types fade (`.dimmed`). Rows tagged with the active entity get highlighted borders.

---

## Tab 4: Impact

Field reverse lookup, gotcha cards, and dependency chains. The "if I change X, what breaks?" tab.

### HTML Skeleton

```html
<div
  id="tab-impact"
  class="tab-panel"
  style="flex-direction: column; padding: 20px 30px;"
>
  <div id="impact-content">
    <!-- Built by buildImpactTab() -->
  </div>
</div>
```

### JS Data Structures

```js
// Field reverse lookup — maps source fields to their output locations
const fieldIndex = {
  fieldName: {
    entity: "EntityType",
    cascadesToChildren: true, // Does changing this field trigger child re-processing?
    formatA: [
      {
        converter: "ConverterClassName",
        method: "methodName()",
        output: "OutputType.fieldName",
        note: "How the field is transformed",
      },
    ],
    formatB: [{ converter: "...", method: "...", output: "...", note: "..." }],
    sideProjections: ["ProjectionName"], // Optional
    gotcha: "Warning text if this field has non-obvious behavior", // Optional
  },
};

// Gotcha cards — non-obvious behaviors
const gotchas = [
  {
    severity: "high", // 'high' | 'medium' | 'low'
    title: "Short description",
    location: "ClassName.java:lineNum",
    detail: "HTML explanation of the gotcha",
    impact: "What happens if you miss this",
    tested: false, // Whether this behavior has test coverage
  },
];

// Dependency chains — fields that trigger cascading effects
const dependencyChains = [
  {
    field: "FIELD_NAME",
    impact:
      "Description of the cascade: what gets re-fetched, re-computed, re-published",
  },
];
```

### Rendering: `buildImpactTab()`

The Impact tab has 3 sections:

**1. Field Lookup** (top)

- Dropdown/select listing all fields from `fieldIndex`
- On selection, `renderFieldLookup(fieldKey)` shows:
  - Entity type and cascade indicator
  - Table of converters per output format
  - Side projection list (if any)
  - Gotcha warning (if any)

**2. Gotcha Cards** (middle)

- Cards sorted by severity (high first)
- Each card shows: severity badge, title, location (file:line), detail, impact, tested indicator
- Severity colors: high=red, medium=orange, low=yellow

**3. Dependency Chains** (bottom)

- Table or card list showing fields that trigger cascading re-processing
- Each entry: field name, cascade description

### Entity Highlighting

When an entity is toggled:

- Field lookup dropdown filters to fields for that entity
- Gotcha cards not related to the entity fade
- Dependency chains highlight entries relevant to the entity

---

## Tab 5: FAQ

Interactive decision tree and accordion Q&A for common debugging questions.

### HTML Skeleton

```html
<div
  id="tab-faq"
  class="tab-panel"
  style="flex-direction: column; padding: 20px 30px;"
>
  <div id="faq-content">
    <!-- Built by buildFAQ() -->
  </div>
</div>
```

### JS Rendering: `buildFAQ()`

Two sections:

**1. Decision Tree** — "Why didn't X happen?"

- Interactive flowchart using nested divs (not SVG)
- Each node is a question with yes/no branches
- Leaf nodes are answers (green for "expected", red for "bug", orange for "edge case")
- Entity-specific trees highlighted when entity is toggled

```js
function buildFaqDecisionTree() {
  // Returns HTML string with nested question nodes
  // Structure: question → yes/no → question or leaf
  // CSS handles indentation and branch lines
}

// Question node
function faqQ(id, text) {
  return `<div class="faq-q" id="faq-${id}" onclick="toggleFaqQ('${id}')">
    <span class="faq-arrow">&#9654;</span> ${text}
  </div>
  <div class="faq-branch" id="faq-branch-${id}" style="display:none;">`;
}

// Leaf node (answer)
function faqLeaf(text, cls) {
  // cls: 'expected' (green), 'bug' (red), 'edge-case' (orange)
  return `<div class="faq-leaf faq-leaf-${cls}">${text}</div>`;
}
```

**2. Accordion Q&A** — Common questions

- Collapsible sections with question titles
- Answers contain HTML with code snippets, class references, and links

```js
function toggleFaqAccordion(id) {
  const el = document.getElementById("faq-acc-" + id);
  el.style.display = el.style.display === "none" ? "block" : "none";
}
```

### Decision Tree CSS

```css
.faq-q {
  cursor: pointer;
  padding: 8px 12px;
  margin: 4px 0;
  border-radius: 6px;
  background: var(--bg-tertiary);
  color: var(--text-primary);
  font-size: 13px;
}

.faq-branch {
  margin-left: 24px;
  border-left: 2px solid var(--border);
  padding-left: 16px;
}

.faq-leaf {
  padding: 8px 12px;
  margin: 4px 0;
  border-radius: 6px;
  font-size: 13px;
}

.faq-leaf-expected {
  background: var(--green-dim);
  color: var(--green);
  border: 1px solid var(--green);
}
.faq-leaf-bug {
  background: var(--red-dim);
  color: var(--red);
  border: 1px solid var(--red);
}
.faq-leaf-edge-case {
  background: var(--orange-dim);
  color: var(--orange);
  border: 1px solid var(--orange);
}
```

### Entity Highlighting

When an entity is toggled, FAQ sections tagged with `data-entity` attributes get highlighted/dimmed.

---

## Adapting Patterns to Different Domains

The tab patterns work beyond pipeline architectures. Here's how to adapt each tab:

### Pipeline Tab → Flow Diagram

Whatever the architecture, the Pipeline tab shows **the overall flow**:

- **Request handler**: HTTP request → middleware chain → handler → response
- **ETL**: Extract stages → Transform stages → Load stages
- **Event processor**: Event source → routing → handlers → output

Replace `pipelineSteps` with whatever the ordered processing stages are. Replace `entities` with whatever the variant types are (request types, record types, event types).

### Tracer Tab → Lifecycle Trace

The Tracer shows **one specific type's journey** through the flow:

- **Request handler**: Trace a specific request type through all middleware
- **ETL**: Trace a specific record type through all transforms
- **Event processor**: Trace a specific event type through routing and handling

The `tracerData` keys become whatever the variant types are. `sharedSteps` captures processing common across all variants.

### Comparison Tab → Format Comparison

The Comparison tab shows **equivalent outputs side by side**:

- **Request handler**: REST response vs gRPC response for the same data
- **ETL**: Old schema vs new schema for the same record
- **Event processor**: Output event format A vs format B

If there's only one output format, this tab can compare input vs output, or show the transform mapping.

### Impact Tab → Change Analysis

Works identically for any domain. The `fieldIndex` maps source fields to their output locations. `gotchas` and `dependencyChains` are universal.

### FAQ Tab → Debugging Guide

Works identically. Decision trees answer "why didn't X happen?" for whatever X means in this domain.
