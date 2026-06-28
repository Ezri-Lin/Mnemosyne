# HTML Output Patterns (from The Body Keeps the Score)

> Concrete HTML/CSS/JS patterns used in the reference output.
> Copy and fill data — do NOT restructure.

## Index Page (web/index.html)

### 1. CSS Theme (warm-paper)

```css
:root {
  --ink: #171411; --muted: #6d6258;
  --paper: #f8f2e7; --paper-deep: #ece1cf;
  --line: #d8c8af; --red: #b9422f;
  --blue: #245f73; --green: #4d6f48; --gold: #c2872d;
  --white: #fffaf0;
  --shadow: 0 18px 50px rgba(55,38,19,.14);
  --font-body: "Songti SC","Noto Serif CJK SC",Georgia,serif;
  --font-display: "PingFang SC","Microsoft YaHei",sans-serif;
  --bg: radial-gradient(circle at 22% 12%,rgba(194,135,45,.18),transparent 28rem),
        linear-gradient(135deg,#fbf6ec 0%,#efe1ca 100%);
  --surface: rgba(255,250,240,.62);
  --surface-strong: rgba(255,250,240,.72);
  --bar-bg: rgba(248,242,231,.95);
  --ink-soft: #3d332b;
  --ink-soft-2: #44392f;
  --must: #b9422f; --should: #c2872d; --skip: #6d6258;
}
```

### 2. Hero Section

```html
<div class="hero">
  <div>
    <p class="eyebrow">GOD'S-EYE ARCHITECTURE</p>
    <h1>{{ book_title }}</h1>
    <p class="lede">{{ one_sentence_summary }}</p>
  </div>
  <aside class="thesis">
    <strong>THESIS</strong>
    <span>{{ thesis_text }}</span>
  </aside>
</div>
```

### 3. Chapter Navigation Bar

```html
<nav class="ch-nav">
  <a href="chapters/ch04-slug.html">
    <span class="ch-num">Ch 4</span>
    <span class="ch-en">{{ title_en }}</span>
    <span class="ch-zh">{{ title_zh }}</span>  <!-- if exist -->
  </a>
  <!-- repeat per high-value chapter -->
</nav>
```

### 4. Cluster Cards

```html
<div class="cluster">
  <span class="cluster-label">{{ CLUSTER_LABEL }}</span>
  <p class="cluster-why">{{ cluster_reason }}</p>
  <div class="cluster-ch">
    <span class="ch-num">Ch {{ n }}</span>
    <div class="ch-info">
      <span class="ch-title-en">{{ title_en }}</span>
      <span class="ch-title-zh">{{ title_zh }}</span>
    </div>
    <a class="ch-link" href="chapters/chNN-slug.html">Open →</a>
  </div>
  <!-- repeat per chapter in cluster -->
</div>
```

### 5. Heatmap

```html
<h2 class="section-title">Chapter Value Heatmap</h2>
<div class="heatmap">
  {{ # each chapter }}
  <div class="hm-cell hm-{{ density_class }}" title="{{ tooltip }}">
    <span class="hm-num">{{ ch_number }}</span>
    <span class="hm-short">{{ short_title }}</span>
  </div>
</div>
<div class="heatmap-legend">
  <span class="lg"><span class="sw" style="background:var(--must)"></span>必读</span>
  <span class="lg"><span class="sw" style="background:var(--should)"></span>精读</span>
  <span class="lg"><span class="sw" style="background:var(--paper-deep)"></span>选读/跳读</span>
</div>
```

### 6. Concept Map

```html
<table class="concept-table">
  {{ # each concept }}
  <tr>
    <td class="ct-name">{{ concept_name }}</td>
    <td class="ct-q">{{ core_question }}</td>
    <td class="ct-ch">{{ comma-separated chapter numbers }}</td>
  </tr>
</table>
```

### 7. Grading Matrix

Full table repeating the Phase 2 grading data with links to chapter detail pages.

---

## Chapter Detail Page (web/chapters/chNN-slug.html)

### 8. Subtab System

