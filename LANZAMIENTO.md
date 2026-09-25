# Lanzamiento y SEO — lista de tareas

El código ya resuelve el SEO técnico: páginas por servicio, títulos, descripciones, datos
estructurados, sitemap y velocidad. Lo que sigue depende de datos o de cuentas de la clínica, y
es lo que más pesa para aparecer en Google Maps y en las búsquedas locales.

## 1. Antes de publicar (bloqueante)

- [ ] **Teléfono** en `content.json` → `contacto.telefono`. Sin teléfono, Google no puede mostrar el botón "Llamar".
- [ ] **WhatsApp** en `contacto.whatsapp_digits`, solo números y con código de país (ej. `59899123456`). Activa el botón flotante.
- [ ] **Horario** en `contacto.horario` (texto visible) y en `contacto.horario_schema` (para Google), por ejemplo:
  `[{"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday"], "opens": "08:00", "closes": "19:00"}]`
- [ ] **Revisar con el equipo** las páginas de `contenido/paginas/` y los artículos del blog: es contenido de salud, así que cada texto debe estar validado por el profesional del área.
- [ ] Opcional: `latitud` y `longitud` de la clínica (clic derecho en Google Maps → copiar coordenadas).

## 2. Google Search Console (el mismo día que se publica)

1. Entrar a <https://search.google.com/search-console> con la cuenta de la clínica.
2. Agregar una propiedad de tipo **Prefijo de URL**: `https://hugoabrahamherrera-gif.github.io/clinicatrazosweb/`
3. Verificar con el método **Etiqueta HTML**: pasame el código y lo agrego al sitio.
4. En **Sitemaps**, enviar `sitemap.xml`.
5. En **Inspección de URLs**, pedir la indexación de la portada y de las 5 páginas de servicio.

## 3. Perfil de Empresa de Google (lo más importante para búsquedas locales)

Es la ficha que aparece en Google Maps y a la derecha de los resultados cuando alguien busca
"fonoaudióloga Rivera". Pesa más que el sitio web para las búsquedas "cerca de mí".

1. Crear o reclamar la ficha en <https://business.google.com>.
2. Categoría principal: **Centro de terapia infantil** o **Terapeuta ocupacional**, según lo que
   ofrezca Google. Categorías secundarias: Logopeda, Psicólogo infantil, Psicopedagogo.
3. Nombre exacto: `Clínica Trazos` (igual que en el sitio). Dirección: `Av. Sarandí 832, Rivera`.
   El mismo teléfono que en el sitio.
4. Sitio web: la URL del sitio. Horario, fotos del local (fachada, sala, recepción) y logo.
5. Pedir reseñas a las familias, sin ofrecer nada a cambio (Google lo prohíbe) y respondiendo a todas.
6. Cuando esté creada, pasame el link y lo sumo a `contacto.perfiles` para conectarla con el sitio.

## 4. Dominio propio (recomendado)

Con `github.io/clinicatrazosweb` el sitio funciona y Google lo indexa, pero un dominio propio
(`clinicatrazos.com.uy` o `.uy`) da más confianza, es más fácil de recordar y permite un `robots.txt`
en la raíz. Pasos:

1. Comprar el dominio (en Uruguay, `.com.uy` y `.uy` se registran en nic.uy o con un revendedor).
2. En GitHub → Settings → Pages → Custom domain, poner el dominio y configurar el DNS que indica GitHub.
3. En `content.json` cambiar `sitio.url` al dominio nuevo y correr `build.py`.
4. En Search Console, agregar el dominio nuevo y usar "Cambio de dirección".

## 5. Después del lanzamiento

- Publicar un artículo por semana, según `contenido/blog/_plan-editorial.md`.
- Mirar Search Console una vez por mes: qué búsquedas traen visitas y qué páginas conviene reforzar.
- Oportunidad: la frontera con Santana do Livramento. Una versión en portugués de las páginas de
  servicio podría captar familias brasileñas que buscan "fonoaudióloga em Rivera".
