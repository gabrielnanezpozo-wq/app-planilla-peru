import streamlit as st
import pandas as pd
from datetime import datetime, date
import io

st.set_page_config(page_title="Gestor de Planilla, Tareo y Liquidación - Perú", layout="wide")

# ---------------------------------------------------------
# MEMORIA DE DATOS (DNI, EMPLEADOS Y TAREO)
# ---------------------------------------------------------
if 'empleados_db' not in st.session_state:
    st.session_state.empleados_db = {
        "73187638": {
            "nombre": "Nathaly Pupuche", 
            "sueldo": 1170.0, 
            "ingreso": str(date(2025, 10, 28)),
            "cese": str(date(2026, 7, 20))
        },
        "75163440": {
            "nombre": "Oliver Castillo Perales", 
            "sueldo": 1230.0, 
            "ingreso": str(date(2023, 1, 10)),
            "cese": ""
        }
    }

if 'registros_tareo' not in st.session_state:
    st.session_state.registros_tareo = []

# ---------------------------------------------------------
# CABECERA GENERAL
# ---------------------------------------------------------
st.markdown("## 🏢 Sistema Integral de Planilla, Tareo y Liquidación (Perú)")
st.markdown("Control de asistencia validado con fechas de contrato, tardanzas, horas extras, DSO temporal, CTS y Liquidación exacta.")
st.write("---")

# =========================================================
# SECCIÓN 1: REGISTRO Y GESTIÓN DE COLABORADORES
# =========================================================
st.markdown("### 1. 👤 Base de Datos y Fechas del Colaborador")

with st.expander("📁 Importar colaboradores desde un archivo Excel / CSV"):
    archivo_excel = st.file_uploader("Sube el archivo de la empresa:", type=["xlsx", "csv"], key="carga_masiva")
    
    if archivo_excel is not None:
        try:
            if archivo_excel.name.endswith('.csv'):
                df_carga = pd.read_csv(archivo_excel)
            else:
                df_carga = pd.read_excel(archivo_excel)
            
            df_carga.columns = [str(c).strip().lower() for c in df_carga.columns]
            col_dni = next((c for c in df_carga.columns if 'dni' in c or 'documento' in c), None)
            col_nom = next((c for c in df_carga.columns if 'nom' in c or 'trabajador' in c), None)
            col_sue = next((c for c in df_carga.columns if 'sueldo' in c or 'basico' in c), None)
            
            if col_dni and col_nom:
                for _, row in df_carga.iterrows():
                    dni_val = str(row[col_dni]).strip()
                    nom_val = str(row[col_nom]).strip()
                    sue_val = float(row[col_sue]) if col_sue and pd.notna(row[col_sue]) else 1025.0
                    
                    if len(dni_val) >= 8:
                        st.session_state.empleados_db[dni_val] = {
                            "nombre": nom_val,
                            "sueldo": sue_val,
                            "ingreso": str(date.today()),
                            "cese": ""
                        }
                st.success("¡Colaboradores importados con éxito!")
            else:
                st.error("No se detectaron columnas de DNI y Nombre.")
        except Exception as e:
            st.error(f"Error al procesar archivo: {e}")

with st.expander("➕ Registrar o actualizar trabajador de forma manual"):
    col_reg1, col_reg2, col_reg3 = st.columns(3)
    with col_reg1:
        nuevo_dni = st.text_input("DNI (8 dígitos):", max_chars=8, key="reg_dni")
        fecha_ingreso_reg = st.date_input("Fecha de Ingreso:", value=date(2025, 10, 28), key="reg_ing")
    with col_reg2:
        nuevo_nombre = st.text_input("Nombre Completo:", key="reg_nom")
        tiene_cese = st.checkbox("¿Trabajador cesado?", key="chk_cese", value=True)
    with col_reg3:
        nuevo_sueldo = st.number_input("Sueldo Base (S/):", min_value=1025.0, value=1170.0, step=50.0, key="reg_sue")
        fecha_cese_reg = st.date_input("Fecha de Cese:", value=date(2026, 7, 20), key="reg_ces") if tiene_cese else ""
    
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

# Selector principal por DNI
lista_opciones = [f"{dni} - {info['nombre']}" for dni, info in st.session_state.empleados_db.items()]

