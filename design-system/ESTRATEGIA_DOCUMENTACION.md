# 📋 Estrategia: Documentación Completa de NODO (128 componentes)

## Estado Actual

### ✅ Tenemos:
1. **nodo-design-system.html (v5)** — HTML maestro con estructura Material Design 3
   - Sidebar con navegación jerárquica
   - 128 componentes organizados en ~15 categorías
   - Tabs centrales (Overview, Specs, Guidelines, Accessibility)
   - Previsualizaciones visuales de algunos componentes

2. **design-system/ framework** — Infraestructura de especificaciones
   - `component.schema.json` — Contrato de documentación (13 secciones, 10 reglas)
   - `card-medium.json` — Ejemplo perfecto (72 variantes, 8 estados, 6 partes)
   - `button.json` — Ejemplo de 480 combinaciones verificables
   - `text-field.json` — Ejemplo de componente editable
   - `build.py` — Validador + generador HTML
   - `ANALISIS_PROFUNDO.md` — Análisis exhaustivo de Material Design 3

### 🔴 Falta:
1. **Especificaciones JSON para 125 componentes** (solo 3 documentados)
2. **Integración HTML ↔ JSON** (hoy son 2 silos separados)
3. **Previsualizaciones visuales completas** (Figma AI)
4. **Contenido detallado en cada sección** (anatomy, states, behavior, etc.)

---

## 🎯 Plan de 4 Fases

### Fase 1: Template Generator (2 horas)
**Automatizar creación de specs JSON para todos los 128 componentes**

```bash
python3 design-system/tools/generate_complete_ds.py \
  --from v5.html \
  --output design-system/components/ \
  --template design-system/schema/component.schema.json
```

**Resultado:** 128 × `component-name.json` con estructura base lista para completar

### Fase 2: Figma AI Preview Generation (1-2 horas)
**Pedir a Figma que genere/exporte previsualizaciones visuales de cada componente**

Opciones:
1. **Opción A:** Usar Figma Plugin API para exportar componentes como PNG/SVG
2. **Opción B:** Usar Figma REST API para obtener URLs de preview
3. **Opción C:** Descarga manual desde Figma → Convertir a base64 → Emb en HTML

Comando que necesitarás (después):
```bash
python3 design-system/tools/embed_figma_previews.py \
  --figma-token YOUR_TOKEN \
  --project-id YOUR_PROJECT_ID \
  --output design-system/dist/previews/
```

### Fase 3: Bulk Documentation (2-3 horas)
**Llenar contenido para cada componente usando patrón de card-medium.json**

Estrategia:
1. Agrupar componentes por tipo (buttons, cards, inputs, etc.)
2. Documentar un "campeón" de cada grupo (e.g., button/primary)
3. Aplicar variaciones para el resto (button/secondary, button/outlined, etc.)
4. Usar template fill-in para minimizar repetición

Template a completar por componente:
```json
{
  "identity": { /* Nombre, versión, status, etc */ },
  "purpose": { /* Qué es, cuándo usarlo */ },
  "anatomy": { /* Partes numeradas */ },
  "variants": { /* Ejes ortogonales */ },
  "specs": { /* Tokens por parte */ },
  "states": { /* Deltas de estado */ },
  "behavior": { /* Interacciones, gestos, motion */ },
  "composition": { /* Slots, cardinalidad, lista blanca */ },
  "guidelines": { /* Do/Don't */ },
  "accessibility": { /* ARIA, keyboard, contraste */ },
  "code": { /* HTML + CSS ejecutable */ }
}
```

### Fase 4: HTML Integration (1-2 horas)
**Conectar JSON specs con HTML maestro**

Script que:
1. Lee cada `component.json`
2. Inyecta contenido en HTML (overview, anatomy, specs, etc.)
3. Genera tabs dinámicas con la información
4. Renderiza tablas de estados, specs, keyboard, contraste
5. Embebe previsualizaciones visuales
6. Genera `nodo-design-system-complete.html`

---

## 📊 Mapa de Componentes (128 total)

### Categorías Principales

```
1. Feedback (8)
   - badge, badge-icon, badge-count, badge-discount
   - progress, loader, skeleton, toast, alert

2. Input (12)
   - text-field, text-area, dropdown, multi-select
   - radio, checkbox, switch, slider
   - date-picker, time-picker, autocomplete, combo-box

3. Navigation (9)
   - navbar, sidebar, breadcrumb, pagination, stepper
   - tabs, bottom-nav, drawer, menu

4. Surface (10)
   - card, sheet, modal, dialog, panel
   - container, section, frame, surface, elevation

5. Action (7)
   - button, icon-button, fab
   - segmented-button, chip, toggle-button, action-chip

6. Display (15)
   - heading, paragraph, label, caption, quote
   - divider, spacer, list, table, grid
   - avatar, icon, image, video, code

7. Selection (6)
   - list-item, data-table, picker, selector
   - radio-group, checkbox-group

8. Temporal (5)
   - date-picker, time-picker, range-picker
   - duration-picker, schedule

9. Communication (8)
   - tooltip, popover, contextual-help, announcement
   - banner, message, chat-bubble, comment

10. Data (9)
    - chart-bar, chart-line, chart-pie, chart-scatter
    - chart-area, gauge, heatmap, tree-map, metric

11. Media (7)
    - image-container, gallery, carousel, lightbox
    - video-player, audio-player, media-grid

12. Pattern (11)
    - form, wizard, dashboard, empty-state, error-state
    - settings, account, profile, notification-center
    - search-results, filter-panel

13. Overlay (6)
    - modal, drawer, popover, menu
    - dropdown, tooltip
```

