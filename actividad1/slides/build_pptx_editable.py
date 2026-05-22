from __future__ import annotations

from pathlib import Path
from shutil import copyfile

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt


BASE = Path(__file__).resolve().parent
PIXEL_SOURCE = BASE / "Actividad1_AMR_FOD_Kitting.pptx"
PIXEL_OUT = BASE / "Actividad1_AMR_FOD_Kitting_pixel_perfect.pptx"
EDITABLE_OUT = BASE / "Actividad1_AMR_FOD_Kitting_editable.pptx"


W, H = 13.333333, 7.5

COLORS = {
    "ink": RGBColor(16, 32, 51),
    "muted": RGBColor(81, 97, 115),
    "line": RGBColor(213, 222, 232),
    "paper": RGBColor(247, 249, 252),
    "panel": RGBColor(255, 255, 255),
    "navy": RGBColor(10, 35, 66),
    "teal": RGBColor(31, 122, 140),
    "cyan": RGBColor(45, 183, 229),
    "green": RGBColor(42, 157, 143),
    "amber": RGBColor(244, 162, 97),
    "red": RGBColor(185, 28, 28),
    "violet": RGBColor(109, 91, 208),
    "white": RGBColor(255, 255, 255),
}


def img(name: str) -> str:
    return str((BASE / name).resolve())


def rgb(name: str) -> RGBColor:
    return COLORS[name]


def set_fill(shape, color: str, transparency: int = 0) -> None:
    shape.fill.solid()
    shape.fill.fore_color.rgb = rgb(color)
    shape.fill.transparency = transparency


def set_line(shape, color: str, width: float = 0.75, transparency: int = 0) -> None:
    shape.line.color.rgb = rgb(color)
    shape.line.width = Pt(width)
    shape.line.transparency = transparency


def add_text(slide, text: str, x: float, y: float, w: float, h: float, *,
             size: float = 14, color: str = "ink", bold: bool = False,
             align=PP_ALIGN.LEFT, font: str = "Aptos", valign: bool = False):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.clear()
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    r = p.add_run()
    r.text = text
    r.font.name = font
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.color.rgb = rgb(color)
    if valign:
        tf.vertical_anchor = 3
    return box


def add_multiline(slide, lines: list[str], x: float, y: float, w: float, h: float,
                  *, size: float = 11, color: str = "ink", bullet: bool = False,
                  line_spacing: float = 1.0):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.clear()
    tf.word_wrap = True
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line
        p.font.name = "Aptos"
        p.font.size = Pt(size)
        p.font.color.rgb = rgb(color)
        p.line_spacing = line_spacing
        if bullet:
            p.level = 0
            p._p.get_or_add_pPr().set("marL", "171450")
            p._p.get_or_add_pPr().set("indent", "-114300")
    return box


def add_rect(slide, x: float, y: float, w: float, h: float, fill: str = "panel",
             line: str = "line", radius: bool = True, transparency: int = 0):
    shape_type = MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE
    s = slide.shapes.add_shape(shape_type, Inches(x), Inches(y), Inches(w), Inches(h))
    set_fill(s, fill, transparency)
    set_line(s, line, 0.75)
    return s


def add_card(slide, x, y, w, h, title, body, color="teal", value=None):
    add_rect(slide, x, y, w, h, "panel", color)
    if value:
        add_text(slide, value, x + 0.18, y + 0.12, w - 0.36, 0.35, size=18, color=color, bold=True)
        ty = y + 0.55
    else:
        ty = y + 0.18
    add_text(slide, title, x + 0.18, ty, w - 0.36, 0.28, size=11, color=color, bold=True)
    add_text(slide, body, x + 0.18, ty + 0.36, w - 0.36, h - 0.62, size=9.2, color="ink")