if lista_opciones:
    seleccion_actual = st.selectbox("Seleccione o busque al colaborador por DNI/Nombre:", lista_opciones)
    dni_activo = seleccion_actual.split(" - ")[0]
    datos_trabajador = st.session_state.empleados_db[dni_activo]
    nombre_colaborador = datos_trabajador["nombre"]
    
    col_dt1, col_dt2, col_dt3, col_dt4 = st.columns(4)
    with col_dt1:
        sueldo_base = st.number_input("Sueldo Bruto Base (S/):", min_value=1025.0, value=float(datos_trabajador["sueldo"]), step=100.0)
    with col_dt2:
        asig_familiar = st.checkbox("Asignación Familiar (S/ 102.50)", value=False)
    with col_dt3:
        regimen_laboral = st.selectbox("Régimen Laboral:", ["Regimen General (D. Leg. 728)", "Pequeña Empresa (Mype)", "Micro Empresa (Mype)", "CAS (D. Leg. 1057)"])
    with col_dt4:
        sistema_pension = st.selectbox("Sistema de Pensiones:", ["ONP (13%)", "AFP Integra (Flujo)", "AFP Prima (Flujo)", "AFP Habitat (Flujo)", "AFP Profuturo (Flujo)", "Exonerado"])
        
    seguro_vida_ley = st.checkbox("Aplica Seguro de Vida Ley (~0.6%)", value=True)
    
    st.info(f"🆔 **DNI:** {dni_activo} | **Ingreso:** {datos_trabajador['ingreso']} | **Cese:** {datos_trabajador['cese'] if datos_trabajador['cese'] else 'Activo'}")
else:
    st.warning("No hay trabajadores registrados.")
    dni_activo = ""
    nombre_colaborador = ""
    sueldo_base = 1025.0
    asig_familiar = False
    regimen_laboral = "Regimen General (D. Leg. 728)"
    sistema_pension = "ONP (13%)"
    seguro_vida_ley = False

st.write("---")

# =========================================================
# SECCIÓN 2: MÓDULO DE TAREO DIARIO Y CONDICIONES (CON CRUCE DE FECHAS)
# =========================================================
st.markdown("### 2. 📅 Módulo de Tareo Diario, Incidencias y DSO Temporal")

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
        st.info("📅 Rango de fechas para el DSO Temporal:")
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
        if estado_asistencia == "DSO Temporal (Sin labor / No remunerado)":
            st.warning("ℹ️ DSO Temporal: 0.0 hrs (Sin afectación negativa).")
        else:
            st.warning(f"ℹ️ Incidencia '{estado_asistencia}': Horas automáticas en 0.0 hrs.")
    elif estado_asistencia == "Tardanza":
        horas_trabajadas = 8.0
        minutos_tardanza_ingresados = st.number_input("Minutos de tardanza:", min_value=1, max_value=300, value=15, step=1)
    elif estado_asistencia == "Trabajo en Día de Descanso (100%)":
        horas_trabajadas = st.number_input("Horas laboradas en día libre:", min_value=0.0, max_value=12.0, value=8.0, step=0.5)
        st.info("ℹ️ Generará pago con sobretasa del 100%.")
    else:
        horas_trabajadas = st.number_input("Horas laboradas:", min_value=0.0, max_value=12.0, value=8.0, step=0.5)
        
    with st.expander("➕ Registrar Horas Extras en este día"):
        horas_extras_ingresadas = st.number_input("Cantidad de Horas Extras:", min_value=0.0, max_value=4.0, value=0.0, step=0.5)
        porcentaje_he = st.selectbox("Porcentaje de pago HE:", [25, 35, 50, 100], index=0)

with col_t3:
    archivo_sustento = st.file_uploader("Subir sustento (PDF / Imagen):", type=["pdf", "png", "jpg", "jpeg"])
    nombre_archivo = archivo_sustento.name if archivo_sustento else "Sin sustento"

