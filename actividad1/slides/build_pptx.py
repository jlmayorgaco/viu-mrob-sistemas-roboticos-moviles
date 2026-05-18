from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZipFile


OUT = Path(__file__).with_name("Actividad1_AMR_FOD_Kitting.pptx")
EMU = 914400
SLIDE_W = int(13.333 * EMU)
SLIDE_H = int(7.5 * EMU)


COLORS = {
    "navy": "0F2742",
    "teal": "1F7A8C",
    "cyan": "38BDF8",
    "green": "2A9D8F",
    "amber": "F4A261",
    "red": "B91C1C",
    "ink": "0F172A",
    "muted": "475569",
    "line": "CBD5E1",
    "soft": "F4F7FA",
    "white": "FFFFFF",
}


def emu(inches: float) -> int:
    return int(inches * EMU)


def xml(text: object) -> str:
    return escape(str(text), {"'": "&apos;", '"': "&quot;"})


class SlideBuilder:
    def __init__(self) -> None:
        self.parts: list[str] = []
        self.shape_id = 1

    def _id(self) -> int:
        self.shape_id += 1
        return self.shape_id

    def rect(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        fill: str = "FFFFFF",
        line: str | None = None,
        radius: bool = False,
    ) -> None:
        sid = self._id()
        geometry = "roundRect" if radius else "rect"
        ln = (
            f'<a:ln w="9525"><a:solidFill><a:srgbClr val="{line}"/></a:solidFill></a:ln>'
            if line
            else '<a:ln><a:noFill/></a:ln>'
        )
        self.parts.append(
            f"""
<p:sp>
  <p:nvSpPr><p:cNvPr id="{sid}" name="Shape {sid}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
  <p:spPr>
    <a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/><a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm>
    <a:prstGeom prst="{geometry}"><a:avLst/></a:prstGeom>
    <a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>{ln}
  </p:spPr>
</p:sp>"""
        )

    def textbox(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        paragraphs: list[str],
        size: int = 18,
        color: str = "0F172A",
        bold: bool = False,
        bullet: bool = False,
        align: str = "l",
        fill: str | None = None,
        line: str | None = None,
    ) -> None:
        sid = self._id()
        fill_xml = (
            f'<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>'
            if fill
            else "<a:noFill/>"
        )
        line_xml = (
            f'<a:ln w="9525"><a:solidFill><a:srgbClr val="{line}"/></a:solidFill></a:ln>'
            if line
            else '<a:ln><a:noFill/></a:ln>'
        )
        paragraph_xml = "\n".join(
            self._paragraph(item, size=size, color=color, bold=bold, bullet=bullet, align=align)
            for item in paragraphs
        )
        self.parts.append(
            f"""
<p:sp>
  <p:nvSpPr><p:cNvPr id="{sid}" name="Text {sid}"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>
  <p:spPr>
    <a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/><a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm>
    <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>{fill_xml}{line_xml}
  </p:spPr>
  <p:txBody>
    <a:bodyPr wrap="square" rtlCol="0" anchor="t"><a:spAutoFit/></a:bodyPr>
    <a:lstStyle/>
    {paragraph_xml}
  </p:txBody>
</p:sp>"""
        )

    @staticmethod
    def _paragraph(
        text: str,
        size: int,
        color: str,
        bold: bool,
        bullet: bool,
        align: str,
    ) -> str:
        ppr = f'<a:pPr algn="{align}"/>'
        if bullet:
            ppr = '<a:pPr marL="285750" indent="-171450"><a:buChar char="•"/></a:pPr>'
        b = ' b="1"' if bold else ""
        return (
            f"<a:p>{ppr}<a:r><a:rPr lang=\"es-ES\" sz=\"{size * 100}\"{b}>"
            f"<a:solidFill><a:srgbClr val=\"{color}\"/></a:solidFill>"
            f"<a:latin typeface=\"Aptos\"/></a:rPr><a:t>{xml(text)}</a:t></a:r></a:p>"
        )

    def xml(self) -> str:
        return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
       xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
       xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld>
    <p:spTree>
      <p:nvGrpSpPr>
        <p:cNvPr id="1" name=""/>
        <p:cNvGrpSpPr/>
        <p:nvPr/>
      </p:nvGrpSpPr>
      <p:grpSpPr>
        <a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm>
      </p:grpSpPr>
      {''.join(self.parts)}
    </p:spTree>
  </p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sld>"""


def standard_slide(title: str, subtitle: str, bullets: list[str], accent: str = "teal") -> str:
    s = SlideBuilder()
    s.rect(0, 0, 13.333, 7.5, COLORS["white"])
    s.rect(0, 0, 13.333, 0.16, COLORS[accent])
    s.textbox(0.58, 0.42, 9.5, 0.6, [title], size=29, color=COLORS["navy"], bold=True)
    if subtitle:
        s.textbox(0.62, 1.03, 11.5, 0.38, [subtitle], size=13, color=COLORS["muted"])
    s.rect(0.62, 1.62, 12.05, 4.75, COLORS["soft"], COLORS["line"], radius=True)
    s.textbox(1.0, 1.95, 11.3, 3.95, bullets, size=17, color=COLORS["ink"], bullet=True)
    footer(s)
    return s.xml()


def two_column_slide(
    title: str,
    left_title: str,
    left: list[str],
    right_title: str,
    right: list[str],
    accent: str = "teal",
) -> str:
    s = SlideBuilder()
    s.rect(0, 0, 13.333, 7.5, COLORS["white"])
    s.rect(0, 0, 13.333, 0.16, COLORS[accent])
    s.textbox(0.58, 0.42, 11.8, 0.6, [title], size=29, color=COLORS["navy"], bold=True)
    s.rect(0.62, 1.35, 5.95, 4.9, COLORS["soft"], COLORS["line"], radius=True)
    s.rect(6.78, 1.35, 5.95, 4.9, COLORS["soft"], COLORS["line"], radius=True)
    s.textbox(0.95, 1.66, 5.25, 0.35, [left_title], size=16, color=COLORS["teal"], bold=True)
    s.textbox(7.12, 1.66, 5.25, 0.35, [right_title], size=16, color=COLORS["teal"], bold=True)
    s.textbox(0.98, 2.12, 5.25, 3.7, left, size=14, color=COLORS["ink"], bullet=True)
    s.textbox(7.15, 2.12, 5.25, 3.7, right, size=14, color=COLORS["ink"], bullet=True)
    footer(s)
    return s.xml()


def cover_slide() -> str:
    s = SlideBuilder()
    s.rect(0, 0, 13.333, 7.5, COLORS["navy"])
    s.rect(0, 0, 13.333, 0.22, COLORS["teal"])
    s.rect(0.72, 0.78, 1.0, 0.09, COLORS["cyan"])
    s.textbox(0.72, 1.05, 11.2, 0.75, ["Sistema AMR-FOD-Kitting"], size=34, color=COLORS["white"], bold=True)
    s.textbox(0.72, 1.86, 10.8, 0.75, ["Oferta de automatizacion para la linea HTP A320"], size=25, color="DCEBFF", bold=True)
    s.textbox(0.75, 3.12, 10.2, 0.8, ["Actividad 1 - Sistemas Roboticos Moviles"], size=19, color=COLORS["white"])
    s.textbox(0.75, 4.22, 10.6, 1.05, [
        "Universidad Internacional de Valencia",
        "Profesor: Jose I. Iñiguez",
        "Autor: Jorge Luis Mayorga Taborda",
        "Entrega: 26 de mayo de 2026"
    ], size=15, color="DCEBFF")
    s.rect(9.65, 5.65, 2.5, 0.76, COLORS["teal"], None, radius=True)
    s.textbox(9.78, 5.83, 2.24, 0.35, ["Lunabotics"], size=18, color=COLORS["white"], bold=True, align="c")
    return s.xml()


def architecture_slide() -> str:
    s = SlideBuilder()
    s.rect(0, 0, 13.333, 7.5, COLORS["white"])
    s.rect(0, 0, 13.333, 0.16, COLORS["teal"])
    s.textbox(0.58, 0.42, 11.8, 0.6, ["Sensores y arquitectura"], size=29, color=COLORS["navy"], bold=True)
    layers = [
        ("Percepcion", "LiDAR 2D/3D, RGB-D, QR/RFID"),
        ("Localizacion", "SLAM, odometria, IMU"),
        ("Misiones", "colas, prioridades, trazabilidad"),
        ("Control", "base omnidireccional, seguridad"),
        ("Planta", "MES/ERP, HMI, base de datos")
    ]
    x = 0.65
    for i, (name, desc) in enumerate(layers):
        fill = COLORS["soft"] if i % 2 == 0 else "EAF7F8"
        s.rect(x, 1.55, 2.25, 3.15, fill, COLORS["line"], radius=True)
        s.textbox(x + 0.17, 1.84, 1.9, 0.35, [name], size=14, color=COLORS["teal"], bold=True, align="c")
        s.textbox(x + 0.2, 2.38, 1.85, 1.35, [desc], size=12, color=COLORS["ink"], align="c")
        if i < len(layers) - 1:
            s.textbox(x + 2.3, 2.85, 0.35, 0.35, ["->"], size=18, color=COLORS["teal"], bold=True, align="c")
        x += 2.45
    s.rect(1.1, 5.28, 11.1, 0.78, "F8FAFC", COLORS["line"], radius=True)
    s.textbox(1.3, 5.48, 10.65, 0.3, ["La arquitectura separa navegacion segura, supervision de misiones y registro verificable de entregas/FOD."], size=13, color=COLORS["muted"], align="c")
    footer(s)
    return s.xml()


def budget_slide() -> str:
    s = SlideBuilder()
    s.rect(0, 0, 13.333, 7.5, COLORS["white"])
    s.rect(0, 0, 13.333, 0.16, COLORS["amber"])
    s.textbox(0.58, 0.42, 11.8, 0.6, ["Presupuesto detallado"], size=29, color=COLORS["navy"], bold=True)
    s.textbox(0.62, 1.02, 11.6, 0.35, ["Estimacion academica, no cotizacion real. Importes sin IVA."], size=13, color=COLORS["muted"])
    headers = ["Escenario", "CAPEX", "TCO 3 anos", "Uso previsto"]
    rows = [
        ["1 robot", "206.304 EUR", "237.704 EUR", "piloto controlado"],
        ["7 robots", "974.848 EUR", "1.121.648 EUR", "expansion de linea"],
        ["17 robots", "2.253.888 EUR", "2.576.688 EUR", "despliegue extendido"],
    ]
    x0, y0 = 0.75, 1.72
    widths = [2.2, 2.4, 2.5, 5.0]
    s.rect(x0, y0, sum(widths), 0.52, COLORS["navy"], None)
    x = x0
    for w, h in zip(widths, headers):
        s.textbox(x + 0.08, y0 + 0.13, w - 0.16, 0.22, [h], size=12, color=COLORS["white"], bold=True, align="c")
        x += w
    for r, row in enumerate(rows):
        y = y0 + 0.58 + r * 0.66
        s.rect(x0, y, sum(widths), 0.58, "F8FAFC" if r % 2 == 0 else "EAF7F8", COLORS["line"])
        x = x0
        for w, cell in zip(widths, row):
            s.textbox(x + 0.08, y + 0.14, w - 0.16, 0.22, [cell], size=12, color=COLORS["ink"], align="c")
            x += w
    s.textbox(0.95, 4.38, 11.3, 1.18, [
        "Partidas incluidas: robots, sensores, utiles de transporte, software, ingenieria, instalacion, formacion, mantenimiento, desplazamientos y margen comercial.",
        "La decision recomendada es un piloto de 1 robot con metricas de exito antes de escalar a 7 y 17 unidades."
    ], size=14, color=COLORS["ink"], bullet=True)
    footer(s)
    return s.xml()


def footer(s: SlideBuilder) -> None:
    s.textbox(0.62, 6.92, 6.2, 0.24, ["Actividad 1 - Sistemas Roboticos Moviles"], size=9, color="64748B")
    s.textbox(9.8, 6.92, 2.9, 0.24, ["Lunabotics / Alestis Puerto Real"], size=9, color="64748B", align="r")


SLIDES = [
    cover_slide(),
    standard_slide("Objetivo de la propuesta", "Convertir el problema logistico de planta en una solucion AMR defendible tecnica y comercialmente.", [
        "Reducir desplazamientos improductivos de operarios y esperas por kits.",
        "Aumentar trazabilidad de herramientas, consumibles y entregas.",
        "Disminuir riesgo FOD mediante inspeccion preventiva y registro.",
        "Validar el despliegue con simulacion en CoppeliaSim y piloto medible."
    ]),
    standard_slide("Presentacion de Lunabotics", "Empresa ficticia que formula una oferta tecnica y comercial para Alestis Puerto Real.", [
        "Empresa joven de integracion de robotica movil industrial.",
        "Capacidades: CoppeliaSim, AMR, LiDAR/RGB-D/RFID, HMI y datos de planta.",
        "Experiencia de referencia: pilotos intralogisticos y celdas con bases omnidireccionales.",
        "Enfoque comercial: piloto medible, expansion controlada y despliegue con KPIs validados."
    ]),
    two_column_slide("Contexto industrial", "HTP y seccion 19.1", [
        "HTP: estabilizador horizontal del A320.",
        "Estructuras grandes, utiles especificos y control de configuracion.",
        "Seccion 19.1: entorno de integracion y montaje con alta dependencia logistica."
    ], "Reto de planta", [
        "Produccion actual aproximada: 40 HTP/mes.",
        "Objetivo futuro: 80 HTP/mes o mas.",
        "La robotica movil debe apoyar el escalado sin prometer duplicacion automatica."
    ]),
    standard_slide("Informacion obtenida de la entrevista", "Entrevista simulada a Carlos Perez, trabajador con mas de 10 anos de experiencia en Alestis Puerto Real.", [
        "Los operarios pierden tiempo buscando kits, consumibles y herramientas compartidas.",
        "La trazabilidad fina no siempre queda ligada al momento exacto de entrega.",
        "La gestion FOD exige disciplina, inspeccion y evidencia documentada.",
        "La automatizacion aceptable debe convivir con operarios y estructuras aeronauticas."
    ]),
    standard_slide("Problemas detectados", "Problemas elegidos por impacto operacional y relacion directa con robotica movil.", [
        "Desplazamientos internos repetitivos y de bajo valor anadido.",
        "Esperas por falta de sincronizacion entre logistica y estacion de trabajo.",
        "Riesgo FOD por restos, utiles olvidados o control visual insuficiente.",
        "Trazabilidad incompleta de kits, herramientas retornadas y eventos de entrega.",
        "Necesidad de escalar capacidad sin saturar pasillos ni equipos de soporte."
    ], accent="amber"),
    standard_slide("Requisitos, trazabilidad y KPIs", "Cada requisito se vincula con una funcion verificable y una metrica de aceptacion.", [
        "Navegacion autonoma interior con zonas restringidas y parada segura.",
        "Maniobrabilidad omnidireccional en estaciones con espacio limitado.",
        "RFID/QR para confirmar kit, herramienta, estacion, hora y responsable.",
        "KPIs: tiempo improductivo, entregas a tiempo, eventos FOD y disponibilidad AMR.",
        "Escalabilidad de 1 a 7 y 17 robots sin redisenar la arquitectura."
    ]),
    two_column_slide("Alternativas roboticas", "Opciones descartadas", [
        "AGV: robusto pero dependiente de rutas fijas.",
        "Orugas: innecesarias en nave interior pavimentada.",
        "Dron: riesgo operativo y baja utilidad con carga.",
        "Robot con patas: coste y complejidad no justificados."
    ], "Opcion seleccionada", [
        "AMR omnidireccional equivalente a KUKA YouBot/Omnirob en CoppeliaSim.",
        "Movimiento lateral sin reorientar la carga.",
        "Mayor adaptacion a cambios de estacion que un AGV."
    ]),
    standard_slide("Robot seleccionado", "Plataforma AMR omnidireccional disponible o representable en CoppeliaSim.", [
        "Base mecanum/omnidireccional para maniobras precisas junto a utiles y estaciones.",
        "Carga util moderada para kits, consumibles y herramientas, no fabricacion directa.",
        "Integracion de bandejas, cajon seguro, lector RFID/QR y HMI.",
        "Operacion supervisada, con escalado multi-robot cuando el piloto lo justifique."
    ]),
    architecture_slide(),
    standard_slide("Flujo operativo", "Secuencia diaria propuesta para misiones de kitting, entrega, inspeccion y retorno.", [
        "Planificacion de mision desde supervisor/MES.",
        "Carga de kit o herramienta y lectura RFID/QR.",
        "Navegacion autonoma hasta estacion asignada.",
        "Entrega con confirmacion digital y registro de evento.",
        "Inspeccion FOD si aplica y retorno de utiles usados o nueva mision."
    ]),
    standard_slide("Validacion en CoppeliaSim", "La simulacion reduce riesgo antes de entrar en una planta aeronautica real.", [
        "Modelo de pasillos, estaciones HTP, zonas de espera y muelles de carga.",
        "Escenarios: entrega nominal, obstaculo temporal, cruce con operario y zona restringida.",
        "Metricas: exito de mision, distancia recorrida, esperas, paradas de seguridad y congestion.",
        "Criterio de paso: piloto solo si el comportamiento simulado es estable y auditable."
    ]),
    two_column_slide("Escenarios de despliegue", "Piloto: 1 robot", [
        "Validar rutas, aceptacion operativa y registro de trazabilidad.",
        "Coste CAPEX estimado: 206.304 EUR.",
        "Exito: misiones sin incidentes y reduccion medible de esperas."
    ], "Expansion: 7 y 17 robots", [
        "7 robots: cobertura de varias estaciones y turnos.",
        "17 robots: despliegue extendido con gestion de flota.",
        "Escalado condicionado a KPIs, seguridad y disponibilidad."
    ]),
    standard_slide("Viabilidad y beneficios", "Solucion realista: aporta capacidad indirecta, no promete duplicar produccion por si sola.", [
        "Beneficios: menos esperas, menos desplazamientos y mejor trazabilidad.",
        "Seguridad: LiDAR, escaner laser, bumpers, emergencia y supervision.",
        "Riesgos mitigados: saturacion de pasillos, rechazo operativo, falsas detecciones FOD e integracion MES.",
        "Alineacion con el objetivo de pasar de 40 a 80 HTP/mes mediante soporte logistico robusto."
    ], accent="green"),
    budget_slide(),
    standard_slide("Conclusion", "La propuesta cumple los tres bloques de la actividad: entrevista, oferta tecnica y oferta comercial.", [
        "La solucion AMR-FOD-Kitting ataca problemas reales de intralogistica aeronautica.",
        "La eleccion omnidireccional es coherente con CoppeliaSim, seguridad y maniobrabilidad.",
        "El presupuesto por escenarios permite decidir con piloto, expansion y despliegue extendido.",
        "El resultado es viable, escalable y defendible dentro de Sistemas Roboticos Moviles."
    ], accent="green"),
]


def content_types() -> str:
    slide_overrides = "\n".join(
        f'<Override PartName="/ppt/slides/slide{i}.xml" '
        f'ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
        for i in range(1, len(SLIDES) + 1)
    )
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
  <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>
  <Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>
  <Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>
  <Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>
  {slide_overrides}
</Types>"""


