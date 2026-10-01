%%writefile streamlit_app.py

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

# Presets de Dados de Entrada
PRESETS = {
    "Exercício Anexo (AP1 - Navio 129m)": {
        "Lm": 4.30, "Sm": 3.75, "rhom": 1000.0, "num": 1.14e-6,
        "Ls": 129.00, "rhos": 1025.0, "nus": 1.19e-6, "g": 9.81,
        "k": 1.15, "Vm": 1.50, "Rtm": 18.00,
        "vm_list": "0.80, 1.00, 1.20, 1.40, 1.50, 1.60, 1.80, 2.00, 2.20, 2.40, 2.60"
    },
    "Caso de Estudo Wave Glider (NPL 30m)": {
        "Lm": 2.00, "Sm": 0.54, "rhom": 1000.0, "num": 1.2845e-6,
        "Ls": 30.00, "rhos": 1025.0, "nus": 1.19e-6, "g": 9.81,
        "k": 1.20, "Vm": 1.33, "Rtm": 3.85,
        "vm_list": "0.44, 0.66, 0.88, 1.11, 1.33, 1.55, 1.77, 1.99, 2.21"
    },
    "Customizado / Entrada Livre": {
        "Lm": 4.30, "Sm": 3.75, "rhom": 1000.0, "num": 1.14e-6,
        "Ls": 129.00, "rhos": 1025.0, "nus": 1.19e-6, "g": 9.81,
        "k": 1.15, "Vm": 1.50, "Rtm": 18.00,
        "vm_list": "0.80, 1.00, 1.20, 1.40, 1.50, 1.60, 1.80, 2.00, 2.20, 2.40, 2.60"
    }
}

st.title("⚓ Calculadora Hidrodinâmica")
st.markdown("Métodos de Froude e Hughes com Linha de Atrito ITTC-1957")

selected_preset = st.sidebar.selectbox(
    "Selecione um Caso Preset:",
    list(PRESETS.keys())
)

# Initialize values based on preset
def get_preset_values(preset_name):
    return PRESETS[preset_name]

p = get_preset_values(selected_preset)

st.sidebar.header("1. Dados do Modelo (Tanque)")
Lm = st.sidebar.number_input("L_m (m):", value=p["Lm"], format="%.2f")
Sm = st.sidebar.number_input("S_m (m²):", value=p["Sm"], format="%.2f")
rhom = st.sidebar.number_input("ρ_m (kg/m³):", value=p["rhom"], format="%.1f")
num = st.sidebar.number_input("ν_m (m²/s) (e.g., 1.14e-6):", value=p["num"], format="%.2e")

st.sidebar.header("2. Dados do Protótipo (Navio)")
Ls = st.sidebar.number_input("L_s (m):", value=p["Ls"], format="%.2f")
rhos = st.sidebar.number_input("ρ_s (kg/m³):", value=p["rhos"], format="%.1f")
nus = st.sidebar.number_input("ν_s (m²/s) (e.g., 1.19e-6):", value=p["nus"], format="%.2e")
g = st.sidebar.number_input("g (m/s²):", value=p["g"], format="%.2f")

st.sidebar.header("3. Fator de Forma e Ensaio")
k_factor = st.sidebar.number_input("(1+k):", value=p["k"], format="%.2f")
Vm_single = st.sidebar.number_input("V_m (m/s) (para ponto único):", value=p["Vm"], format="%.2f")
Rtm_single = st.sidebar.number_input("R_Tm (N) (para ponto único):", value=p["Rtm"], format="%.2f")

vm_list_str = st.sidebar.text_input(
    "Série V_m (m/s) (separado por vírgulas):",
    value=p["vm_list"]
)

