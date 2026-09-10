#!/usr/bin/env python3
"""
NODO Design System Generator
Extrae componentes de nodo-design-system5.html y genera documentación completa
con estructura Material Design 3 (sidebar + tabs + 7 secciones por componente)
"""

import json
import re
from pathlib import Path
from html import escape
from typing import Dict, List, Any

# Ruta de salida
OUTPUT_DIR = Path("/Users/JCCX-IBK/Documents/jccxdsgnops.github.io")
COMPONENTS_JSON_DIR = OUTPUT_DIR / "design-system" / "components"
V5_FILE = Path("/Users/JCCX-IBK/Downloads/nodo-design-system5.html")

# Template base para cada sección de componente
COMPONENT_TEMPLATE = """
<section id="comp-{slug}" class="component-page" style="display:none">
  <div class="page-header">
    <h1>{name}</h1>
    <p class="lead">{description}</p>
    <div class="component-meta">
      <span class="badge badge-status">{status}</span>
      <span class="badge badge-category">{category}</span>
      <span class="badge badge-variants">{variant_count} variants</span>
    </div>
  </div>

  <!-- Tabs -->
  <div class="tabs-header">
    <button class="tab-btn active" onclick="switchTab(this, '{slug}', 'overview')">Overview</button>
    <button class="tab-btn" onclick="switchTab(this, '{slug}', 'anatomy')">Anatomy</button>
    <button class="tab-btn" onclick="switchTab(this, '{slug}', 'specs')">Specs</button>
    <button class="tab-btn" onclick="switchTab(this, '{slug}', 'behavior')">Behavior</button>
    <button class="tab-btn" onclick="switchTab(this, '{slug}', 'guidelines')">Guidelines</button>
    <button class="tab-btn" onclick="switchTab(this, '{slug}', 'accessibility')">Accessibility</button>
    <button class="tab-btn" onclick="switchTab(this, '{slug}', 'code')">Code</button>
  </div>

  <!-- TAB 1: Overview -->
  <div id="tab-{slug}-overview" class="tab-content active">
    <h2>Purpose</h2>
    <p>{purpose_summary}</p>
    
    <h3>When to use</h3>
    <ul>
      {when_to_use}
    </ul>
    
    <h3>When NOT to use</h3>
    <ul>
      {when_not_to_use}
    </ul>

    <div class="preview-block">
      <h3>Visual Preview</h3>
      {preview_html}
    </div>
  </div>

  <!-- TAB 2: Anatomy -->
  <div id="tab-{slug}-anatomy" class="tab-content">
    <h2>Anatomy</h2>
    <p>This component is composed of the following parts:</p>
    <table class="anatomy-table">
      <thead>
        <tr><th>#</th><th>Part ID</th><th>Name</th><th>Required</th><th>Description</th><th>Contains</th></tr>
      </thead>
      <tbody>
        {anatomy_rows}
      </tbody>
    </table>
    <div class="anatomy-diagram">{anatomy_diagram}</div>
  </div>

  <!-- TAB 3: Specs -->
  <div id="tab-{slug}-specs" class="tab-content">
    <h2>Specifications</h2>
    
    <h3>Base Specs (default state)</h3>
    <table class="specs-table">
      <thead>
        <tr><th>Part</th><th>Property</th><th>Token / Value</th><th>Resolved</th></tr>
      </thead>
      <tbody>
        {specs_rows}
      </tbody>
    </table>

    <h3>Variants</h3>
    <div class="variants-list">
      {variants_section}
    </div>

    <h3>Sizing</h3>
    <table class="sizing-table">
      <thead>
        <tr><th>Size</th><th>Dimensions</th><th>Padding</th><th>Gap</th></tr>
      </thead>
      <tbody>
        {sizing_rows}
      </tbody>
    </table>
  </div>

  <!-- TAB 4: Behavior -->
  <div id="tab-{slug}-behavior" class="tab-content">
    <h2>Behavior & Interaction</h2>
    
    <h3>Interaction Model</h3>
    <p><strong>Type:</strong> {interaction_model}</p>
    
    <h3>States & State Layers</h3>
    <table class="states-table">
      <thead>
        <tr><th>State</th><th>Trigger</th><th>Visual Delta</th><th>Motion</th></tr>
      </thead>
      <tbody>
        {states_rows}
      </tbody>
    </table>

    <h3>Gestures</h3>
    <ul>
      {gestures_list}
    </ul>

    <h3>Motion & Easing</h3>
    <ul>
      {motion_list}
    </ul>
  </div>

  <!-- TAB 5: Guidelines -->
  <div id="tab-{slug}-guidelines" class="tab-content">
    <h2>Usage Guidelines</h2>
    
    <div class="do-dont-grid">
      <div class="do-card">
        <h3>✓ Do</h3>
        <ul>
          {do_list}
        </ul>
      </div>
      <div class="dont-card">
        <h3>✗ Don't</h3>
        <ul>
          {dont_list}
        </ul>
      </div>
    </div>

    <h3>Content Guidelines</h3>
    <p>{content_guidelines}</p>
  </div>

  <!-- TAB 6: Accessibility -->
  <div id="tab-{slug}-accessibility" class="tab-content">
    <h2>Accessibility</h2>
    
    <h3>Semantic Role</h3>
    <p><code>role="{aria_role}"</code></p>
    
    <h3>Keyboard Support</h3>
    <table class="keyboard-table">
      <thead>
        <tr><th>Key</th><th>Action</th></tr>
      </thead>
      <tbody>
        {keyboard_rows}
      </tbody>
    </table>

    <h3>ARIA Attributes</h3>
    <ul>
      {aria_list}
    </ul>

    <h3>Focus Management</h3>
    <p>{focus_management}</p>

    <h3>Contrast Ratios (WCAG 2.1 AA)</h3>
    <table class="contrast-table">
      <thead>
        <tr><th>Color Pair</th><th>Ratio</th><th>Minimum</th><th>Pass</th></tr>
      </thead>
      <tbody>
        {contrast_rows}
      </tbody>
    </table>

    <h3>Screen Reader</h3>
    <p>{screenreader_info}</p>
  </div>

  <!-- TAB 7: Code -->
  <div id="tab-{slug}-code" class="tab-content">
    <h2>Implementation</h2>
    
    <h3>HTML Structure</h3>
    <pre><code class="language-html">{html_code}</code></pre>

    <h3>CSS (uses only design tokens)</h3>
    <pre><code class="language-css">{css_code}</code></pre>

    <h3>Usage Example</h3>
    <pre><code class="language-html">{usage_example}</code></pre>
  </div>
</section>
"""