def root_rels() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>"""


def app_props() -> str:
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
            xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>Microsoft PowerPoint</Application>
  <PresentationFormat>On-screen Show (16:9)</PresentationFormat>
  <Slides>{len(SLIDES)}</Slides>
  <Company>Lunabotics</Company>
</Properties>"""


def core_props() -> str:
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
                   xmlns:dc="http://purl.org/dc/elements/1.1/"
                   xmlns:dcterms="http://purl.org/dc/terms/"
                   xmlns:dcmitype="http://purl.org/dc/dcmitype/"
                   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>Actividad 1 - Sistema AMR-FOD-Kitting</dc:title>
  <dc:subject>Sistemas Roboticos Moviles</dc:subject>
  <dc:creator>Jorge Luis Mayorga Taborda</dc:creator>
  <cp:keywords>AMR; FOD; HTP; A320; CoppeliaSim; robotica movil</cp:keywords>
  <dc:description>Presentacion editable de la oferta tecnica y comercial para Alestis Puerto Real.</dc:description>
  <dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified>
</cp:coreProperties>"""


def presentation_xml() -> str:
    slide_ids = "\n".join(
        f'<p:sldId id="{255 + i}" r:id="rId{i + 1}"/>' for i in range(1, len(SLIDES) + 1)
    )
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
                xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
                xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst>
  <p:sldIdLst>{slide_ids}</p:sldIdLst>
  <p:sldSz cx="{SLIDE_W}" cy="{SLIDE_H}" type="wide"/>
  <p:notesSz cx="6858000" cy="9144000"/>
  <p:defaultTextStyle/>
</p:presentation>"""


