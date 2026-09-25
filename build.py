#!/usr/bin/env python3
"""
Genera el sitio completo de Clínica Trazos (multi-página, con SEO) a partir de:

  content.json                    datos globales + portada
  contenido/paginas/*.md          páginas de servicio, convenios y contacto
  contenido/blog/*.md             artículos del blog (se publican los que tienen fecha <= hoy)
  plantillas/base.html            cabecera, pie y <head> con SEO (común a todas las páginas)
  plantillas/inicio.html          cuerpo de la portada

Salida (lo que publica GitHub Pages):
  index.html, <slug>/index.html, blog/index.html, blog/<slug>/index.html,
  404.html, sitemap.xml, robots.txt

Uso:
  python3 build.py             genera el sitio
  python3 build.py --borradores  incluye también los artículos con fecha futura (solo para revisar)

Sin dependencias: Python 3 puro.
"""
import datetime as dt
import html
import json
import re
import shutil
import sys
from pathlib import Path
from urllib.parse import quote, urlparse

ROOT = Path(__file__).parent
CONTENT = ROOT / "content.json"
PLANTILLAS = ROOT / "plantillas"
PAGINAS_DIR = ROOT / "contenido" / "paginas"
BLOG_DIR = ROOT / "contenido" / "blog"

HOY = dt.date.today()
INCLUIR_BORRADORES = "--borradores" in sys.argv

# Carpetas que genera este script: se borran y se regeneran en cada build.
# (Nunca borrar a mano otra cosa del repo desde acá.)
GENERADAS_REGISTRO = ROOT / ".generadas.json"

ICONS = {
    "to": '<svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="12" r="6"></circle><circle cx="15" cy="12" r="6"></circle></svg>',
    "psicomotricidad": '<svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="5" r="2"></circle><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="13" x2="8" y2="19"></line><line x1="12" y1="13" x2="16" y2="19"></line><line x1="12" y1="10" x2="8" y2="13"></line><line x1="12" y1="10" x2="16" y2="13"></line></svg>',
    "fono": '<svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="5" width="16" height="10" rx="3"></rect><path d="M8 15L6 19L10 17Z"></path><circle cx="9" cy="10" r="0.8"></circle><circle cx="12" cy="10" r="0.8"></circle><circle cx="15" cy="10" r="0.8"></circle></svg>',
    "psicopedagogia": '<svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M12 7L4 6V17L12 18Z"></path><path d="M12 7L20 6V17L12 18Z"></path><line x1="12" y1="7" x2="12" y2="18"></line></svg>',
    "psicologia": '<svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="7"></circle><circle cx="12" cy="12" r="2.5"></circle><line x1="12" y1="3" x2="12" y2="5.5"></line><line x1="12" y1="18.5" x2="12" y2="21"></line></svg>',
}

CONTACT_ICONS = {
    "direccion": '<path d="M12 21C12 21 5 14 5 9A7 7 0 0 1 19 9C19 14 12 21 12 21Z"></path><circle cx="12" cy="9" r="2.4"></circle>',
    "telefono": '<path d="M5 4H9L11 9L8.5 10.5C9.5 12.8 11.2 14.5 13.5 15.5L15 13L20 15V19C20 20.1 19.1 21 18 21C10.8 21 5 15.2 5 8C5 6.9 5 4 5 4Z"></path>',
    "email": '<rect x="3" y="5" width="18" height="14" rx="2"></rect><path d="M3 7L12 13L21 7"></path>',
    "horario": '<circle cx="12" cy="12" r="8.5"></circle><line x1="12" y1="12" x2="12" y2="7"></line><line x1="12" y1="12" x2="16" y2="14"></line>',
}

AVISOS = []


def es_dato_pendiente(valor):
    """Un dato entre corchetes ("[+598 XXX XXX]") es un placeholder: nunca se publica."""
    return not valor or bool(re.search(r"\[[^\]]*\]", str(valor)))


# ---------------------------------------------------------------- Markdown mínimo

def parse_front_matter(texto, origen):
    if not texto.startswith("---"):
        raise ValueError(f"{origen}: falta el bloque --- de datos al principio")
    _, fm, cuerpo = texto.split("---", 2)
    datos = {}
    for linea in fm.strip().splitlines():
        if ":" in linea:
            clave, valor = linea.split(":", 1)
            datos[clave.strip()] = valor.strip()
    return datos, cuerpo.strip()


def inline_md(texto, base):
    t = html.escape(texto, quote=False)

    def link(m):
        etiqueta, url = m.group(1), m.group(2)
        if url.startswith("/"):
            return f'<a href="{base}{url}">{etiqueta}</a>'
        if url.startswith("http"):
            return f'<a href="{url}" target="_blank" rel="noopener">{etiqueta}</a>'
        return f'<a href="{url}">{etiqueta}</a>'

    t = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![*\w])\*([^*\n]+)\*(?![*\w])", r"<em>\1</em>", t)
    return t


