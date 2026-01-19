# UI Mockup - Paste Server

Visual reference for the chat-like interface.

---

## Full Layout

```
┌──────────────────────────────────────────────────────────────────┐
│  [☰]  Paste Dumps                      [+ New Dump]  [🌙]  [🔒] │ ← Top Bar
├─────────────────┬────────────────────────────────────────────────┤
│                 │                                                │
│   SIDEBAR       │              MAIN READING AREA                 │
│                 │                                                │
│ [Search...]     │  ┌──────────────────────────────────────────┐ │
│                 │  │  Just pasted some code from phone        │ │
│ Today           │  │                                          │ │
│ ┣━ 14:32  ✓     │  │  function hello() {                      │ │ ← Latest paste
│ ┣━ 14:15        │  │    console.log("Hi");                    │ │   (selected)
│ ┗━ 13:05        │  │  }                                       │ │
│                 │  │                                          │ │
│ Yesterday       │  │  Created: Today at 14:32                 │ │
│ ┣━ 23:15        │  │  [📋 Copy]  [🗑️ Delete]                  │ │
│ ┣━ 19:42        │  └──────────────────────────────────────────┘ │
│ ┗━ 18:10        │                                                │
│                 │                                                │
│ Jan 18          │                                                │
│ ┣━ 16:20        │                                                │
│ ┣━ 12:33        │                                                │
│ ┗━ 09:15        │                                                │
│                 │                                                │
│ Jan 17          │                                                │
│ ┣━ 22:05        │                                                │
│ ┗━ 14:30        │                                                │
│                 │                                                │
│ [Load More...]  │                                                │
│                 │                                                │
└─────────────────┴────────────────────────────────────────────────┘
```

---

## Sidebar Detail

### Light Mode
```
┌───────────────────┐
│ [🔍 Search...]    │
├───────────────────┤
│                   │
│ Today       ▼     │  ← Collapsible
│ ┣━ 14:32  ✓       │  ← Selected (checkmark)
│ ┃  Just pasted... │  ← Preview (30 chars)
│ ┣━ 14:15          │
│ ┃  Shopping list  │
│ ┗━ 13:05          │
│    Bug fix code   │
│                   │
│ Yesterday   ▼     │
│ ┣━ 23:15          │
│ ┃  Meeting notes  │
│ ┣━ 19:42          │
│ ┃  API endpoint   │
│ ┗━ 18:10          │
│    Random idea    │
│                   │
└───────────────────┘
```

### Dark Mode
```
┌───────────────────┐
│ [🔍 Search...]    │  Background: #1e1e1e
├───────────────────┤  Text: #e0e0e0
│                   │
│ Today       ▼     │
│ ┣━ 14:32  ✓       │  Selected: #2d2d2d highlight
│ ┃  Just pasted... │
│ ┣━ 14:15          │
│ ┃  Shopping list  │
│ ┗━ 13:05          │
│    Bug fix code   │
│                   │
└───────────────────┘
```

---

## Main Area Detail

### Single Paste View
```
┌────────────────────────────────────────────┐
│                                            │
│  ┌────────────────────────────────────┐   │
│  │                                    │   │
│  │  [Paste Content]                   │   │
│  │                                    │   │
│  │  Line 1 of paste                   │   │
│  │  Line 2 of paste                   │   │
│  │  ...                               │   │
│  │                                    │   │
│  │  Lots of vertical space            │   │
│  │  for comfortable reading           │   │
│  │                                    │   │
│  └────────────────────────────────────┘   │
│                                            │
│  Created: Today at 14:32                   │
│  [📋 Copy to Clipboard]  [🗑️ Delete]       │
│                                            │
└────────────────────────────────────────────┘
```

### Multi-Paste View (Future)
```
┌────────────────────────────────────────────┐
│                                            │
│  ┌────────────────────────────────────┐   │
│  │  Latest paste content              │   │
│  └────────────────────────────────────┘   │
│  Today at 14:32  [📋 Copy]  [🗑️ Delete]    │
│                                            │
│  ─────────────────────────────────────────│
│                                            │
│  ┌────────────────────────────────────┐   │
│  │  Previous paste content            │   │
│  └────────────────────────────────────┘   │
│  Today at 14:15  [📋 Copy]  [🗑️ Delete]    │
│                                            │
│  ─────────────────────────────────────────│
│                                            │
│  ┌────────────────────────────────────┐   │
│  │  Earlier paste content             │   │
│  └────────────────────────────────────┘   │
│  Today at 13:05  [📋 Copy]  [🗑️ Delete]    │
│                                            │
└────────────────────────────────────────────┘
```

