import streamlit as st
import pandas as pd
from datetime import datetime, date
import io

# Configuración inicial de la página
st.set_page_config(
    page_title="Sistema de Planilla y Tareo - Perú", 
    page_icon="🏢", 
    layout="wide"
)

# =========================================================
# ESTILOS CSS PERSONALIZADOS (Diseño Novedoso y Limpio)
# =========================================================
st.markdown("""
    <style>
    /* Fondo general y tipografía */
    .main {
        background-color: #f8f9fa;
    }
    
    /* Estilo para las tarjetas o contenedores */
    .card {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
        border: 1px solid #e9ecef;
    }
    
    /* Botones principales personalizados */
    .stButton>button {
        background-color: #0d6efd;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #0b5ed7;
        box-shadow: 0 4px 8px rgba(13, 110, 253, 0.2);
    }
    
    /* Títulos y cabeceras */
    h1, h2, h3 {
        color: #212529;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

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

# =========================================================
# CABECERA VISUAL DE LA APLICACIÓN
# =========================================================
st.markdown("""
    <div style="padding: 20px 0; border-bottom: 2px solid #e9ecef; margin-bottom: 25px;">
        <h1 style="margin: 0; color: #1e293b;">🏢 Sistema Integral de Planilla, Tareo y Liquidación</h1>
        <p style="margin: 5px 0 0 0; color: #64748b; font-size: 1.1rem;">
            Plataforma corporativa de gestión de asistencia, normativa laboral peruana y beneficios sociales.
        </p>
    </div>
""", unsafe_allow_html=True)

# =========================================================
# NAVEGACIÓN POR PESTAÑAS (Interfaz Limpia y Organizada)
# =========================================================
tab1, tab2, tab3 = st.tabs([
    "👤 1. Gestión de Colaboradores", 
    "📅 2. Módulo de Tareo e Incidencias", 
    "📊 3. Planilla, Cálculos y Liquidación"
])

# ---------------------------------------------------------
# PESTAÑA 1: COLABORADORES
# ---------------------------------------------------------
with tab1:
    st.markdown("### Directorio y Altas de Personal")
    
    col_sub1, col_sub2 = st.columns(2)
    
    with col_sub1:
        with st.container():
            st.markdown("#### 📁 Importación Masiva")
            archivo_excel = st.file_uploader("Sube el archivo Excel / CSV de la empresa:", type=["xlsx", "csv"], key="carga_masiva")
            if archivo_excel is not None:
                try:
                    df_carga = pd.read_csv(archivo_excel) if archivo_excel.name.endswith('.csv') else pd.read_excel(archivo_excel)
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
                                    "nombre": nom_val, "sueldo": sue_val, "ingreso": str(date.today()), "cese": ""
                                }
                        st.success("¡Colaboradores importados con éxito!")
                    else:
                        st.error("No se detectaron columnas válidas de DNI y Nombre.")
                except Exception as e:
                    st.error(f"Error al procesar archivo: {e}")

    with col_sub2:
        with st.container():
            st.markdown("#### ➕ Registro / Edición Manual")
            nuevo_dni = st.text_input("DNI (8 dígitos):", max_chars=8, key="reg_dni")
            nuevo_nombre = st.text_input("Nombre Completo:", key="reg_nom")
            nuevo_sueldo = st.number_input("Sueldo Base (S/):", min_value=1025.0, value=1170.0, step=50.0, key="reg_sue")
            fecha_ingreso_reg = st.date_input("Fecha de Ingreso:", value=date(2025, 10, 28), key="reg_ing")
            tiene_cese = st.checkbox("¿Trabajador cesado?", key="chk_cese", value=True)
            fecha_cese_reg = st.date_input("Fecha de Cese:", value=date(2026, 7, 20), key="reg_ces") if tiene_cese else ""
            
            if st.button("Guardar / Actualizar Trabajador"):
                if nuevo_dni and len(nuevo_dni) == 8 and nuevo_nombre:
                    st.session_state.empleados_db[nuevo_dni] = {
                        "nombre": nuevo_nombre, "sueldo": nuevo_sueldo,
                        "ingreso": str(fecha_ingreso_reg), "cese": str(fecha_cese_reg) if tiene_cese else ""
                    }
                    st.success(f"¡Trabajador {nuevo_nombre} guardado correctamente!")
                    st.rerun()
                else:
                    st.warning("Ingresa un DNI válido de 8 dígitos y el nombre completo.")

    st.markdown("---")
    st.markdown("#### 📋 Listado Actual de Personal Registrado")
    if st.session_state.empleados_db:
        df_emps = pd.DataFrame.from_dict(st.session_state.empleados_db, orient='index').reset_index()
        df_emps.columns = ["DNI", "Nombre Completo", "Sueldo Base (S/)", "Fecha Ingreso", "Fecha Cese"]
        st.dataframe(df_emps, use_container_width=True)

# ---------------------------------------------------------
# PESTAÑA 2: TAREO DIARIO
# ---------------------------------------------------------
with tab2:
    st.markdown("### Registro de Asistencia, Tardanzas y DSO Temporal")
    
    lista_opciones = [f"{dni} - {info['nombre']}" for dni, info in st.session_state.empleados_db.items()]
    
    if lista_opciones:
        seleccion_actual = st.selectbox("Seleccione al colaborador:", lista_opciones, key="sel_colab_tareo")
        dni_activo = seleccion_actual.split(" - ")[0]
        datos_trabajador = st.session_state.empleados_db[dni_activo]
        nombre_colaborador = datos_trabajador["nombre"]
        
        st.info(f"👤 **Colaborador Activo:** {nombre_colaborador} | 🆔 **DNI:** {dni_activo} | 📅 **Periodo Laboral:** {datos_trabajador['ingreso']} al {datos_trabajador['cese'] if datos_trabajador['cese'] else 'Activo'}")
        
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
                if estado_asistencia == "DSO Temporal (Sin labor / No remunerado)":
                    st.warning("ℹ️ DSO Temporal: 0.0 hrs (Sin afectación negativa).")
                else:
                    st.warning(f"ℹ️ Incidencia '{estado_asistencia}': 0.0 hrs.")
            elif estado_asistencia == "Tardanza":
                horas_trabajadas = 8.0
                minutos_tardanza_ingresados = st.number_input("Minutos de tardanza:", min_value=1, max_value=300, value=15, step=1)
            elif estado_asistencia == "Trabajo en Día de Descanso (100%)":
                horas_trabajadas = st.number_input("Horas laboradas en día libre:", min_value=0.0, max_value=12.0, value=8.0, step=0.5)
                st.info("ℹ️ Generará sobretasa del 100%.")
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
                        st.error(f"❌ Error de validación: El rango ({fecha_inicio_dso} a {fecha_fin_dso}) está fuera del periodo laboral activo ({datos_trabajador['ingreso']} al {datos_trabajador['cese'] if datos_trabajador['cese'] else 'Presente'}).")
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
                    st.error(f"❌ Error de validación: La fecha {fecha_registro} está fuera del periodo laboral del colaborador.")
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
# PESTAÑA 3: RESUMEN Y LIQUIDACIÓN
# ---------------------------------------------------------
with tab3:
    st.markdown("### Resumen Mensual y Liquidación Profesional")
    
    if lista_opciones:
        # Usamos el mismo colaborador activo seleccionado
        dni_activo_l = seleccion_actual.split(" - ")[0]
        datos_trabajador_l = st.session_state.empleados_db[dni_activo_l]
        
        col_cfg1, col_cfg2, col_cfg3 = st.columns(3)
        with col_cfg1:
            sueldo_base = st.number_input("Sueldo Bruto Base (S/):", min_value=1025.0, value=float(datos_trabajador_l["sueldo"]), step=100.0, key="sue_liq")
        with col_cfg2:
            asig_familiar = st.checkbox("Asignación Familiar (S/ 102.50)", value=False, key="af_liq")
        with col_cfg3:
            sistema_pension = st.selectbox("Sistema de Pensiones:", ["ONP (13%)", "AFP Integra (Flujo)", "AFP Prima (Flujo)", "AFP Habitat (Flujo)", "AFP Profuturo (Flujo)", "Exonerado"], key="pension_liq")
            
        seguro_vida_ley = st.checkbox("Aplica Seguro de Vida Ley (~0.6%)", value=True, key="sv_liq")
        
        monto_asig_fam = 102.50 if asig_familiar else 0.0
        sueldo_bruto_total = sueldo_base + monto_asig_fam
        
        faltas_injustificadas = 0
        total_minutos_tardanza = 0
        total_horas_extras_25 = 0.0
        total_horas_extras_35 = 0.0
        dias_descanso_trabajados = 0
        
        for reg in st.session_state.registros_tareo:
            if reg["DNI"] == dni_activo_l:
                cond = reg["Condición"]
                if cond == "Falta Injustificada": faltas_injustificadas += 1
                elif cond == "Tardanza": total_minutos_tardanza += reg.get("Min_Tardanza", 0)
                elif cond == "Trabajo en Día de Descanso (100%)": dias_descanso_trabajados += 1
                
                he = reg.get("Horas_Extras", 0.0)
                pct = reg.get("Porcentaje_HE", 25)
                if he > 0:
                    if pct == 25: total_horas_extras_25 += he
                    else: total_horas_extras_35 += he

        valor_dia = sueldo_base / 30.0
        valor_hora = sueldo_base / 240.0
        valor_minuto = sueldo_base / 14400.0
        
        descuento_faltas = valor_dia * faltas_injustificadas
        descuento_tardanzas = valor_minuto * total_minutos_tardanza
        total_pago_he = (total_horas_extras_25 * valor_hora * 1.25) + (total_horas_extras_35 * valor_hora * 1.35)
        pago_descanso_trabajado = valor_dia * dias_descanso_trabajados
        
        sueldo_bruto_ajustado = max(0.0, sueldo_bruto_total - descuento_faltas - descuento_tardanzas + total_pago_he + pago_descanso_trabajado)
        
        descuento_pension = sueldo_bruto_ajustado * 0.13 if "ONP" in sistema_pension else (sueldo_bruto_ajustado * 0.1115 if "AFP" in sistema_pension else 0.0)
        descuento_seguro_vida = sueldo_bruto_ajustado * 0.006 if seguro_vida_ley else 0.0
        sueldo_neto = sueldo_bruto_ajustado - descuento_pension - descuento_seguro_vida
        
        st.markdown("---")
        st.markdown("#### 💵 Simulación de Pago Mensual")
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Sueldo Bruto Inicial", f"S/ {sueldo_bruto_total:.2f}")
        m2.metric("Descuentos", f"- S/ {(descuento_faltas + descuento_tardanzas):.2f}", delta=f"{faltas_injustificadas} faltas, {total_minutos_tardanza}m tard.", delta_color="inverse")
        m3.metric("Adicionales (HE/Desc)", f"+ S/ {(total_pago_he + pago_descanso_trabajado):.2f}")
        m4.metric("Descuentos Ley", f"- S/ {(descuento_pension + descuento_seguro_vida):.2f}")
        m5.metric("Neto a Pagar Mensual", f"S/ {sueldo_neto:.2f}")
        
        st.markdown("---")
        st.markdown("#### 📐 Simulación de Liquidación y Beneficios Truncos (Normativa Peruana)")
        if datos_trabajador_l['cese']:
            st.warning(f"⚠️ El trabajador cuenta con fecha de cese ({datos_trabajador_l['cese']}). Calculando liquidación final...")
            try:
                f_ing = datetime.strptime(datos_trabajador_l['ingreso'], "%Y-%m-%d")
                f_ces = datetime.strptime(datos_trabajador_l['cese'], "%Y-%m-%d")
                dias_totales_servicio = (f_ces - f_ing).days + 1
                
                rem_computable_cts = sueldo_bruto_total + (sueldo_bruto_total / 6.0)
                dias_semestre_cts = dias_totales_servicio % 180 if dias_totales_servicio > 180 else dias_totales_servicio
                cts_truncas = (rem_computable_cts / 360.0) * dias_semestre_cts
                
                meses_completos_grati = (f_ces.month - 1) % 6
                grati_truncas = (sueldo_bruto_total / 6.0) * meses_completos_grati + (sueldo_bruto_total / 180.0) * f_ces.day
                bonif_ley_grati = grati_truncas * 0.09
                vacaciones_truncas = (sueldo_base / 360.0) * (dias_totales_servicio % 365)
                
                total_liquidacion = cts_truncas + grati_truncas + bonif_ley_grati + vacaciones_truncas
                
                l1, l2, l3, l4 = st.columns(4)
                l1.metric("CTS Truncas", f"S/ {cts_truncas:.2f}")
                l2.metric("Gratificación + Bonif", f"S/ {(grati_truncas + bonif_ley_grati):.2f}")
                l3.metric("Vacaciones Truncas", f"S/ {vacaciones_truncas:.2f}")
                l4.metric("Total Liquidación Neta", f"S/ {total_liquidacion:.2f}")
            except Exception as e:
                st.error(f"Error en cálculo de liquidación: {e}")
        else:
            st.info("💡 Para simular la liquidación, marca la casilla de trabajador cesado con su fecha de cese en la Pestaña 1.")
            
        st.markdown("---")
        st.markdown("#### 📥 Reportes de Tareo Consolidado")
        if st.session_state.registros_tareo:
            df_tareo = pd.DataFrame(st.session_state.registros_tareo)
            st.dataframe(df_tareo, use_container_width=True)
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_tareo.to_excel(writer, index=False, sheet_name='Tareo_Consolidado')
            
            st.download_button(
                label="📥 Descargar Reporte Completo de Tareo en Excel",
                data=output.getvalue(),
                file_name="reporte_tareo_y_planilla.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary"
            )
        else:
            st.info("No hay registros de tareo generados todavía.")

---

<ElicitationsGroup>
<FollowUp>
¿Qué te parece este nuevo diseño con pestañas organizadas y un aspecto visual mucho más limpio y profesional para el usuario final?
</FollowUp>
</ElicitationsGroup>