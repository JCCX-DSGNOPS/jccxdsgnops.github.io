#!/usr/bin/env python3
"""
NODO Design System — validador y generador de documentación de componentes.

Lee las especificaciones JSON de `design-system/components/`, aplica el checklist
de completitud definido en `nodo-architecture.json` y renderiza la documentación
HTML con las mismas clases CSS que consume `nodo-design-system.html`.

Uso:
    python3 tools/build.py validate
    python3 tools/build.py render [--out dist/components.html]
    python3 tools/build.py all
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from html import escape
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parent.parent
COMPONENTS_DIR = ROOT / "components"
DIST_DIR = ROOT / "dist"

TOKEN_PREFIXES = ("--", "nodo.comp.")
TYPOGRAPHY_ROLES = ("display/", "headline/", "title/", "body/", "label/")


# --------------------------------------------------------------------------- #
# Modelo
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class Issue:
    """Un incumplimiento del contrato de documentación."""

    component: str
    check: str
    severity: str
    message: str

    def __str__(self) -> str:
        mark = "ERROR" if self.severity == "error" else "WARN "
        return f"  [{mark}] {self.check}: {self.message}"


@dataclass
class Component:
    """Especificación de un componente cargada desde disco."""

    path: Path
    data: dict[str, Any]

    @property
    def id(self) -> str:
        return self.data.get("identity", {}).get("id", self.path.stem)

    @property
    def slug(self) -> str:
        return self.id.replace("/", "-")

    def section(self, name: str) -> dict[str, Any]:
        return self.data.get(name) or {}

    @classmethod
    def load_all(cls, directory: Path) -> list["Component"]:
        files = sorted(p for p in directory.glob("*.json"))
        if not files:
            raise SystemExit(f"No se encontraron especificaciones en {directory}")
        return [cls(path=p, data=json.loads(p.read_text(encoding="utf-8"))) for p in files]


# --------------------------------------------------------------------------- #
# Validación
# --------------------------------------------------------------------------- #

class CompletenessValidator:
    """Aplica el checklist C01–C25 del contrato de agente."""

    REQUIRED_SECTIONS = (
        "identity", "purpose", "anatomy", "variants", "specs",
        "states", "behavior", "composition", "guidelines", "accessibility", "code",
    )
    # Estados obligatorios segun el modelo de interaccion del componente.
    REQUIRED_STATES = {
        "activatable": ("hover", "focus-visible", "pressed", "disabled"),
        "editable": ("hover", "focused", "error", "disabled"),
        "selectable": ("hover", "focus-visible", "selected", "disabled"),
        "static": (),
    }

    def validate(self, component: Component) -> list[Issue]:
        issues: list[Issue] = []
        for check in (
            self._sections, self._identity, self._purpose, self._anatomy,
            self._variants, self._specs, self._states, self._behavior,
            self._composition, self._responsive, self._guidelines,
            self._accessibility, self._code, self._governance,
        ):
            issues.extend(check(component))
        return issues

    # -- helpers ------------------------------------------------------------ #

    @staticmethod
    def _issue(cid: str, comp: Component, msg: str, severity: str = "error") -> Issue:
        return Issue(component=comp.id, check=cid, severity=severity, message=msg)

    @staticmethod
    def _is_token(value: Any) -> bool:
        if not isinstance(value, str):
            return False
        return value.startswith(TOKEN_PREFIXES) or value.startswith(TYPOGRAPHY_ROLES)

    @staticmethod
    def _iter_style_values(style_maps: Iterable[dict[str, Any]]) -> Iterable[tuple[str, Any]]:
        color_props = {"background", "foreground", "border", "outline", "stateLayer"}
        for smap in style_maps:
            for prop, value in smap.items():
                if prop in color_props:
                    yield prop, value

    # -- checks ------------------------------------------------------------- #

    def _sections(self, c: Component) -> list[Issue]:
        return [
            self._issue("C00", c, f"falta la sección obligatoria `{name}`")
            for name in self.REQUIRED_SECTIONS
            if name not in c.data
        ]

    def _identity(self, c: Component) -> list[Issue]:
        identity = c.section("identity")
        missing = [k for k in ("id", "name", "category", "status", "version") if not identity.get(k)]
        return [self._issue("C01", c, f"identity incompleto: falta {', '.join(missing)}")] if missing else []

    def _purpose(self, c: Component) -> list[Issue]:
        purpose = c.section("purpose")
        issues = []
        if not purpose.get("whenToUse"):
            issues.append(self._issue("C02", c, "sin `whenToUse`"))
        not_use = purpose.get("whenNotToUse") or []
        if not not_use:
            issues.append(self._issue("C02", c, "sin `whenNotToUse`"))
        for entry in not_use:
            if not entry.get("useInstead"):
                issues.append(self._issue("C02", c, f"`whenNotToUse` sin alternativa: {entry.get('case')}"))
        return issues

    def _anatomy(self, c: Component) -> list[Issue]:
        parts = c.section("anatomy").get("parts") or []
        issues = []
        if not any(p.get("required") for p in parts):
            issues.append(self._issue("C03", c, "ninguna parte marcada como required"))
        indexes = [p.get("index") for p in parts]
        if indexes != list(range(1, len(parts) + 1)):
            issues.append(self._issue("C04", c, f"índices de anatomía no contiguos: {indexes}"))
        return issues

    def _variants(self, c: Component) -> list[Issue]:
        variants = c.section("variants")
        issues = []
        for named in variants.get("named") or []:
            if not named.get("overrides"):
                issues.append(self._issue("C05", c, f"variante `{named.get('id')}` sin overrides explícitos"))
        axes = variants.get("axes") or []
        if axes:
            expected = 1
            for axis in axes:
                expected *= max(len(axis.get("values") or []), 1)
            declared = variants.get("variantCount")
            if declared != expected:
                issues.append(self._issue(
                    "C06", c,
                    f"variantCount declarado {declared} != producto de ejes {expected}",
                ))
        return issues

    def _specs(self, c: Component) -> list[Issue]:
        specs = c.section("specs")
        issues = []
        base = specs.get("base") or {}
        part_ids = {p["id"] for p in (c.section("anatomy").get("parts") or [])}
        for part_id in base:
            if part_id not in part_ids:
                issues.append(self._issue("C07", c, f"`specs.base` referencia parte inexistente `{part_id}`"))
        for part_id in part_ids:
            if part_id not in base:
                issues.append(self._issue("C07", c, f"parte `{part_id}` sin specs en `base`", severity="warning"))
        for prop, value in self._iter_style_values(base.values()):
            if not self._is_token(value) and value not in ("none", "transparent", "inherit", "locked"):
                issues.append(self._issue("C08", c, f"valor literal en `{prop}`: {value!r}"))
        measurements = specs.get("measurements") or {}
        for key in ("radius", "padding"):
            if key not in measurements:
                issues.append(self._issue("C09", c, f"`measurements` sin `{key}`"))
        return issues

    def _states(self, c: Component) -> list[Issue]:
        states = c.section("states")
        listed = states.get("list") or []
        ids = {s.get("id") for s in listed}
        issues = []
        if "default" not in ids:
            issues.append(self._issue("C10", c, "sin estado `default`"))
        if states.get("interactive", True):
            model = states.get("interactionModel", "activatable")
            required = self.REQUIRED_STATES.get(model)
            if required is None:
                issues.append(self._issue("C10", c, f"interactionModel desconocido: {model!r}"))
            else:
                missing = [s for s in required if s not in ids]
                if missing:
                    issues.append(self._issue(
                        "C10", c,
                        f"modelo `{model}` sin estados: {', '.join(missing)}",
                    ))
        for state in listed:
            if state.get("id") != "default" and not state.get("delta"):
                issues.append(self._issue("C11", c, f"estado `{state.get('id')}` sin delta declarado"))
        disabled = next((s for s in listed if s.get("id") == "disabled"), None)
        if disabled:
            opacities = [
                sm.get("opacity")
                for sm in (disabled.get("delta") or {}).values()
                if isinstance(sm, dict) and "opacity" in sm
            ]
            if len(opacities) < 2:
                issues.append(self._issue("C12", c, "`disabled` debe declarar opacidad de contenedor y de contenido"))
        return issues

    def _behavior(self, c: Component) -> list[Issue]:
        behavior = c.section("behavior")
        issues = []
        interactions = behavior.get("interactions") or []
        if not interactions:
            issues.append(self._issue("C13", c, "sin interacciones declaradas"))
        for entry in interactions:
            motion = entry.get("motion") or {}
            if not motion.get("duration") or not motion.get("easing"):
                issues.append(self._issue("C13", c, f"interacción `{entry.get('id')}` sin duration/easing"))
        if not behavior.get("reducedMotion"):
            issues.append(self._issue("C14", c, "sin comportamiento para prefers-reduced-motion"))
        return issues

    def _composition(self, c: Component) -> list[Issue]:
        composition = c.section("composition")
        issues = []
        for slot in composition.get("slots") or []:
            if not slot.get("accepts") or not slot.get("cardinality"):
                issues.append(self._issue("C15", c, f"slot `{slot.get('id')}` sin accepts/cardinality"))
        for prop in composition.get("props") or []:
            if "default" not in prop or not prop.get("type"):
                issues.append(self._issue("C16", c, f"prop `{prop.get('name')}` sin type/default"))
            if prop.get("type") == "enum" and not prop.get("enum"):
                issues.append(self._issue("C16", c, f"prop enum `{prop.get('name')}` sin valores permitidos"))
        return issues

    def _responsive(self, c: Component) -> list[Issue]:
        responsive = c.section("responsive")
        if not responsive.get("breakpoints") and not responsive.get("fluid"):
            return [self._issue("C17", c, "sin comportamiento responsive ni `fluid: true`", severity="warning")]
        return []

    def _guidelines(self, c: Component) -> list[Issue]:
        guidelines = c.section("guidelines")
        issues = []
        for key, cid in (("do", "C18"), ("dont", "C18")):
            entries = guidelines.get(key) or []
            if len(entries) < 2:
                issues.append(self._issue(cid, c, f"`{key}` necesita al menos 2 entradas (hay {len(entries)})"))
        content = guidelines.get("content") or {}
        if not content.get("goodExample") or not content.get("badExample"):
            issues.append(self._issue("C19", c, "content guidelines sin ejemplo bueno y malo"))
        return issues

    def _accessibility(self, c: Component) -> list[Issue]:
        a11y = c.section("accessibility")
        issues = []
        for key in ("role", "accessibleName", "keyboard"):
            if not a11y.get(key):
                issues.append(self._issue("C20", c, f"accessibility sin `{key}`"))
        contrast = a11y.get("contrast") or []
        themes = {entry.get("theme") for entry in contrast}
        if not {"light", "dark"}.issubset(themes):
            issues.append(self._issue("C21", c, "contraste no verificado en light Y dark"))
        for entry in contrast:
            if not entry.get("pass"):
                issues.append(self._issue(
                    "C21", c,
                    f"contraste insuficiente ({entry.get('theme')}): {entry.get('pair')} "
                    f"= {entry.get('ratio')}:1 < {entry.get('requirement')}:1",
                    severity="warning",
                ))
        touch = a11y.get("touchTarget") or {}
        if not touch.get("min") or not touch.get("achievedBy"):
            issues.append(self._issue("C22", c, "touchTarget sin `min` o sin `achievedBy`"))
        return issues

    def _code(self, c: Component) -> list[Issue]:
        code = c.section("code")
        issues = []
        html = code.get("html") or ""
        if not html:
            issues.append(self._issue("C23", c, "sin snippet HTML de referencia"))
        css = code.get("css") or ""
        if css and "#" in css:
            hexes = [tok for tok in css.split() if tok.startswith("#") and len(tok.strip(";")) in (4, 7)]
            if hexes:
                issues.append(self._issue("C23", c, f"el CSS usa literales hex en lugar de tokens: {hexes[:3]}"))
        a11y_attrs = [a.get("attribute", "") for a in (c.section("accessibility").get("ariaAttributes") or [])]
        declared = [a for a in a11y_attrs if a.startswith("aria-")]
        if declared and not any(a in html for a in declared):
            issues.append(self._issue("C24", c, "el snippet no muestra ninguno de los atributos ARIA declarados", severity="warning"))
        return issues

    def _governance(self, c: Component) -> list[Issue]:
        identity = c.section("identity")
        missing = [k for k in ("owner", "lastReview") if not identity.get(k)]
        if missing or not c.section("related"):
            return [self._issue("C25", c, "governance incompleto: falta owner/lastReview/related", severity="warning")]
        return []


# --------------------------------------------------------------------------- #
# Render
# --------------------------------------------------------------------------- #

class HtmlRenderer:
    """Renderiza una especificación al markup de `nodo-design-system.html`."""

    TABS = ("overview", "anatomy", "specs", "behavior", "guidelines", "accessibility", "code")

    def render_all(self, components: list[Component]) -> str:
        body = "\n".join(self.render(c) for c in components)
        return (
            '<section class="doc-section" id="component-details">\n'
            "  <h2>Component Reference</h2>\n"
            '  <p class="section-desc">Especificaciones generadas desde '
            "<code>design-system/components/*.json</code>. Cada bloque cumple el contrato de "
            "documentación y es suficiente para reconstruir el componente.</p>\n"
            f"{body}\n</section>\n"
        )

    def render(self, c: Component) -> str:
        identity, purpose = c.section("identity"), c.section("purpose")
        variants = c.section("variants")
        tabs = "".join(
            f'<button class="comp-tab{" active" if i == 0 else ""}" '
            f"onclick=\"switchTab(this,'{tab}')\">{tab.capitalize()}</button>"
            for i, tab in enumerate(self.TABS)
        )
        panes = "".join(
            f'<div class="comp-tab-content{" active" if i == 0 else ""}" data-tab="{tab}">'
            f"{getattr(self, f'_tab_{tab}')(c)}</div>"
            for i, tab in enumerate(self.TABS)
        )
        return f"""