def add_header(slide, n: int, kicker: str, title: str, color: str = "teal") -> None:
    bg = slide.background.fill
    bg.solid()
    bg.fore_color.rgb = rgb("paper")
    top = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(W), Inches(0.22))
    set_fill(top, "white")
    top.line.fill.background()
    prog = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(W * n / 24), Inches(0.07))
    set_fill(prog, color)
    prog.line.fill.background()
    add_text(slide, kicker, 0.6, 0.26, 2.5, 0.18, size=7.2, color=color, bold=True)
    add_text(slide, title, 0.6, 0.52, 10.8, 0.45, size=24, color="ink", bold=True)
    add_text(slide, f"{n}/24", 11.95, 0.28, 0.8, 0.2, size=8, color="muted", bold=True, align=PP_ALIGN.RIGHT)
    add_text(slide, "Actividad 1 • Sistemas Robóticos Móviles", 0.6, 7.17, 3.6, 0.18, size=7.4, color="muted")
    add_text(slide, "Lunabotics • Alestis Puerto Real • HTP A320", 6.9, 7.17, 4.8, 0.18, size=7.4, color="muted", align=PP_ALIGN.RIGHT)
    circ = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(12.02), Inches(6.88), Inches(0.45), Inches(0.45))
    set_fill(circ, "white")
    set_line(circ, "teal", 1.0)
    add_text(slide, "LB", 12.02, 6.99, 0.45, 0.18, size=9, color="teal", bold=True, align=PP_ALIGN.CENTER)


def add_table(slide, x, y, w, h, rows, cols, data, font_size=7.2):
    table = slide.shapes.add_table(rows, cols, Inches(x), Inches(y), Inches(w), Inches(h)).table
    for r in range(rows):
        for c in range(cols):
            cell = table.cell(r, c)
            cell.text = str(data[r][c]) if r < len(data) and c < len(data[r]) else ""
            cell.text_frame.paragraphs[0].font.size = Pt(font_size)
            cell.text_frame.paragraphs[0].font.name = "Aptos"
            cell.text_frame.paragraphs[0].font.color.rgb = rgb("ink")
            if r == 0:
                cell.fill.solid()
                cell.fill.fore_color.rgb = RGBColor(232, 245, 247)
                cell.text_frame.paragraphs[0].font.bold = True
    return table


def add_flow(slide, labels, y, color="teal"):
    x = 0.95
    box_w = 2.5
    for i, (title, body) in enumerate(labels):
        add_card(slide, x, y, box_w, 1.0, title, body, color)
        if i < len(labels) - 1:
            line = slide.shapes.add_connector(1, Inches(x + box_w + 0.05), Inches(y + 0.5), Inches(x + box_w + 0.45), Inches(y + 0.5))
            set_line(line, color, 1.4)
        x += box_w + 0.65


def slide_cover(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = rgb("navy")
    p = BASE / "../figures/source/alestis_htp_nave.png"
    if p.exists():
        pic = s.shapes.add_picture(str(p.resolve()), 0, 0, width=Inches(W), height=Inches(H))
        pic._element.getparent().remove(pic._element)
        s.shapes._spTree.insert(2, pic._element)
        overlay = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(W), Inches(H))
        set_fill(overlay, "navy", 18)
        overlay.line.fill.background()
    add_text(s, "LUNABOTICS • OFERTA TÉCNICA Y COMERCIAL", 0.7, 0.38, 4.8, 0.24, size=8, color="white", bold=True)
    add_text(s, "Sistema\nAMR-FOD-Kitting", 0.7, 1.2, 5.5, 1.35, size=34, color="white", bold=True)
    add_text(s, "Automatización intralogística para HTP A320 y sección 19.1", 0.75, 2.78, 5.4, 0.5, size=14, color="white")
    add_text(s, "TESIS", 8.1, 4.55, 1.2, 0.24, size=8, color="cyan", bold=True)
    add_text(s, "Medir un piloto AMR antes de escalar la flota.", 8.1, 4.92, 4.0, 0.75, size=22, color="white", bold=True)
    add_text(s, "Actividad 1 • Sistemas Robóticos Móviles\nProfesor: José I. Iñiguez\nAutor: Jorge Luis Mayorga Taborda\nEntrega: 26 de mayo de 2026", 0.75, 5.7, 5.8, 0.9, size=9, color="white")


