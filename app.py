import streamlit as st
import pandas as pd
from datetime import datetime, date
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Configuración de la página
st.set_page_config(
    page_title="Sistema de Planilla, Tareo y Liquidación - Perú", 
    page_icon="🏢", 
    layout="wide"
)

# =========================================================
# ESTILOS CSS PERSONALIZADOS
# =========================================================
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button {
        background-color: #0d6efd;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        border: none;
    }
    .stButton>button:hover { background-color: #0b5ed7; }
    h1, h2, h3 { color: #1e293b; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# HELPER DE PARSEO FLEXIBLE DE FECHAS
# ---------------------------------------------------------
def parsear_fecha_flexible(val):
    if pd.isna(val) or val is None or str(val).strip() == "":
        return ""
    if isinstance(val, (datetime, date)):
        return pd.to_datetime(val).strftime("%Y-%m-%d")
    val_str = str(val).strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d", "%d/%m/%y"):
        try:
            return datetime.strptime(val_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            pass
    try:
        return pd.to_datetime(val_str).strftime("%Y-%m-%d")
    except Exception:
        return ""

# ---------------------------------------------------------
# GENERADOR DE PDFs (REPORTLAB)
# ---------------------------------------------------------
def generar_pdf_boleta(datos_emp, resumen_pago, periodicidad):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=16, leading=20, textColor=colors.HexColor("#1e293b"), alignment=1)
    subtitle_style = ParagraphStyle('SubTitleStyle', parent=styles['Normal'], fontSize=10, leading=12, textColor=colors.HexColor("#64748b"), alignment=1)
    bold_style = ParagraphStyle('BoldStyle', parent=styles['Normal'], fontSize=9, leading=11, fontName='Helvetica-Bold')
    normal_style = ParagraphStyle('NormalStyle', parent=styles['Normal'], fontSize=9, leading=11)
    
    elements = []
    
    elements.append(Paragraph("<b>AGROEXPORT S.A.C.</b>", title_style))
    elements.append(Paragraph("RUC: 20123456789 | R.M. 091-92-TR", subtitle_style))
    elements.append(Paragraph(f"<b>BOLETA DE PAGO - PAGO {periodicidad.upper()}</b>", ParagraphStyle('Sub', parent=title_style, fontSize=12, leading=15)))
    elements.append(Spacer(1, 10))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#0d6efd"), spaceAfter=10))
    
    data_trab = [
        [Paragraph("<b>DNI:</b>", bold_style), Paragraph(datos_emp['dni'], normal_style), Paragraph("<b>Fecha Ingreso:</b>", bold_style), Paragraph(datos_emp['ingreso'], normal_style)],
        [Paragraph("<b>Trabajador:</b>", bold_style), Paragraph(datos_emp['nombre'], normal_style), Paragraph("<b>Fecha Cese:</b>", bold_style), Paragraph(datos_emp['cese'] if datos_emp['cese'] else "ACTIVO", normal_style)],
        [Paragraph(f"<b>Sueldo Base ({periodicidad}):</b>", bold_style), Paragraph(f"S/ {resumen_pago['sueldo_base_periodo']:.2f}", normal_style), Paragraph("<b>Asig. Familiar:</b>", bold_style), Paragraph(f"S/ {resumen_pago['asig_fam']:.2f}", normal_style)]
    ]
    t_trab = Table(data_trab, colWidths=[110, 150, 100, 180])
    t_trab.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8f9fa")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e9ecef")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#ced4da")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    elements.append(t_trab)
    elements.append(Spacer(1, 15))
    
    data_conceptos = [
        [Paragraph("<b>CONCEPTO / INGRESOS</b>", bold_style), Paragraph("<b>MONTO (S/)</b>", bold_style), Paragraph("<b>DESCUENTOS / RETENCIONES</b>", bold_style), Paragraph("<b>MONTO (S/)</b>", bold_style)],
        [Paragraph("Remuneración + Asig. Fam.", normal_style), Paragraph(f"{resumen_pago['sueldo_bruto_init']:.2f}", normal_style), Paragraph("Descuento Faltas / Tardanzas", normal_style), Paragraph(f"{resumen_pago['desc_asistencia']:.2f}", normal_style)],
        [Paragraph("Horas Extras / Adicionales", normal_style), Paragraph(f"{resumen_pago['pago_adicional']:.2f}", normal_style), Paragraph("Pensiones (ONP / AFP)", normal_style), Paragraph(f"{resumen_pago['desc_pension']:.2f}", normal_style)],
        [Paragraph("", normal_style), Paragraph("", normal_style), Paragraph("Seguro de Vida Ley", normal_style), Paragraph(f"{resumen_pago['desc_seguro']:.2f}", normal_style)],
        [Paragraph("<b>TOTAL INGRESOS BRUTOS</b>", bold_style), Paragraph(f"<b>S/ {resumen_pago['sueldo_bruto_ajustado']:.2f}</b>", bold_style), Paragraph("<b>TOTAL DESCUENTOS</b>", bold_style), Paragraph(f"<b>S/ {resumen_pago['total_descuentos']:.2f}</b>", bold_style)]
    ]
    t_con = Table(data_conceptos, colWidths=[180, 90, 180, 90])
    t_con.setStyle(TableStyle([
        ('HEADERBACKGROUND', (0,0), (-1,0), colors.HexColor("#0d6efd")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e9ecef")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#ced4da")),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    elements.append(t_con)
    elements.append(Spacer(1, 15))
    
    data_neto = [[Paragraph("<b>NETO A RECIBIR:</b>", ParagraphStyle('N1', parent=bold_style, fontSize=11)), Paragraph(f"<b>S/ {resumen_pago['sueldo_neto']:.2f}</b>", ParagraphStyle('N2', parent=bold_style, fontSize=11, textColor=colors.HexColor("#0d6efd")))]]
    t_neto = Table(data_neto, colWidths=[380, 160])
    t_neto.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#e7f1ff")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#0d6efd")),
        ('ALIGN', (1,0), (1,0), 'RIGHT'),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    elements.append(t_neto)
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

def generar_pdf_liquidacion(datos_emp, liq):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=16, leading=20, textColor=colors.HexColor("#1e293b"), alignment=1)
    subtitle_style = ParagraphStyle('SubTitleStyle', parent=styles['Normal'], fontSize=10, leading=12, textColor=colors.HexColor("#64748b"), alignment=1)
    bold_style = ParagraphStyle('BoldStyle', parent=styles['Normal'], fontSize=9, leading=11, fontName='Helvetica-Bold')
    normal_style = ParagraphStyle('NormalStyle', parent=styles['Normal'], fontSize=9, leading=11)
    
    elements = []
    
    elements.append(Paragraph("<b>AGROEXPORT S.A.C.</b>", title_style))
    elements.append(Paragraph("RUC: 20123456789 | R.M. 091-92-TR", subtitle_style))
    elements.append(Paragraph("<b>LIQUIDACIÓN DE BENEFICIOS SOCIALES (TRUNCOS)</b>", ParagraphStyle('Sub', parent=title_style, fontSize=12, leading=15)))
    elements.append(Spacer(1, 10))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#198754"), spaceAfter=10))
    
    data_trab = [
        [Paragraph("<b>DNI:</b>", bold_style), Paragraph(datos_emp['dni'], normal_style), Paragraph("<b>Fecha Ingreso:</b>", bold_style), Paragraph(datos_emp['ingreso'], normal_style)],
        [Paragraph("<b>Trabajador:</b>", bold_style), Paragraph(datos_emp['nombre'], normal_style), Paragraph("<b>Fecha Cese:</b>", bold_style), Paragraph(datos_emp['cese'], normal_style)],
        [Paragraph("<b>Tiempo Servicio:</b>", bold_style), Paragraph(f"{liq['dias_servicio']} días", normal_style), Paragraph("<b>Sueldo Computable:</b>", bold_style), Paragraph(f"S/ {liq['rem_computable']:.2f}", normal_style)]
    ]
    t_trab = Table(data_trab, colWidths=[100, 170, 110, 160])
    t_trab.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8f9fa")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e9ecef")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#ced4da")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    elements.append(t_trab)
    elements.append(Spacer(1, 15))
    
    data_liq = [
        [Paragraph("<b>BENEFICIO SOCIAL TRUNCO</b>", bold_style), Paragraph("<b>MONTO A BONAR (S/)</b>", bold_style)],
        [Paragraph("Compensación por Tiempo de Servicios (CTS Trunca)", normal_style), Paragraph(f"S/ {liq['cts']:.2f}", normal_style)],
        [Paragraph("Gratificación Trunca + Bonificación Extraordinaria (Ley 29351 - 9%)", normal_style), Paragraph(f"S/ {liq['grati_tot']:.2f}", normal_style)],
        [Paragraph("Vacaciones Truncas (D. Leg. 713)", normal_style), Paragraph(f"S/ {liq['vacaciones']:.2f}", normal_style)],
        [Paragraph("<b>TOTAL LIQUIDACIÓN NETA A PAGAR</b>", bold_style), Paragraph(f"<b>S/ {liq['total']:.2f}</b>", bold_style)]
    ]
    t_l = Table(data_liq, colWidths=[380, 160])
    t_l.setStyle(TableStyle([
        ('HEADERBACKGROUND', (0,0), (-1,0), colors.HexColor("#198754")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e9ecef")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#ced4da")),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(t_l)
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

# ---------------------------------------------------------
# MEMORIA DE DATOS
# ---------------------------------------------------------
if 'empleados_db' not in st.session_state:
    st.session_state.empleados_db = {
        "73187638": {
            "nombre": "Nathaly Pupuche", 
            "sueldo": 1170.0, 
            "ingreso": "2025-10-28",
            "cese": "2026-07-20"
        },
        "75163440": {
            "nombre": "Oliver Castillo Perales", 
            "sueldo": 1230.0, 
            "ingreso": "2023-01-10",
            "cese": ""
        }
    }

if 'registros_tareo' not in st.session_state:
    st.session_state.registros_tareo = []

# =========================================================
# CABECERA VISUAL
# =========================================================
st.markdown("""
    <div style="padding: 15px 0; border-bottom: 2px solid #e9ecef; margin-bottom: 20px;">
        <h1 style="margin: 0;">🏢 Sistema Integral de Planilla, Tareo y Liquidación</h1>
        <p style="margin: 5px 0 0 0; color: #64748b;">
            Gestión corporativa de asistencia, validación de fechas de contrato y emisión de boletas/liquidaciones en PDF.
        </p>
    </div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs([
    "👤 1. Gestión de Colaboradores", 
    "📅 2. Módulo de Tareo e Incidencias", 
    "📊 3. Resumen Monetario y Generación de PDF"
])

# ---------------------------------------------------------
# PESTAÑA 1: GESTIÓN DE COLABORADORES
# ---------------------------------------------------------
with tab1:
    st.markdown("### Directorio y Altas de Personal")
    col_sub1, col_sub2 = st.columns(2)
    
    with col_sub1:
        st.markdown("#### 📁 Importación Masiva (Excel / CSV)")
        archivo_excel = st.file_uploader("Sube el archivo con Fechas de Ingreso y Cese:", type=["xlsx", "csv"], key="carga_masiva")
        if archivo_excel is not None:
            try:
                df_carga = pd.read_csv(archivo_excel) if archivo_excel.name.endswith('.csv') else pd.read_excel(archivo_excel)
                df_carga.columns = [str(c).strip().lower() for c in df_carga.columns]
                
                col_dni = next((c for c in df_carga.columns if 'dni' in c or 'documento' in c), None)
                col_nom = next((c for c in df_carga.columns if 'nom' in c or 'trabajador' in c), None)
                col_sue = next((c for c in df_carga.columns if 'sueldo' in c or 'basico' in c), None)
                col_ing = next((c for c in df_carga.columns if 'ingreso' in c or 'inicio' in c), None)
                col_ces = next((c for c in df_carga.columns if 'cese' in c or 'fin' in c or 'salida' in c), None)
                
                if col_dni and col_nom:
                    c_nuevos = 0
                    for _, row in df_carga.iterrows():
                        dni_val = str(row[col_dni]).strip()
                        nom_val = str(row[col_nom]).strip()
                        sue_val = float(row[col_sue]) if col_sue and pd.notna(row[col_sue]) else 1025.0
                        ing_val = parsear_fecha_flexible(row[col_ing]) if col_ing else str(date.today())
                        ces_val = parsear_fecha_flexible(row[col_ces]) if col_ces else ""
                        
                        if len(dni_val) >= 8:
                            st.session_state.empleados_db[dni_val] = {
                                "nombre": nom_val,
                                "sueldo": sue_val,
                                "ingreso": ing_val if ing_val else str(date.today()),
                                "cese": ces_val
                            }
                            c_nuevos += 1
                    st.success(f"¡Se importaron / actualizaron {c_nuevos} colaboradores exitosamente!")
                else:
                    st.error("No se detectaron columnas válidas de DNI y Nombre.")
            except Exception as e:
                st.error(f"Error al procesar archivo: {e}")

    with col_sub2:
        st.markdown("#### ➕ Registro / Edición Manual")
        nuevo_dni = st.text_input("DNI (8 dígitos):", max_chars=8, key="reg_dni")
        nuevo_nombre = st.text_input("Nombre Completo:", key="reg_nom")
        nuevo_sueldo = st.number_input("Sueldo Base (S/):", min_value=1025.0, value=1170.0, step=50.0, key="reg_sue")
        fecha_ingreso_reg = st.date_input("Fecha de Ingreso:", value=date(2025, 10, 28), key="reg_ing")
        tiene_cese = st.checkbox("¿Trabajador cesado?", key="chk_cese", value=True)
        fecha_cese_reg = st.date_input("Fecha de Cese / Salida:", value=date(2026, 7, 20), key="reg_ces") if tiene_cese else ""
        
        if st.button("Guardar / Actualizar Trabajador"):
            if nuevo_dni and len(nuevo_dni) == 8 and nuevo_nombre:
                st.session_state.empleados_db[nuevo_dni] = {
                    "nombre": nuevo_nombre, 
                    "sueldo": nuevo_sueldo,
                    "ingreso": str(fecha_ingreso_reg), 
                    "cese": str(fecha_cese_reg) if tiene_cese else ""
                }
                st.success(f"¡Trabajador {nuevo_nombre} guardado correctamente!")
                st.rerun()
            else:
                st.warning("Ingresa un DNI válido de 8 dígitos y el nombre completo.")

    st.markdown("---")
    st.markdown("#### 📋 Listado de Personal Registrado")
    if st.session_state.empleados_db:
        lista_tabla = []
        for dni, info in st.session_state.empleados_db.items():
            lista_tabla.append({
                "DNI": dni,
                "Nombre Completo": info["nombre"],
                "Sueldo Base (S/)": info["sueldo"],
                "Fecha Ingreso": info["ingreso"],
                "Fecha Cese": info["cese"] if info["cese"] else "Activo"
            })
        df_emps = pd.DataFrame(lista_tabla)
        st.dataframe(df_emps, use_container_width=True)

# ---------------------------------------------------------
# PESTAÑA 2: TAREO DIARIO Y VALIDACIONES
# ---------------------------------------------------------
with tab2:
    st.markdown("### Control de Asistencia, Tardanzas y DSO Temporal")
    lista_opciones = [f"{dni} - {info['nombre']}" for dni, info in st.session_state.empleados_db.items()]
    
    if lista_opciones:
        seleccion_actual = st.selectbox("Seleccione al colaborador:", lista_opciones, key="sel_colab_tareo")
        dni_activo = seleccion_actual.split(" - ")[0]
        datos_trabajador = st.session_state.empleados_db[dni_activo]
        nombre_colaborador = datos_trabajador["nombre"]
        
        st.info(f"👤 **Colaborador Activo:** {nombre_colaborador} | 🆔 **DNI:** {dni_activo} | 📅 **Contrato:** {datos_trabajador['ingreso']} al {datos_trabajador['cese'] if datos_trabajador['cese'] else 'Activo'}")
        
        col_t1, col_t2, col_t3 = st.columns(3)
        
        with col_t1:
            estado_asistencia = st.selectbox("Condición / Incidencia:", [
                "Asistencia Normal (DSO / Labor)",
                "Falta Injustificada",
                "Tardanza",
                "Descanso Médico",
                "Permiso con Goce",
                "Vacaciones",
                "Suspensión",
                "Trabajo en Día de Descanso (100%)",
                "DSO Temporal (Sin labor / No remunerado)"
            ])
            
            if estado_asistencia == "DSO Temporal (Sin labor / No remunerado)":
                st.markdown("📅 **Rango de fechas para DSO Temporal:**")
                fecha_inicio_dso = st.date_input("Fecha de Inicio:", value=date.today(), key="dso_ini")
                fecha_fin_dso = st.date_input("Fecha de Fin:", value=date.today(), key="dso_fin")
            else:
                fecha_registro = st.date_input("Fecha de Asistencia:", value=date.today(), key="asist_unica")

        with col_t2:
            minutos_tardanza_ingresados = 0
            horas_extras_ingresadas = 0.0
            porcentaje_he = 25
            
            if estado_asistencia in ["Falta Injustificada", "Descanso Médico", "Vacaciones", "Suspensión", "DSO Temporal (Sin labor / No remunerado)"]:
                horas_trabajadas = 0.0
                st.warning("ℹ️ Registro automático en 0.0 hrs.")
            elif estado_asistencia == "Tardanza":
                horas_trabajadas = 8.0
                minutos_tardanza_ingresados = st.number_input("Minutos de tardanza:", min_value=1, max_value=300, value=15, step=1)
            elif estado_asistencia == "Trabajo en Día de Descanso (100%)":
                horas_trabajadas = st.number_input("Horas laboradas en día libre:", min_value=0.0, max_value=12.0, value=8.0, step=0.5)
            else:
                horas_trabajadas = st.number_input("Horas laboradas:", min_value=0.0, max_value=12.0, value=8.0, step=0.5)
                
            with st.expander("➕ Registrar Horas Extras"):
                horas_extras_ingresadas = st.number_input("Cantidad de Horas Extras:", min_value=0.0, max_value=4.0, value=0.0, step=0.5)
                porcentaje_he = st.selectbox("Porcentaje HE:", [25, 35, 50, 100], index=0)

        with col_t3:
            archivo_sustento = st.file_uploader("Subir sustento (PDF/Imagen):", type=["pdf", "png", "jpg", "jpeg"])
            nombre_archivo = archivo_sustento.name if archivo_sustento else "Sin sustento"

        if st.button("Registrar / Actualizar Asistencia en el Tareo", type="primary"):
            f_ingreso_emp = datetime.strptime(datos_trabajador["ingreso"], "%Y-%m-%d").date()
            f_cese_emp = datetime.strptime(datos_trabajador["cese"], "%Y-%m-%d").date() if datos_trabajador["cese"] else None
            
            if estado_asistencia == "DSO Temporal (Sin labor / No remunerado)":
                if fecha_inicio_dso <= fecha_fin_dso:
                    if fecha_inicio_dso < f_ingreso_emp or (f_cese_emp and fecha_fin_dso > f_cese_emp):
                        st.error(f"❌ Error de validación: El rango ({fecha_inicio_dso} a {fecha_fin_dso}) está fuera del periodo laboral activo del trabajador ({datos_trabajador['ingreso']} al {datos_trabajador['cese'] if datos_trabajador['cese'] else 'Presente'}).")
                    else:
                        for f_item in pd.date_range(start=fecha_inicio_dso, end=fecha_fin_dso):
                            str_f = f_item.strftime("%Y-%m-%d")
                            idx_ex = next((i for i, r in enumerate(st.session_state.registros_tareo) if r["DNI"] == dni_activo and r["Fecha"] == str_f), -1)
                            nuevo_item = {
                                "DNI": dni_activo, "Colaborador": nombre_colaborador, "Fecha": str_f,
                                "Condición": estado_asistencia, "Horas": 0.0, "Min_Tardanza": 0,
                                "Horas_Extras": 0.0, "Porcentaje_HE": 25, "Sustento": nombre_archivo
                            }
                            if idx_ex != -1: st.session_state.registros_tareo[idx_ex] = nuevo_item
                            else: st.session_state.registros_tareo.append(nuevo_item)
                        st.success(f"¡Rango de DSO Temporal registrado con éxito del {fecha_inicio_dso} al {fecha_fin_dso}!")
                        st.rerun()
                else:
                    st.error("La fecha de inicio no puede ser posterior a la fecha de fin.")
            else:
                if fecha_registro < f_ingreso_emp or (f_cese_emp and fecha_registro > f_cese_emp):
                    st.error(f"❌ Error de validación: La fecha {fecha_registro} está fuera del periodo laboral activo.")
                else:
                    idx_ex = next((i for i, r in enumerate(st.session_state.registros_tareo) if r["DNI"] == dni_activo and r["Fecha"] == str(fecha_registro)), -1)
                    nuevo_item = {
                        "DNI": dni_activo, "Colaborador": nombre_colaborador, "Fecha": str(fecha_registro),
                        "Condición": estado_asistencia, "Horas": horas_trabajadas,
                        "Min_Tardanza": minutos_tardanza_ingresados if estado_asistencia == "Tardanza" else 0,
                        "Horas_Extras": horas_extras_ingresadas, "Porcentaje_HE": porcentaje_he, "Sustento": nombre_archivo
                    }
                    if idx_ex != -1: st.session_state.registros_tareo[idx_ex] = nuevo_item
                    else: st.session_state.registros_tareo.append(nuevo_item)
                    st.success(f"¡Asistencia registrada para el {fecha_registro}!")
                    st.rerun()
    else:
        st.warning("Primero registra colaboradores en la Pestaña 1.")

# ---------------------------------------------------------
# PESTAÑA 3: RESUMEN MONETARIO Y DESCARGA DE PDF INDIVIDUAL
# ---------------------------------------------------------
with tab3:
    st.markdown("### Cálculo Monetario y Emisión de Documentos en PDF")
    
    if lista_opciones:
        seleccion_calculo = st.selectbox("Seleccione el colaborador a consultar:", lista_opciones, key="sel_calculo_mon")
        dni_calc = seleccion_calculo.split(" - ")[0]
        datos_emp = st.session_state.empleados_db[dni_calc]
        datos_emp['dni'] = dni_calc
        
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1:
            periodicidad = st.selectbox("Periodicidad de Pago:", ["Mensual", "Quincenal", "Semanal"], key="per_pago")
        with col_c2:
            asig_fam_check = st.checkbox("Incluir Asig. Familiar (Proporcional)", value=False, key="af_calc")
            seguro_vida_check = st.checkbox("Aplica Seguro de Vida Ley", value=True, key="sv_calc")
        with col_c3:
            sistema_pension = st.selectbox("Sistema de Pensiones:", ["ONP (13%)", "AFP Integra (Flujo)", "AFP Prima (Flujo)", "AFP Habitat (Flujo)", "AFP Profuturo (Flujo)", "Exonerado"], key="p_calc")

        # FACTOR DE PROPORCIÓN SEGÚN PERIODICIDAD
        sueldo_base_mensual = float(datos_emp["sueldo"])
        monto_af_mensual = 102.50 if asig_fam_check else 0.0
        
        if periodicidad == "Quincenal":
            factor = 0.5
            sueldo_base_periodo = sueldo_base_mensual * factor
            monto_af_periodo = monto_af_mensual * factor
        elif periodicidad == "Semanal":
            factor = 0.25
            sueldo_base_periodo = sueldo_base_mensual * factor
            monto_af_periodo = monto_af_mensual * factor
        else: # Mensual
            factor = 1.0
            sueldo_base_periodo = sueldo_base_mensual
            monto_af_periodo = monto_af_mensual

        sueldo_bruto_init = sueldo_base_periodo + monto_af_periodo
        
        faltas_injustificadas = 0
        total_minutos_tardanza = 0
        total_he_25 = 0.0
        total_he_35 = 0.0
        dias_descanso_trab = 0
        
        for reg in st.session_state.registros_tareo:
            if reg["DNI"] == dni_calc:
                cond = reg["Condición"]
                if cond == "Falta Injustificada": faltas_injustificadas += 1
                elif cond == "Tardanza": total_minutos_tardanza += reg.get("Min_Tardanza", 0)
                elif cond == "Trabajo en Día de Descanso (100%)": dias_descanso_trab += 1
                
                he = reg.get("Horas_Extras", 0.0)
                pct = reg.get("Porcentaje_HE", 25)
                if he > 0:
                    if pct == 25: total_he_25 += he
                    else: total_he_35 += he

        valor_dia = sueldo_base_mensual / 30.0
        valor_hora = sueldo_base_mensual / 240.0
        valor_minuto = sueldo_base_mensual / 14400.0
        
        desc_faltas = valor_dia * faltas_injustificadas
        desc_tardanzas = valor_minuto * total_minutos_tardanza
        desc_asistencia = desc_faltas + desc_tardanzas
        
        pago_he = (total_he_25 * valor_hora * 1.25) + (total_he_35 * valor_hora * 1.35)
        pago_descanso = valor_dia * dias_descanso_trab
        pago_adicional = pago_he + pago_descanso
        
        sueldo_bruto_ajustado = max(0.0, sueldo_bruto_init - desc_asistencia + pago_adicional)
        
        desc_pension = sueldo_bruto_ajustado * 0.13 if "ONP" in sistema_pension else (sueldo_bruto_ajustado * 0.1115 if "AFP" in sistema_pension else 0.0)
        desc_seguro = sueldo_bruto_ajustado * 0.006 if seguro_vida_check else 0.0
        total_descuentos = desc_asistencia + desc_pension + desc_seguro
        sueldo_neto = sueldo_bruto_ajustado - desc_pension - desc_seguro

        resumen_pago = {
            "sueldo_base_periodo": sueldo_base_periodo,
            "sueldo_bruto_init": sueldo_bruto_init,
            "asig_fam": monto_af_periodo,
            "desc_asistencia": desc_asistencia,
            "pago_adicional": pago_adicional,
            "sueldo_bruto_ajustado": sueldo_bruto_ajustado,
            "desc_pension": desc_pension,
            "desc_seguro": desc_seguro,
            "total_descuentos": total_descuentos,
            "sueldo_neto": sueldo_neto
        }

        st.markdown("---")
        st.markdown(f"#### 💵 Resumen de Pago ({periodicidad}) del Colaborador")
        col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
        col_m1.metric(f"Bruto Inicial ({periodicidad})", f"S/ {sueldo_bruto_init:.2f}")
        col_m2.metric("Descuentos Asistencia", f"- S/ {desc_asistencia:.2f}")
        col_m3.metric("Adicionales", f"+ S/ {pago_adicional:.2f}")
        col_m4.metric("Descuentos Ley", f"- S/ {(desc_pension + desc_seguro):.2f}")
        col_m5.metric(f"Neto a Pagar ({periodicidad})", f"S/ {sueldo_neto:.2f}")

        pdf_boleta_bytes = generar_pdf_boleta(datos_emp, resumen_pago, periodicidad)
        st.download_button(
            label=f"📄 Descargar Boleta de Pago ({periodicidad}) en PDF",
            data=pdf_boleta_bytes,
            file_name=f"boleta_{periodicidad.lower()}_{dni_calc}_{datos_emp['nombre'].replace(' ', '_')}.pdf",
            mime="application/pdf",
            type="primary"
        )

        st.markdown("---")
        st.markdown("#### 📐 Cálculo de Liquidación de Beneficios Sociales (Si aplica Cese)")
        
        if datos_emp['cese']:
            st.warning(f"⚠️ Trabajador cesado con fecha oficial de salida: {datos_emp['cese']}")
            try:
                f_ing = datetime.strptime(datos_emp['ingreso'], "%Y-%m-%d")
                f_ces = datetime.strptime(datos_emp['cese'], "%Y-%m-%d")
                dias_totales_servicio = (f_ces - f_ing).days + 1
                
                rem_computable_cts = sueldo_base_mensual + monto_af_mensual + ((sueldo_base_mensual + monto_af_mensual) / 6.0)
                dias_semestre_cts = dias_totales_servicio % 180 if dias_totales_servicio > 180 else dias_totales_servicio
                cts_truncas = (rem_computable_cts / 360.0) * dias_semestre_cts
                
                meses_completos_grati = (f_ces.month - 1) % 6
                grati_truncas = ((sueldo_base_mensual + monto_af_mensual) / 6.0) * meses_completos_grati + ((sueldo_base_mensual + monto_af_mensual) / 180.0) * f_ces.day
                bonif_ley_grati = grati_truncas * 0.09
                grati_total = grati_truncas + bonif_ley_grati
                
                vacaciones_truncas = (sueldo_base_mensual / 360.0) * (dias_totales_servicio % 365)
                total_liq = cts_truncas + grati_total + vacaciones_truncas
                
                resumen_liq = {
                    "dias_servicio": dias_totales_servicio,
                    "rem_computable": rem_computable_cts,
                    "cts": cts_truncas,
                    "grati_tot": grati_total,
                    "vacaciones": vacaciones_truncas,
                    "total": total_liq
                }
                
                col_l1, col_l2, col_l3, col_l4 = st.columns(4)
                col_l1.metric("CTS Truncas", f"S/ {cts_truncas:.2f}")
                col_l2.metric("Gratificación + Bonif.", f"S/ {grati_total:.2f}")
                col_l3.metric("Vacaciones Truncas", f"S/ {vacaciones_truncas:.2f}")
                col_l4.metric("Total Liquidación Neta", f"S/ {total_liq:.2f}")
                
                pdf_liq_bytes = generar_pdf_liquidacion(datos_emp, resumen_liq)
                st.download_button(
                    label="📄 Descargar Hoja de Liquidación de Beneficios (PDF)",
                    data=pdf_liq_bytes,
                    file_name=f"liquidacion_{dni_calc}_{datos_emp['nombre'].replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    type="primary"
                )
            except Exception as e:
                st.error(f"Error al calcular liquidación: {e}")
        else:
            st.info("💡 El colaborador se encuentra en estado ACTIVO. Si deseas emitir su liquidación, registra su Fecha de Cese en la Pestaña 1.")
    else:
        st.warning("No hay colaboradores registrados para consultar.")