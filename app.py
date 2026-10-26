import streamlit as st
import pandas as pd
import datetime

# ---------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA Y ESTILO MINIMALISTA AZUL
# ---------------------------------------------------------
st.set_page_config(
    page_title="Sistema de Planilla & Tareo Acumulativo",
    page_icon="💼",
    layout="wide"
)

st.markdown("""
    <style>
    .stApp {
        background-color: #F8FAFC;
        font-family: 'Inter', system-ui, sans-serif;
    }
    .main-title {
        color: #1E3A8A;
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        color: #64748B;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }
    .stButton>button {
        background-color: #2563EB;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
    .stButton>button:hover {
        background-color: #1D4ED8;
        color: white;
    }
    .kpi-card {
        background-color: #FFFFFF;
        border-radius: 10px;
        padding: 1.2rem;
        border: 1px solid #E2E8F0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
    }
    .kpi-title {
        font-size: 0.8rem;
        color: #64748B;
        text-transform: uppercase;
        font-weight: 600;
    }
    .kpi-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #1E3A8A;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# MEMORIA TEMPORAL (SESIÓN)
# ---------------------------------------------------------
if 'registros_tareo' not in st.session_state:
    st.session_state.registros_tareo = []

# ---------------------------------------------------------
# CABECERA Y DATOS DEL TRABAJADOR
# ---------------------------------------------------------
st.markdown('<div class="main-title">Sistema de Gestor de Planilla y Tareo Mensual</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Registro diario de asistencia, acumulación de incidencias y cálculo de liquidación neta.</div>', unsafe_allow_html=True)

col_trabajador, col_regimen = st.columns([1.2, 1], gap="medium")

with col_trabajador:
    st.subheader("👤 Datos del Colaborador")
    nombre_colaborador = st.text_input("Nombre Completo:", value="Juan Pérez")
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        sueldo_base = st.number_input("Sueldo Bruto Base (S/):", min_value=1025.0, value=2500.0, step=100.0)
    with col_s2:
        asig_familiar = st.checkbox("Asignación Familiar (S/ 102.50)", value=False)

with col_regimen:
    st.subheader("⚖️ Régimen Laboral & Pensiones")
    regimen = st.selectbox(
        "Régimen Laboral Aplicable:",
        [
            "Régimen General (Empresa Grande - D. Leg. 728)",
            "Régimen MYPE - Pequeña Empresa",
            "Régimen MYPE - Microempresa"
        ]
    )
    pension = st.selectbox("Sistema de Pensiones:", ["AFP (Aporte Obligatorio ~13%)", "ONP (13%)"])

st.markdown("---")

# ---------------------------------------------------------
# REGISTRO DIARIO DE ASISTENCIA
# ---------------------------------------------------------
st.subheader("📝 Módulo de Registro Diario de Tareo")

col_f1, col_f2, col_f3 = st.columns([1, 1, 1.2])

with col_f1:
    fecha_reg = st.date_input("Fecha a evaluar:", datetime.date(2026, 10, 26))
    fecha_str = fecha_reg.strftime("%d/%m/%Y")

with col_f2:
    estado_asistencia = st.selectbox(
        "Estado de Asistencia:",
        [
            "Asistió",
            "Tardanza",
            "Faltó (Falta Injustificada)",
            "Falta Justificada",
            "DSO Médico (Descanso Médico)"
        ]
    )

with col_f3:
    detalles = ""
    min_tardanza = 0
    adjunto_nombre = "Ninguno"
    
    if estado_asistencia == "Tardanza":
        min_tardanza = st.number_input("Minutos de tardanza:", min_value=1, max_value=480, value=15)
        detalles = f"{min_tardanza} min de tardanza"
    elif estado_asistencia == "Falta Justificada":
        detalles = st.text_input("Motivo / Sustento:", placeholder="Ej. Trámite personal")
        archivo = st.file_uploader("Adjuntar documento:", type=["pdf", "jpg", "png"])
        if archivo:
            adjunto_nombre = archivo.name
    elif estado_asistencia == "DSO Médico (Descanso Médico)":
        detalles = st.text_input("Centro Médico / Diagnóstico:", placeholder="Ej. CITT ESSALUD")
        archivo = st.file_uploader("Adjuntar CITT / Remisión:", type=["pdf", "jpg", "png"])
        if archivo:
            adjunto_nombre = archivo.name

if st.button("➕ Registrar Día en el Tareo Mensual"):
    fechas_existentes = [r['Fecha'] for r in st.session_state.registros_tareo]
    if fecha_str in fechas_existentes:
        st.warning(f"La fecha {fecha_str} ya fue registrada.")
    else:
        st.session_state.registros_tareo.append({
            "Fecha": fecha_str,
            "Estado": estado_asistencia,
            "Min. Tardanza": min_tardanza,
            "Detalle / Sustento": detalles if detalles else "-",
            "Adjunto": adjunto_nombre
        })
        st.success(f"Día {fecha_str} agregado correctamente.")

# ---------------------------------------------------------
# TABLA ACUMULATIVA Y CÁLCULO MENSUAL
# ---------------------------------------------------------
st.markdown("---")
st.subheader("📋 Tabla Acumulativa de Tareo Mensual")

if len(st.session_state.registros_tareo) > 0:
    df_tareo = pd.DataFrame(st.session_state.registros_tareo)
    st.dataframe(df_tareo, use_container_width=True)
    
    if st.button("🗑️ Limpiar Todo el Tareo"):
        st.session_state.registros_tareo = []
        st.rerun()

    cant_faltas = len(df_tareo[df_tareo['Estado'] == "Faltó (Falta Injustificada)"])
    total_min_tardanza = df_tareo['Min. Tardanza'].sum()

    valor_dia = sueldo_base / 30.0
    valor_hora = valor_dia / 8.0
    valor_minuto = valor_hora / 60.0

    descuento_faltas = cant_faltas * valor_dia
    descuento_tardanzas = total_min_tardanza * valor_minuto
    total_descuentos = descuento_faltas + descuento_tardanzas

    monto_asig_fam = 102.50 if asig_familiar else 0.0
    ingresos_brutos = sueldo_base + monto_asig_fam
    base_imponible = ingresos_brutos - total_descuentos
    
    descuento_pension = base_imponible * 0.13
    sueldo_neto_final = base_imponible - descuento_pension

    st.markdown("### 💵 Resumen Mensual de Liquidación")
    
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""
        <div class="kpi-card" style="border-left: 4px solid #2563EB;">
            <div class="kpi-title">Ingresos Brutos</div>
            <div class="kpi-value">S/ {ingresos_brutos:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    with k2:
        st.markdown(f"""
        <div class="kpi-card" style="border-left: 4px solid #EF4444;">
            <div class="kpi-title" style="color:#991B1B;">Desc. Tareo Acumulado</div>
            <div class="kpi-value" style="color:#991B1B;">S/ {total_descuentos:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    with k3:
        st.markdown(f"""
        <div class="kpi-card" style="border-left: 4px solid #F59E0B;">
            <div class="kpi-title" style="color:#92400E;">Aporte Previsional</div>
            <div class="kpi-value" style="color:#92400E;">S/ {descuento_pension:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    with k4:
        st.markdown(f"""
        <div class="kpi-card" style="border-left: 4px solid #10B981; background-color: #ECFDF5;">
            <div class="kpi-title" style="color:#065F46;">Sueldo Neto a Pagar</div>
            <div class="kpi-value" style="color:#065F46;">S/ {sueldo_neto_final:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)

else:
    st.info("💡 Aún no has registrado días en el tareo. Utiliza el formulario superior.")