---

## "New Dump" Modal

```
                ┌─────────────────────────────────┐
                │  New Dump               [✕]    │
                ├─────────────────────────────────┤
                │                                 │
                │  ┌─────────────────────────┐  │
                │  │                         │  │
                │  │  Type or paste text     │  │
                │  │  here...                │  │
                │  │                         │  │
                │  │                         │  │
                │  │                         │  │
                │  └─────────────────────────┘  │
                │                                 │
                │          [Cancel]  [Save]       │
                └─────────────────────────────────┘
```

**Overlay**: Semi-transparent dark background
**Modal**: Centered, white (light) or dark gray (dark mode)
**Textarea**: Auto-focus on open

---

## Mobile Layout

### Portrait (Sidebar Hidden)
```
┌──────────────────────────┐
│ [☰] Paste Dumps  [+ New] │
├──────────────────────────┤
│                          │
│   Main Area (Full Width) │
│                          │
│  ┌──────────────────┐   │
│  │  Paste content   │   │
│  └──────────────────┘   │
│                          │
│  [📋 Copy]  [🗑️ Delete]  │
│                          │
└──────────────────────────┘
```

### Sidebar Opened (Overlay)
```
┌──────────────────────────┐
│  [✕] Paste Dumps         │
├────────┬─────────────────┤
│        │                 │
│ Today  │  [Overlay]      │
│ ▸14:32 │                 │
│  14:15 │  Sidebar covers │
│        │  main area      │
│ Yester │                 │
│ ▸23:15 │  Click outside  │
│        │  to close       │
│        │                 │
└────────┴─────────────────┘
```

---

## Color Palette

### Light Mode
```
Background (Primary):   #ffffff
Background (Secondary): #f5f5f5
Sidebar Background:     #fafafa
Text (Primary):         #1a1a1a
Text (Secondary):       #666666
Border:                 #e0e0e0
Accent (Blue):          #007bff
Hover:                  #f0f0f0
Selected:               #e8f4ff
```

### Dark Mode
```
Background (Primary):   #1e1e1e
Background (Secondary): #2d2d2d
Sidebar Background:     #252525
Text (Primary):         #e0e0e0
Text (Secondary):       #a0a0a0
Border:                 #444444
Accent (Blue):          #4a9eff
Hover:                  #333333
Selected:               #2a4a66
```

---

## Interaction States

### Sidebar Item
```
Normal:    Gray background, no highlight
Hover:     Light gray highlight
Selected:  Blue-tinted background, checkmark
```

### Buttons
```
Normal:    Flat, colored text
Hover:     Slight background color
Active:    Darker background
Disabled:  Gray text, no interaction
```

### Modal
```
Opening:   Fade in (200ms)
Closing:   Fade out (200ms)
Overlay:   rgba(0,0,0,0.5) in light mode
           rgba(0,0,0,0.7) in dark mode
```

---

## Typography

### Fonts
```
Body:      -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif
Code:      'Courier New', Courier, monospace
```

### Sizes
```
Heading (Top Bar):     18px, bold
Sidebar Groups:        14px, bold
Sidebar Items:         13px
Paste Content:         16px
Paste Timestamp:       13px, gray
Buttons:               14px
```

---

## Responsive Breakpoints

```
Mobile:    < 768px   (Sidebar overlay)
Tablet:    768-1024px (Sidebar 200px)
Desktop:   > 1024px   (Sidebar 250px)
```

---

## Animations

### Sidebar Toggle
```css
transition: transform 0.3s ease;
```

### Modal
```css
transition: opacity 0.2s ease;
```

### Hover States
```css
transition: background-color 0.15s ease;
```

### Dark Mode Toggle
```css
transition: background-color 0.3s ease, color 0.3s ease;
```

---

## Accessibility

- **Focus states**: Blue outline on keyboard navigation
- **ARIA labels**: All buttons have labels
- **Keyboard shortcuts**:
  - `Ctrl+N`: New dump
  - `Ctrl+K`: Focus search
  - `Escape`: Close modal
  - `↑/↓`: Navigate sidebar
  - `Enter`: Select item
- **Screen reader**: Proper semantic HTML

---

## Inspiration References

**Similar to**:
- ChatGPT (chat.openai.com)
- Claude.ai (claude.ai)
- Discord (sidebar + main area)
- Slack (conversations list)

**Key takeaways**:
- Clean, uncluttered
- Comfortable whitespace
- Easy scanning (grouped dates)
- Single-column reading (main area)
- Familiar patterns (everyone knows this layout)

---

_This mockup guides the implementation. Keep it simple, keep it familiar._