```html
<div class="subtabs">
  <button class="subtab" aria-selected="true" data-panel="s1">Overview</button>
  <button class="subtab" data-panel="s2">Causal Chain</button>
  <button class="subtab" data-panel="s3">Frameworks</button>
  <button class="subtab" data-panel="s4">Cases</button>
  <button class="subtab" data-panel="s5">Research+Rules</button>
</div>

<div id="s1" class="panel" role="tabpanel"><!-- Overview content --></div>
<div id="s2" class="panel" role="tabpanel" hidden><!-- Causal Chain --></div>
<!-- ... -->
```

```javascript
// Subtab switching
document.querySelectorAll('.subtab').forEach(function(btn) {
  btn.addEventListener('click', function() {
    document.querySelectorAll('.subtab').forEach(function(b) { b.setAttribute('aria-selected','false'); });
    this.setAttribute('aria-selected','true');
    document.querySelectorAll('.panel').forEach(function(p) { p.hidden = true; });
    document.getElementById(this.dataset.panel).hidden = false;
  });
});
```

### 9. Source Drawer

```html
<div class="drawer-backdrop" hidden></div>
<div class="drawer" hidden>
  <button class="drawer-close">×</button>
  <div class="drawer-content">
    <h3 id="drawer-title">{{ passage_title }}</h3>
    <blockquote id="drawer-text">{{ passage_text }}</blockquote>
  </div>
</div>
```

Each "src ↗" chip links to a passage:
```html
<a class="src-chip" onclick="openDrawer('ch_key')">src ↗</a>
```

```javascript
var passages = {
  "ch_key": { title: "Ch N · Topic", text: "Original passage..." }
};
function openDrawer(key) {
  var p = passages[key];
  if (!p) return;
  document.getElementById('drawer-title').textContent = p.title;
  document.getElementById('drawer-text').textContent = p.text;
  document.querySelector('.drawer').hidden = false;
  document.querySelector('.drawer-backdrop').hidden = false;
}
document.querySelector('.drawer-close').onclick = function() {
  document.querySelector('.drawer').hidden = true;
  document.querySelector('.drawer-backdrop').hidden = true;
};
```

### 10. Overview Tab — Note Cards Grid

```html
<div class="overview-grid">
  <div class="note-card">
    <strong class="nc-label">{{ label }}</strong>
    <p class="nc-text">{{ point }}</p>
  </div>
  <!-- repeat 6-8 cards per chapter -->
</div>
```

### 11. Causal Chain — Steps

```html
<div class="causal-chain">
  <div class="cc-step">
    <span class="cc-num">{{ n }}</span>
    <div class="cc-card">
      <p>{{ step_description }}</p>
    </div>
  </div>
  <!-- repeat -->
</div>
```

### 12. Frameworks — Accordion

```html
<div class="fw-item">
  <button class="fw-header" onclick="this.parentElement.classList.toggle('open')">
    {{ framework_name }}
  </button>
  <div class="fw-body">
    <p>{{ description }}</p>
    <ol>{{ # each step }}<li>{{ step }}</li>{{ /each }}</ol>
  </div>
</div>
```

### 13. Cases — Story Cards

```html
<div class="story-card">
  <p class="sc-text">{{ case_story }}</p>
  <a class="src-chip" onclick="openDrawer('source_key')">src ↗</a>
</div>
```

### 14. Research Timeline + Decision Rules

```html
<!-- Timeline -->
<div class="tl-item">
  <span class="tl-year">{{ year }}</span>
  <p class="tl-text">{{ finding }}</p>
</div>

<!-- Decision Rules -->
<ul class="dr-list">
  <li><strong>Rule:</strong> {{ rule }}<br><em>Why:</em> {{ rationale }}</li>
</ul>

<!-- Key Takeaways -->
<ul class="kt-list">
  <li>{{ takeaway }}</li>
</ul>
```

---

## File Naming

- Index: `web/index.html`
- Chapters: `web/chapters/chNN-<slug>.html` (NN = zero-padded chapter number)
- Chapter number must match the order in the index's cluster cards
- All internal links: relative paths (`./chapters/chNN-slug.html`, `../index.html`)