def md_a_bloques(cuerpo):
    """Divide el markdown en bloques: ('h2', txt) ('h3', txt) ('p', txt) ('ul', [..]) ('ol', [..])."""
    bloques, parrafo, lista, tipo_lista = [], [], [], None

    def cerrar():
        nonlocal parrafo, lista, tipo_lista
        if parrafo:
            bloques.append(("p", " ".join(parrafo)))
            parrafo = []
        if lista:
            bloques.append((tipo_lista, lista))
            lista, tipo_lista = [], None

    for linea in cuerpo.splitlines():
        l = linea.strip()
        if not l:
            cerrar()
        elif l.startswith("### "):
            cerrar(); bloques.append(("h3", l[4:].strip()))
        elif l.startswith("## "):
            cerrar(); bloques.append(("h2", l[3:].strip()))
        elif l.startswith("# "):
            cerrar(); bloques.append(("h2", l[2:].strip()))  # el H1 es siempre el título
        elif re.match(r"^[-*] ", l):
            if parrafo or tipo_lista == "ol":
                cerrar()
            tipo_lista = "ul"; lista.append(l[2:].strip())
        elif re.match(r"^\d+[.)] ", l):
            if parrafo or tipo_lista == "ul":
                cerrar()
            tipo_lista = "ol"; lista.append(re.sub(r"^\d+[.)] ", "", l))
        else:
            if lista:
                cerrar()
            parrafo.append(l)
    cerrar()
    return bloques


def slugify(texto):
    t = texto.lower()
    for a, b in zip("áéíóúüñ", "aeiouun"):
        t = t.replace(a, b)
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def bloques_a_html(bloques, base):
    out = []
    for tipo, valor in bloques:
        if tipo in ("h2", "h3"):
            out.append(f'<{tipo} id="{slugify(valor)}">{inline_md(valor, base)}</{tipo}>')
        elif tipo == "p":
            out.append(f"<p>{inline_md(valor, base)}</p>")
        else:
            items = "".join(f"<li>{inline_md(i, base)}</li>" for i in valor)
            out.append(f"<{tipo}>{items}</{tipo}>")
    return "\n".join(out)


def extraer_faq(bloques):
    """Pares (pregunta, respuesta) de la sección '## Preguntas frecuentes'."""
    faq, dentro, pregunta, respuesta = [], False, None, []
    for tipo, valor in bloques:
        if tipo == "h2":
            if pregunta:
                faq.append((pregunta, " ".join(respuesta)))
                pregunta, respuesta = None, []
            dentro = valor.lower().startswith("preguntas frecuentes")
            continue
        if not dentro:
            continue
        if tipo == "h3":
            if pregunta:
                faq.append((pregunta, " ".join(respuesta)))
            pregunta, respuesta = valor, []
        elif tipo == "p" and pregunta:
            respuesta.append(valor)
        elif tipo in ("ul", "ol") and pregunta:
            respuesta.append(" ".join(valor))
    if pregunta:
        faq.append((pregunta, " ".join(respuesta)))
    limpiar = lambda t: re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t).replace("**", "").replace("*", "")
    return [(limpiar(q), limpiar(a)) for q, a in faq if a]


def contar_palabras(cuerpo):
    return len(re.findall(r"\w+", cuerpo))


# ---------------------------------------------------------------- Piezas compartidas

def jsonld(obj):
    return '<script type="application/ld+json">\n' + json.dumps(obj, ensure_ascii=False, indent=2) + "\n</script>"


def breadcrumb_ld(sitio_url, migas):
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": nombre, "item": sitio_url + ruta}
            for i, (nombre, ruta) in enumerate(migas)
        ],
    }


def faq_ld(faq):
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in faq
        ],
    }