**Estrategia de priorización:**
- **🔴 Críticos (20-30):** button, card, text-field, dropdown, modal, navbar, badge
- **🟡 Importantes (30-40):** switch, chips, progress, list-item, tabs, breadcrumb
- **🟢 Complementarios (rest):** charts, media, patterns, temporales

---

## 💡 Cómo Completar (Paso a Paso)

### Para cada componente:

1. **Copia template**
   ```bash
   cp design-system/components/card-medium.json \
      design-system/components/COMPONENT-NAME.json
   ```

2. **Rellena identity + purpose** (5 min)
   ```json
   "identity": {
     "id": "component-name",
     "name": "Component Name",
     "category": "categoria",
     "status": "stable",
     "version": "1.0.0",
     "m3Equivalent": "MD3 component or null"
   },
   "purpose": {
     "summary": "Brief one-liner",
     "whenToUse": [...],
     "whenNotToUse": [...]
   }
   ```

3. **Documenta anatomy** (10 min)
   - Mira el componente en Figma
   - Identifica partes numeradas
   - Documenta cardinality y style

4. **Documenta specs** (10 min)
   - Tokens: --nodo-primary, --radius-md, etc.
   - Propiedades: background, foreground, elevation, gap, etc.
   - Resueltos: 16px, 12px, etc.

5. **Documenta states** (10 min)
   - Copia deltas de M3 o Material Design 3 spec
   - default, hover, focus-visible, pressed, disabled
   - Para editable: focused, error
   - Para selectable: selected

6. **Documenta guidelines** (10 min)
   - Do: 3-5 buenas prácticas
   - Don't: 3-5 anti-patrones

7. **Documenta accessibility** (10 min)
   - role: button, article, option, etc.
   - ARIA: aria-label, aria-pressed, aria-disabled, etc.
   - keyboard: Tab, Enter, Space, Arrow keys
   - Contraste: medido automáticamente por build.py

8. **Valida con build.py** (2 min)
   ```bash
   python3 design-system/tools/build.py validate \
     --component design-system/components/COMPONENT-NAME.json
   ```

**Total por componente: 60 minutos aprox**  
**Para 128: ~128 horas = 3-4 semanas con 1 dev FT**

---

## 🛠 Herramientas Disponibles

### 1. **build.py** — Validador + Generador
```bash
# Validar un componente
python3 design-system/tools/build.py validate \
  --component design-system/components/button.json

# Generar HTML renderizado
python3 design-system/tools/build.py render \
  --output dist/components.html

# Validar TODO + generar
python3 design-system/tools/build.py all
```

**Detecta automáticamente:**
- ✅ Campos obligatorios faltantes
- ✅ Tokens inválidos (no existen en sistema)
- ✅ Violaciones WCAG 2.1 AA
- ✅ Variantes no contables desde ejes
- ✅ Slots sin cardinalidad

### 2. **component.schema.json** — Validador JSON Schema
```bash
# Validar contra schema
python3 -m jsonschema \
  --instance design-system/components/button.json \
  design-system/schema/component.schema.json
```

### 3. **generate_complete_ds.py** — Generator (WIP)
Automatiza:
- Lectura de v5.html
- Extracción de componentes
- Generación de JSON templates
- Inyección en HTML maestro

---

## 📈 Roadmap Realista

| Semana | Tarea | Horas | Resultado |
|---|---|---|---|
| **Semana 1** | Fase 1 + Figma API | 8 | 128 templates JSON + previews |
| **Semana 2-3** | Fase 3 (bulk docs) | 40 | 128 componentes documentados |
| **Semana 3-4** | Fase 4 (HTML integration) | 8 | HTML maestro integrado |
| **Semana 4** | QA + refinamiento | 4 | Push final |

**Total: ~60 horas de trabajo**

---

## 🎁 Con Todo Listo, un Agente Podrá:

```python
# Agente pregunta al Design System

# 1. "¿Qué es un Button?"
-> Respuesta: identity + purpose + m3Equivalent

# 2. "Genera un botón primary large"
-> Respuesta: HTML + CSS con tokens correctos
-> Automáticamente: accessible, con keyboard support, responsive

# 3. "¿Qué estados tiene?"
-> Respuesta: tabla de 8 estados con deltas medibles
-> Automáticamente: hover (opacity 0.08), pressed (scale 0.995), etc.

# 4. "¿Puedo meter un icon dentro?"
-> Respuesta: Sí, slot "icon" cardinalidad 0..1, tipos permitidos: [SVG, component]

# 5. "¿WCAG AA?"
-> Respuesta: Ratios de contraste medidos ✓✓✓ (todos pass)

# 6. "Código"
-> Respuesta: HTML + CSS ejecutable, solo con tokens
```

---

## ✨ Siguiente Paso: ¿Empezamos?

Opciones:

### **Opción A:** Yo hago Fase 1 + 2 (Template Gen + Figma API)
- Creas los 128 templates JSON vacíos automáticamente
- Exportas previsualizaciones desde Figma
- **Tiempo: 2-3 horas**
- **Resultado: Estructura lista para llenar**

### **Opción B:** Yo hago TODO (Fases 1-4)
- Genero templates + integración HTML completa
- Relleno 80% con patrón de Material Design 3
- Dejas pendiente solo los casos especiales
- **Tiempo: 24-32 horas**
- **Resultado: 100% funcional mañana**

### **Opción C:** Divido trabajo conmigo
- Yo: Fase 1 (templates) + Fase 4 (integration)
- Tú/Equipo: Fase 3 (documentación específica con patrón)
- Figma AI: Fase 2 (previsualizaciones)
- **Tiempo: 1 semana con async work**
- **Resultado: 128 componentes documentados**

¿Cuál prefieres? 🚀

