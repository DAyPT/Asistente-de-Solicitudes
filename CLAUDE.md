# Asistente de Solicitudes — CLAUDE.md

## ¿Qué es esta app?

Herramienta web estática para personal de brigadas de investigaciones de la Policía de la Ciudad. Guía al usuario según los datos disponibles como disparadores (teléfono, IP, email, cuenta bancaria, etc.) para identificar qué información puede obtener y a qué empresa solicitársela mediante oficio judicial.

## Arquitectura

- **`index.html`** — toda la lógica de la interfaz (HTML + JS inline)
- **`asot.css`** — estilos
- **`asot-data.js`** — catálogo de servicios, mapeos de datos → información → servicios. Es el único archivo que se edita para actualizar el contenido
- **`icons/`** — íconos PNG locales de cada servicio (64x64, descargados de Google Favicons)

No hay backend, build system, ni dependencias externas. La app debe poder abrirse directamente como archivo local (`file://`) sin servidor.

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

## Funcionalidad planeada

- Exportar la nota de solicitud como archivo `.docx` usando un modelo de Word predefinido
