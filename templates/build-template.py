#!/usr/bin/env python3
"""
Regenera asot-templates.js a partir de templates/nota-solicitud.docx.

Uso:
    python templates/build-template.py

El script lee la plantilla .docx (que debe contener los placeholders
{fecha}, {ipp}, {caratula}, {fiscalia}, {fiscal}, {secretaria},
{destinatario_titulo}, {destinatario_organismo}, {destinatario_sector},
{solicitud}), la codifica en base64 y la embebe en asot-templates.js.

Por qué embebido en JS: la app debe funcionar abriendo el index.html como
file:// (sin servidor) y los navegadores bloquean fetch() de archivos
locales por seguridad. Embeberlo evita esa restricción.
"""
import base64
import os
import re
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCX = os.path.join(ROOT, "templates", "nota-solicitud.docx")
OUT = os.path.join(ROOT, "asot-templates.js")

EXPECTED_PLACEHOLDERS = {
    "fecha", "ipp", "caratula", "fiscalia", "fiscal", "secretaria",
    "destinatario_titulo", "destinatario_organismo", "destinatario_sector",
    "solicitud",
}


def main():
    if not os.path.isfile(DOCX):
        print(f"ERROR: no encontre {DOCX}", file=sys.stderr)
        sys.exit(1)

    with zipfile.ZipFile(DOCX, "r") as z:
        xml = z.read("word/document.xml").decode("utf-8")

    found = set(re.findall(r"\{([a-z_]+)\}", xml))
    missing = EXPECTED_PLACEHOLDERS - found
    if missing:
        print(f"WARN: faltan placeholders en la plantilla: {sorted(missing)}", file=sys.stderr)

    extra = found - EXPECTED_PLACEHOLDERS
    if extra:
        print(f"NOTA: placeholders extra (no se rellenarán): {sorted(extra)}", file=sys.stderr)

    with open(DOCX, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")

    content = (
        "/**\n"
        " * Plantillas de notas de solicitud, embebidas como base64.\n"
        " *\n"
        " * Embebidas (no cargadas vía fetch) para que la app funcione bajo file://\n"
        " * sin servidor (el navegador bloquea fetch() de archivos locales).\n"
        " *\n"
        " * Generado por templates/build-template.py.\n"
        " * Para regenerar: editar templates/nota-solicitud.docx y correr el script.\n"
        " */\n"
        "window.ASOT_TEMPLATES = {\n"
        "    'default': {\n"
        "        nombre: 'Nota de solicitud (modelo Policía de la Ciudad)',\n"
        "        archivo: 'nota-solicitud.docx',\n"
        f"        b64: '{b64}'\n"
        "    }\n"
        "};\n"
    )

    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)

    print(f"OK — actualizado {OUT}")
    print(f"   docx: {os.path.getsize(DOCX)} bytes  |  b64: {len(b64)} chars")


if __name__ == "__main__":
    main()