def presentation_rels() -> str:
    rels = [
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>'
    ]
    for i in range(1, len(SLIDES) + 1):
        rels.append(
            f'<Relationship Id="rId{i + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i}.xml"/>'
        )
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  {' '.join(rels)}
</Relationships>"""


def slide_rels() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
</Relationships>"""


def slide_master() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
             xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
             xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld><p:spTree>
    <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
    <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
  </p:spTree></p:cSld>
  <p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/>
  <p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst>
  <p:txStyles><p:titleStyle/><p:bodyStyle/><p:otherStyle/></p:txStyles>
</p:sldMaster>"""


def slide_master_rels() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/>
</Relationships>"""


def slide_layout() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
             xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
             xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
             type="blank" preserve="1">
  <p:cSld name="Blank"><p:spTree>
    <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
    <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
  </p:spTree></p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sldLayout>"""


def slide_layout_rels() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/>
</Relationships>"""


def theme() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="Lunabotics">
  <a:themeElements>
    <a:clrScheme name="Lunabotics">
      <a:dk1><a:srgbClr val="0F172A"/></a:dk1><a:lt1><a:srgbClr val="FFFFFF"/></a:lt1>
      <a:dk2><a:srgbClr val="0F2742"/></a:dk2><a:lt2><a:srgbClr val="F4F7FA"/></a:lt2>
      <a:accent1><a:srgbClr val="1F7A8C"/></a:accent1><a:accent2><a:srgbClr val="38BDF8"/></a:accent2>
      <a:accent3><a:srgbClr val="2A9D8F"/></a:accent3><a:accent4><a:srgbClr val="F4A261"/></a:accent4>
      <a:accent5><a:srgbClr val="B91C1C"/></a:accent5><a:accent6><a:srgbClr val="475569"/></a:accent6>
      <a:hlink><a:srgbClr val="1F7A8C"/></a:hlink><a:folHlink><a:srgbClr val="0F2742"/></a:folHlink>
    </a:clrScheme>
    <a:fontScheme name="Lunabotics"><a:majorFont><a:latin typeface="Aptos Display"/></a:majorFont><a:minorFont><a:latin typeface="Aptos"/></a:minorFont></a:fontScheme>
    <a:fmtScheme name="Lunabotics"><a:fillStyleLst/><a:lnStyleLst/><a:effectStyleLst/><a:bgFillStyleLst/></a:fmtScheme>
  </a:themeElements>
</a:theme>"""


def build() -> None:
    with ZipFile(OUT, "w", ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types())
        z.writestr("_rels/.rels", root_rels())
        z.writestr("docProps/app.xml", app_props())
        z.writestr("docProps/core.xml", core_props())
        z.writestr("ppt/presentation.xml", presentation_xml())
        z.writestr("ppt/_rels/presentation.xml.rels", presentation_rels())
        z.writestr("ppt/slideMasters/slideMaster1.xml", slide_master())
        z.writestr("ppt/slideMasters/_rels/slideMaster1.xml.rels", slide_master_rels())
        z.writestr("ppt/slideLayouts/slideLayout1.xml", slide_layout())
        z.writestr("ppt/slideLayouts/_rels/slideLayout1.xml.rels", slide_layout_rels())
        z.writestr("ppt/theme/theme1.xml", theme())
        for i, slide in enumerate(SLIDES, start=1):
            z.writestr(f"ppt/slides/slide{i}.xml", slide)
            z.writestr(f"ppt/slides/_rels/slide{i}.xml.rels", slide_rels())
    print(f"Created {OUT}")


if __name__ == "__main__":
    build()
