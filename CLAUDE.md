# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

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

Las únicas excepciones son GoatCounter (analytics, `gc.zgo.at` + `jesifu.goatcounter.com`) que ya están autorizadas en la CSP.

## Comandos

Regenerar `asot-templates.js` después de editar el .docx:
```bash
python templates/build-template.py
```

No hay servidor de desarrollo, tests, ni linter. Abrir `index.html` directamente en el navegador es suficiente para probar.

## Flujo de datos

El catálogo en `asot-data.js` define tres mapeos encadenados:

```
dato seleccionado (ej: 'telefono')
  → datosAInformacion['telefono']  → ['Registro de Llamadas', 'Geolocalización', ...]
  → informacionAServicios['Registro de Llamadas'] → ['movistar', 'personal', 'claro', ...]
  → servicios['movistar']          → ficha completa del servicio
```

`calcularInfoYServicios()` en `index.html` realiza este recorrido a partir de `estado.seleccionados`.

## Máquina de estados de la UI

La variable `estado.vista` controla qué sección se muestra. `setVista(nombre)` aplica el cambio ocultando/mostrando secciones:

| Vista | Elemento visible | Cuándo |
|---|---|---|
| `'home'` | `#estadoHome` | Sin datos seleccionados |
| `'resultados'` | `#estadoResultados` | Con al menos un dato seleccionado |
| `'catalogo'` | `#estadoCatalogo` | Al hacer "Ver todos" o buscar directo |
| `'detalle'` | `#detailPanel` | Al hacer clic en un servicio |

`estado.vistaAnterior` se guarda antes de entrar a `'detalle'` para poder volver correctamente con el botón "← Volver".

## Generación del Word

`descargarNotaWord()` en `index.html`:

1. Toma la plantilla base64 de `TEMPLATES['default']` (definido en `asot-templates.js`)
2. La descomprime con PizZip y edita `word/document.xml`
3. Reemplaza los placeholders `{clave}` ordenando las claves por longitud descendente (evita sustituciones parciales)
4. El campo `{solicitud}` convierte `\n` a saltos de línea Word (`<w:br/>`)
5. Genera un blob `.docx` y lo descarga via `<a download>`

El bloque del firmante (jerarquía, nombre, L.P., dependencia, FIRMA) se deja como texto fijo: el usuario lo completa manualmente en Word después de descargar.

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
