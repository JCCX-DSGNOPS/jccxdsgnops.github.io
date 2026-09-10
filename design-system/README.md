# 🎨 NODO Design System — 10 Componentes Críticos

## 🏠 **[OPEN DESIGN SYSTEM →](dist/index.html)**

**Único punto de entrada:** Un home central con sidebar navigation + 7 tabs por componente.

```
design-system/
├── dist/
│   └── index.html                ⭐ MAIN HOME (navegación + 10 componentes)
├── components/                   JSON specifications (10 componentes)
├── schema/component.schema.json  JSON Schema validator
├── nodo-architecture.json        System architecture + roadmap
└── tools/build.py                Validator
```

## Comandos

```bash
cd design-system
python3 tools/build.py validate                              # aplica el checklist C01–C25
python3 tools/build.py render                                # genera dist/components.html
python3 tools/build.py render --standalone --out dist/preview.html   # página previsualizable
python3 tools/build.py all                                   # valida y genera
```

`validate` devuelve exit code 1 si hay errores, por lo que sirve como gate de CI.

---

## 1. El principio

> Un componente está documentado cuando un agente puede reconstruirlo sin acceso al diseño.

La documentación actual de NODO describe componentes. Este framework los **especifica**.
La diferencia está en tres cosas que hoy faltan:

| Falta hoy | Consecuencia | Cómo lo resuelve el contrato |
|---|---|---|
| Anatomía | No se sabe de qué partes se compone | `anatomy.parts[]` numeradas, con `required` y `cardinality` |
| Deltas de estado | «hover/elevated» no dice qué cambia | `states.list[].delta` = mapa parte → propiedad → token |
| Tokens por elemento | «usa `--primary`» no dice dónde | `specs.base` = mapa parte → propiedad → token |

## 2. Las 13 secciones

| # | Sección | Obligatoria | Responde |
|---|---|:---:|---|
| 1 | `identity` | ✅ | Cómo se llama en cada sistema, qué versión y quién lo mantiene |
| 2 | `purpose` | ✅ | Para qué existe, cuándo usarlo y con qué sustituirlo si no aplica |
| 3 | `anatomy` | ✅ | De qué partes está hecho y cuáles son obligatorias |
| 4 | `variants` | ✅ | Qué formas nombradas existen y qué override aplica cada una |
| 5 | `specs` | ✅ | Qué token exacto tiene cada propiedad de cada parte |
| 6 | `states` | ✅ | Qué cambia visualmente en cada estado, como delta |
| 7 | `behavior` | ✅ | Cómo responde a la interacción, al gesto y al tiempo |
| 8 | `composition` | ✅ | Qué acepta dentro (slots) y con qué props se configura |
| 9 | `responsive` | ⬜ | Cómo se adapta por breakpoint |
| 10 | `guidelines` | ✅ | Do/Don't accionables y reglas de contenido con ejemplos |
| 11 | `accessibility` | ✅ | Rol, teclado, foco, lector de pantalla y contraste medido |
| 12 | `code` | ✅ | Implementación de referencia ejecutable, solo con tokens |
| 13 | `related` | ⬜ | Relaciones, alternativas y gobierno |

Estas 13 secciones se renderizan en **7 pestañas**: Overview · Anatomy · Specs ·
Behavior · Guidelines · Accessibility · Code.

## 3. Las 10 reglas deterministas

1. **R1** Toda propiedad visual se expresa como token. Sin token, no hay documentación.
2. **R2** Cada parte declara `id`, `name`, `required` y su mapa completo de propiedades.
3. **R3** Cada estado se declara como **delta sobre `default`**, nunca en prosa.
4. **R4** Cada variante declara su override exacto respecto de la base.
5. **R5** `variantCount` debe ser **calculable** desde los ejes, no declarado a mano.
6. **R6** Cada slot declara tipo aceptado, cardinalidad y lista blanca de componentes.
7. **R7** Cada interacción declara trigger, resultado, duración y easing.
8. **R8** Todo componente interactivo declara rol ARIA, tab stops, teclas y nombre accesible.
9. **R9** El bloque `code` es HTML+CSS ejecutable que solo usa tokens del sistema.
10. **R10** Ningún componente se publica sin superar el checklist.

## 4. `interactionModel`: qué estados son obligatorios

No todos los componentes tienen los mismos estados. Un input no tiene `pressed`.
El campo `states.interactionModel` determina qué exige el validador:

