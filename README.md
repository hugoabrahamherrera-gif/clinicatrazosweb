# Sitio web — Clínica Trazos

Repositorio de trabajo para el sitio web de la clínica. **No es código desplegable**: el sitio se construye directamente en WordPress.com (editor de bloques), vía navegador. Este repo guarda la fuente de contenido, la identidad de marca y el registro de decisiones para no perder nada entre sesiones.

## Estado actual (2026-09-22)

- Dominio de trabajo: `riveraclc.wordpress.com` (se migrará a `clinicatrazos` más adelante).
- El plan gratuito de WordPress.com bloquea las herramientas MCP de edición automática — la construcción se hace a mano vía automatización de navegador (Claude in Chrome), bloque por bloque.
- Mockup de dirección visual (landing de una página: Inicio, Servicios, Convenios, Novedades, Contacto) aprobado en dirección, ver `mockup/mockup-landing.html` o el Artifact publicado: https://claude.ai/artifact/P97uFZ5X6q9oQtHbZhYrxk
- Identidad de marca tomada de `assets/manual-de-marca-trazos.pdf` (mismo manual que se está aplicando al rediseño del sistema de gestión de la clínica).

## Identidad de marca

- **Paleta**: `#69662C` (oliva, ancla), `#C98271` (terracota), `#F09367` (coral), `#FCD38C` (amarillo), `#FDD0BD` (durazno), `#C2CCAB` (salvia).
- **Tipografía**: Poppins.
- **Logo**: isotipo circular con motivo de "cerebro/trazos" multicolor + wordmark "TRAZOS". Dos variantes en `assets/`:
  - `logo-circulo-claro.png` — fondo blanco, para superficies claras.
  - `logo-circulo-oscuro.png` — círculo oliva sólido, texto/ícono claros, para superficies oscuras.
- Contraste verificado: `#69662C` + texto blanco pasa AA (~5.9:1); `#F09367` necesita texto oscuro (`#2E2B15`), no blanco.

## Contenido

Borradores de copy por sección en `contenido/`, con `[placeholders entre corchetes]` donde falta un dato real (dirección, teléfono, email, horarios). Completar esos datos antes de publicar cada sección en WordPress.

## Estructura

```
assets/       — logo (2 variantes), manual de marca original
contenido/    — borradores de copy por sección
mockup/       — fuente del mockup de dirección visual (Artifact "Design canvas")
```
