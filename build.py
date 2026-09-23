#!/usr/bin/env python3
"""
Genera index.html a partir de template.html + content.json.

Uso: python3 build.py
"""
import json
import re
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).parent
TEMPLATE = ROOT / "template.html"
CONTENT = ROOT / "content.json"
OUTPUT = ROOT / "index.html"

ICONS = {
    "to": '<svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="12" r="6"></circle><circle cx="15" cy="12" r="6"></circle></svg>',
    "psicomotricidad": '<svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="5" r="2"></circle><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="13" x2="8" y2="19"></line><line x1="12" y1="13" x2="16" y2="19"></line><line x1="12" y1="10" x2="8" y2="13"></line><line x1="12" y1="10" x2="16" y2="13"></line></svg>',
    "fono": '<svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="5" width="16" height="10" rx="3"></rect><path d="M8 15L6 19L10 17Z"></path><circle cx="9" cy="10" r="0.8"></circle><circle cx="12" cy="10" r="0.8"></circle><circle cx="15" cy="10" r="0.8"></circle></svg>',
    "psicopedagogia": '<svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M12 7L4 6V17L12 18Z"></path><path d="M12 7L20 6V17L12 18Z"></path><line x1="12" y1="7" x2="12" y2="18"></line></svg>',
    "psicologia": '<svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="7"></circle><circle cx="12" cy="12" r="2.5"></circle><line x1="12" y1="3" x2="12" y2="5.5"></line><line x1="12" y1="18.5" x2="12" y2="21"></line></svg>',
}


def build_nav(items):
    lines = []
    for item in items:
        lines.append(
            f'      <a href="{item["href"]}" style="font-size: 15px; font-weight: 500; color: #2E2B15;">{item["label"]}</a>'
        )
    return "\n".join(lines)


def build_servicios_cards(items):
    cards = []
    for item in items:
        icon_svg = ICONS.get(item["icon"], "")
        cards.append(f'''      <div style="background: #FBF9F4; border: 1px solid #EDE7D8; border-radius: 20px; padding: 32px; display: flex; flex-direction: column; gap: 16px;">
        <div style="width: 56px; height: 56px; border-radius: 16px; background: {item["bg"]}; display: flex; align-items: center; justify-content: center; color: {item["fg"]};">
          {icon_svg}
        </div>
        <h3 style="margin: 0; font-size: 19px; font-weight: 600; color: #2E2B15;">{item["title"]}</h3>
        <p style="margin: 0; font-size: 15px; line-height: 1.6; color: #4A4736;">{item["desc"]}</p>
      </div>
''')
    return "\n".join(cards)


def build_convenios_pills(items):
    pills = []
    for item in items:
        pills.append(f'''      <div style="background: #FFFFFF; border: 1.5px solid #69662C; border-radius: 999px; padding: 14px 22px; display: flex; align-items: center; gap: 10px;">
        <div style="width: 8px; height: 8px; border-radius: 50%; background: {item["color"]}; flex-shrink: 0;"></div>
        <span style="font-size: 14px; font-weight: 600; color: #2E2B15;">{item["label"]}</span>
      </div>''')
    return "\n".join(pills)


def build_whatsapp_button(digits):
    digits = (digits or "").strip()
    if not digits:
        return ""
    return f'''<a href="https://wa.me/{digits}" target="_blank" rel="noopener" aria-label="Escribir por WhatsApp" style="position: fixed; bottom: 24px; right: 24px; width: 56px; height: 56px; border-radius: 50%; background: #25D366; display: flex; align-items: center; justify-content: center; box-shadow: 0 8px 20px rgba(0,0,0,0.25); z-index: 100;">
  <svg viewBox="0 0 24 24" width="30" height="30" fill="#FFFFFF"><path d="M12.04 2C6.58 2 2.13 6.45 2.13 11.91c0 1.75.46 3.45 1.32 4.95L2 22l5.29-1.39a9.9 9.9 0 0 0 4.75 1.21h.01c5.46 0 9.9-4.45 9.9-9.91C21.96 6.45 17.5 2 12.04 2zm5.8 14.08c-.24.68-1.4 1.3-1.94 1.38-.5.08-1.12.11-1.81-.11-.42-.13-.95-.31-1.64-.6-2.88-1.24-4.76-4.14-4.9-4.33-.14-.19-1.17-1.56-1.17-2.98 0-1.42.74-2.11 1.01-2.4.26-.28.57-.35.76-.35h.55c.17 0 .41-.03.63.48.24.57.81 1.99.88 2.13.07.14.11.31.02.5-.09.19-.14.31-.28.47-.14.17-.29.37-.42.5-.14.14-.28.29-.12.57.16.28.72 1.19 1.55 1.92 1.06.95 1.96 1.24 2.24 1.38.28.14.44.12.6-.07.16-.19.68-.79.87-1.06.19-.28.37-.23.62-.14.26.09 1.63.77 1.91.91.28.14.47.21.53.33.07.13.07.71-.17 1.39z"></path></svg>
</a>'''