def clinica_ld(c, sitio_url, servicios):
    ct = c["contacto"]
    d = {
        "@context": "https://schema.org",
        "@type": "MedicalClinic",
        "@id": sitio_url + "/#clinica",
        "name": c["site_title"],
        "description": c["meta_description"],
        "url": sitio_url + "/",
        "logo": sitio_url + "/assets/logo-444.png",
        "image": sitio_url + "/assets/og-imagen.png",
        "address": {
            "@type": "PostalAddress",
            "streetAddress": ct["calle"],
            "addressLocality": ct["ciudad"],
            "addressRegion": ct["departamento"],
            "postalCode": ct["codigo_postal"],
            "addressCountry": "UY",
        },
        "areaServed": [{"@type": "City", "name": z} for z in ct.get("zona_de_atencion", [])],
        "availableService": [
            {"@type": "MedicalTherapy", "name": s["title"], "url": sitio_url + f"/{s['pagina']}/"}
            for s in servicios
        ],
        "isAcceptingNewPatients": True,
    }
    if not es_dato_pendiente(ct.get("email")):
        d["email"] = ct["email"]
    if not es_dato_pendiente(ct.get("telefono")):
        d["telephone"] = ct["telefono"]
    if ct.get("latitud") and ct.get("longitud"):
        d["geo"] = {"@type": "GeoCoordinates", "latitude": ct["latitud"], "longitude": ct["longitud"]}
    if ct.get("horario_schema"):
        d["openingHoursSpecification"] = ct["horario_schema"]
    if ct.get("perfiles"):
        d["sameAs"] = ct["perfiles"]
    return d


def build_nav(items, base, actual):
    lineas = []
    for item in items:
        href = base + item["href"]
        marca = ' aria-current="page"' if item["href"] == actual else ""
        lineas.append(f'      <a href="{href}" class="text-link"{marca} style="font-size: 15px; font-weight: 500; color: #2E2B15;">{item["label"]}</a>')
    return "\n".join(lineas)


def build_whatsapp_button(digits):
    digits = (digits or "").strip()
    if not digits:
        return ""
    return f'''<a href="https://wa.me/{digits}" target="_blank" rel="noopener" aria-label="Escribir por WhatsApp" style="position: fixed; bottom: 24px; right: 24px; width: 56px; height: 56px; border-radius: 50%; background: #25D366; display: flex; align-items: center; justify-content: center; box-shadow: 0 8px 20px rgba(0,0,0,0.25); z-index: 100;">
  <svg viewBox="0 0 24 24" width="30" height="30" fill="#FFFFFF" aria-hidden="true"><path d="M12.04 2C6.58 2 2.13 6.45 2.13 11.91c0 1.75.46 3.45 1.32 4.95L2 22l5.29-1.39a9.9 9.9 0 0 0 4.75 1.21h.01c5.46 0 9.9-4.45 9.9-9.91C21.96 6.45 17.5 2 12.04 2zm5.8 14.08c-.24.68-1.4 1.3-1.94 1.38-.5.08-1.12.11-1.81-.11-.42-.13-.95-.31-1.64-.6-2.88-1.24-4.76-4.14-4.9-4.33-.14-.19-1.17-1.56-1.17-2.98 0-1.42.74-2.11 1.01-2.4.26-.28.57-.35.76-.35h.55c.17 0 .41-.03.63.48.24.57.81 1.99.88 2.13.07.14.11.31.02.5-.09.19-.14.31-.28.47-.14.17-.29.37-.42.5-.14.14-.28.29-.12.57.16.28.72 1.19 1.55 1.92 1.06.95 1.96 1.24 2.24 1.38.28.14.44.12.6-.07.16-.19.68-.79.87-1.06.19-.28.37-.23.62-.14.26.09 1.63.77 1.91.91.28.14.47.21.53.33.07.13.07.71-.17 1.39z"></path></svg>
</a>'''


def contacto_items(ct, oscuro=True):
    color = "#FFFFFF" if oscuro else "#2E2B15"
    filas = []
    tel = ct.get("telefono")
    datos = [
        ("direccion", ct["direccion"], None),
        ("telefono", tel, f"tel:{re.sub(r'[^0-9+]', '', tel or '')}"),
        ("email", ct.get("email"), f"mailto:{ct.get('email')}"),
        ("horario", ct.get("horario"), None),
    ]
    for clave, valor, href in datos:
        if es_dato_pendiente(valor):
            AVISOS.append(f"contacto.{clave} sin completar: no se muestra en el sitio")
            continue
        texto = html.escape(valor)
        if href:
            texto = f'<a href="{href}" style="color: {color}; text-decoration: underline; text-underline-offset: 3px;">{texto}</a>'
        filas.append(f'''        <div style="display: flex; align-items: center; gap: 14px;">
          <svg aria-hidden="true" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#F09367" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">{CONTACT_ICONS[clave]}</svg>
          <span style="font-size: 15px; color: {color};">{texto}</span>
        </div>''')
    return "\n".join(filas)


def footer_contacto(ct):
    partes = []
    if not es_dato_pendiente(ct.get("telefono")):
        tel = ct["telefono"]
        partes.append(f'        <a class="footer-link" href="tel:{re.sub(r"[^0-9+]", "", tel)}">{html.escape(tel)}</a><br>')
    if not es_dato_pendiente(ct.get("email")):
        partes.append(f'        <a class="footer-link" href="mailto:{ct["email"]}">{html.escape(ct["email"])}</a>')
    return "\n".join(partes)