def build_editable():
    prs = Presentation()
    prs.slide_width = Inches(W)
    prs.slide_height = Inches(H)

    slide_cover(prs)

    specs = [
        ("Mensaje ejecutivo", "Necesidad, piloto y decisión", "violet", [
            ("01 Problema", "8–15 % del turno en logística auxiliar; hipótesis de entrevista", "amber", None),
            ("02 Piloto", "1 AMR omnidireccional + sensores integrados + 237 k€", "teal", None),
            ("03 Decisión", "Escalado 1 → 7 → 17 condicionado a KPIs y umbral económico", "green", None),
        ], "Alcance: el AMR estabiliza soporte logístico; fabricación, inspección certificada y decisiones de calidad quedan fuera del piloto."),
        ("Lunabotics", "Integrador de robótica móvil industrial", "teal", [
            ("Análisis de flujo", "Misiones AMR y puntos de entrega/retorno.", "teal", None),
            ("Modelado", "CoppeliaSim con YouBot/Omnirob como proxy holonómico.", "violet", None),
            ("Selección industrial", "Plataforma, sensores, safety pack y HMI.", "amber", None),
            ("Integración", "RFID/QR, registro de misiones y evidencia FOD.", "green", None),
        ], "Pilotos AMR antes de flota: integrar ROS 2, seguridad, HMI, datos y pruebas de planta."),
        ("Tesis", "Estabilizar el flujo que rodea al HTP", "teal", [
            ("40 → 80", "HTP/mes: el AMR actúa sobre la palanca logística.", "teal", None),
            ("Menos esperas", "Entregas trazadas en estación.", "amber", None),
            ("Registro", "RFID/QR para cerrar cada entrega.", "violet", None),
            ("FOD", "Captura RGB-D y revisión humana.", "green", None),
        ], "El robot coordina entregas y registro para liberar tiempo en la estación."),
        ("Seguridad", "Límites normativos antes de operar en planta", "violet", [
            ("ISO 3691-4", "Velocidad, parada, zonas lentas y operación cerca de personas.", "teal", None),
            ("NAS 412 / FOD", "Evidencia FOD revisable; certificación por calidad.", "amber", None),
            ("AS9100", "Trazabilidad y cambios controlados.", "violet", None),
            ("CE", "Conjunto AMR + portakits + sensores.", "green", None),
        ], "Regla: la seguridad funcional tiene prioridad sobre navegación y productividad."),
        ("Dolor operativo", "Recorridos pequeños que frenan el flujo", "amber", [
            ("Estación", "El operario abandona el puesto para buscar útiles.", "amber", None),
            ("Kits", "Un kit incompleto bloquea trabajo sin ser gran parada.", "teal", None),
            ("FOD", "Exige inspección, disciplina y evidencia revisable.", "red", None),
            ("Registro", "La entrega debe quedar ligada a misión.", "violet", None),
        ], "Supuesto a validar: logística auxiliar = 8–15 % del tiempo de turno afectado."),
        ("Contexto", "Flujo auxiliar en HTP A320 y sección 19.1", "cyan", [
            ("Kit validado", "RFID–QR", "teal", None),
            ("Entrega HTP", "Punto trazado", "amber", None),
            ("Registro", "Misión cerrada", "violet", None),
            ("Retorno FOD", "Evidencia", "green", None),
        ], "Distancias estimadas: kit → estación 40 m • retorno útiles 25 m • ronda FOD 80 m."),
        ("Alcance", "Dónde entra el AMR y dónde no entra", "cyan", [
            ("Base logística", "∼2 min carga + lectura", "teal", None),
            ("Pasillo seguro", "∼3 min ruta limitada", "cyan", None),
            ("Estación HTP", "∼1 min entrega + confirmación", "amber", None),
            ("Retorno / FOD", "∼4–6 min retorno y evidencia", "green", None),
        ], "Fuera de alcance: montaje, mecanizado y manipulación directa del HTP."),
        ("Entrevista", "Hallazgos convertidos en requisitos", "violet", [
            ("Alcance", "Kits, herramientas, retorno y registro.", "teal", None),
            ("Pasillos", "Base omnidireccional con SLAM y gestor de misiones.", "cyan", None),
            ("FOD", "Ronda RGB-D, evento trazado y revisión humana.", "amber", None),
            ("Escalado", "Pasar de 1 a 7 solo si los KPIs lo justifican.", "green", None),
        ], "Prioridad de planta: menos vueltas y cada entrega registrada."),
        ("Requisitos", "Criterios de aceptación conectados con el temario", "teal", [
            ("≥ 95 %", "Misiones completadas en piloto.", "teal", None),
            ("≥ 98 %", "Registro completo por misión.", "green", None),
            ("≥ 90 %", "Disponibilidad AMR en turno.", "cyan", None),
            ("0", "Contactos no previstos / incidentes con daño.", "red", None),
        ], "Medición: logs, RFID/QR, estado AMR, eventos safety y revisión FOD."),
        ("Alternativas", "Matriz de decisión con criterios ponderados", "green", [
            ("AMR omnidireccional", "4,20", "green", None),
            ("AMR diferencial", "3,90", "teal", None),
            ("AGV", "3,15", "amber", None),
            ("Dron / orugas / patas", "≤ 1,85", "red", None),
        ], "El omni gana por maniobra en estación, el criterio de mayor peso."),
        ("Robot", "Modelo elegido y opciones reales de compra", "teal", [
            ("Selección", "RB-KAIROS-class; base holonómica, ROS 2 y ∼250 kg.", "teal", None),
            ("Alternativa", "AGILOX ODM para intralogística 300 kg.", "green", None),
            ("Descartado", "KUKA omniMove: sobredimensionado para HTP 19.1.", "red", None),
            ("Simulación", "YouBot/Omnirob como proxy mecanum en CoppeliaSim.", "violet", None),
        ], "Solo base móvil + portakits; sin brazo manipulador ni manipulación directa del HTP."),
        ("Dimensionamiento", "El número de robots sale de misiones y ciclo", "green", [
            ("80 HTP/mes", "20 días productivos → 4 HTP/día.", "teal", None),
            ("41 misiones/HTP", "15 kits + 10 reposiciones + 8 retornos + 5 FOD + 3 consumibles.", "amber", None),
            ("189 misiones/día", "164 base + 15 % margen.", "violet", None),
            ("7 robots", "189 / 28 = 6,75 → 7.", "green", None),
        ], "Capacidad por robot: 8h × 60 × 0,70 / 12 ≈ 28 misiones/día."),
        ("Arquitectura", "Control por capas: navegar, actuar y dejar evidencia", "violet", [
            ("Percepción", "LiDAR, RGB-D, RFID/QR.", "teal", None),
            ("Localización", "SLAM, IMU y encoders.", "cyan", None),
            ("Planificación", "Global A*/Dijkstra; local TEB.", "amber", None),
            ("Control", "vx, vy, ω → ruedas mecanum.", "green", None),
        ], "Registro: robot_id, kit_id, origen, destino, ruta, RFID, QR, timestamps y evento_FOD."),
        ("Operación", "Un ciclo cerrado: pedir, mover, confirmar, registrar", "teal", [
            ("Planificar", "HMI/MES lanza orden de entrega.", "teal", None),
            ("Validar kit", "Carga, RFID/QR y destino.", "green", None),
            ("Navegar", "Ruta SLAM y obstáculos.", "cyan", None),
            ("Cerrar", "Entrega, FOD, retorno y BD.", "violet", None),
        ], "Confirmación mínima en recepción, sin abandonar el puesto ni añadir tarea administrativa."),
        ("CoppeliaSim", "Validación previa al piloto físico", "cyan", [
            ("Escena real", "Nave, HTP, kitting y operarios.", "teal", None),
            ("Proxy", "YouBot mecanum; RB-KAIROS como referencia industrial.", "green", None),
            ("Ruta", "Parada/esquiva ante operario y zonas marcadas.", "amber", None),
            ("Salida", "Error ≤ 0,25 m, cero contactos, rutas alternativas.", "violet", None),
        ], "CoppeliaSim valida rutas y lógica; FAT/SAT valida carga real y seguridad."),
        ("Despliegue", "Tres fases con entregables y criterio de paso", "green", [
            ("1 piloto", "S1–S12 • 237.444 €.", "teal", None),
            ("Hito 1", "KPIs piloto.", "amber", None),
            ("7 expansión", "M4–M12 • 1.100.252 €.", "green", None),
            ("17 tentativo", "Año 2 • 2.495.768 €.", "violet", None),
        ], "Criterio 2: ≥ 1,1 HTP/mes de capacidad protegida o reducción ≥ 20 % de microesperas."),
        ("Presupuesto", "CAPEX y TCO por escenario", "amber", [
            ("1 robot", "237.444 €", "teal", None),
            ("7 robots", "1.100.252 €", "green", None),
            ("17 robots", "2.495.768 €", "violet", None),
            ("TCO 3 años", "284 k€ / 1,30 M€ / 2,95 M€", "amber", None),
        ], "Mapa rúbrica: personal, materiales, equipos y desplazamientos/logística quedan etiquetados."),
        ("ROI", "Decisión por datos de piloto", "violet", [
            ("18,4 €/h", "CHC = 24.000 × 1,35 / 1.760.", "teal", None),
            ("Piloto", "Compra seguridad, aceptación, rutas y KPIs reales.", "amber", None),
            ("7 robots", "Solo si demuestra ≥ 1,25 HTP/mes protegido.", "green", None),
            ("17 robots", "Decisión estratégica: multi-zona o doble turno.", "violet", None),
        ], "No se asume sustitución 1:1; se monetiza tiempo recuperado y continuidad de flujo."),
        ("Oferta comercial", "Entregables y condiciones de aceptación", "amber", [
            ("Entregables", "Mapa, configuración AMR, registro, FOD, CoppeliaSim y escalado.", "teal", None),
            ("Aceptación", "0 contactos, ≥95 % misiones, ≥98 % registro, ≥90 % disponibilidad.", "green", None),
            ("Usuarios", "Formación y protocolo de parada entendidos.", "violet", None),
            ("Pago", "M0 30 % • M3 40 % • M5 20 % • M6 10 %.", "red", None),
        ], "Pago por hitos: evita pagar toda la fase sin validar entrega y KPIs."),
        ("Recomendación", "Medir antes de escalar", "green", [
            ("S1", "Levantamiento de planta.", "teal", None),
            ("S2–S4", "Mapa, rutas, carga y SAT inicial.", "amber", None),
            ("S5–S10", "Operación piloto y captura de KPIs.", "green", None),
            ("S11–S12", "Revisión KPI y decisión.", "violet", None),
        ], "1 robot primero. Escalar solo con datos."),
        ("AMDEC piloto", "Riesgos principales y mitigaciones", "teal", [
            ("Contacto operario", "Zonas lentas, escáner, bumper y E-stop.", "red", None),
            ("FOD por AMR", "Portakits cerrados, limpieza y ronda RGB-D.", "amber", None),
            ("Pasillo/grúa", "Zonificación dinámica y replanificación TEB.", "green", None),
            ("RFID/WiFi", "Doble lectura, buffer local y contingencia manual.", "violet", None),
        ], "Riesgos aeronáuticos explícitos: AS9100/NAS 412, FOD del propio AMR y grúa puente."),
    ]

    for idx, (kicker, title, color, cards, note) in enumerate(specs, start=2):
        s = prs.slides.add_slide(prs.slide_layouts[6])
        add_header(s, idx, kicker, title, color)
        # Special media slides
        if idx == 7:
            p = (BASE / "../figures/source/alestis_estacion_herramientas.png").resolve()
            if p.exists():
                s.shapes.add_picture(str(p), Inches(0.85), Inches(1.35), width=Inches(4.2))
                x0 = 5.5
            else:
                x0 = 0.95
            for j, c in enumerate(cards):
                add_card(s, x0 + (j % 2) * 3.1, 1.45 + (j // 2) * 1.45, 2.75, 1.1, c[0], c[1], c[2])
        elif idx == 12:
            p = (BASE / "../figures/source/robotnik_rb_kairos.png").resolve()
            if p.exists():
                s.shapes.add_picture(str(p), Inches(0.85), Inches(1.38), width=Inches(5.0), height=Inches(3.4))
            for j, c in enumerate(cards):
                add_card(s, 6.2, 1.28 + j * 1.0, 5.9, 0.78, c[0], c[1], c[2])
        elif idx == 16:
            for j, name in enumerate(["../figures/coppeliasim/ss2.png", "../figures/coppeliasim/ss1.png", "../figures/coppeliasim/ss3.png"]):
                p = (BASE / name).resolve()
                if p.exists():
                    s.shapes.add_picture(str(p), Inches(0.75 + j * 3.35), Inches(1.35), width=Inches(3.15), height=Inches(2.05))
            for j, c in enumerate(cards):
                add_card(s, 0.85 + j * 3.05, 4.05, 2.75, 1.15, c[0], c[1], c[2])
        elif idx == 18:
            for j, c in enumerate(cards):
                add_card(s, 0.85 + j * 3.05, 1.25, 2.75, 1.0, c[0], c[1], c[2], value=c[1])
            budget_rows = [
                ["Partida", "1 robot", "7 robots", "17 robots*"],
                ["Equipos: AMR + sensores + carga", "78.500", "549.500", "1.334.500"],
                ["Personal: ingeniería + CE", "46.000", "126.000", "245.000"],
                ["Personal: instalación + SAT", "20.000", "60.000", "135.000"],
                ["Logística y medios", "5.000", "20.000", "40.000"],
                ["Contingencia + margen", "41.144", "190.652", "432.468"],
            ]
            add_table(s, 0.85, 2.65, 11.75, 2.35, len(budget_rows), 4, budget_rows, 7.0)
        elif idx == 22:
            risk_rows = [
                ["Riesgo", "Mitigación", "RPN"],
                ["Contacto con operario", "Zonas lentas + E-stop", "36"],
                ["FOD generado por AMR", "Portakits + ronda RGB-D", "72"],
                ["Pasillo/grúa bloquea ruta", "Zonificación + TEB", "84"],
                ["RFID/WiFi", "Doble lectura + buffer", "54/60"],
                ["Escalado prematuro", "Gates con umbral medido", "32"],
            ]
            add_table(s, 0.85, 1.35, 11.7, 3.3, len(risk_rows), 3, risk_rows, 8.2)
        else:
            for j, c in enumerate(cards):
                x = 0.85 + (j % 2) * 5.9
                y = 1.35 + (j // 2) * 1.55
                add_card(s, x, y, 5.4, 1.15, c[0], c[1], c[2], value=c[3])
        add_rect(s, 0.85, 6.05, 11.75, 0.65, "panel", color)
        add_text(s, note, 1.05, 6.22, 11.3, 0.25, size=9, color="ink", bold=True)

    # Slide 23: thanks
    s = prs.slides.add_slide(prs.slide_layouts[6])
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = rgb("paper")
    add_text(s, "¡Muchas gracias!", 0, 3.25, W, 0.8, size=48, color="navy", bold=True, align=PP_ALIGN.CENTER)

    # Slide 24: references
    s = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(s, 24, "", "Referencias", "violet")
    refs = [
        "[1] ISO 3691-4, Driverless industrial trucks and their systems.",
        "[2] SAE NAS 412, Foreign Object Damage / Foreign Object Debris Prevention.",
        "[3] EN 9100 / AS9100D, sistemas de gestión de calidad aeroespacial.",
        "[4] Coppelia Robotics, CoppeliaSim User Manual, 2026.",
        "[5] Siegwart, Nourbakhsh y Scaramuzza, Introduction to Autonomous Mobile Robots.",
        "[6] Robotnik Automation, RB-KAIROS Datasheet, 2024–2026.",
        "[7] AGILOX ODM; MiR250 Specifications, benchmarks AMR.",
        "[8] Intel RealSense D435i, Hokuyo UST-10LX y Zebra FX9600.",
    ]
    add_multiline(s, refs, 0.95, 1.25, 11.5, 4.9, size=10.5, color="ink", bullet=False, line_spacing=1.05)
    add_text(s, "Referencias completas, enlaces y fechas de consulta: bibliografía del informe técnico.", 0.95, 6.35, 11.8, 0.25, size=8.5, color="muted")

    prs.save(EDITABLE_OUT)


def main() -> None:
    if PIXEL_SOURCE.exists():
        copyfile(PIXEL_SOURCE, PIXEL_OUT)
    build_editable()
    print(f"Pixel-perfect: {PIXEL_OUT}")
    print(f"Editable:      {EDITABLE_OUT}")


if __name__ == "__main__":
    main()
