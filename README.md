# Sitio web — Clínica Trazos

Sitio estático multi-página, optimizado para Google (SEO), publicado con GitHub Pages en
<https://hugoabrahamherrera-gif.github.io/clinicatrazosweb/>.

El WordPress (`riveraclc.wordpress.com`) quedó como alternativa descartada: el plan gratuito no
permite controlar los metadatos ni los datos estructurados que Google necesita.

## Cómo editar

**No edites a mano los `index.html` ni `sitemap.xml`**: se regeneran solos. El flujo es:

1. Editá lo que corresponda:
   - `content.json`: datos generales, portada, teléfono, horario, WhatsApp, URL del sitio.
   - `contenido/paginas/*.md`: una página por servicio, más Convenios y Contacto.
   - `contenido/blog/*.md`: artículos del blog, uno por archivo.
2. Corré `python3 build.py`.
3. Leé los avisos que imprime: te dice qué datos faltan o qué títulos son demasiado largos.
4. Commit y push. GitHub Pages publica en uno o dos minutos.

Para ver el sitio en tu compu antes de publicar: `cd ~/Desktop && python3 -m http.server 8765` y
abrí <http://localhost:8765/clinicatrazosweb/>.

### El blog

Cada artículo es un `.md` con un bloque de datos al principio (`title`, `slug`, `description`,
`keyword`, `categoria`, `servicio`, `fecha`). **Se publican solo los que tienen `fecha` de hoy o
anterior**: para programar un artículo, poné una fecha futura y corré `build.py` ese día.
Para revisar todos, incluidos los programados, en local: `python3 build.py --borradores`
(no publiques ese resultado).

Los archivos que empiezan con `_` (por ejemplo `_plan-editorial.md`) son notas internas y no se publican.

## Qué genera `build.py`

| Salida | Para qué |
|---|---|
| `index.html` y `<servicio>-rivera/index.html` | Una página por búsqueda: "fonoaudióloga Rivera", "psicomotricidad Rivera", etc. |
| `convenios/`, `contacto/`, `blog/` | Páginas propias para "ayudas extraordinarias BPS Rivera", ubicación y artículos |
| Datos estructurados (JSON-LD) | `MedicalClinic` (dirección, servicios, zona), migas de pan, preguntas frecuentes, artículos |
| `<title>`, descripción, canónica, Open Graph | Cómo aparece cada página en Google y al compartir el link por WhatsApp o Facebook |
| `sitemap.xml`, `robots.txt`, `404.html` | Para que Google encuentre todas las páginas |

Los datos entre corchetes en `content.json` (por ejemplo `"[+598 XXX XXX]"`) **no se publican**:
el build los oculta y avisa. Completalos para que aparezcan en el sitio y en Google.

## Pendiente para el lanzamiento

Ver `LANZAMIENTO.md`.

## Identidad de marca

- **Paleta**: `#69662C` (oliva), `#C98271` (terracota), `#F09367` (coral), `#FCD38C` (amarillo), `#FDD0BD` (durazno), `#C2CCAB` (salvia).
- **Tipografía**: Poppins.
- **Logo**: `assets/logo-trazos.png` (original, el mismo `logo1.png` del sistema de gestión). Versiones optimizadas: `logo-130.png` (cabecera), `logo-444.png` (portada), `favicon-32.png`, `apple-touch-icon.png`, `og-imagen.png` (vista previa al compartir).
- Coral (`#F09367`) lleva texto oscuro, nunca blanco.

## Estructura

```
build.py            generador (Python 3, sin dependencias)
content.json        datos globales y portada
plantillas/         base.html (head SEO + cabecera + pie) e inicio.html (cuerpo de la portada)
contenido/paginas/  servicios, convenios, contacto (Markdown)
contenido/blog/     artículos (Markdown) + _plan-editorial.md
assets/             logos, íconos, imagen para compartir, manual de marca
mockup/             mockup original de dirección visual
```