def extract_component_list(html_file: Path) -> List[Dict[str, str]]:
    """Extrae lista de componentes de v5.html"""
    content = html_file.read_text()
    
    # Buscar todos los comp-detail-*
    pattern = r'id="comp-detail-([^"]+)"'
    matches = re.findall(pattern, content)
    
    components = []
    for match in matches:
        components.append({
            "id": match,
            "slug": match.replace("_", "-")
        })
    
    return list(dict.fromkeys(components))  # Remover duplicados

def load_component_spec(component_id: str) -> Dict[str, Any]:
    """Carga especificación JSON si existe, sino retorna template vacío"""
    spec_file = COMPONENTS_JSON_DIR / f"{component_id}.json"
    
    if spec_file.exists():
        return json.loads(spec_file.read_text())
    
    # Template por defecto (vacío, necesita ser llenado)
    return {
        "identity": {
            "id": component_id,
            "name": component_id.replace("-", " ").title(),
            "status": "stable",
            "category": "generic"
        },
        "purpose": {
            "summary": "Component documentation pending...",
            "whenToUse": ["To be documented"],
            "whenNotToUse": []
        },
        "anatomy": {"parts": []},
        "variants": {"list": []},
        "specs": {},
        "states": {"list": []},
        "behavior": {},
        "guidelines": {"do": [], "dont": []},
        "accessibility": {"role": "article"},
        "code": {"html": "", "css": ""}
    }

