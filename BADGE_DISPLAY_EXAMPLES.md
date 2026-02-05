# META Dashboard Badge Display - Before & After

## Before Implementation
```
┌─────────────────────────────────────┐
│ Name: John Smith                     │
│ Phone: 555-1234                      │
│ Created: 2 hours ago                 │
│                                      │
│ ID: #345                             │ ← Shows database ID
└─────────────────────────────────────┘
```

## After Implementation
```
┌─────────────────────────────────────┐
│ Name: John Smith                     │
│ Phone: 555-1234                      │
│ Created: 2 hours ago                 │
│                                      │
│ 2021 or later                        │ ← Shows driver license answer
│ (indigo badge)                       │
└─────────────────────────────────────┘
```

## Badge Display Logic

```javascript
if (lead.isManual || lead.is_manual) {
    // Manual leads show yellow badge
    badge = "Manual Lead" (yellow)
} 
else if (lead.driver_license_received) {
    // Leads with question answer show indigo badge
    badge = lead.driver_license_received (indigo)
    Examples: "2021 or later", "2020 or before"
} 
else {
    // Fallback to ID for leads without the answer
    badge = "ID: #123" (slate)
}
```

## Badge Styling

### When Answer is Provided
```css
text-[10px] font-semibold mt-1 px-2 py-1 rounded border w-fit ml-7
text-indigo-700 bg-indigo-50 border-indigo-200
```
- Font: Semi-bold, small text
- Color: Indigo text on light indigo background
- Appearance: Professional, easily readable

### When No Answer (Fallback to ID)
```css
text-[10px] font-mono mt-1 px-1.5 py-0.5 rounded border w-fit ml-7
text-slate-400 bg-slate-50 border-slate-100
```
- Font: Monospace (computer-like feel for IDs)
- Color: Slate gray (subtle, de-emphasized)
- Appearance: Fallback appearance when needed

### Manual Leads
```css
text-[10px] font-bold mt-1 px-2 py-1 rounded border w-fit ml-7
bg-yellow-100 text-yellow-700 border-yellow-300
```
- Color: Yellow (indicates manual entry)
- Font: Bold (stands out)
- Appearance: Clearly distinguishes from auto leads

## Real-World Examples on Dashboard

### Example 1: Auto Insurance Lead with Answer
```
┌──────────────────────────┐
│ Alice Johnson            │
│ (555) 123-4567          │
│ 3 days ago              │
│ 2021 or later           │ ← Driver license answer
└──────────────────────────┘
```

### Example 2: Another Auto Insurance Lead
```
┌──────────────────────────┐
│ Bob Williams             │
│ (555) 234-5678          │
│ 1 day ago               │
│ 2020 or before          │ ← Different answer
└──────────────────────────┘
```

### Example 3: Manual Entry
```
┌──────────────────────────┐
│ Charlie Brown            │
│ (555) 345-6789          │
│ 5 hours ago             │
│ Manual Lead             │ ← Yellow badge
└──────────────────────────┘
```

### Example 4: No Answer (Fallback)
```
┌──────────────────────────┐
│ Diana Davis              │
│ (555) 456-7890          │
│ 2 hours ago             │
│ ID: #789                │ ← Shows ID as fallback
└──────────────────────────┘
```

## Visual Hierarchy
The indigo answer badge stands out more than the slate ID fallback, making leads with quality data (those who answered the question) more visually prominent.

This encourages leads that complete the full form to be more visible in your workflow.