def build_novedades_cards(posts):
    cards = []
    for post in posts:
        cards.append(f'''      <div style="border: 1px solid #EDE7D8; border-radius: 20px; overflow: hidden; display: flex; flex-direction: column;">
        <div style="height: 160px; background: {post["bg"]}; display: flex; align-items: center; justify-content: center;">
          <span style="font-size: 13px; color: {post["img_color"]}; font-weight: 500;">[Imagen de la novedad]</span>
        </div>
        <div style="padding: 24px; display: flex; flex-direction: column; gap: 10px;">
          <span style="font-size: 12px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; color: {post["cat_color"]};">{post["category"]}</span>
          <h3 style="margin: 0; font-size: 17px; font-weight: 600; color: #2E2B15; line-height: 1.4;">{post["title"]}</h3>
          <p style="margin: 0; font-size: 14px; line-height: 1.6; color: #4A4736;">{post["excerpt"]}</p>
          <span style="font-size: 13px; color: #8A8567; margin-top: 4px;">{post["date"]}</span>
        </div>
      </div>
''')
    return "\n".join(cards)


def main():
    content = json.loads(CONTENT.read_text(encoding="utf-8"))
    html = TEMPLATE.read_text(encoding="utf-8")

    tokens = {
        "site_title": content["site_title"],
        "meta_tagline": content["meta_tagline"],
        "meta_description": content["meta_description"],
        "logo_mark": content["logo_mark"],
        "footer_wordmark": content["footer_wordmark"],
        "cta_header": content["cta_header"],
        "hero_place": content["hero"]["place"],
        "hero_badge": content["hero"]["badge"],
        "hero_title": content["hero"]["title"],
        "hero_subtitle": content["hero"]["subtitle"],
        "hero_modalidad_presencial": content["hero"]["modalidad_presencial"],
        "hero_modalidad_online": content["hero"]["modalidad_online"],
        "hero_cta_primary": content["hero"]["cta_primary"],
        "hero_cta_secondary": content["hero"]["cta_secondary"],
        "hero_badge_media": content["hero"]["badge_media"],
        "servicios_eyebrow": content["servicios"]["eyebrow"],
        "servicios_title": content["servicios"]["title"],
        "servicios_cta_title": content["servicios"]["cta_title"],
        "servicios_cta_text": content["servicios"]["cta_text"],
        "servicios_cta_button": content["servicios"]["cta_button"],
        "convenios_eyebrow": content["convenios"]["eyebrow"],
        "convenios_title": content["convenios"]["title"],
        "convenios_subtitle": content["convenios"]["subtitle"],
        "novedades_eyebrow": content["novedades"]["eyebrow"],
        "novedades_title": content["novedades"]["title"],
        "novedades_ver_todas": content["novedades"]["ver_todas"],
        "contacto_eyebrow": content["contacto"]["eyebrow"],
        "contacto_title": content["contacto"]["title"],
        "contacto_subtitle": content["contacto"]["subtitle"],
        "contacto_direccion": content["contacto"]["direccion"],
        "contacto_telefono": content["contacto"]["telefono"],
        "contacto_email": content["contacto"]["email"],
        "contacto_horario": content["contacto"]["horario"],
        "contacto_mapa_embed_url": f"https://www.google.com/maps?q={quote(content['contacto']['direccion'])}&output=embed",
        "contacto_form_title": content["contacto"]["form_title"],
        "contacto_form_button": content["contacto"]["form_button"],
        "contacto_form_email": content["contacto"]["form_email"],
        "footer_copyright": content["footer"]["copyright"],
    }

    for key, value in tokens.items():
        html = html.replace("{{" + key + "}}", value)

    html = html.replace("{{NAV_LINKS}}", build_nav(content["nav"]))
    html = html.replace("{{SERVICIOS_CARDS}}", build_servicios_cards(content["servicios"]["items"]))
    html = html.replace("{{CONVENIOS_PILLS}}", build_convenios_pills(content["convenios"]["items"]))
    html = html.replace("{{NOVEDADES_CARDS}}", build_novedades_cards(content["novedades"]["posts"]))
    html = html.replace("{{WHATSAPP_BUTTON}}", build_whatsapp_button(content["contacto"].get("whatsapp_digits", "")))

    remaining = re.findall(r"\{\{[a-zA-Z_]+\}\}", html)
    if remaining:
        print("Atención: quedaron placeholders sin reemplazar:", set(remaining))

    OUTPUT.write_text(html, encoding="utf-8")
    print(f"Listo: {OUTPUT}")


if __name__ == "__main__":
    main()
