# Asistente de Solicitudes — CLAUDE.md

## ¿Qué es esta app?

Herramienta web estática para personal de brigadas de investigaciones de la Policía de la Ciudad. Guía al usuario según los datos disponibles como disparadores (teléfono, IP, email, cuenta bancaria, etc.) para identificar qué información puede obtener y a qué empresa solicitársela mediante oficio judicial.

## Arquitectura

- **`index.html`** — toda la lógica de la interfaz (HTML + JS inline)
- **`asot.css`** — estilos
- **`asot-data.js`** — catálogo de servicios, mapeos de datos → información → servicios. Es el único archivo que se edita para actualizar el contenido
- **`asot-templates.js`** — plantilla .docx embebida en base64 (autogenerado, no editar a mano)
- **`templates/nota-solicitud.docx`** — modelo Word con placeholders `{fecha}`, `{ipp}`, `{caratula}`, `{fiscalia}`, `{fiscal}`, `{secretaria}`, `{destinatario_titulo}`, `{destinatario_organismo}`, `{destinatario_sector}`, `{solicitud}`. Es la fuente de verdad
- **`templates/build-template.py`** — regenera `asot-templates.js` a partir del .docx
- **`vendor/pizzip.min.js`** — librería ZIP (necesaria para armar el .docx en el browser)
- **`icons/`** — íconos PNG locales de cada servicio (64x64, descargados de Google Favicons)

No hay backend, build system runtime, ni dependencias de red. La app debe poder abrirse directamente como archivo local (`file://`) sin servidor — por eso la plantilla va embebida en base64 (los navegadores bloquean `fetch()` de archivos locales).

## Despliegue

Actualmente en GitHub Pages (organización DAyPT). El objetivo es que sea completamente autocontenida y funcione offline sin depender de ningún servicio externo.

## Cómo agregar un nuevo servicio

1. Agregar la entrada en `asot-data.js` siguiendo la estructura existente
2. Agregar el ícono en `icons/{id}.png` (64x64 PNG)
3. Si el tipo de dato que dispara el servicio es nuevo, actualizar `datosAInformacion` e `informacionAServicios`

## Seguridad — reglas establecidas

- Todo dato del catálogo insertado en el DOM debe pasar por `escapeHtml()`
- Las URLs de contactos deben validarse con `esUrlSegura()` antes de usarse en `href`
- No incluir emails ni datos de personas físicas en `asot-data.js` — solo contactos institucionales
- La CSP está configurada en el `<meta>` del `<head>`: no agregar orígenes externos sin evaluar el impacto
- Los íconos deben ser locales (`icons/`), no cargarse desde servicios externos

## Cómo modificar el modelo de la nota Word

1. Editar `templates/nota-solicitud.docx` en Word — mantener los placeholders entre llaves intactos (cada uno debe quedar dentro de un solo run de texto, sin partir el placeholder con cambios de formato)
2. Correr `python templates/build-template.py` — regenera `asot-templates.js`
3. El bloque del firmante (jerarquía, nombre, L.P., dependencia, FIRMA) se deja como texto fijo: el usuario lo completa manualmente en Word después de descargar
