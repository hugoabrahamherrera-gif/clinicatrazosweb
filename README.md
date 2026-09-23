# Sitio web — Clínica Trazos

Este repo tiene **dos cosas en paralelo**:

1. **El sitio real**, hoy en `riveraclc.wordpress.com` (WordPress.com, plan gratuito, sin la marca aplicada todavía por la restricción de estilos del plan free).
2. **Una versión estática con la marca completa** (`index.html`), pensada para verla "en su esplendor" gratis en GitHub Pages mientras se decide si se paga el plan de WordPress o se termina usando esta versión estática como sitio final.

## Cómo editar el contenido (versión estática)

**No edites `index.html` a mano** — se regenera solo y se pierde el cambio. El flujo es:

1. Editá `content.json` (textos, teléfono, dirección, servicios, convenios, novedades, etc. — todo en un solo archivo, en español, sin HTML).
2. Corré `python3 build.py` en la carpeta del repo.
3. Eso regenera `index.html` a partir de `template.html` (el diseño/estilos) + `content.json` (el contenido).
4. Commit y push — si GitHub Pages está activado, el sitio se actualiza solo.

Si no querés tocar nada vos, simplemente pedime el cambio en una conversación y yo edito `content.json` y corro el build.

## Estado actual (2026-09-23)

- Dominio de trabajo real: `riveraclc.wordpress.com` (se migrará a `clinicatrazos` más adelante). Sitio en modo privado/"coming soon", con la página Inicio publicada y fijada como portada.
- El plan gratuito de WordPress.com bloquea la personalización de fuentes/colores a nivel sitio — por eso el WordPress usa la tipografía/colores por defecto del tema, sin la marca Trazos aplicada todavía.
- Versión estática (`index.html`) con la marca completa (Poppins + paleta real + logo), pensada para hosting gratis (GitHub Pages) sin depender de WordPress.
- Identidad de marca tomada de `assets/manual-de-marca-trazos.pdf` (mismo manual que se está aplicando al rediseño del sistema de gestión de la clínica).

## Identidad de marca

- **Paleta**: `#69662C` (oliva, ancla), `#C98271` (terracota), `#F09367` (coral), `#FCD38C` (amarillo), `#FDD0BD` (durazno), `#C2CCAB` (salvia).
- **Tipografía**: Poppins.
- **Logo**: isotipo circular con motivo de "cerebro/trazos" multicolor + wordmark "TRAZOS". Dos variantes en `assets/`:
  - `logo-circulo-claro.png` — fondo blanco, para superficies claras.
  - `logo-circulo-oscuro.png` — círculo oliva sólido, texto/ícono claros, para superficies oscuras.
- Contraste verificado: `#69662C` + texto blanco pasa AA (~5.9:1); `#F09367` necesita texto oscuro (`#2E2B15`), no blanco.

## Pendiente

- Completar los datos reales entre `[corchetes]` en `content.json` (dirección, teléfono, email, horario) antes de compartir el link ampliamente.
- El formulario de contacto usa `mailto:` (sin backend) — funciona pero abre el cliente de correo del visitante; si se quiere algo más prolijo más adelante, hay servicios gratis tipo Formspree.
- Decidir si el sitio final termina siendo esta versión estática (gratis, sin editor visual) o el WordPress con plan pago (con editor visual, $48/año).

## Estructura

```
index.html       — sitio generado (NO editar a mano, ver arriba)
template.html    — diseño/estructura/estilos (el "molde")
content.json     — todo el contenido editable (el "relleno")
build.py         — script que junta template.html + content.json → index.html
assets/          — logo (2 variantes), manual de marca original
contenido/       — borradores de copy por sección (referencia, ya volcados a content.json)
mockup/          — fuente del primer mockup de dirección visual (Artifact "Design canvas")
```
