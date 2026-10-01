# ==============================================================================
# CALCULADORA HIDRODINÂMICA DE EXTRAPOLAÇÃO - GOOGLE COLAB
# Métodos de Froude e Hughes com Linha de Atrito ITTC-1957
# ==============================================================================
# Como usar no Google Colab:
# 1. Abra um novo notebook no Google Colab (colab.research.google.com).
# 2. Crie uma célula de código, cole este arquivo inteiro e clique no Play (Ctrl+Enter).
# 3. A interface interativa abrirá diretamente abaixo da célula!
# ==============================================================================

# --- Passo 1: Instalação Automática de Dependências ---
import sys
import subprocess

print("⏳ Verificando e instalando dependências no Google Colab...")
try:
    import ipywidgets
    import pandas
    import matplotlib
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "ipywidgets", "pandas", "numpy", "matplotlib", "streamlit"])
    print("✅ Dependências instaladas!")

# Ativa suporte a widgets no Google Colab
try:
    from google.colab import output
    output.enable_custom_widget_manager()
except Exception:
    pass

# --- Passo 2: Código do Aplicativo Interativo ---
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import ipywidgets as widgets
from IPython.display import display, HTML, clear_output

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

# Criando Elementos Visuais
preset_dropdown = widgets.Dropdown(
    options=list(PRESETS.keys()),
    value="Exercício Anexo (AP1 - Navio 129m)",
    description="Caso Preset:",
    style={'description_width': 'initial'},
    layout=widgets.Layout(width='450px')
)

w_Lm = widgets.FloatText(value=4.30, description="L_m (m):", layout=widgets.Layout(width='200px'))
w_Sm = widgets.FloatText(value=3.75, description="S_m (m²):", layout=widgets.Layout(width='200px'))
w_rhom = widgets.FloatText(value=1000.0, description="ρ_m (kg/m³):", layout=widgets.Layout(width='200px'))
w_num = widgets.FloatText(value=1.14e-6, description="ν_m (m²/s):", format='%.2e', layout=widgets.Layout(width='200px'))

w_Ls = widgets.FloatText(value=129.00, description="L_s (m):", layout=widgets.Layout(width='200px'))
w_rhos = widgets.FloatText(value=1025.0, description="ρ_s (kg/m³):", layout=widgets.Layout(width='200px'))
w_nus = widgets.FloatText(value=1.19e-6, description="ν_s (m²/s):", format='%.2e', layout=widgets.Layout(width='200px'))
w_g = widgets.FloatText(value=9.81, description="g (m/s²):", layout=widgets.Layout(width='200px'))
w_k = widgets.FloatText(value=1.15, description="(1+k):", layout=widgets.Layout(width='200px'))

w_Vm = widgets.FloatText(value=1.50, description="V_m (m/s):", layout=widgets.Layout(width='200px'))
w_Rtm = widgets.FloatText(value=18.00, description="R_Tm (N):", layout=widgets.Layout(width='200px'))
w_vmlist = widgets.Text(
    value="0.80, 1.00, 1.20, 1.40, 1.50, 1.60, 1.80, 2.00, 2.20, 2.40, 2.60",
    description="Série V_m (m/s):",
    style={'description_width': 'initial'},
    layout=widgets.Layout(width='450px')
)

btn_calc = widgets.Button(
    description="🚀 Calcular Extrapolação",
    button_style='primary',
    icon='calculator',
    layout=widgets.Layout(width='250px', height='40px')
)

out_display = widgets.Output()

def on_preset_change(change):
    p = PRESETS[change['new']]
    w_Lm.value = p["Lm"]
    w_Sm.value = p["Sm"]
    w_rhom.value = p["rhom"]
    w_num.value = p["num"]
    w_Ls.value = p["Ls"]
    w_rhos.value = p["rhos"]
    w_nus.value = p["nus"]
    w_g.value = p["g"]
    w_k.value = p["k"]
    w_Vm.value = p["Vm"]
    w_Rtm.value = p["Rtm"]
    w_vmlist.value = p["vm_list"]

preset_dropdown.observe(on_preset_change, names='value')