if st.button("Registrar / Actualizar Asistencia en el Tareo", type="primary"):
    if dni_activo:
        f_ingreso_emp = datetime.strptime(datos_trabajador["ingreso"], "%Y-%m-%d").date()
        f_cese_emp = datetime.strptime(datos_trabajador["cese"], "%Y-%m-%d").date() if datos_trabajador["cese"] else None
        
        if estado_asistencia == "DSO Temporal (Sin labor / No remunerado)":
            if fecha_inicio_dso <= fecha_fin_dso:
                if fecha_inicio_dso < f_ingreso_emp or (f_cese_emp and fecha_fin_dso > f_cese_emp):
                    st.error(f"❌ Error de validación: El rango de fechas ({fecha_inicio_dso} a {fecha_fin_dso}) está fuera del periodo laboral activo del trabajador ({datos_trabajador['ingreso']} al {datos_trabajador['cese'] if datos_trabajador['cese'] else 'Presente'}).")
                else:
                    fechas_rango = pd.date_range(start=fecha_inicio_dso, end=fecha_fin_dso)
                    for f_item in fechas_rango:
                        str_f = f_item.strftime("%Y-%m-%d")
                        idx_existente = -1
                        for idx, reg in enumerate(st.session_state.registros_tareo):
                            if reg["DNI"] == dni_activo and reg["Fecha"] == str_f:
                                idx_existente = idx
                                break
                        
                        nuevo_item = {
                            "DNI": dni_activo,
                            "Colaborador": nombre_colaborador,
                            "Fecha": str_f,
                            "Condición": estado_asistencia,
                            "Horas": 0.0,
                            "Min_Tardanza": 0,
                            "Horas_Extras": 0.0,
                            "Porcentaje_HE": 25,
                            "Sustento": nombre_archivo
                        }
                        if idx_existente != -1:
                            st.session_state.registros_tareo[idx_existente] = nuevo_item
                        else:
                            st.session_state.registros_tareo.append(nuevo_item)
                    st.success(f"¡Rango de DSO Temporal registrado con éxito del {fecha_inicio_dso} al {fecha_fin_dso}!")
                    st.rerun()
            else:
                st.error("La fecha de inicio no puede ser posterior a la fecha de fin.")
        else:
            if fecha_registro < f_ingreso_emp or (f_cese_emp and fecha_registro > f_cese_emp):
                st.error(f"❌ Error de validación: La fecha {fecha_registro} no está comprendida dentro del periodo laboral del colaborador ({datos_trabajador['ingreso']} al {datos_trabajador['cese'] if datos_trabajador['cese'] else 'Presente'}).")
            else:
                idx_existente = -1
                for idx, reg in enumerate(st.session_state.registros_tareo):
                    if reg["DNI"] == dni_activo and reg["Fecha"] == str(fecha_registro):
                        idx_existente = idx
                        break
                
                nuevo_item = {
                    "DNI": dni_activo,
                    "Colaborador": nombre_colaborador,
                    "Fecha": str(fecha_registro),
                    "Condición": estado_asistencia,
                    "Horas": horas_trabajadas,
                    "Min_Tardanza": minutos_tardanza_ingresados if estado_asistencia == "Tardanza" else 0,
                    "Horas_Extras": horas_extras_ingresadas,
                    "Porcentaje_HE": porcentaje_he,
                    "Sustento": nombre_archivo
                }
                
                if idx_existente != -1:
                    st.session_state.registros_tareo[idx_existente] = nuevo_item
                    st.success(f"¡Registro actualizado con éxito para el {fecha_registro}!")
                else:
                    st.session_state.registros_tareo.append(nuevo_item)
                    st.success(f"¡Asistencia registrada para {nombre_colaborador} el {fecha_registro}!")
                st.rerun()
    else:
        st.warning("Selecciona un colaborador válido.")

st.write("---")

# =========================================================
# SECCIÓN 3: CÁLCULO DE PLANILLA, BENEFICIOS Y LIQUIDACIÓN EXACTA
# =========================================================
st.markdown("### 3. 📊 Resumen Mensual, Beneficios Sociales y Liquidación Profesional")

monto_asig_fam = 102.50 if asig_familiar else 0.0
sueldo_bruto_total = sueldo_base + monto_asig_fam

faltas_injustificadas = 0
total_minutos_tardanza = 0
total_horas_extras_25 = 0.0
total_horas_extras_35 = 0.0
dias_descanso_trabajados = 0

for reg in st.session_state.registros_tareo:
    if reg["DNI"] == dni_activo:
        cond = reg["Condición"]
        if cond == "Falta Injustificada":
            faltas_injustificadas += 1
        elif cond == "Tardanza":
            total_minutos_tardanza += reg.get("Min_Tardanza", 0)
        elif cond == "Trabajo en Día de Descanso (100%)":
            dias_descanso_trabajados += 1
        
        he = reg.get("Horas_Extras", 0.0)
        pct = reg.get("Porcentaje_HE", 25)
        if he > 0:
            if pct == 25:
                total_horas_extras_25 += he
            else:
                total_horas_extras_35 += he

valor_dia = sueldo_base / 30.0
valor_hora = sueldo_base / 240.0
valor_minuto = sueldo_base / 14400.0

descuento_faltas = valor_dia * faltas_injustificadas
descuento_tardanzas = valor_minuto * total_minutos_tardanza

pago_he_25 = total_horas_extras_25 * valor_hora * 1.25
pago_he_35 = total_horas_extras_35 * valor_hora * 1.35
total_pago_he = pago_he_25 + pago_he_35

pago_descanso_trabajado = valor_dia * dias_descanso_trabajados

sueldo_bruto_ajustado = sueldo_bruto_total - descuento_faltas - descuento_tardanzas + total_pago_he + pago_descanso_trabajado
if sueldo_bruto_ajustado < 0:
    sueldo_bruto_ajustado = 0.0

