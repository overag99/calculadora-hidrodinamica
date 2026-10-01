import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Streamlit Page Configuration
st.set_page_config(
    page_title="Calculadora Hidrodinâmica - Froude & Hughes",
    page_icon="⚓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling for a modern UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        color: #1E3A8A;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F3F4F6;
        border-radius: 8px;
        padding: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .stTable {
        font-size: 0.95rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">⚓ Calculadora Hidrodinâmica de Extrapolação</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Extrapolação de Resistência ao Avanço (Modelo → Protótipo) utilizando os métodos de <b>Froude</b> e <b>Hughes</b> com a linha de atrito <b>ITTC-1957</b>.</div>', unsafe_allow_html=True)

# Sidebar - Configuration and Preset Selector
st.sidebar.header("⚙️ Configurações e Entradas")

preset_option = st.sidebar.selectbox(
    "Carregar Caso Predefinido (Preset):",
    ["Customizado / Entrada Livre", "Exercício Anexo (AP1 - Navio 129m)", "Caso de Estudo Wave Glider (NPL 30m)"]
)

# Default values based on preset
if preset_option == "Exercício Anexo (AP1 - Navio 129m)":
    default_Lm = 4.30
    default_Sm = 3.75
    default_rhom = 1000.0
    default_num = 1.14e-6
    default_Ls = 129.00
    default_rhos = 1025.0
    default_nus = 1.19e-6
    default_g = 9.81
    default_k = 1.15
    default_Vm = 1.50
    default_Rtm = 18.00
elif preset_option == "Caso de Estudo Wave Glider (NPL 30m)":
    default_Lm = 2.00
    default_Sm = 0.54
    default_rhom = 1000.0
    default_num = 1.2845e-6
    default_Ls = 30.00
    default_rhos = 1025.0
    default_nus = 1.19e-6
    default_g = 9.81
    default_k = 1.20
    default_Vm = 1.33
    default_Rtm = 3.85
else:
    default_Lm = 4.30
    default_Sm = 3.75
    default_rhom = 1000.0
    default_num = 1.14e-6
    default_Ls = 129.00
    default_rhos = 1025.0
    default_nus = 1.19e-6
    default_g = 9.81
    default_k = 1.15
    default_Vm = 1.50
    default_Rtm = 18.00

st.sidebar.subheader("1. Modelo de Ensaio (Tanque)")
L_m = st.sidebar.number_input("Comprimento L_m (m)", value=default_Lm, min_value=0.10, step=0.10, format="%.2f")
S_m = st.sidebar.number_input("Área Molhada S_m (m²)", value=default_Sm, min_value=0.01, step=0.10, format="%.2f")
rho_m = st.sidebar.number_input("Massa Específica ρ_m (kg/m³)", value=default_rhom, step=1.0)
nu_m = st.sidebar.number_input("Viscosidade Cinemática ν_m (m²/s)", value=default_num, format="%.4e")

st.sidebar.subheader("2. Protótipo / Navio Real")
L_s = st.sidebar.number_input("Comprimento L_s (m)", value=default_Ls, min_value=1.00, step=1.00, format="%.2f")
rho_s = st.sidebar.number_input("Massa Específica ρ_s (kg/m³)", value=default_rhos, step=1.0)
nu_s = st.sidebar.number_input("Viscosidade Cinemática ν_s (m²/s)", value=default_nus, format="%.4e")
g = st.sidebar.number_input("Gravidade g (m/s²)", value=default_g, step=0.01, format="%.2f")

st.sidebar.subheader("3. Fator de Forma (Hughes)")
k_factor = st.sidebar.number_input("Fator (1+k)", value=default_k, min_value=1.00, max_value=2.50, step=0.01, format="%.2f")

# Calculations for Scale and Area
scale = L_s / L_m
S_s = S_m * (scale ** 2)

# Navigation Tabs
tab1, tab2, tab3 = st.tabs(["📊 Cálculo de Ponto Único", "📈 Tabela Multi-Velocidades & Gráficos", "📚 Fundamentação Teórica"])

with tab1:
    st.header("1. Análise de Ponto Único de Ensaio")
    st.markdown("Insira a velocidade e a resistência medida em um ensaio específico do tanque para obter a extrapolação direta:")
    
    col_input1, col_input2 = st.columns(2)
    with col_input1:
        V_m_single = st.number_input("Velocidade do Ensaio V_m (m/s)", value=default_Vm, min_value=0.01, step=0.05, format="%.2f")
    with col_input2:
        R_Tm_single = st.number_input("Resistência Medida R_Tm (N)", value=default_Rtm, min_value=0.01, step=0.10, format="%.2f")

    # Kinematics & Non-dimensionals
    V_s_m_s = V_m_single * np.sqrt(scale)
    V_s_knots = V_s_m_s * 1.94384
    Fr = V_m_single / np.sqrt(g * L_m)

    Re_m = (V_m_single * L_m) / nu_m
    Re_s = (V_s_m_s * L_s) / nu_s

    C_Fm = 0.075 / ((np.log10(Re_m) - 2) ** 2)
    C_Fs = 0.075 / ((np.log10(Re_s) - 2) ** 2)

    q_m = 0.5 * rho_m * (V_m_single ** 2) * S_m
    C_Tm = R_Tm_single / q_m

    # Froude Method
    C_Rm = C_Tm - C_Fm
    C_Rs = C_Rm
    C_Ts_froude = C_Fs + C_Rs
    q_s = 0.5 * rho_s * (V_s_m_s ** 2) * S_s
    R_Ts_froude = C_Ts_froude * q_s
    P_E_froude_kW = (R_Ts_froude * V_s_m_s) / 1000.0

    # Hughes Method
    C_Vm = k_factor * C_Fm
    C_Wm = C_Tm - C_Vm
    C_Ws = C_Wm
    C_Vs = k_factor * C_Fs
    C_Ts_hughes = C_Vs + C_Ws
    R_Ts_hughes = C_Ts_hughes * q_s
    P_E_hughes_kW = (R_Ts_hughes * V_s_m_s) / 1000.0

    # Summary Cards
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Fator de Escala (λ)", f"{scale:.2f}")
    m2.metric("Área Molhada Navio (S_s)", f"{S_s:.1f} m²")
    m3.metric("Velocidade Navio (V_s)", f"{V_s_knots:.2f} nós", f"{V_s_m_s:.2f} m/s")
    m4.metric("Número de Froude (Fr)", f"{Fr:.3f}")

    st.subheader("Resultados da Extrapolação (Comparativo Froude vs Hughes)")
    
    df_single = pd.DataFrame([
        {
            "Método": "Método de Froude (sem 1+k)",
            "C_F (Modelo)": C_Fm * 1000,
            "C_F (Navio)": C_Fs * 1000,
            "C_R / C_W": C_Rm * 1000,
            "C_Ts (x10³)": C_Ts_froude * 1000,
            "R_Ts (kN)": R_Ts_froude / 1000.0,
            "Potência Efetiva P_E (kW)": P_E_froude_kW,
            "Potência Efetiva P_E (hp)": P_E_froude_kW * 1.34102
        },
        {
            "Método": f"Método de Hughes (1+k = {k_factor:.2f})",
            "C_F (Modelo)": C_Fm * 1000,
            "C_F (Navio)": C_Fs * 1000,
            "C_R / C_W": C_Wm * 1000,
            "C_Ts (x10³)": C_Ts_hughes * 1000,
            "R_Ts (kN)": R_Ts_hughes / 1000.0,
            "Potência Efetiva P_E (kW)": P_E_hughes_kW,
            "Potência Efetiva P_E (hp)": P_E_hughes_kW * 1.34102
        }
    ])

    st.dataframe(
        df_single.style.format({
            "C_F (Modelo)": "{:.4f}",
            "C_F (Navio)": "{:.4f}",
            "C_R / C_W": "{:.4f}",
            "C_Ts (x10³)": "{:.4f}",
            "R_Ts (kN)": "{:.2f}",
            "Potência Efetiva P_E (kW)": "{:.1f}",
            "Potência Efetiva P_E (hp)": "{:.1f}"
        }),
        use_container_width=True
    )

    diff_R = ((R_Ts_froude - R_Ts_hughes) / R_Ts_froude) * 100.0
    st.info(f"💡 **Observação:** O Método de Hughes resulta em uma resistência **{diff_R:.1f}% menor** do que o Método de Froude para esta condição, devido ao amortecimento da parcela de atrito plano pelo fator de forma $(1+k)$.")

with tab2:
    st.header("2. Tabela Multi-Velocidades & Curvas Hidrodinâmicas")
    st.markdown("Forneça uma série de velocidades $V_m$ para obter a curva completa de resistência e potência efetiva:")

    default_vm_list = "0.80, 1.00, 1.20, 1.40, 1.50, 1.60, 1.80, 2.00, 2.20, 2.40, 2.60" if preset_option != "Caso de Estudo Wave Glider (NPL 30m)" else "0.44, 0.66, 0.88, 1.11, 1.33, 1.55, 1.77, 1.99, 2.21"
    
    vm_str = st.text_input("Lista de velocidades do modelo V_m (m/s) separadas por vírgula:", default_vm_list)
    
    try:
        v_m_arr = np.array([float(x.strip()) for x in vm_str.split(",") if x.strip()])
        
        # Power scaling rule based on baseline point for demonstration or accurate fitting
        k_rtm = R_Tm_single / (V_m_single ** 1.85)
        r_tm_arr = k_rtm * (v_m_arr ** 1.85)
        
        table_data = []
        for vm, rtm in zip(v_m_arr, r_tm_arr):
            vs_ms = vm * np.sqrt(scale)
            vs_kn = vs_ms * 1.94384
            fr_i = vm / np.sqrt(g * L_m)
            
            re_m_i = (vm * L_m) / nu_m
            re_s_i = (vs_ms * L_s) / nu_s
            
            cfm_i = 0.075 / ((np.log10(re_m_i) - 2) ** 2)
            cfs_i = 0.075 / ((np.log10(re_s_i) - 2) ** 2)
            
            qm_i = 0.5 * rho_m * (vm ** 2) * S_m
            ctm_i = rtm / qm_i
            
            # Froude
            crm_i = ctm_i - cfm_i
            cts_froude_i = cfs_i + crm_i
            qs_i = 0.5 * rho_s * (vs_ms ** 2) * S_s
            rts_froude_i = cts_froude_i * qs_i
            pe_froude_kW_i = (rts_froude_i * vs_ms) / 1000.0
            
            # Hughes
            cvm_i = k_factor * cfm_i
            cwm_i = ctm_i - cvm_i
            cvs_i = k_factor * cfs_i
            cts_hughes_i = cvs_i + cwm_i
            rts_hughes_i = cts_hughes_i * qs_i
            pe_hughes_kW_i = (rts_hughes_i * vs_ms) / 1000.0
            
            table_data.append({
                "V_m (m/s)": vm,
                "R_Tm (N)": rtm,
                "Fr": fr_i,
                "V_s (nós)": vs_kn,
                "R_Ts Froude (kN)": rts_froude_i / 1000.0,
                "R_Ts Hughes (kN)": rts_hughes_i / 1000.0,
                "P_E Froude (kW)": pe_froude_kW_i,
                "P_E Hughes (kW)": pe_hughes_kW_i
            })
            
        df_multi = pd.DataFrame(table_data)
        
        st.subheader("Tabela de Resultados Extrapolados")
        st.dataframe(
            df_multi.style.format({
                "V_m (m/s)": "{:.2f}",
                "R_Tm (N)": "{:.2f}",
                "Fr": "{:.3f}",
                "V_s (nós)": "{:.2f}",
                "R_Ts Froude (kN)": "{:.2f}",
                "R_Ts Hughes (kN)": "{:.2f}",
                "P_E Froude (kW)": "{:.1f}",
                "P_E Hughes (kW)": "{:.1f}"
            }),
            use_container_width=True
        )

        # Download CSV Button
        csv_buffer = df_multi.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Baixar Tabela em CSV",
            data=csv_buffer,
            file_name="extrapolacao_hidrodinamica_resultados.csv",
            mime="text/csv"
        )
        
        st.subheader("Gráficos Comparativos de Extrapolação")
        c1, c2 = st.columns(2)
        
        with c1:
            fig, ax = plt.subplots(figsize=(6, 4.5), dpi=150)
            ax.plot(df_multi["V_s (nós)"], df_multi["R_Ts Froude (kN)"], "o-", label="Método de Froude", color="#1E3A8A", linewidth=2.2, markersize=6)
            ax.plot(df_multi["V_s (nós)"], df_multi["R_Ts Hughes (kN)"], "s--", label=f"Método de Hughes (1+k={k_factor})", color="#D97706", linewidth=2.2, markersize=6)
            ax.set_xlabel("Velocidade do Navio $V_s$ (nós)", fontsize=10, fontweight="bold")
            ax.set_ylabel("Resistência Total $R_{Ts}$ (kN)", fontsize=10, fontweight="bold")
            ax.set_title("Resistência Total do Protótipo vs Velocidade", fontsize=11, fontweight="bold", pad=12)
            ax.grid(True, linestyle="--", alpha=0.5)
            ax.legend(frameon=True, facecolor="white", framealpha=0.9)
            plt.tight_layout()
            st.pyplot(fig)

        with c2:
            fig2, ax2 = plt.subplots(figsize=(6, 4.5), dpi=150)
            ax2.plot(df_multi["V_s (nós)"], df_multi["P_E Froude (kW)"], "o-", label="Método de Froude", color="#059669", linewidth=2.2, markersize=6)
            ax2.plot(df_multi["V_s (nós)"], df_multi["P_E Hughes (kW)"], "s--", label=f"Método de Hughes (1+k={k_factor})", color="#DC2626", linewidth=2.2, markersize=6)
            ax2.set_xlabel("Velocidade do Navio $V_s$ (nós)", fontsize=10, fontweight="bold")
            ax2.set_ylabel("Potência Efetiva $P_E$ (kW)", fontsize=10, fontweight="bold")
            ax2.set_title("Potência Efetiva do Protótipo vs Velocidade", fontsize=11, fontweight="bold", pad=12)
            ax2.grid(True, linestyle="--", alpha=0.5)
            ax2.legend(frameon=True, facecolor="white", framealpha=0.9)
            plt.tight_layout()
            st.pyplot(fig2)

    except Exception as err:
        st.error(f"Erro ao calcular tabela: {err}")

with tab3:
    st.header("📚 Fundamentação Teórica & Formulação")
    st.markdown("""
    ### 1. Linha de Atrito ITTC-1957
    A correlação de atrito plano adotada internacionalmente é definida por:
    $$C_F = \\frac{0{,}075}{(\\log_{10} Re - 2)^2}$$
    onde o Número de Reynolds é $Re = \\frac{V \\cdot L}{\\nu}$.

    ---
    ### 2. Método de Froude
    O Método de Froude assume que a resistência total $C_T$ se decompõe em atrito plano $C_F$ e residual $C_R$:
    $$C_{Tm} = C_{Fm} + C_{Rm} \\implies C_{Rm} = C_{Tm} - C_{Fm}$$
    Assumindo igualdade do Número de Froude ($Fr_m = Fr_s$), temos $C_{Rs} = C_{Rm}$:
    $$C_{Ts} = C_{Fs} + C_{Rs}$$
    $$R_{Ts} = C_{Ts} \\cdot \\left(\\frac{1}{2} \\rho_s V_s^2 S_s\\right)$$

    ---
    ### 3. Método de Hughes (Fator de Forma)
    O Método de Hughes considera o efeito tridimensional da forma do casco sobre a viscosidade através do fator $(1+k)$:
    $$C_{Vm} = (1+k) C_{Fm} \\implies C_{Wm} = C_{Tm} - C_{Vm}$$
    A componente de ondas $C_W$ é mantida constante na escala ($C_{Ws} = C_{Wm}$):
    $$C_{Ts} = (1+k) C_{Fs} + C_{Ws}$$
    $$P_E = R_{Ts} \\cdot V_s$$
    """)
