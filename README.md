# Derma · Análisis Estético

Aplicación de estudio en español basada en los dos PDF facilitados: **UNIDAD 1. AE** (13 páginas) y **UD 1 ANÁLISIS ESTÉTICO – LA PIEL** (35 diapositivas), de María Roselló Simó.

## Abrir la aplicación

No necesita instalar dependencias ni crear una cuenta. Abre **index.html** en un navegador moderno. Mantén juntos los archivos y la carpeta `assets`.

También puedes servirla desde la carpeta del proyecto:

```bash
cd /workspace/aplicacion-analisis-estetico-
python3 -m http.server 8000 --bind 0.0.0.0
```

## Dos apartados

- **Estudio:** 14 temas, esquema de capas interactivo, 78 tarjetas y preguntas de autoevaluación con explicación, mini-reto de parejas, seguimiento y consulta de ambos PDF. Incluye un visor de las 35 diapositivas originales y búsqueda en los documentos.
- **Examen:** 14 preguntas de desarrollo que cubren todos los temas. Redacta, avanza entre temas y retoma el borrador. Para finalizar se requiere una respuesta no vacía en cada tema; no se impone un mínimo de palabras. Después puedes revisar la guía, marcar criterios, descargar las respuestas o copiarlas para solicitar una corrección en ChatGPT.

La revisión por criterios es una **autoevaluación manual**, no una nota automática. El examen no llama a ninguna API. El botón de ChatGPT copia un texto con preguntas, respuestas, guía y contexto; debes pegarlo tú y seleccionar GPT-6.1 Sol allí si está disponible. La aplicación no controla el modelo de ChatGPT ni asegura la disponibilidad de ese nombre. No requiere claves.

## Progreso y privacidad

Las respuestas, tarjetas, errores y temas estudiados se guardan en `localStorage` del navegador, asociados al origen o archivo desde el que lo abres. No se envían a un servidor ni a ChatGPT automáticamente. Cambiar de navegador, dirección o dispositivo no transfiere los datos.

En **Estudio → Progreso** puedes descargar/restaurar una copia JSON. La restauración pide confirmación antes de sustituir el progreso. Exporta una copia antes de borrar datos del navegador. Si el almacenamiento no está disponible, aparece un aviso y puedes descargar tu examen. Cambiar una respuesta después de finalizar reinicia la lista de autoevaluación para evitar mantener criterios de una versión anterior.

## Organización y fidelidad al material

1. La piel y sus características.
2. Epidermis y células.
3. Estratos epidérmicos.
4. Dermis.
5. Hipodermis.
6. Irrigación.
7. Inervación y receptores.
8. Queratinización.
9. Melanogénesis.
10. Protección y barrera.
11. Termorregulación.
12. Inmunidad y metabolismo.
13. Secreción y reserva.
14. Relación con desviaciones estéticas.

Las lecciones enlazan con las páginas y diapositivas de origen. Los documentos originales y sus imágenes se conservan en `assets`. La búsqueda de diapositivas usa OCR y puede tener errores; comprueba el PDF o su imagen. Las explicaciones han sido redactadas para estudiar; las reglas mnemotécnicas nuevas se identifican como tales.

Se aclaran dos simplificaciones de la diapositiva 18: Ruffini es un mecanorreceptor de estiramiento, aunque el material también lo asocia con calor; la ausencia de vasos propios en la epidermis no implica ausencia absoluta de inervación. No se enseñan anexos en profundidad porque los PDF reservan ese contenido a la UD2.

## Archivos

- `index.html`, `styles.css`, `app.js`: interfaz y lógica sin frameworks.
- `content.js`: temas, preguntas, guías del examen y textos de búsqueda.
- `assets/docs`: PDF originales.
- `assets/slides`: imágenes de las diapositivas.
- `tests/smoke.py`: comprobaciones funcionales con Playwright y Chromium.

## Validación

Con el servidor iniciado, ejecuta las pruebas si Python tiene Playwright y Chromium disponibles:

```bash
python3 tests/smoke.py
```

La aplicación normal no necesita estas herramientas. Las pruebas usan un contexto nuevo de navegador y no alteran tu progreso habitual.

Resultados de validación en este entorno: pasaron los recorridos de estudio, test, parejas, examen completo, autoguardado al recargar, exportación/restauración y validación de copias; 24 vistas en tres tamaños sin desbordamiento horizontal y sin errores JavaScript. Los recursos también funcionaron con la red desactivada y entrega local interceptada. La apertura `file://` no pudo comprobarse aquí porque la política de Chromium la bloquea; el funcionamiento servido por HTTP sí está verificado.

## Publicación con un enlace web compartible

Las rutas `/workspace/...` pertenecen al entorno de desarrollo y no son enlaces públicos ni archivos adjuntos del chat. La web necesita publicarse para poder compartirla desde otro dispositivo.

Se incluye `.github/workflows/pages.yml`, con ejecución manual. Después de subir los archivos a GitHub y autorizar su publicación, selecciona **Settings → Pages → Source: GitHub Actions** y ejecuta **Actions → Publicar Derma → Run workflow**. GitHub mostrará la dirección real cuando termine. El sitio incluye el botón **Descargar aplicación ZIP** con un archivo servido desde la propia web.

La publicación incluye los dos PDF originales y sus diapositivas; no contiene respuestas de usuarios, que se guardan en sus navegadores. La versión publicada se encuentra en la rama `gh-pages`, configurada como fuente de GitHub Pages. GitHub confirmó el despliegue correcto del commit `c366380`.

Puedes preparar y verificar los archivos localmente con `python3 tools/build_site.py`; el resultado se guarda en `_site`, ignorado por Git. No necesita dependencias adicionales.

## Aplicación publicada

- Web: https://kiiarahoyoss.github.io/aplicacion-analisis-estetico-/
- ZIP descargable: https://github.com/kiiarahoyoss/aplicacion-analisis-estetico-/raw/refs/heads/gh-pages/downloads/Derma.zip

El ZIP público se descargó y verificó íntegramente (HTTP 200). GitHub Actions confirmó el despliegue correcto: https://github.com/kiiarahoyoss/aplicacion-analisis-estetico-/actions/runs/39147800082. El acceso directo al dominio de Pages desde la máquina de desarrollo está restringido; las comprobaciones funcionales se realizaron sobre los mismos archivos antes de subirlos. No se ha modificado la restricción de red del entorno para publicar la web.