if "ONP" in sistema_pension:
    descuento_pension = sueldo_bruto_ajustado * 0.13
elif "AFP" in sistema_pension:
    descuento_pension = sueldo_bruto_ajustado * 0.1115
else:
    descuento_pension = 0.0

descuento_seguro_vida = (sueldo_bruto_ajustado * 0.006) if seguro_vida_ley else 0.0
sueldo_neto = sueldo_bruto_ajustado - descuento_pension - descuento_seguro_vida

col_res1, col_res2, col_res3, col_res4, col_res5 = st.columns(5)
col_res1.metric("Sueldo Bruto Inicial", f"S/ {sueldo_bruto_total:.2f}")
col_res2.metric("Descuentos", f"- S/ {(descuento_faltas + descuento_tardanzas):.2f}", delta=f"{faltas_injustificadas} faltas, {total_minutos_tardanza}m tard.", delta_color="inverse")
col_res3.metric("Adicionales (HE / Desc.)", f"+ S/ {(total_pago_he + pago_descanso_trabajado):.2f}")
col_res4.metric("Descuentos Ley", f"- S/ {(descuento_pension + descuento_seguro_vida):.2f}")
col_res5.metric("Neto a Pagar Mensual", f"S/ {sueldo_neto:.2f}")

st.write("---")

# Módulo de Liquidación / Beneficios Truncos Exactos (Norma Peruana)
st.markdown("#### 📐 Cálculo de Beneficios Sociales y Liquidación (CTS, Gratificación y Vacaciones Truncas)")
if datos_trabajador['cese']:
    st.warning(f"⚠️ El trabajador cuenta con fecha de cese registrada ({datos_trabajador['cese']}). Calculando liquidación final bajo normativa peruana...")
    try:
        f_ing = datetime.strptime(datos_trabajador['ingreso'], "%Y-%m-%d")
        f_ces = datetime.strptime(datos_trabajador['cese'], "%Y-%m-%d")
        
        dias_totales_servicio = (f_ces - f_ing).days + 1
        
        rem_computable_cts = sueldo_bruto_total + (sueldo_bruto_total / 6.0)
        dias_semestre_cts = dias_totales_servicio % 180 if dias_totales_servicio > 180 else dias_totales_servicio
        cts_truncas = (rem_computable_cts / 360.0) * dias_semestre_cts
        
        meses_completos_grati = (f_ces.month - 1) % 6
        grati_truncas = (sueldo_bruto_total / 6.0) * meses_completos_grati + (sueldo_bruto_total / 180.0) * f_ces.day
        bonif_ley_grati = grati_truncas * 0.09
        
        vacaciones_truncas = (sueldo_base / 360.0) * (dias_totales_servicio % 365)
        
        total_liquidacion = cts_truncas + grati_truncas + bonif_ley_grati + vacaciones_truncas
        
        col_liq1, col_liq2, col_liq3, col_liq4 = st.columns(4)
        col_liq1.metric("CTS Truncas", f"S/ {cts_truncas:.2f}")
        col_liq2.metric("Gratificación Trunca + Bonif", f"S/ {(grati_truncas + bonif_ley_grati):.2f}")
        col_liq3.metric("Vacaciones Truncas", f"S/ {vacaciones_truncas:.2f}")
        col_liq4.metric("Total Liquidación Neta", f"S/ {total_liquidacion:.2f}")
    except Exception as e:
        st.error(f"No se pudo calcular la liquidación automática: {e}")
else:
    st.info("💡 Para calcular la liquidación por cese, edita el trabajador en la Sección 1 y marca la casilla '¿Trabajador cesado?' indicando su fecha de cese.")

st.markdown("#### Historial de Tareo Registrado")

if st.session_state.registros_tareo:
    df_tareo = pd.DataFrame(st.session_state.registros_tareo)
    
    ver_todos = st.checkbox("Mostrar registros de tareo de todos los colaboradores", value=True)
    if not ver_todos and dni_activo:
        df_mostrar = df_tareo[df_tareo["DNI"] == dni_activo]
    else:
        df_mostrar = df_tareo
        
    st.dataframe(df_mostrar, use_container_width=True)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_tareo.to_excel(writer, index=False, sheet_name='Tareo_Consolidado')
    processed_data = output.getvalue()

    st.download_button(
        label="📥 Descargar Reporte Completo de Tareo en Excel",
        data=processed_data,
        file_name="reporte_tareo_y_planilla.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary"
    )
    
    if st.button("🗑️ Limpiar Todo el Historial de Tareo"):
        st.session_state.registros_tareo = []
        st.rerun()
else:
    st.info("Aún no hay registros de tareo acumulados.")