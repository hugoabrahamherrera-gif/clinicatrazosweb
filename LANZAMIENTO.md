# Lanzamiento y SEO — lista de tareas

El código ya resuelve el SEO técnico: páginas por servicio, títulos, descripciones, datos
estructurados, sitemap y velocidad. Lo que sigue depende de datos o de cuentas de la clínica, y
es lo que más pesa para aparecer en Google Maps y en las búsquedas locales.

## 0. Revisión del 2026-11-01: decisiones antes de lanzar

**El sitio ya es público** en la dirección de github.io, aunque Google todavía no lo muestra para "Clínica Trazos". Hoy publicar = `git push` de `main`.

1. [ ] **Publicidad en salud (Ley 18.211 art. 20, Decreto 272/011).** Sin autorización previa del MSP, la publicidad se limita a datos identificatorios, títulos y especialidades registrados ante el MSP. Lo que exceda eso requiere autorización; las infracciones van de 30 a 500 UR y el MSP puede suspender la publicidad. Consultar con el asesor o el MSP si los textos de servicios y el blog entran en esa autorización. No es asesoramiento legal.
2. [ ] **Dominio propio antes de lanzar** (`clinicatrazos.com.uy` no tenía DNS el 2026-11-01; confirmar en nic.uy). Sin dominio, `robots.txt` no funciona: Google solo lo lee en la raíz.
3. [ ] **Teléfono, WhatsApp y horario** (la clínica ya opera): pesan para el Perfil de Empresa y el contacto en celular.
4. [ ] **Revisión profesional de los 6 artículos** y dato `revisado_por:` en cada uno (nombre y título registrado).
5. [ ] **Página de equipo** con nombres y títulos, con consentimiento de cada profesional.
6. [ ] **Nutrición y Maestra especializada** no tienen página. Faltan definir alcance y datos.
7. [ ] **Confirmar Terapia Ocupacional y BPS:** no figura en la habilitación informada. El sitio no afirma nada.
8. [ ] **WordPress `riveraclc.wordpress.com`:** sigue mostrando "próximamente" con el nombre de la clínica. Ponerlo privado o borrarlo.
9. [ ] **Instalar el workflow del blog** (sección 5): sin él los artículos no salen solos. Ninguno se publicó en septiembre ni octubre.
10. [ ] Después del primer push: comprobar que `README.md`, `build.py` y `contenido/` den 404 (se ocultan con `_config.yml`).
11. [ ] Cuando BPS apruebe: cambiar "en proceso de habilitación" en todas las páginas (`grep -rn "habilitaci" contenido content.json`).

**Siguiente etapa:** páginas en portugués con hreflang (solo para lo que atienden profesionales de Livramento) y artículos 7 a 12 del plan editorial.

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

## 5. Publicación automática del blog

`herramientas/publicar-blog.yml` publica los artículos los lunes a las 08:00 (Uruguay). Hay que
instalarlo una vez desde la web de GitHub, porque el token de la compu no tiene permiso `workflow`:

1. En el repo, **Add file → Create new file**, con el nombre `.github/workflows/publicar-blog.yml`.
2. Pegar el contenido de `herramientas/publicar-blog.yml` y hacer **Commit changes**.
3. En la compu: `git pull`.

## 6. Después del lanzamiento

- Publicar un artículo por semana, según `contenido/blog/_plan-editorial.md`.
- Mirar Search Console una vez por mes: qué búsquedas traen visitas y qué páginas conviene reforzar.
- Oportunidad: la frontera con Santana do Livramento. Una versión en portugués de las páginas de
  servicio podría captar familias brasileñas que buscan "fonoaudióloga em Rivera".
