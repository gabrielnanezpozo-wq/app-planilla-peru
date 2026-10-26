import streamlit as st
import pandas as pd

# ---------------------------------------------------------
# MEMORIA DE COLABORADORES (DNI COMO CLAVE ÚNICA)
# ---------------------------------------------------------
if 'empleados_db' not in st.session_state:
    st.session_state.empleados_db = {
        "45871234": {"nombre": "Juan Pérez", "sueldo": 2500.0},
        "71234567": {"nombre": "María Gómez", "sueldo": 3000.0},
        "10293847": {"nombre": "Carlos Ruiz", "sueldo": 1800.0}
    }

if 'registros_tareo' not in st.session_state:
    st.session_state.registros_tareo = []

# ---------------------------------------------------------
# CABECERA Y SELECCIÓN POR DNI
# ---------------------------------------------------------
st.markdown('<div class="main-title">Sistema de Gestor de Planilla y Tareo Mensual</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Control de asistencia por DNI e incidencias acumuladas.</div>', unsafe_allow_html=True)

col_trabajador, col_regimen = st.columns([1.2, 1], gap="medium")

with col_trabajador:
    st.subheader("👤 Búsqueda por DNI / Colaborador")
    
    # Formulario para registrar nuevos colaboradores con DNI
    with st.expander("➕ Registrar nuevo trabajador en la Base de Datos"):
        nuevo_dni = st.text_input("DNI (8 dígitos):", max_chars=8)
        nuevo_nombre = st.text_input("Nombre Completo:")
        nuevo_sueldo = st.number_input("Sueldo Base por defecto (S/):", min_value=1025.0, value=2500.0, step=100.0)
        
        if st.button("Guardar Trabajador"):
            if nuevo_dni and len(nuevo_dni) == 8 and nuevo_nombre:
                st.session_state.empleados_db[nuevo_dni] = {
                    "nombre": nuevo_nombre,
                    "sueldo": nuevo_sueldo
                }
                st.success(f"¡Trabajador {nuevo_nombre} (DNI: {nuevo_dni}) registrado con éxito!")
                st.rerun()
            else:
                st.warning("Ingresa un DNI válido de 8 dígitos y el nombre completo.")

    # Selector inteligente que muestra "DNI - Nombre" (Streamlit permite buscar escribiendo el DNI directamente)
    lista_opciones = [f"{dni} - {info['nombre']}" for dni, info in st.session_state.empleados_db.items()]
    
    if lista_opciones:
        seleccion_actual = st.selectbox("Seleccione o busque por DNI/Nombre:", lista_opciones)
        
        # Extraer el DNI de la selección (los primeros 8 caracteres)
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
        sueldo_base = 2500.0
        asig_familiar = False
        nombre_colaborador = "Sin registro"