# Main calculation function
def calculate_extrapolation(
    Lm, Sm, rhom, num, Ls, rhos, nus, g, k_factor, Vm_single, Rtm_single, vm_list_str
):
    scale = Ls / Lm
    Ss = Sm * (scale ** 2)

    # Ponto Único
    Vs_ms = Vm_single * np.sqrt(scale)
    Vs_knots = Vs_ms * 1.94384
    Fr = Vm_single / np.sqrt(g * Lm)

    Rem = (Vm_single * Lm) / num
    Res = (Vs_ms * Ls) / nus

    CFm = 0.075 / ((np.log10(Rem) - 2) ** 2)
    CFs = 0.075 / ((np.log10(Res) - 2) ** 2)

    qm = 0.5 * rhom * (Vm_single ** 2) * Sm
    CTm = Rtm_single / qm

    # Método de Froude
    CRm = CTm - CFm
    CTs_froude = CFs + CRm
    qs = 0.5 * rhos * (Vs_ms ** 2) * Ss
    RTs_froude = CTs_froude * qs
    PE_froude_kW = (RTs_froude * Vs_ms) / 1000.0

    # Método de Hughes
    CVm = k_factor * CFm
    CWm = CTm - CVm
    CVs = k_factor * CFs
    CTs_hughes = CVs + CWm
    RTs_hughes = CTs_hughes * qs
    PE_hughes_kW = (RTs_hughes * Vs_ms) / 1000.0

    st.subheader(f"⚓ Resultados da Extrapolação (Escala λ = {scale:.2f})")
    st.markdown(
        f"**Área Molhada (S_s):** {Ss:.1f} m² | **Velocidade Navio (V_s):** {Vs_knots:.2f} nós ({Vs_ms:.2f} m/s) | **Número de Froude:** {Fr:.3f}"
    )

    df_single = pd.DataFrame([{
        "Método": "Froude (sem 1+k)", "C_Fm (x10³)": CFm * 1000, "C_Fs (x10³)": CFs * 1000,
        "C_R / C_W (x10³)": CRm * 1000, "C_Ts (x10³)": CTs_froude * 1000, "R_Ts (kN)": RTs_froude / 1000,
        "P_E (kW)": PE_froude_kW, "P_E (hp)": PE_froude_kW * 1.34102
    }, {
        "Método": f"Hughes (1+k = {k_factor:.2f})", "C_Fm (x10³)": CFm * 1000, "C_Fs (x10³)": CFs * 1000,
        "C_R / C_W (x10³)": CWm * 1000, "C_Ts (x10³)": CTs_hughes * 1000, "R_Ts (kN)": RTs_hughes / 1000,
        "P_E (kW)": PE_hughes_kW, "P_E (hp)": PE_hughes_kW * 1.34102
    }])

    st.markdown("#### 1. Tabela Comparativa de Ponto Único")
    st.dataframe(df_single.style.format({
        "C_Fm (x10³)": "{:.4f}", "C_Fs (x10³)": "{:.4f}", "C_R / C_W (x10³)": "{:.4f}",
        "C_Ts (x10³)": "{:.4f}", "R_Ts (kN)": "{:.2f}", "P_E (kW)": "{:.1f}", "P_E (hp)": "{:.1f}"
    }))

    # Cálculo Multi-Velocidades
    try:
        vm_arr = np.array([float(x.strip()) for x in vm_list_str.split(",") if x.strip()])
        k_rtm = Rtm_single / (Vm_single ** 1.85)
        rtm_arr = k_rtm * (vm_arr ** 1.85)

        multi_data = []
        for vm, rtm in zip(vm_arr, rtm_arr):
            vs_i = vm * np.sqrt(scale)
            vs_kn_i = vs_i * 1.94384
            fr_i = vm / np.sqrt(g * Lm)
            rem_i = (vm * Lm) / num
            res_i = (vs_i * Ls) / nus
            cfm_i = 0.075 / ((np.log10(rem_i) - 2) ** 2)
            cfs_i = 0.075 / ((np.log10(res_i) - 2) ** 2)
            qm_i = 0.5 * rhom * (vm ** 2) * Sm
            ctm_i = rtm / qm_i

            crm_i = ctm_i - cfm_i
            cts_f_i = cfs_i + crm_i
            qs_i = 0.5 * rhos * (vs_i ** 2) * Ss
            rts_f_i = cts_f_i * qs_i
            pe_f_i = (rts_f_i * vs_i) / 1000.0

            cvm_i = k_factor * cfm_i
            cwm_i = ctm_i - cvm_i
            cvs_i = k_factor * cfs_i
            cts_h_i = cvs_i + cwm_i
            rts_h_i = cts_h_i * qs_i
            pe_h_i = (rts_h_i * vs_i) / 1000.0

            multi_data.append({
                "V_m (m/s)": vm, "R_Tm (N)": rtm, "Fr": fr_i, "V_s (nós)": vs_kn_i,
                "R_Ts Froude (kN)": rts_f_i / 1000, "R_Ts Hughes (kN)": rts_h_i / 1000,
                "P_E Froude (kW)": pe_f_i, "P_E Hughes (kW)": pe_h_i
            })

        df_multi = pd.DataFrame(multi_data)
        st.markdown("#### 2. Tabela de Extrapolação Multi-Velocidades")
        st.dataframe(df_multi.style.format({
            "V_m (m/s)": "{:.2f}", "R_Tm (N)": "{:.2f}", "Fr": "{:.3f}", "V_s (nós)": "{:.2f}",
            "R_Ts Froude (kN)": "{:.2f}", "R_Ts Hughes (kN)": "{:.2f}",
            "P_E Froude (kW)": "{:.1f}", "P_E Hughes (kW)": "{:.1f}"
        }))

        # Gráficos
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 4.5), dpi=120)

        ax1.plot(df_multi["V_s (nós)"], df_multi["R_Ts Froude (kN)"], "o-", label="Froude", color="#1E3A8A", linewidth=2)
        ax1.plot(df_multi["V_s (nós)"], df_multi["R_Ts Hughes (kN)"], "s--", label=f"Hughes (1+k={k_factor:.2f})", color="#D97706", linewidth=2)
        ax1.set_xlabel("Velocidade V_s (nós)", fontweight="bold")
        ax1.set_ylabel("Resistência R_Ts (kN)", fontweight="bold")
        ax1.set_title("Resistência Total do Protótipo", fontweight="bold")
        ax1.grid(True, linestyle="--", alpha=0.5)
        ax1.legend()

        ax2.plot(df_multi["V_s (nós)"], df_multi["P_E Froude (kW)"], "o-", label="Froude", color="#059669", linewidth=2)
        ax2.plot(df_multi["V_s (nós)"], df_multi["P_E Hughes (kW)"], "s--", label=f"Hughes (1+k={k_factor:.2f})", color="#DC2626", linewidth=2)
        ax2.set_xlabel("Velocidade V_s (nós)", fontweight="bold")
        ax2.set_ylabel("Potência Efetiva P_E (kW)", fontweight="bold")
        ax2.set_title("Potência Efetiva do Protótipo", fontweight="bold")
        ax2.grid(True, linestyle="--", alpha=0.5)
        ax2.legend()

        st.pyplot(fig)

    except Exception as e:
        st.error(f"Erro no cálculo multi-velocidades: {e}")

# Run the calculation when the app starts or inputs change
calculate_extrapolation(
    Lm, Sm, rhom, num, Ls, rhos, nus, g, k_factor, Vm_single, Rtm_single, vm_list_str
)