def render_component_section(comp_id: str, spec: Dict[str, Any]) -> str:
    """Renderiza una sección de componente con todas sus tabs"""
    
    # Extraer datos de la especificación
    identity = spec.get("identity", {})
    purpose = spec.get("purpose", {})
    anatomy = spec.get("anatomy", {})
    specs = spec.get("specs", {})
    states = spec.get("states", {})
    behavior = spec.get("behavior", {})
    guidelines = spec.get("guidelines", {})
    accessibility = spec.get("accessibility", {})
    code = spec.get("code", {})
    
    # Renderizar secciones
    anatomy_rows = render_anatomy_rows(anatomy.get("parts", []))
    specs_rows = render_specs_rows(specs.get("base", {}))
    states_rows = render_states_rows(states.get("list", []))
    keyboard_rows = render_keyboard_rows(accessibility.get("keyboard", []))
    contrast_rows = render_contrast_rows(accessibility.get("contrast", []))
    
    when_to_use = "\n".join(f"<li>{escape(item)}</li>" for item in purpose.get("whenToUse", []))
    when_not_to_use = "\n".join(f"<li>{escape(item)}</li>" for item in purpose.get("whenNotToUse", []))
    do_list = "\n".join(f"<li>{escape(item)}</li>" for item in guidelines.get("do", []))
    dont_list = "\n".join(f"<li>{escape(item)}</li>" for item in guidelines.get("dont", []))
    aria_list = "\n".join(f"<li><code>{escape(attr)}</code></li>" for attr in accessibility.get("ariaAttributes", []))
    
    return COMPONENT_TEMPLATE.format(
        slug=identity.get("id", comp_id),
        name=escape(identity.get("name", comp_id.title())),
        description=escape(purpose.get("summary", "Pending documentation")),
        status=identity.get("status", "stable"),
        category=identity.get("category", "generic"),
        variant_count=len(spec.get("variants", {}).get("list", [])),
        purpose_summary=escape(purpose.get("summary", "")),
        when_to_use=when_to_use,
        when_not_to_use=when_not_to_use,
        anatomy_rows=anatomy_rows,
        anatomy_diagram="[Diagram placeholder]",
        specs_rows=specs_rows,
        variants_section=render_variants(spec.get("variants", {})),
        sizing_rows=render_sizing_rows(),
        interaction_model=states.get("interactionModel", "activatable"),
        states_rows=states_rows,
        gestures_list="<li>Pending documentation</li>",
        motion_list="<li>Pending documentation</li>",
        do_list=do_list,
        dont_list=dont_list,
        content_guidelines="To be documented",
        aria_role=accessibility.get("role", "article"),
        keyboard_rows=keyboard_rows,
        aria_list=aria_list,
        focus_management="To be documented",
        contrast_rows=contrast_rows,
        screenreader_info="To be documented",
        html_code=escape(code.get("html", "<div>HTML pending</div>")),
        css_code=escape(code.get("css", ".component { /* CSS pending */ }")),
        usage_example=escape(code.get("usage", "<!-- Usage example pending -->"))
        preview_html=get_preview_visual(comp_id)
    )

def render_anatomy_rows(parts: List[Dict]) -> str:
    """Renderiza filas de anatomía"""
    rows = []
    for part in parts:
        rows.append(f"""
        <tr>
            <td>{part.get('index', '—')}</td>
            <td><code>{part.get('id', '—')}</code></td>
            <td>{part.get('name', '—')}</td>
            <td>{'✓' if part.get('required', False) else '○'}</td>
            <td>{escape(part.get('description', '—'))}</td>
            <td>{', '.join(part.get('contains', []))}</td>
        </tr>
        """)
    return "\n".join(rows) if rows else "<tr><td colspan='6'>Anatomy pending documentation</td></tr>"

def render_specs_rows(specs: Dict) -> str:
    """Renderiza filas de especificaciones"""
    rows = []
    for part_id, props in specs.items():
        if isinstance(props, dict):
            for prop, value in props.items():
                rows.append(f"""
                <tr>
                    <td><code>{part_id}</code></td>
                    <td>{prop}</td>
                    <td><code>{value}</code></td>
                    <td>Resolving...</td>
                </tr>
                """)
    return "\n".join(rows) if rows else "<tr><td colspan='4'>Specs pending documentation</td></tr>"

def render_states_rows(states: List[Dict]) -> str:
    """Renderiza filas de estados"""
    rows = []
    for state in states:
        rows.append(f"""
        <tr>
            <td><strong>{state.get('id', '—')}</strong></td>
            <td>{escape(state.get('trigger', '—'))}</td>
            <td><code>{json.dumps(state.get('delta', {}))}</code></td>
            <td>{state.get('motion', '—')}</td>
        </tr>
        """)
    return "\n".join(rows) if rows else "<tr><td colspan='4'>States pending documentation</td></tr>"

def render_keyboard_rows(keyboard: List[Dict]) -> str:
    """Renderiza filas de teclado"""
    rows = []
    for item in keyboard:
        rows.append(f"""
        <tr>
            <td><kbd>{item.get('key', '—')}</kbd></td>
            <td>{escape(item.get('action', '—'))}</td>
        </tr>
        """)
    return "\n".join(rows) if rows else "<tr><td colspan='2'>Keyboard support pending documentation</td></tr>"