| Modelo | Estados obligatorios | Ejemplos |
|---|---|---|
| `activatable` | hover, focus-visible, pressed, disabled | button, card, chip |
| `editable` | hover, focused, error, disabled | text-field, text-area, search |
| `selectable` | hover, focus-visible, selected, disabled | check-radio, switch, tabs |
| `static` | — | divider, gradients, status-bars |

## 5. Convención de state layers

Adoptada de Material Design 3 y hoy ausente en NODO. El color del state layer es
**siempre el foreground de la variante**:

| Estado | Opacidad |
|---|---|
| hover | 0.08 |
| focus-visible | 0.10 |
| pressed | 0.10 |
| dragged | 0.16 |
| disabled — contenedor | 0.12 |
| disabled — contenido | 0.38 |

## 6. Checklist de completitud (C01–C25)

Implementado en `tools/build.py`. Los `error` bloquean; los `warning` son deuda visible.

| Grupo | Checks |
|---|---|
| identity | C01 |
| purpose | C02 |
| anatomy | C03 índices contiguos · C04 parte obligatoria |
| variants | C05 overrides explícitos · **C06 variantCount = producto de ejes** |
| specs | C07 cobertura de partes · **C08 sin literales** · C09 measurements |
| states | C10 estados del modelo · **C11 todo estado tiene delta** · C12 disabled 12/38 |
| behavior | C13 motion completo · C14 reduced-motion |
| composition | C15 slots tipados · C16 props con default |
| responsive | C17 breakpoints o `fluid` |
| guidelines | C18 ≥2 do y ≥2 dont · C19 ejemplo bueno y malo |
| accessibility | C20 rol y teclado · **C21 contraste medido en light Y dark** · C22 touch target |
| code | C23 snippet solo con tokens · C24 ARIA presente en el snippet |
| governance | C25 owner, lastReview, related |

## 7. Ejemplos de referencia

| Archivo | Qué demuestra |
|---|---|
| [components/card-medium.json](components/card-medium.json) | Anatomía compleja de 8 partes, slots con lista blanca, gestos, container transform |
| [components/button.json](components/button.json) | Matriz de variantes verificable (4×5×3×4×2 = 480), state layers, tiers de tamaño |
| [components/text-field.json](components/text-field.json) | Modelo `editable`, validación, mensajería accesible con `role="alert"` |

## 8. Hallazgos del análisis del sistema actual

Detalle completo en [nodo-architecture.json](nodo-architecture.json) → `documentationArchitecture.diagnostico`.

**Críticos**
- **D1** El contenido de las 128 fichas está plantillado: la tabla de `Sizing` es idéntica
  en Button y en Card (xSmall 32dp … xLarge 64dp), aunque una Card no tiene altura fija.
- **D2** No existe anatomía. «Anatomy Index» es un inventario, no una descomposición.
- **D3** No hay preview renderizado ni código de referencia.
- **Motion** solo existe en el CSS del sitio de documentación, no como foundation.
- **Layout** no existe: cero breakpoints, cero grid, cero comportamiento responsive.
- Falta la **capa de component tokens** (`md.comp.*`), que es justamente la que aporta
  el determinismo que un agente necesita.

**Deuda de contraste detectada por el validador** (real, sobre la paleta actual):

| Par | Tema | Ratio | Mínimo |
|---|---|---|---|
| `--outline` sobre `--surface` | light | 2.6:1 | 3.0:1 |
| `--outline-high` sobre `--surface` | light | 1.3:1 | 3.0:1 |
| `--on-surface-low` sobre `--surface-container-low` | light | 2.6:1 | 4.5:1 |

`--on-surface-low` se usa hoy como color de subhead y de placeholder: no alcanza AA
para texto. `--outline-high` no alcanza el mínimo de elementos no textuales, lo que
afecta al borde en reposo de todos los campos de formulario.

## 9. Cómo añadir un componente

```bash
cp components/card-medium.json components/mi-componente.json
# editar; el $schema da autocompletado y validación en VS Code
python3 tools/build.py validate
python3 tools/build.py render --standalone --out dist/preview.html
```

## 10. Roadmap

1. **Cerrar foundations** — publicar Motion, Layout e Interaction States; completar los
   pares `on-*` que faltan (warning, info, plin, complementary).
2. **Introducir component tokens** — `nodo.comp.<component>.<element>.<property>.<state>`.
3. **Migrar los 128 componentes** al contrato y sustituir las specs plantilladas.
4. **Automatizar** — generación desde JSON, validación en CI y verificación del
   `variantCount` contra la librería de Figma.