def pagina_completa(base_tpl, c, base, sitio_url, *, ruta, titulo, descripcion, contenido,
                    lds, og_tipo="website", nav_actual="", robots="index, follow"):
    tokens = {
        "titulo": html.escape(titulo),
        "descripcion": html.escape(descripcion),
        "url_canonica": sitio_url + ruta,
        "robots": robots,
        "og_tipo": og_tipo,
        "og_imagen": sitio_url + "/assets/og-imagen.png",
        "site_title": c["site_title"],
        "meta_tagline": c["meta_tagline"],
        "cta_header": c["cta_header"],
        "footer_wordmark": c["footer_wordmark"],
        "footer_copyright": c["footer"]["copyright"],
        "contacto_direccion": html.escape(c["contacto"]["direccion"]),
    }
    out = base_tpl
    out = out.replace("{{CONTENIDO}}", contenido)
    out = out.replace("{{JSONLD}}", "\n".join(jsonld(x) for x in lds))
    out = out.replace("{{NAV_LINKS}}", build_nav(c["nav"], base, nav_actual))
    out = out.replace("{{FOOTER_SERVICIOS}}", "\n".join(
        f'      <a class="footer-link" href="{base}/{s["pagina"]}/">{s["title"]}</a>' for s in c["servicios"]["items"]))
    out = out.replace("{{FOOTER_CONTACTO}}", footer_contacto(c["contacto"]))
    out = out.replace("{{WHATSAPP_BUTTON}}", build_whatsapp_button(c["contacto"].get("whatsapp_digits", "")))
    for k, v in tokens.items():
        out = out.replace("{{" + k + "}}", v)
    out = out.replace("{{BASE}}", base)
    return out


# ---------------------------------------------------------------- Portada

def build_servicios_cards(items, base):
    cards = []
    for item in items:
        cards.append(f'''      <a href="{base}/{item["pagina"]}/" class="card-link" style="background: #FBF9F4; border: 1px solid #EDE7D8; border-radius: 20px; padding: 32px; display: flex; flex-direction: column; gap: 16px; color: inherit;">
        <div aria-hidden="true" style="width: 56px; height: 56px; border-radius: 16px; background: {item["bg"]}; display: flex; align-items: center; justify-content: center; color: {item["fg"]};">
          {ICONS.get(item["icon"], "")}
        </div>
        <h3 style="margin: 0; font-size: 19px; font-weight: 600; color: #2E2B15;">{item["title"]}</h3>
        <p style="margin: 0; font-size: 15px; line-height: 1.6; color: #4A4736;">{item["desc"]}</p>
        <span style="margin-top: auto; font-size: 14px; font-weight: 600; color: #69662C;">{item["title"]} en Rivera →</span>
      </a>
''')
    return "\n".join(cards)


def build_convenios_pills(items):
    return "\n".join(f'''      <div style="background: #FFFFFF; border: 1.5px solid #69662C; border-radius: 999px; padding: 14px 22px; display: flex; align-items: center; gap: 10px;">
        <div aria-hidden="true" style="width: 8px; height: 8px; border-radius: 50%; background: {item["color"]}; flex-shrink: 0;"></div>
        <span style="font-size: 14px; font-weight: 600; color: #2E2B15;">{item["label"]}</span>
      </div>''' for item in items)


CATEGORIA_COLORES = {
    "Guías para familias": ("#F5D9CB", "#8A5240"),
    "Desarrollo infantil": ("#C2CCAB", "#3F4A2B"),
    "Aprendizaje y escuela": ("#FCEFD2", "#6E5418"),
    "Convenios y trámites": ("#E4E8D9", "#4F4C20"),
}


def fecha_legible(f):
    meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
             "septiembre", "octubre", "noviembre", "diciembre"]
    return f"{f.day} de {meses[f.month - 1]} de {f.year}"


def tarjeta_post(p, base):
    bg, fg = CATEGORIA_COLORES.get(p["categoria"], ("#F3EFE2", "#4F4C20"))
    return f'''      <a href="{base}/blog/{p["slug"]}/" class="card-link" style="border: 1px solid #EDE7D8; border-radius: 20px; overflow: hidden; display: flex; flex-direction: column; background: #FFFFFF; color: inherit;">
        <div aria-hidden="true" style="height: 8px; background: {bg};"></div>
        <div style="padding: 24px; display: flex; flex-direction: column; gap: 10px; flex: 1;">
          <span style="font-size: 12px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; color: {fg};">{html.escape(p["categoria"])}</span>
          <h3 style="margin: 0; font-size: 18px; font-weight: 600; color: #2E2B15; line-height: 1.4;">{html.escape(p["title"])}</h3>
          <p style="margin: 0; font-size: 14px; line-height: 1.6; color: #4A4736;">{html.escape(p["description"])}</p>
          <time datetime="{p["fecha"].isoformat()}" style="font-size: 13px; color: #6B5A40; margin-top: auto;">{fecha_legible(p["fecha"])}</time>
        </div>
      </a>
'''


