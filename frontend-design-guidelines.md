# Frontend Design Guidelines for NSTV

## Design Philosophy
- **Modern & Clean**: Professional interface with smooth animations and gradients
- **Consistent**: All pages follow the same design language
- **User-Friendly**: Clear visual hierarchy, intuitive navigation, immediate feedback
- **No Clutter**: Removed pagination for simpler browsing experience

## Color Palette

### CSS Variables (Defined in base.html)
```css
--primary-color: #667eea      /* Purple - main brand color */
--primary-dark: #5a67d8        /* Darker purple for hover states */
--secondary-color: #764ba2     /* Deep purple - gradient end */
--success-color: #48bb78       /* Green for success messages */
--warning-color: #ed8936       /* Orange for warnings */
--error-color: #f56565         /* Red for errors */
--info-color: #4299e1          /* Blue for info messages */
--bg-color: #f7fafc            /* Light gray background */
--card-bg: #ffffff             /* White for cards/tables */
--text-primary: #2d3748        /* Dark gray for headings */
--text-secondary: #4a5568      /* Medium gray for body text */
--border-color: #e2e8f0        /* Light gray for borders */
```

### Primary Gradient
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```
**Usage**: Navigation bar, buttons, headings, active states

## Typography

### Font Family
```css
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
```

### Font Sizes
- **Page Headers**: 2.5rem - 3rem (40-48px)
- **Section Titles**: 1.8rem (28.8px)
- **Card Titles**: 1.5rem (24px)
- **Body Text**: 1rem (16px)
- **Small Text**: 0.85rem - 0.9rem (13.6-14.4px)

### Font Weights
- **Headings**: 700 (bold)
- **Subheadings**: 600 (semi-bold)
- **Buttons/Labels**: 500-600 (medium to semi-bold)
- **Body**: 400 (regular)

### Gradient Text for Headers
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
-webkit-background-clip: text;
-webkit-text-fill-color: transparent;
background-clip: text;
```

## Layout Components

### Container
```html
<div class="container">
  <!-- Max-width: 1400px, centered, 20px padding -->
</div>
```

### Page Header Pattern
```html
<div class="page-header">
    <h1>🎬 Page Title</h1>
    <p>Brief description of page purpose</p>
</div>
```

### Card Pattern
```html
<div class="card">
    <div class="card-title">Card Title</div>
    <!-- Content -->
</div>
```
**Properties**: White background, 12px border-radius, box-shadow, 24px padding

### Action Container Pattern
```html
<div class="action-container">
    <h4>📁 Section Title</h4>
    <button class="plex-action-btn">
        <span id="btn-text">🎬 Action</span>
        <span id="btn-spinner" style="display:none;">⏳ Loading...</span>
    </button>
    <p>Helpful description of what this action does</p>
</div>
```

## Button Styles

### Primary Button
```html
<button class="button">📥 Action Text</button>
```
**Styling**:
- Gradient background (primary → secondary)
- White text, 600 weight
- 12px vertical, 28px horizontal padding
- 8px border-radius
- Box shadow with hover transform
- Smooth transitions (0.3s ease)

### Plex Action Button
```html
<button class="plex-action-btn">Action</button>
```
**Usage**: File movement, sync operations
**Styling**: Similar to primary but larger (14px/32px padding, 10px radius)