def calculate_and_render(b=None):
    with out_display:
        clear_output()
        Lm, Sm, rhom, num = w_Lm.value, w_Sm.value, w_rhom.value, w_num.value
        Ls, rhos, nus, g, k_factor = w_Ls.value, w_rhos.value, w_nus.value, w_g.value, w_k.value
        Vm_single, Rtm_single = w_Vm.value, w_Rtm.value
        
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
        
        display(HTML(f"""
        <div style='background-color:#EBF8FF; padding:15px; border-radius:8px; border-left:5px solid #3182CE; margin-bottom:15px; font-family:sans-serif;'>
            <h3 style='margin:0; color:#2B6CB0;'>⚓ Resultados da Extrapolação (Escala λ = {scale:.2f})</h3>
            <p style='margin:5px 0 0 0;'><b>Área Molhada (S_s):</b> {Ss:.1f} m² | <b>Velocidade Navio (V_s):</b> {Vs_knots:.2f} nós ({Vs_ms:.2f} m/s) | <b>Número de Froude:</b> {Fr:.3f}</p>
        </div>
        """))
        
        df_single = pd.DataFrame([
            {"Método": "Froude (sem 1+k)", "C_Fm (x10³)": CFm*1000, "C_Fs (x10³)": CFs*1000, "C_R / C_W (x10³)": CRm*1000, "C_Ts (x10³)": CTs_froude*1000, "R_Ts (kN)": RTs_froude/1000, "P_E (kW)": PE_froude_kW, "P_E (hp)": PE_froude_kW*1.34102},
            {"Método": f"Hughes (1+k = {k_factor:.2f})", "C_Fm (x10³)": CFm*1000, "C_Fs (x10³)": CFs*1000, "C_R / C_W (x10³)": CWm*1000, "C_Ts (x10³)": CTs_hughes*1000, "R_Ts (kN)": RTs_hughes/1000, "P_E (kW)": PE_hughes_kW, "P_E (hp)": PE_hughes_kW*1.34102}
        ])
        
        display(HTML("<h4 style='font-family:sans-serif;'>1. Tabela Comparativa de Ponto Único</h4>"))
        display(df_single.style.format({
            "C_Fm (x10³)": "{:.4f}", "C_Fs (x10³)": "{:.4f}", "C_R / C_W (x10³)": "{:.4f}",
            "C_Ts (x10³)": "{:.4f}", "R_Ts (kN)": "{:.2f}", "P_E (kW)": "{:.1f}", "P_E (hp)": "{:.1f}"
        }))
        
        # Cálculo Multi-Velocidades
        try:
            vm_arr = np.array([float(x.strip()) for x in w_vmlist.value.split(",") if x.strip()])
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
                    "R_Ts Froude (kN)": rts_f_i/1000, "R_Ts Hughes (kN)": rts_h_i/1000,
                    "P_E Froude (kW)": pe_f_i, "P_E Hughes (kW)": pe_h_i
                })
            
            df_multi = pd.DataFrame(multi_data)
            display(HTML("<br><h4 style='font-family:sans-serif;'>2. Tabela de Extrapolação Multi-Velocidades</h4>"))
            display(df_multi.style.format({
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
            
            plt.tight_layout()
            plt.show()
            
        except Exception as e:
            print("Erro no cálculo multi-velocidades:", e)

btn_calc.on_click(calculate_and_render)

# Montagem dos Componentes
box_inputs = widgets.VBox([
    widgets.HTML("<h2 style='color:#1E3A8A; font-family:sans-serif;'>⚓ Calculadora Hidrodinâmica - Google Colab</h2>"),
    preset_dropdown,
    widgets.HTML("<b>1. Dados do Modelo (Tanque):</b>"),
    widgets.HBox([w_Lm, w_Sm, w_rhom, w_num]),
    widgets.HTML("<b>2. Dados do Protótipo (Navio):</b>"),
    widgets.HBox([w_Ls, w_rhos, w_nus, w_g]),
    widgets.HTML("<b>3. Fator de Forma e Ensaio:</b>"),
    widgets.HBox([w_k, w_Vm, w_Rtm]),
    w_vmlist,
    widgets.HTML("<br>"),
    btn_calc
])

display(box_inputs)
display(out_display)
calculate_and_render()