# ---------------------------------------------------------------- Páginas interiores

def cabecera_interior(eyebrow, h1, intro, migas, base):
    miga_html = " <span aria-hidden=\"true\">/</span> ".join(
        f'<a href="{base}{ruta}" style="color: #6B5A40;">{html.escape(n)}</a>' if i < len(migas) - 1
        else f'<span aria-current="page">{html.escape(n)}</span>'
        for i, (n, ruta) in enumerate(migas))
    return f'''<section style="width: 100%; background: #F3EFE2;">
  <div style="max-width: 1200px; margin: 0 auto; padding: 40px 32px 64px;">
    <nav aria-label="Ruta de navegación" style="font-size: 14px; color: #6B5A40; margin-bottom: 32px;">{miga_html}</nav>
    <div style="max-width: 780px; display: flex; flex-direction: column; gap: 16px;">
      <span style="font-size: 13px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: #8A5240;">{html.escape(eyebrow)}</span>
      <h1 style="margin: 0; font-size: 44px; line-height: 1.15; font-weight: 700; color: #2E2B15;">{html.escape(h1)}</h1>
      {f'<p style="margin: 0; font-size: 19px; line-height: 1.6; color: #4A4736;">{intro}</p>' if intro else ''}
    </div>
  </div>
</section>'''


def aside_cta(c, base, texto_extra=""):
    return f'''<aside style="position: sticky; top: 24px; background: #69662C; border-radius: 20px; padding: 32px; display: flex; flex-direction: column; gap: 14px; color: #FFFFFF;">
      <h2 style="margin: 0; font-size: 20px; font-weight: 600; color: #FFFFFF;">¿Querés hacer una consulta?</h2>
      <p style="margin: 0; font-size: 15px; line-height: 1.6; color: #E4E4D5;">Te orientamos según la edad y la situación de tu hijo o hija. {texto_extra}</p>
      <a href="{base}/contacto/" class="btn btn-solid-inverse" style="background: #FFFFFF; color: #69662C; padding: 12px 20px; border-radius: 999px; font-weight: 600; font-size: 14px; align-self: flex-start;">{c["cta_header"]}</a>
      <p style="margin: 8px 0 0; font-size: 13px; line-height: 1.6; color: #E4E4D5;">{html.escape(c["contacto"]["direccion"])}</p>
    </aside>'''


def cuerpo_con_aside(prosa_html, aside_html, extra_abajo=""):
    return f'''<section style="width: 100%; background: #FFFFFF;">
  <div class="articulo-grid" style="max-width: 1200px; margin: 0 auto; padding: 72px 32px; display: grid; grid-template-columns: minmax(0, 1fr) 320px; gap: 64px; align-items: start;">
    <div class="prose" style="max-width: 720px;">
{prosa_html}
    </div>
    {aside_html}
  </div>
{extra_abajo}
</section>'''


def cargar_md(carpeta):
    docs = []
    if not carpeta.exists():
        return docs
    for f in sorted(carpeta.glob("*.md")):
        if f.name.startswith("_"):
            continue  # notas internas (plan editorial, etc.): no se publican
        datos, cuerpo = parse_front_matter(f.read_text(encoding="utf-8"), f.name)
        faltan = [k for k in ("title", "slug", "description") if not datos.get(k)]
        if faltan:
            raise ValueError(f"{f.name}: faltan datos obligatorios {faltan}")
        datos["cuerpo"], datos["archivo"] = cuerpo, f.name
        if "[DATO A CONFIRMAR" in cuerpo:
            AVISOS.append(f"{f.name}: tiene [DATO A CONFIRMAR] pendientes")
        if len(datos["title"]) > 65:
            AVISOS.append(f"{f.name}: título de {len(datos['title'])} caracteres (Google corta en ~60)")
        if not 110 <= len(datos["description"]) <= 165:
            AVISOS.append(f"{f.name}: descripción de {len(datos['description'])} caracteres (ideal 140-160)")
        docs.append(datos)
    return docs


# ---------------------------------------------------------------- Main