### Button States
- **Hover**: `translateY(-2px)` + increased shadow
- **Active**: `translateY(0)`
- **Disabled**: Gray background (#cbd5e0), no shadow, `cursor: not-allowed`

### Loading State Pattern
```javascript
$("#btn").click(function() {
    let btn = $(this);
    btn.prop('disabled', true);
    $('#btn-text').hide();
    $('#btn-spinner').show();
    
    // ... AJAX call ...
    
    // On error:
    btn.prop('disabled', false);
    $('#btn-text').show();
    $('#btn-spinner').hide();
});
```

## Tables

### Structure
```css
table {
    width: 100%;
    background: white;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 6px rgba(0,0,0,0.07);
}
```

### Headers
- Gradient background (primary → secondary)
- White text, 600 weight
- 16px padding
- Uppercase, 0.5px letter-spacing
- Font size: 0.85rem

### Rows
- 14px vertical, 16px horizontal padding
- Light border between rows
- Hover effect: `background-color: #f7fafc`
- No border on last row

## Forms

### Form Container
```html
<div class="card" style="max-width: 600px; margin: 0 auto;">
    <form>
        <!-- Form fields -->
    </form>
</div>
```

### Input Fields
```css
input[type="text"],
input[type="number"],
select,
textarea {
    width: 100%;
    padding: 12px 16px;
    border: 2px solid var(--border-color);
    border-radius: 8px;
    font-size: 15px;
    transition: border-color 0.3s ease;
    margin-bottom: 16px;
}
```

### Focus State
```css
:focus {
    outline: none;
    border-color: var(--primary-color);
}
```

### Labels
```css
label {
    display: block;
    margin-bottom: 8px;
    font-weight: 500;
    color: var(--text-primary);
}
```

### Checkboxes
For grid layouts:
```html
<div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px;">
    <div style="display: flex; align-items: center; gap: 8px;">
        <input type="checkbox" id="option" style="width: auto; margin: 0;">
        <label for="option" style="margin: 0; cursor: pointer;">🎬 Label</label>
    </div>
</div>
```

## Messages / Alerts

### Django Messages Pattern
```html
{% if messages %}
<ul class="messages">
    {% for message in messages %}
    <li class="{{ message.tags }}">{{ message }}</li>
    {% endfor %}
</ul>
{% endif %}
```

### Message Types
- **`.success`**: Green (#d4edda), left border (#48bb78)
- **`.error`**: Red (#f8d7da), left border (#f56565)
- **`.warning`**: Yellow (#fff3cd), left border (#ed8936)
- **`.info`**: Blue (#d1ecf1), left border (#4299e1)

### Styling
- 16px vertical, 20px horizontal padding
- 8px border-radius
- 4px left border for type indication
- Slide-in animation (0.3s ease)
- Box shadow

## Navigation Bar

### Structure
```html
<div id="navbar">
    <ul>
        <li><a href="/">🏠 Home</a></li>
        <li><a href="/shows_index">📺 Shows</a></li>
        <!-- etc -->
    </ul>
</div>
```

### Styling
- Gradient background
- Sticky positioning (`position: sticky; top: 0; z-index: 1000`)
- Centered flex layout
- 18px vertical, 24px horizontal padding per link
- 3px transparent bottom border
- Hover: Semi-transparent white background + visible bottom border

## Icons

### Emoji Usage
Use relevant emoji icons consistently across the site:
- 🏠 Home
- 📺 TV Shows / Episodes
- 🎬 Movies
- ➕ Add
- 🔍 Search / Missing
- 📥 Import / Download
- 📁 Files
- ⏳ Loading
- ✓ Success
- 👥 Cast
- 🎭 Cast Member

## Special Components

### Collapsible Cast Section (show.html)
```html
<button type="button" class="collapsible" id="cast-toggle">
    👥 View Cast ({{ count }})
</button>
<div class="content" id="cast-content">
    <div class="cast-grid">
        <!-- Grid of cast cards -->
    </div>
</div>
```

**Cast Grid**: `grid-template-columns: repeat(auto-fill, minmax(150px, 1fr))`

**Cast Card**:
- White background
- 16px padding
- 12px border-radius
- Image: 150px height, object-fit: cover
- Hover: `translateY(-4px)` + enhanced shadow

### Collapsible Toggle Script
```javascript
document.getElementById('cast-toggle')?.addEventListener('click', function() {
    this.classList.toggle('active');
    let content = document.getElementById('cast-content');
    content.classList.toggle('show');
});
```

## Animations & Transitions

### Standard Transition
```css
transition: all 0.3s ease;
```

### Button Hover
```css
transform: translateY(-2px);
box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
```

### Message Slide-In
```css
@keyframes slideIn {
    from {
        transform: translateY(-20px);
        opacity: 0;
    }
    to {
        transform: translateY(0);
        opacity: 1;
    }
}
```

### Collapsible Content
```css
transition: max-height 0.3s ease;
max-height: 0;      /* Collapsed */
max-height: 2000px; /* Expanded */
```

## Responsive Design

### Container Max-Width
- 1400px for main content
- 800px for search forms
- 600px for add show/movie forms

### Grid Layouts
Use `repeat(auto-fill, minmax(...))` for responsive grids:
```css
/* Cast members */
grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));

/* Checkboxes */  
grid-template-columns: repeat(2, 1fr);
```

## Template Inheritance

### All pages extend base.html
```django
{% extends "base.html" %}
{% block content %}
<!-- Page content -->
{% endblock %}
```

### Do NOT include in child templates
- `<!DOCTYPE html>` (already in base.html)
- `<html>`, `<head>`, `<body>` tags
- jQuery script tag
- CSS reset/normalize

## AJAX Pattern

### Standard Form with CSRF
```javascript
$("#button").click(function() {
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            let cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                let cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    let csrf_token = getCookie('csrftoken');
    
    $.ajax({
        type: "POST",
        url: "/endpoint",
        headers: {"X-CSRFToken": csrf_token},
        success: function(data) {
            location.reload();
        },
        error: function(xhr, status, error) {
            alert('Error: ' + (xhr.responseJSON?.message || 'Operation failed'));
        }
    });
});
```

## Utility Classes

```css
.text-center { text-align: center; }

.mb-1 { margin-bottom: 8px; }
.mb-2 { margin-bottom: 16px; }
.mb-3 { margin-bottom: 24px; }
.mb-4 { margin-bottom: 32px; }

.mt-1 { margin-top: 8px; }
.mt-2 { margin-top: 16px; }
.mt-3 { margin-top: 24px; }
.mt-4 { margin-top: 32px; }
```

## Page-Specific Notes

### Shows Index / Movies Index
- Remove pagination (show all items)
- Order shows alphabetically by title
- Include file management action container at top

### Show Detail Page
- Large gradient title
- Action buttons for TVDB import and missing episodes
- Collapsible cast section with grid layout
- Episodes table ordered by season/episode number

### Missing Episodes
- Back button to return to show page
- Show name in page header

### Search Page
- Checkbox grid for filters (2 columns)
- Result cards with hover effects
- Icons for each result type

### Add Show / Add Movie
- Centered form card (max 600px)
- Full-width submit button

## Common Patterns to Avoid

### ❌ Don't Use
- Inline `<center>` tags (use CSS instead)
- Multiple `<html>`, `<head>`, `<body>` tags in child templates
- Hardcoded colors (use CSS variables)
- Alert popups for messages (use Django messages framework)
- Old-style button elements without classes

### ✓ Do Use
- Flexbox/Grid for layouts
- CSS classes and variables
- Django template inheritance
- Toast-style messages with auto-dismiss
- Consistent spacing with utility classes
- Semantic HTML5 elements
- Loading states for async operations

## Design Checklist for New Pages

- [ ] Extends base.html
- [ ] Has page-header with icon and description
- [ ] Uses CSS variables for colors
- [ ] Includes CSRF token in forms
- [ ] Buttons have hover/disabled states
- [ ] Tables use gradient headers
- [ ] Messages display via messages framework
- [ ] Icons are consistent with site theme
- [ ] Loading states for async operations
- [ ] Responsive max-widths on containers
- [ ] No hardcoded colors or fonts
- [ ] Follows existing component patterns

## Future Enhancements to Consider

- Dark mode toggle
- Mobile hamburger menu
- Poster image galleries
- Filtering/sorting on index pages
- Keyboard shortcuts
- Progressive web app features
- Image lazy loading
- Skeleton loading states
