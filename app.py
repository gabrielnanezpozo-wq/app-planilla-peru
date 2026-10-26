import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="Gestor de Planilla y Tareo", layout="wide")

# ---------------------------------------------------------
# MEMORIA DE DATOS (DNI & TAREO)
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
# CABECERA
# ---------------------------------------------------------
st.markdown("## 🏢 Sistema de Gestor de Planilla y Tareo Mensual")
st.markdown("Control de asistencia por DNI, tareo diario e incidencias acumuladas en Perú.")
st.write("---")

# ---------------------------------------------------------
# DISEÑO EN 2 COLUMNAS (IZQ: Colaborador / DER: Tareo Diario)
# ---------------------------------------------------------
col_trabajador, col_tareo = st.columns(2, gap="medium")

dni_activo = ""
nombre_colaborador = ""
sueldo_base = 1025.0
asig_familiar = False

with col_trabajador:
    st.subheader("👤 Datos del Colaborador")
    
    with st.expander("➕ Registrar nuevo trabajador en la Base de Datos"):
        nuevo_dni = st.text_input("DNI (8 dígitos):", max_chars=8, key="reg_dni")
        nuevo_nombre = st.text_input("Nombre Completo:", key="reg_nom")
        nuevo_sueldo = st.number_input("Sueldo Base por defecto (S/):", min_value=1025.0, value=1230.0, step=50.0, key="reg_sue")
        
        if st.button("Guardar Trabajador"):
            if nuevo_dni and len(nuevo_dni) == 8 and nuevo_nombre:
                st.session_state.empleados_db[nuevo_dni] = {
                    "nombre": nuevo_nombre,
                    "sueldo": nuevo_sueldo
                }
                st.success(f"¡Trabajador {nuevo_nombre} registrado con éxito!")
                st.rerun()
            else:
                st.warning("Ingresa un DNI válido de 8 dígitos y el nombre completo.")

    lista_opciones = [f"{dni} - {info['nombre']}" for dni, info in st.session_state.empleados_db.items()]
    
    if lista_opciones:
        seleccion_actual = st.selectbox("Seleccione o busque por DNI/Nombre:", lista_opciones)
        dni_activo = seleccion_actual.split(" - ")[0]
        datos_trabajador = st.session_state.empleados_db[dni_activo]
        
        nombre_colaborador = datos_trabajador["nombre"]
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            sueldo_base = st.number_input("Sueldo Bruto Base (S/):", min_value=1025.0, value=float(datos_trabajador["sueldo"]), step=100.0)
        with col_s2:
            asig_familiar = st.checkbox("Asignación Familiar (S/ 102.50)", value=False)
            
        st.caption(f"🆔 **DNI Activo:** {dni_activo} | **Colaborador:** {nombre_colaborador}")
    else:
        st.warning("No hay trabajadores registrados.")

with col_tareo:
    st.subheader("📅 Módulo de Tareo Diario")
    
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
    
    horas_trabajadas = st.number_input("Horas laboradas:", min_value=0.0, max_value=12.0, value=8.0, step=0.5)

    if st.button("Registrar Asistencia en Tareo"):
        if dni_activo:
            st.session_state.registros_tareo.append({
                "DNI": dni_activo,
                "Colaborador": nombre_colaborador,
                "Fecha": str(fecha_registro),
                "Condición": estado_asistencia,
                "Horas": horas_trabajadas
            })
            st.success(f"¡Asistencia guardada para {nombre_colaborador} ({fecha_registro})!")
        else:
            st.warning("Selecciona un colaborador válido primero.")

st.write("---")

# ---------------------------------------------------------
# SECCIÓN DE RESUMEN Y TABLA ACUMULATIVA DE TAREO
# ---------------------------------------------------------
st.subheader("📊 Resumen Acumulado de Tareo Mensual")

if st.session_state.registros_tareo:
    df_tareo = pd.DataFrame(st.session_state.registros_tareo)
    
    ver_todos = st.checkbox("Ver registros de todos los colaboradores", value=True)
    if not ver_todos and dni_activo:
        df_mostrar = df_tareo[df_tareo["DNI"] == dni_activo]
    else:
        df_mostrar = df_tareo
        
    st.dataframe(df_mostrar, use_container_width=True)
    
    col_btn1, col_btn2 = st.columns([1, 4])
    with col_btn1:
        if st.button("🗑️ Limpiar Historial"):
            st.session_state.registros_tareo = []
            st.rerun()
            
    sueldo_total_bruto = sueldo_base + (102.50 if asig_familiar else 0.0)
    st.info(f"💡 **Información de Planilla para {nombre_colaborador}:** Sueldo Bruto Calculado: **S/ {sueldo_total_bruto:.2f}** (Incluye Asig. Familiar: {'Sí' if asig_familiar else 'No'})")
else:
    st.info("Aún no hay registros en el tareo. Utiliza el módulo superior derecho para empezar a registrar asistencias.")