def main():
    c = json.loads(CONTENT.read_text(encoding="utf-8"))
    sitio_url = c["sitio"]["url"].rstrip("/")
    base = urlparse(sitio_url).path.rstrip("/")  # "/clinicatrazosweb" en GitHub Pages, "" con dominio propio
    base_tpl = (PLANTILLAS / "base.html").read_text(encoding="utf-8")
    servicios = c["servicios"]["items"]
    archivos = {}  # ruta relativa -> contenido
    sitemap = []   # (ruta, lastmod)

    # ---- Blog
    posts = []
    programados = []
    for p in cargar_md(BLOG_DIR):
        p["fecha"] = dt.date.fromisoformat(p.get("fecha", HOY.isoformat()))
        p.setdefault("categoria", "Guías para familias")
        pendiente = "[DATO A CONFIRMAR" in p["cuerpo"]
        if (p["fecha"] > HOY or pendiente) and not INCLUIR_BORRADORES:
            p["motivo"] = "tiene [DATO A CONFIRMAR]" if pendiente else "fecha futura"
            programados.append(p)
            continue
        posts.append(p)
    posts.sort(key=lambda p: p["fecha"], reverse=True)

    # ---- Portada
    inicio = (PLANTILLAS / "inicio.html").read_text(encoding="utf-8")
    ct = c["contacto"]
    tok = {
        "site_title": c["site_title"],
        "hero_place": c["hero"]["place"], "hero_badge": c["hero"]["badge"],
        "hero_title": c["hero"]["title"], "hero_subtitle": c["hero"]["subtitle"],
        "hero_modalidad_presencial": c["hero"]["modalidad_presencial"],
        "hero_modalidad_online": c["hero"]["modalidad_online"],
        "hero_cta_primary": c["hero"]["cta_primary"], "hero_cta_secondary": c["hero"]["cta_secondary"],
        "hero_badge_media": c["hero"]["badge_media"],
        "servicios_eyebrow": c["servicios"]["eyebrow"], "servicios_title": c["servicios"]["title"],
        "servicios_cta_title": c["servicios"]["cta_title"], "servicios_cta_text": c["servicios"]["cta_text"],
        "servicios_cta_button": c["servicios"]["cta_button"],
        "convenios_eyebrow": c["convenios"]["eyebrow"], "convenios_title": c["convenios"]["title"],
        "convenios_subtitle": c["convenios"]["subtitle"],
        "novedades_eyebrow": c["novedades"]["eyebrow"], "novedades_title": c["novedades"]["title"],
        "novedades_ver_todas": c["novedades"]["ver_todas"],
        "contacto_eyebrow": ct["eyebrow"], "contacto_title": ct["title"], "contacto_subtitle": ct["subtitle"],
        "contacto_form_title": ct["form_title"], "contacto_form_button": ct["form_button"],
        "contacto_form_email": ct["form_email"],
    }
    for k, v in tok.items():
        inicio = inicio.replace("{{" + k + "}}", v)
    inicio = inicio.replace("{{SERVICIOS_CARDS}}", build_servicios_cards(servicios, base))
    inicio = inicio.replace("{{CONVENIOS_PILLS}}", build_convenios_pills(c["convenios"]["items"]))
    inicio = inicio.replace("{{CONTACTO_ITEMS}}", contacto_items(ct))
    inicio = inicio.replace("{{contacto_mapa_embed_url}}", f"https://www.google.com/maps?q={quote(ct['direccion'])}&output=embed")
    if posts:
        inicio = inicio.replace("{{BLOG_INICIO_ABRE}}", "").replace("{{BLOG_INICIO_CIERRA}}", "")
        inicio = inicio.replace("{{NOVEDADES_CARDS}}", "".join(tarjeta_post(p, base) for p in posts[:3]))
    else:
        inicio = re.sub(r"\{\{BLOG_INICIO_ABRE\}\}.*?\{\{BLOG_INICIO_CIERRA\}\}", "", inicio, flags=re.S)
    home_lds = [
        clinica_ld(c, sitio_url, servicios),
        {"@context": "https://schema.org", "@type": "WebSite", "name": c["site_title"], "url": sitio_url + "/", "inLanguage": "es-UY"},
    ]
    archivos["index.html"] = pagina_completa(
        base_tpl, c, base, sitio_url, ruta="/", titulo=c["seo_titulo_inicio"],
        descripcion=c["meta_description"], contenido=inicio, lds=home_lds, nav_actual="/")
    sitemap.append(("/", HOY))

    # ---- Páginas (servicios, convenios, contacto)
    por_servicio = {s["pagina"]: s for s in servicios}
    for pg in cargar_md(PAGINAS_DIR):
        ruta = f"/{pg['slug']}/"
        bloques = md_a_bloques(pg["cuerpo"])
        faq = extraer_faq(bloques)
        migas = [("Inicio", "/"), (pg.get("miga", pg["h1"] if pg.get("h1") else pg["title"]), ruta)]
        serv = por_servicio.get(pg["slug"])
        relacionados = [p for p in posts if p.get("servicio") and pg["slug"].startswith(p["servicio"])][:3]
        extra = ""
        if relacionados:
            extra = f'''  <div style="max-width: 1200px; margin: 0 auto; padding: 0 32px 72px;">
    <h2 style="font-size: 24px; color: #2E2B15; margin: 0 0 24px;">Artículos relacionados</h2>
    <div class="novedades-grid" style="display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 24px;">
{"".join(tarjeta_post(p, base) for p in relacionados)}
    </div>
  </div>'''
        if pg["slug"] == "contacto":
            aside = f'''<aside style="background: #2E2B15; border-radius: 20px; padding: 32px; display: flex; flex-direction: column; gap: 18px;">
      <h2 style="margin: 0; font-size: 20px; font-weight: 600; color: #FFFFFF;">Datos de contacto</h2>
{contacto_items(ct)}
    </aside>'''
            mapa = f'''  <div style="max-width: 1200px; margin: 0 auto; padding: 0 32px 72px;">
    <div style="border-radius: 20px; overflow: hidden; line-height: 0;">
      <iframe src="https://www.google.com/maps?q={quote(ct['direccion'])}&amp;output=embed" width="100%" height="360" style="border: 0; display: block;" allowfullscreen loading="lazy" referrerpolicy="no-referrer-when-downgrade" title="Mapa: {html.escape(c['site_title'])}, {html.escape(ct['direccion'])}"></iframe>
    </div>
  </div>'''
            extra = mapa + extra
        else:
            aside = aside_cta(c, base)
        contenido = cabecera_interior(pg.get("eyebrow", ""), pg.get("h1", pg["title"]),
                                      inline_md(pg.get("intro", ""), base), migas, base)
        contenido += "\n" + cuerpo_con_aside(bloques_a_html(bloques, base), aside, extra)
        lds = [breadcrumb_ld(sitio_url, migas)]
        if serv:
            lds.append({
                "@context": "https://schema.org",
                "@type": "MedicalTherapy",
                "name": serv["title"],
                "description": pg["description"],
                "url": sitio_url + ruta,
                "provider": {"@id": sitio_url + "/#clinica"},
            })
        if pg["slug"] == "contacto":
            lds.append(clinica_ld(c, sitio_url, servicios))
        if faq:
            lds.append(faq_ld(faq))
        archivos[f"{pg['slug']}/index.html"] = pagina_completa(
            base_tpl, c, base, sitio_url, ruta=ruta, titulo=pg["title"], descripcion=pg["description"],
            contenido=contenido, lds=lds, nav_actual=ruta)
        sitemap.append((ruta, HOY))
        if pg["slug"] != "contacto" and contar_palabras(pg["cuerpo"]) < 300:
            AVISOS.append(f"{pg['archivo']}: solo {contar_palabras(pg['cuerpo'])} palabras (poco contenido para posicionar)")

    # ---- Blog: índice y artículos
    migas_blog = [("Inicio", "/"), ("Blog", "/blog/")]
    if posts:
        lista = "".join(tarjeta_post(p, base) for p in posts)
        cuerpo_blog = f'''<section style="width: 100%; background: #FFFFFF;">
  <div style="max-width: 1200px; margin: 0 auto; padding: 72px 32px;">
    <div class="novedades-grid" style="display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 24px;">
{lista}
    </div>
  </div>
</section>'''
    else:
        cuerpo_blog = '<section style="background: #FFFFFF;"><div style="max-width: 1200px; margin: 0 auto; padding: 72px 32px;"><p>Pronto vas a encontrar acá artículos para familias.</p></div></section>'
    contenido = cabecera_interior("Blog", "Blog para familias",
                                  "Guías sobre desarrollo infantil, aprendizaje y trámites, escritas por el equipo de Clínica Trazos en Rivera.",
                                  migas_blog, base) + "\n" + cuerpo_blog
    archivos["blog/index.html"] = pagina_completa(
        base_tpl, c, base, sitio_url, ruta="/blog/",
        titulo="Blog para familias | Clínica Trazos, Rivera",
        descripcion="Guías sobre desarrollo infantil, lenguaje, aprendizaje y trámites de BPS para familias de Rivera, escritas por el equipo de Clínica Trazos.",
        contenido=contenido, lds=[breadcrumb_ld(sitio_url, migas_blog)], nav_actual="/blog/",
        robots="index, follow" if posts else "noindex, follow")
    if posts:
        sitemap.append(("/blog/", max(p["fecha"] for p in posts)))

    for p in posts:
        ruta = f"/blog/{p['slug']}/"
        bloques = md_a_bloques(p["cuerpo"])
        faq = extraer_faq(bloques)
        migas = migas_blog + [(p["title"], ruta)]
        serv = por_servicio.get(next((s["pagina"] for s in servicios if s["pagina"].startswith(p.get("servicio", "-"))), ""), None)
        texto_serv = f'Conocé cómo trabajamos <a href="{base}/{serv["pagina"]}/" style="color: #FFFFFF; text-decoration: underline;">{serv["title"].lower()}</a> en la clínica.' if serv else ""
        meta = f'<p style="margin: 0 0 32px; font-size: 14px; color: #6B5A40;">Por {html.escape(p.get("autor", "Equipo Clínica Trazos"))} · <time datetime="{p["fecha"].isoformat()}">{fecha_legible(p["fecha"])}</time></p>'
        contenido = cabecera_interior(p["categoria"], p["title"], "", migas, base)
        contenido += "\n" + cuerpo_con_aside(meta + bloques_a_html(bloques, base), aside_cta(c, base, texto_serv))
        lds = [
            breadcrumb_ld(sitio_url, migas),
            {
                "@context": "https://schema.org",
                "@type": "BlogPosting",
                "headline": p["title"],
                "description": p["description"],
                "datePublished": p["fecha"].isoformat(),
                "dateModified": p.get("actualizado", p["fecha"].isoformat()),
                "inLanguage": "es-UY",
                "mainEntityOfPage": sitio_url + ruta,
                "image": sitio_url + "/assets/og-imagen.png",
                "author": {"@type": "Organization", "name": c["site_title"], "url": sitio_url + "/"},
                "publisher": {"@id": sitio_url + "/#clinica"},
                "keywords": ", ".join(x for x in [p.get("keyword", "")] + p.get("keywords_secundarias", "").split(",") if x.strip()),
            },
        ]
        if faq:
            lds.append(faq_ld(faq))
        archivos[f"blog/{p['slug']}/index.html"] = pagina_completa(
            base_tpl, c, base, sitio_url, ruta=ruta, titulo=f"{p['title']} | Clínica Trazos",
            descripcion=p["description"], contenido=contenido, lds=lds, og_tipo="article", nav_actual="/blog/")
        sitemap.append((ruta, p["fecha"]))

    # ---- 404
    contenido404 = cabecera_interior("Error 404", "No encontramos esta página",
                                     f'Puede que el link esté mal escrito o que la página se haya movido. <a href="{base}/">Volver al inicio</a> o <a href="{base}/contacto/">escribinos</a>.',
                                     [("Inicio", "/"), ("Página no encontrada", "/404.html")], base)
    archivos["404.html"] = pagina_completa(
        base_tpl, c, base, sitio_url, ruta="/404.html", titulo="Página no encontrada | Clínica Trazos",
        descripcion=c["meta_description"], contenido=contenido404, lds=[], robots="noindex, follow")

    # ---- sitemap.xml y robots.txt
    urls = "\n".join(f"  <url><loc>{sitio_url}{r}</loc><lastmod>{f.isoformat()}</lastmod></url>" for r, f in sitemap)
    archivos["sitemap.xml"] = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n'
    archivos["robots.txt"] = f"User-agent: *\nAllow: /\nDisallow: {base}/contenido/\nDisallow: {base}/plantillas/\nDisallow: {base}/mockup/\n\nSitemap: {sitio_url}/sitemap.xml\n"

    # ---- Escribir (borrando primero lo generado en el build anterior)
    previas = json.loads(GENERADAS_REGISTRO.read_text()) if GENERADAS_REGISTRO.exists() else []
    for rel in previas:
        f = ROOT / rel
        if f.exists() and rel not in archivos:
            f.unlink()
            try:
                f.parent.rmdir() if f.parent != ROOT else None
                f.parent.parent.rmdir() if f.parent.parent != ROOT else None
            except OSError:
                pass
    for rel, texto in archivos.items():
        destino = ROOT / rel
        destino.parent.mkdir(parents=True, exist_ok=True)
        restos = re.findall(r"\{\{[A-Za-z_]+\}\}", texto)
        if restos:
            AVISOS.append(f"{rel}: quedaron placeholders sin reemplazar {set(restos)}")
        destino.write_text(texto, encoding="utf-8")
    GENERADAS_REGISTRO.write_text(json.dumps(sorted(archivos), indent=1))

    print(f"Listo: {len(archivos)} archivos generados para {sitio_url}/")
    print(f"  Páginas en el sitemap: {len(sitemap)}  ·  Artículos publicados: {len(posts)}")
    if programados:
        print(f"  Artículos NO publicados: {len(programados)}")
        for p in sorted(programados, key=lambda p: p["fecha"]):
            print(f"    {p['fecha']}  {p['title']}  ({p['motivo']})")
    if AVISOS:
        print("\nAtención:")
        for a in dict.fromkeys(AVISOS):
            print("  -", a)


if __name__ == "__main__":
    main()
