# ADF (Atlassian Document Format) Reference

The atlassian-mcp `edit_ticket` tool wraps the `description` parameter in a single ADF paragraph, losing all formatting. To get formatted descriptions, pass raw ADF JSON via the `custom_fields` parameter instead.

## How to Write Formatted Descriptions

Use `edit_ticket` with:

- `issue_key`: the Jira key
- `custom_fields`: a JSON string containing `{"description": {ADF doc}}`
- Do NOT set the `description` parameter (it triggers the broken plain-text wrapper)

## ADF Node Reference

### Document wrapper (required)

```json
{"type": "doc", "version": 1, "content": [...]}
```

### Heading

```json
{
  "type": "heading",
  "attrs": { "level": 2 },
  "content": [{ "type": "text", "text": "Title" }]
}
```

### Paragraph

```json
{
  "type": "paragraph",
  "content": [{ "type": "text", "text": "Body text here." }]
}
```

### Bullet list

```json
{
  "type": "bulletList",
  "content": [
    {
      "type": "listItem",
      "content": [
        {
          "type": "paragraph",
          "content": [{ "type": "text", "text": "Item 1" }]
        }
      ]
    },
    {
      "type": "listItem",
      "content": [
        {
          "type": "paragraph",
          "content": [{ "type": "text", "text": "Item 2" }]
        }
      ]
    }
  ]
}
```

### Hyperlink

```json
{
  "type": "text",
  "text": "link text",
  "marks": [{ "type": "link", "attrs": { "href": "https://example.com" } }]
}
```

Place inside a paragraph's content array alongside other text nodes.

### Inline card (smart link — use sparingly)

```json
{ "type": "inlineCard", "attrs": { "url": "https://example.com" } }
```

Renders as a resolved card chip. Prefer hyperlinks for most cases.

### Italic text

```json
{ "type": "text", "text": "italic text", "marks": [{ "type": "em" }] }
```

### Bold text

```json
{ "type": "text", "text": "bold text", "marks": [{ "type": "strong" }] }
```

### Horizontal rule

```json
{ "type": "rule" }
```

### Empty line (spacing)

```json
{ "type": "paragraph", "content": [] }
```

## Conversion Rules

When converting the epic summary to ADF:

1. Each `## Heading` becomes a heading node with level 2
2. Each paragraph of text becomes a paragraph node
3. Each `- item` becomes a listItem inside a bulletList
4. Each `[text](url)` becomes a text node with a link mark
5. The disclaimer becomes italic text in a paragraph after a rule
6. Multiple consecutive bullet items go into ONE bulletList node
7. Any Jira key mentioned in text (e.g. CONACCESS-18) becomes a hyperlink
   text node with href `https://jira.spotify.net/browse/{KEY}` — do NOT leave Jira keys as plain text