<div class="comp-detail" id="comp-detail-{c.slug}">
  <div class="comp-detail-header">
    <div>
      <div class="cat-tag">{escape(identity.get('category', ''))}</div>
      <h3>{escape(identity.get('name', ''))}</h3>
      <p style="margin:4px 0 0;font-size:13.5px;">{escape(purpose.get('summary', ''))}</p>
    </div>
    <div class="variant-count">{variants.get('variantCount', '?')} variants &middot;
      <code>{escape(identity.get('figmaKey', c.id))}</code> &middot;
      v{escape(identity.get('version', '0.0.0'))} &middot; {escape(identity.get('status', ''))}</div>
  </div>
  <div class="comp-detail-tabs">{tabs}</div>
  {panes}
</div>"""

    # -- tabs --------------------------------------------------------------- #

    def _tab_overview(self, c: Component) -> str:
        purpose, variants = c.section("purpose"), c.section("variants")
        when_to = self._ul(purpose.get("whenToUse"))
        when_not = self._ul(
            f"{escape(e['case'])} → usa <code>{escape(e['useInstead'])}</code>"
            for e in purpose.get("whenNotToUse") or []
        )
        named = "".join(
            f"<tr><td><strong>{escape(v['name'])}</strong></td>"
            f"<td>{escape(v.get('emphasis', '—'))}</td>"
            f"<td>{escape(v['description'])}</td></tr>"
            for v in variants.get("named") or []
        )
        axes = "".join(
            f'<span class="mini-chip">{escape(a["id"])}: {escape(", ".join(a["values"]))}</span>'
            for a in variants.get("axes") or []
        )
        return f"""
      <p>{escape(c.section('purpose').get('description', c.section('purpose').get('summary', '')))}</p>
      <h4>Cuándo usarlo</h4>{when_to}
      <h4>Cuándo NO usarlo</h4>{when_not}
      <h4>Variantes</h4>
      <table class="spec-table"><thead><tr><th>Variante</th><th>Énfasis</th><th>Descripción</th></tr></thead>
      <tbody>{named}</tbody></table>
      <h4>Ejes de variación</h4><div class="chip-row">{axes}</div>"""

    def _tab_anatomy(self, c: Component) -> str:
        anatomy, composition = c.section("anatomy"), c.section("composition")
        parts = "".join(
            f"<tr><td><strong>{p['index']}</strong></td><td><code>{escape(p['id'])}</code></td>"
            f"<td>{escape(p['name'])}</td>"
            f"<td>{'Obligatoria' if p.get('required') else escape(p.get('cardinality', '0..1'))}</td>"
            f"<td>{escape(p['description'])}</td></tr>"
            for p in anatomy.get("parts") or []
        )
        slots = "".join(
            f"<tr><td><code>{escape(s['id'])}</code></td><td>{escape(', '.join(s.get('accepts', [])))}</td>"
            f"<td>{escape(s.get('cardinality', ''))}</td>"
            f"<td>{escape(', '.join(s.get('allowedComponents', [])) or '—')}</td>"
            f"<td>{escape(s.get('constraints', '—'))}</td></tr>"
            for s in composition.get("slots") or []
        )
        props = "".join(
            f"<tr><td><code>{escape(p['name'])}</code></td><td>{escape(p['type'])}</td>"
            f"<td>{escape(', '.join(p.get('enum', [])) or '—')}</td>"
            f"<td><code>{escape(str(p.get('default')))}</code></td></tr>"
            for p in composition.get("props") or []
        )
        rules = self._ul(composition.get("nestingRules"))
        return f"""
      <h4>Partes</h4>
      <table class="spec-table"><thead><tr><th>#</th><th>Id</th><th>Nombre</th><th>Cardinalidad</th><th>Descripción</th></tr></thead>
      <tbody>{parts}</tbody></table>
      <h4>Slots</h4>
      <table class="spec-table"><thead><tr><th>Slot</th><th>Acepta</th><th>Cardinalidad</th><th>Componentes permitidos</th><th>Restricciones</th></tr></thead>
      <tbody>{slots}</tbody></table>
      <h4>Props</h4>
      <table class="spec-table"><thead><tr><th>Prop</th><th>Tipo</th><th>Valores</th><th>Default</th></tr></thead>
      <tbody>{props}</tbody></table>
      <h4>Reglas de composición</h4>{rules}"""

    def _tab_specs(self, c: Component) -> str:
        specs, states = c.section("specs"), c.section("states")
        base = "".join(
            f"<tr><td><code>{escape(part)}</code></td><td><code>{escape(prop)}</code></td>"
            f"<td><code>{escape(str(value))}</code></td></tr>"
            for part, smap in (specs.get("base") or {}).items()
            for prop, value in smap.items()
        )
        measurements = "".join(
            f"<tr><td>{escape(k)}</td><td><code>{escape(str(v))}</code></td></tr>"
            for k, v in (specs.get("measurements", {}).get("resolved") or {}).items()
        )
        state_rows = "".join(
            f"<tr><td><span class='mini-chip state-chip'>{escape(s['id'])}</span></td>"
            f"<td>{escape(s['trigger'])}</td>"
            f"<td>{self._delta(s.get('delta'))}</td></tr>"
            for s in states.get("list") or []
        )
        breakpoints = "".join(
            f"<tr><td>{escape(b['id'])}</td><td>{escape(b.get('minWidth', '—'))}</td>"
            f"<td>{escape(b['behavior'])}</td></tr>"
            for b in (c.section("responsive").get("breakpoints") or [])
        )
        return f"""
      <h4>Tokens por parte y propiedad</h4>
      <table class="spec-table"><thead><tr><th>Parte</th><th>Propiedad</th><th>Token</th></tr></thead>
      <tbody>{base}</tbody></table>
      <h4>Medidas resueltas</h4>
      <table class="spec-table"><thead><tr><th>Medida</th><th>Valor</th></tr></thead>
      <tbody>{measurements}</tbody></table>
      <h4>Estados (delta sobre default)</h4>
      <table class="spec-table"><thead><tr><th>Estado</th><th>Disparador</th><th>Cambios</th></tr></thead>
      <tbody>{state_rows}</tbody></table>
      <h4>Responsive</h4>
      <table class="spec-table"><thead><tr><th>Breakpoint</th><th>Desde</th><th>Comportamiento</th></tr></thead>
      <tbody>{breakpoints}</tbody></table>"""

    def _tab_behavior(self, c: Component) -> str:
        behavior = c.section("behavior")
        interactions = "".join(
            f"<tr><td><code>{escape(i['id'])}</code></td><td>{escape(i['trigger'])}</td>"
            f"<td>{escape(i['result'])}</td>"
            f"<td>{escape(i['motion'].get('pattern', 'none'))} · "
            f"{escape(i['motion']['duration'])} · <code>{escape(i['motion']['easing'])}</code></td></tr>"
            for i in behavior.get("interactions") or []
        )
        gestures = "".join(
            f"<tr><td>{escape(g['gesture'])}</td><td>{escape(g['action'])}</td>"
            f"<td>{escape(g.get('constraint', '—'))}</td></tr>"
            for g in behavior.get("gestures") or []
        )
        overflow = behavior.get("overflow") or {}
        return f"""
      <h4>Interacciones</h4>
      <table class="spec-table"><thead><tr><th>Id</th><th>Disparador</th><th>Resultado</th><th>Motion</th></tr></thead>
      <tbody>{interactions}</tbody></table>
      <h4>Gestos</h4>
      <table class="spec-table"><thead><tr><th>Gesto</th><th>Acción</th><th>Restricción</th></tr></thead>
      <tbody>{gestures}</tbody></table>
      <h4>Desbordamiento</h4>
      <p><strong>{escape(overflow.get('strategy', '—'))}</strong> — {escape(overflow.get('affordance', ''))}</p>
      <h4>Movimiento reducido</h4><p>{escape(behavior.get('reducedMotion', '—'))}</p>
      <h4>Carga</h4><p>{escape(behavior.get('loading', '—'))}</p>
      <h4>Estado vacío</h4><p>{escape(behavior.get('emptyState', '—'))}</p>"""

    def _tab_guidelines(self, c: Component) -> str:
        guidelines = c.section("guidelines")
        content = guidelines.get("content") or {}
        do = self._ul(
            f"<strong>{escape(e['rule'])}</strong>"
            + (f" — {escape(e['rationale'])}" if e.get("rationale") else "")
            for e in guidelines.get("do") or []
        )
        dont = self._ul(
            f"<strong>{escape(e['rule'])}</strong>"
            + (f" — {escape(e['rationale'])}" if e.get("rationale") else "")
            for e in guidelines.get("dont") or []
        )
        return f"""
      <div class="do-dont-grid">
        <div class="do-col"><h4>Do</h4>{do}</div>
        <div class="dont-col"><h4>Don't</h4>{dont}</div>
      </div>
      <h4>Contenido</h4>{self._ul(content.get('rules'))}
      <p><strong>Bien:</strong> {escape(content.get('goodExample', '—'))}</p>
      <p><strong>Mal:</strong> {escape(content.get('badExample', '—'))}</p>
      <h4>Colocación</h4>{self._ul(guidelines.get('placement'))}
      <h4>Densidad</h4><p>{escape(guidelines.get('density', '—'))}</p>"""

    def _tab_accessibility(self, c: Component) -> str:
        a11y = c.section("accessibility")
        keyboard = "".join(
            f"<tr><td><span class='kbd'>{escape(k['key'])}</span></td><td>{escape(k['action'])}</td></tr>"
            for k in a11y.get("keyboard") or []
        )
        aria = "".join(
            f"<tr><td><code>{escape(a['attribute'])}</code></td><td><code>{escape(a['value'])}</code></td>"
            f"<td>{escape(a['when'])}</td></tr>"
            for a in a11y.get("ariaAttributes") or []
        )
        contrast = "".join(
            f"<tr><td><code>{escape(x['pair'])}</code></td><td>{escape(x['theme'])}</td>"
            f"<td>{x['ratio']}:1</td><td>{x['requirement']}:1</td>"
            f"<td>{'✓' if x['pass'] else '✗'}</td></tr>"
            for x in a11y.get("contrast") or []
        )
        focus = a11y.get("focus") or {}
        touch = a11y.get("touchTarget") or {}
        return f"""
      <h4>Rol y nombre accesible</h4>
      <p><code>{escape(a11y.get('role', '—'))}</code> — {escape(a11y.get('roleRationale', ''))}</p>
      <p>{escape(a11y.get('accessibleName', ''))}</p>
      <h4>Atributos ARIA</h4>
      <table class="spec-table"><thead><tr><th>Atributo</th><th>Valor</th><th>Cuándo</th></tr></thead>
      <tbody>{aria}</tbody></table>
      <h4>Teclado</h4>
      <table class="spec-table"><thead><tr><th>Tecla</th><th>Acción</th></tr></thead><tbody>{keyboard}</tbody></table>
      <p><strong>Tab stops:</strong> {escape(a11y.get('tabStops', '—'))}</p>
      <h4>Foco</h4>
      <p>Indicador <code>{escape(str(focus.get('indicator')))}</code>,
      {escape(str(focus.get('width')))} con offset {escape(str(focus.get('offset')))}.
      {escape(str(focus.get('restoreTo', '')))}</p>
      <h4>Lector de pantalla</h4>{self._ul(a11y.get('screenReader'))}
      <h4>Contraste</h4>
      <table class="spec-table"><thead><tr><th>Par</th><th>Tema</th><th>Ratio</th><th>Mínimo</th><th></th></tr></thead>
      <tbody>{contrast}</tbody></table>
      <h4>Objetivo táctil</h4>
      <p><strong>{escape(touch.get('min', '—'))}</strong> — {escape(touch.get('achievedBy', ''))}</p>
      <h4>WCAG 2.2 AA</h4>
      <div class="chip-row">{''.join(f'<span class="mini-chip">{escape(w)}</span>' for w in a11y.get('wcag') or [])}</div>"""

    def _tab_code(self, c: Component) -> str:
        code = c.section("code")
        blocks = [
            ("HTML", code.get("html")),
            ("CSS", code.get("css")),
            ("Uso", code.get("usage")),
        ]
        rendered = "".join(
            f"<h4>{title}</h4><pre style=\"background:var(--surface-container);padding:16px;"
            f"border-radius:var(--radius-sm);overflow-x:auto;font-size:12.5px;line-height:1.5;\">"
            f"<code>{escape(snippet)}</code></pre>"
            for title, snippet in blocks
            if snippet
        )
        variables = "".join(
            f'<span class="mini-chip">{escape(v)}</span>' for v in code.get("cssVariables") or []
        )
        return f"{rendered}<h4>Variables expuestas</h4><div class=\"chip-row\">{variables}</div>"

    # -- helpers de render -------------------------------------------------- #

    @staticmethod
    def _ul(items: Iterable[str] | None) -> str:
        items = list(items or [])
        if not items:
            return "<p>—</p>"
        rows = "".join(f"<li>{item if '<' in item else escape(item)}</li>" for item in items)
        return f'<ul class="feature-list">{rows}</ul>'

    @staticmethod
    def _delta(delta: dict[str, Any] | None) -> str:
        if not delta:
            return "<em>sin cambios</em>"
        return "<br>".join(
            f"<code>{escape(part)}</code>: "
            + ", ".join(f"{escape(k)} → <code>{escape(str(v))}</code>" for k, v in smap.items())
            for part, smap in delta.items()
        )


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def cmd_validate(components: list[Component]) -> int:
    validator = CompletenessValidator()
    errors = warnings = 0
    for component in components:
        issues = validator.validate(component)
        errors += sum(1 for i in issues if i.severity == "error")
        warnings += sum(1 for i in issues if i.severity == "warning")
        mark = "OK" if not issues else ("FAIL" if any(i.severity == "error" for i in issues) else "WARN")
        print(f"[{mark}] {component.id}  ({component.path.name})")
        for issue in issues:
            print(issue)
    print(f"\n{len(components)} componentes · {errors} errores · {warnings} avisos")
    return 1 if errors else 0


def _site_styles() -> str:
    """Reutiliza el bloque <style> de la documentacion publicada."""
    source = ROOT.parent / "nodo-design-system.html"
    if not source.exists():
        return ""
    html = source.read_text(encoding="utf-8")
    start, end = html.find("<style>"), html.find("</style>")
    return html[start:end + len("</style>")] if start != -1 and end != -1 else ""


def cmd_render(components: list[Component], out: Path, standalone: bool = False) -> int:
    body = HtmlRenderer().render_all(components)
    if standalone:
        body = (
            '<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
            "<title>NODO — Component Reference</title>"
            f"{_site_styles()}</head><body>"
            '<main class="main" style="margin-left:0;"><div class="content-max">'
            f"{body}"
            "</div></main>"
            "<script>window.switchTab=function(b,t){"
            "var c=b.closest('.comp-detail');"
            "c.querySelectorAll('.comp-tab').forEach(function(x){x.classList.remove('active')});"
            "c.querySelectorAll('.comp-tab-content').forEach(function(x){x.classList.remove('active')});"
            "b.classList.add('active');"
            "var el=c.querySelector('[data-tab=\"'+t+'\"]');if(el)el.classList.add('active');};"
            "</script></body></html>"
        )
    out = out.resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(body, encoding="utf-8")
    print(f"Documentacion generada: {out} ({out.stat().st_size:,} bytes)")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="NODO Design System — build de documentación")
    parser.add_argument("command", choices=("validate", "render", "all"))
    parser.add_argument("--src", type=Path, default=COMPONENTS_DIR)
    parser.add_argument("--out", type=Path, default=DIST_DIR / "components.html")
    parser.add_argument("--standalone", action="store_true", help="Envuelve la salida en una pagina completa previsualizable")
    args = parser.parse_args(argv)

    components = Component.load_all(args.src)

    if args.command == "validate":
        return cmd_validate(components)
    if args.command == "render":
        return cmd_render(components, args.out, args.standalone)
    return cmd_validate(components) or cmd_render(components, args.out, args.standalone)


if __name__ == "__main__":
    sys.exit(main())