def render_contrast_rows(contrast: List[Dict]) -> str:
    """Renderiza filas de contraste"""
    rows = []
    for pair in contrast:
        ratio = pair.get('ratio', 0)
        minimum = pair.get('minimum', 4.5)
        passed = "✓" if ratio >= minimum else "✗"
        rows.append(f"""
        <tr>
            <td>{escape(pair.get('pair', '—'))}</td>
            <td>{ratio:.1f}:1</td>
            <td>{minimum:.1f}:1</td>
            <td>{passed}</td>
        </tr>
        """)
    return "\n".join(rows) if rows else "<tr><td colspan='4'>Contrast audit pending</td></tr>"

def render_variants(variants: Dict) -> str:
    """Renderiza sección de variantes"""
    variant_list = variants.get("list", [])
    if not variant_list:
        return "<p>Variants pending documentation</p>"
    
    html = '<div class="variants-cards">'
    for variant in variant_list:
        html += f"""
        <div class="variant-card">
            <h4>{escape(variant.get('name', '—'))}</h4>
            <p>{escape(variant.get('description', '—'))}</p>
        </div>
        """
    html += '</div>'
    return html

def render_sizing_rows() -> str:
    """Renderiza filas de tamaño (placeholder)"""
    return "<tr><td colspan='4'>Sizing specifications pending documentation</td></tr>"

def get_preview_visual(comp_id: str) -> str:
    """Retorna HTML de preview visual (placeholder)"""
    return f'<div class="preview-placeholder">Visual preview for <code>{comp_id}</code> pending</div>'

def generate_master_html(components: List[Dict]) -> str:
    """Genera HTML maestro con sidebar + componentes"""
    
    # Generar nav sidebar
    nav_html = generate_sidebar_nav(components)
    
    # Generar secciones de componentes
    component_sections = []
    for comp in components:
        spec = load_component_spec(comp["id"])
        section_html = render_component_section(comp["id"], spec)
        component_sections.append(section_html)
    
    # Template HTML base
    base_template = Path("/Users/JCCX-IBK/Documents/jccxdsgnops.github.io/nodo-design-system.html").read_text()
    
    # TODO: Insertar nav y sections en la posición correcta
    
    return f"""<!-- Generated master HTML with all {len(components)} components -->"""

def generate_sidebar_nav(components: List[Dict]) -> str:
    """Genera navegación del sidebar"""
    nav = '<nav class="sidebar"><div class="sidebar-nav">'
    
    # Agrupar por categoría
    categories = {}
    for comp in components:
        spec = load_component_spec(comp["id"])
        category = spec.get("identity", {}).get("category", "generic")
        if category not in categories:
            categories[category] = []
        categories[category].append(comp)
    
    # Renderizar grupos
    for category, comps in sorted(categories.items()):
        nav += f'''
        <div class="nav-section">
            <button class="cat-toggle" onclick="toggleNavSection(this)">
                {category.replace("-", " ").title()} <span class="chev">▼</span>
            </button>
            <div class="nav-items">
        '''
        for comp in sorted(comps, key=lambda x: x["id"]):
            nav += f'<a href="#comp-{comp["slug"]}" class="nav-item" onclick="navigateTo(event, \'comp-{comp["slug"]}\')">{comp["id"].replace("-", " ").title()}</a>'
        nav += '</div></div>'
    
    nav += '</div></nav>'
    return nav

# MAIN
if __name__ == "__main__":
    print("🚀 NODO Design System Generator")
    print("================================\n")
    
    # Paso 1: Extraer componentes de v5
    print("📋 Extrayendo componentes de v5.html...")
    components = extract_component_list(V5_FILE)
    print(f"   ✓ Encontrados {len(components)} componentes")
    
    # Paso 2: Verificar specs JSON existentes
    print("\n📂 Verificando especificaciones JSON existentes...")
    existing_specs = list(COMPONENTS_JSON_DIR.glob("*.json"))
    print(f"   ✓ {len(existing_specs)} especificaciones documentadas")
    print(f"   ⚠ {len(components) - len(existing_specs)} necesitan documentación")
    
    # Paso 3: Generar HTML maestro
    print("\n🔧 Generando HTML integrado...")
    master_html = generate_master_html(components)
    
    output_file = OUTPUT_DIR / "nodo-design-system-complete.html"
    output_file.write_text(master_html)
    print(f"   ✓ Guardado en {output_file}")
    
    print("\n✅ Generación completada")
    print(f"   - {len(components)} componentes")
    print(f"   - 7 tabs por componente")
    print(f"   - Estructura Material Design 3")
    print(f"   - Pronto push a GitHub")

