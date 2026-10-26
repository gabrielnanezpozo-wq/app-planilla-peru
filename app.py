import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="Gestor de Planilla y Tareo - Perú", layout="wide")

# ---------------------------------------------------------
# MEMORIA DE DATOS (DNI, EMPLEADOS Y TAREO)
# ---------------------------------------------------------
if 'empleados_db' not in st.session_state:
    st.session_state.empleados_db = {
        "75163440": {"nombre": "Oliver Castillo Perales", "sueldo": 1230.0},
        "45871234": {"nombre": "Juan Pérez", "sueldo": 2500.0},
        "71234567": {"nombre": "María Gómez", "sueldo": 3000.0}
    }

if 'registros_tareo' not in st.session_state:
    st.session_state.registros_tareo = []

# ---------------------------------------------------------
# CABECERA GENERAL
# ---------------------------------------------------------
st.markdown("## 🏢 Sistema de Gestor de Planilla y Tareo Mensual (Perú)")
st.markdown("Control de asistencia por DNI, regímenes laborales, subida de sustentos y cálculo de planilla.")
st.write("---")

# =========================================================
# SECCIÓN 1: REGISTRO Y GESTIÓN DE COLABORADORES
# =========================================================
st.markdown("### 1. 👤 Registro y Selección de Colaborador")

with st.expander("➕ Registrar nuevo trabajador en la Base de Datos (DNI único)"):
    col_reg1, col_reg2, col_reg3 = st.columns(3)
    with col_reg1:
        nuevo_dni = st.text_input("DNI (8 dígitos):", max_chars=8, key="reg_dni")
    with col_reg2:
        nuevo_nombre = st.text_input("Nombre Completo:", key="reg_nom")
    with col_reg3:
        nuevo_sueldo = st.number_input("Sueldo Base por defecto (S/):", min_value=1025.0, value=1230.0, step=50.0, key="reg_sue")
    
    if st.button("Guardar Nuevo Trabajador"):
        if nuevo_dni and len(nuevo_dni) == 8 and nuevo_nombre:
            st.session_state.empleados_db[nuevo_dni] = {
                "nombre": nuevo_nombre,
                "sueldo": nuevo_sueldo
            }
            st.success(f"¡Trabajador {nuevo_nombre} (DNI: {nuevo_dni}) registrado con éxito!")
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
        asig_familiar = st.checkbox("Asignación Familiar (S/ 102.50)", value=True)
    with col_dt3:
        regimen_laboral = st.selectbox("Régimen Laboral:", ["Regimen General (D. Leg. 728)", "Pequeña Empresa (Mype)", "Micro Empresa (Mype)", "CAS (D. Leg. 1057)"])
    with col_dt4:
        sistema_pension = st.selectbox("Sistema de Pensiones:", ["ONP (13%)", "AFP Integra (Flujo)", "AFP Prima (Flujo)", "AFP Habitat (Flujo)", "AFP Profuturo (Flujo)", "Exonerado"])
        
    st.info(f"🆔 **DNI Activo:** {dni_activo} | **Colaborador Seleccionado:** {nombre_colaborador} | **Régimen:** {regimen_laboral}")
else:
    st.warning("No hay trabajadores registrados en la base de datos.")
    dni_activo = ""
    nombre_colaborador = ""
    sueldo_base = 1025.0
    asig_familiar = False
    regimen_laboral = "Regimen General (D. Leg. 728)"
    sistema_pension = "ONP (13%)"

st.write("---")

# =========================================================
# SECCIÓN 2: MÓDULO DE TAREO DIARIO Y SUSTENTO
# =========================================================
st.markdown("### 2. 📅 Módulo de Tareo Diario e Incidencias")

col_t1, col_t2, col_t3 = st.columns(3)

with col_t1:
    fecha_registro = st.date_input("Fecha de Asistencia:", value=date.today())
    estado_asistencia = st.selectbox("Condición / Incidencia:", [
        "Asistencia Normal (DSO / Labor)",
        "Falta Injustificada",
        "Tardanza",
        "Descanso Médico",
        "Permiso con Goce",
        "Vacaciones",
        "Suspensión"
    ])

with col_t2:
    # Lógica inteligente de horas según la condición
    if estado_asistencia in ["Falta Injustificada", "Descanso Médico", "Vacaciones", "Suspensión"]:
        horas_trabajadas = 0.0
        st.warning(f"ℹ️ Incidencia '{estado_asistencia}': Horas automáticas en 0.0 hrs.")
    else:
        horas_trabajadas = st.number_input("Horas laboradas en el día:", min_value=0.0, max_value=12.0, value=8.0, step=0.5)

with col_t3:
    archivo_sustento = st.file_uploader("Subir sustento (PDF o Imagen):", type=["pdf", "png", "jpg", "jpeg"])
    nombre_archivo = archivo_sustento.name if archivo_sustento else "Sin sustento adjunto"

if st.button("Registrar Asistencia en el Tareo", type="primary"):
    if dni_activo:
        st.session_state.registros_tareo.append({
            "DNI": dni_activo,
            "Colaborador": nombre_colaborador,
            "Fecha": str(fecha_registro),
            "Condición": estado_asistencia,
            "Horas": horas_trabajadas,
            "Sustento": nombre_archivo
        })
        st.success(f"¡Asistencia de {nombre_colaborador} registrada correctamente para el {fecha_registro}!")
    else:
        st.warning("Selecciona un colaborador válido antes de registrar.")

st.write("---")

# =========================================================
# SECCIÓN 3: CÁLCULO DE PLANILLA Y PAGO MENSUAL
# =========================================================
st.markdown("### 3. 📊 Resumen Acumulado y Cálculo del Pago Mensual")

# Cálculos base peruanos
monto_asig_fam = 102.50 if asig_familiar else 0.0
sueldo_bruto_total = sueldo_base + monto_asig_fam

# Descuento de ley aproximado
if "ONP" in sistema_pension:
    descuento_pension = sueldo_bruto_total * 0.13
elif "AFP" in sistema_pension:
    descuento_pension = sueldo_bruto_total * 0.1115
else:
    descuento_pension = 0.0

sueldo_neto = sueldo_bruto_total - descuento_pension

# Mostrar métricas claras del cálculo al usuario
col_res1, col_res2, col_res3, col_res4 = st.columns(4)
col_res1.metric("Sueldo Bruto Base + Asig.", f"S/ {sueldo_bruto_total:.2f}")
col_res2.metric("Descuento Ley Pensiones", f"- S/ {descuento_pension:.2f}")
col_res3.metric("Neto a Pagar Estimado", f"S/ {sueldo_neto:.2f}")
col_res4.metric("Régimen Aplicado", regimen_laboral.split()[0])

st.markdown("#### Historial y Base de Datos del Tareo Registrado")

if st.session_state.registros_tareo:
    df_tareo = pd.DataFrame(st.session_state.registros_tareo)
    
    # Filtro opcional para ver solo el DNI activo o todos
    ver_todos = st.checkbox("Mostrar registros de tareo de todos los colaboradores", value=True)
    if not ver_todos and dni_activo:
        df_mostrar = df_tareo[df_tareo["DNI"] == dni_activo]
    else:
        df_mostrar = df_tareo
        
    st.dataframe(df_mostrar, use_container_width=True)
    
    if st.button("🗑️ Limpiar Todo el Historial de Tareo"):
        st.session_state.registros_tareo = []
        st.rerun()
else:
    st.info("Aún no hay registros de tareo acumulados en el sistema. Utiliza la Sección 2 para empezar a registrar asistencias.")