import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. HUD & THEME SETUP ---
st.set_page_config(page_title="Ops Executive Brief", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #05070a; color: #e6edf3; }
    
    .metric-container {
        background: #0d1117;
        border: 1px solid #30363d;
        border-left: 5px solid #58a6ff;
        padding: 18px;
        border-radius: 12px;
        margin-bottom: 10px;
    }
    .metric-val { font-size: 32px; font-weight: 900; color: #ffffff; line-height: 1; }
    .metric-lbl { font-size: 11px; color: #8b949e; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 8px; }
    
    .section-box {
        padding: 10px 0px;
        border-bottom: 1px solid #30363d;
        margin-top: 25px;
        margin-bottom: 20px;
        color: #58a6ff;
        font-weight: 800;
        text-transform: uppercase;
        font-size: 13px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CHART STYLING ENGINE (The Organization Fix) ---
def apply_pro_layout(fig, title):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=60, b=20, l=10, r=100), # Large right margin for the legend
        height=350,
        showlegend=True,
        # LEGEND MOVED TO THE RIGHT SIDE
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.1, 
            font=dict(size=11, color="#8b949e")
        ),
        title=dict(
            text=f"<b>{title}</b>",
            x=0.05, # Title aligned to the left
            y=0.95,
            font=dict(size=16, color='#58a6ff')
        )
    )
    fig.update_traces(
        textinfo='value+percent', 
        textposition='inside',
        insidetextorientation='horizontal',
        hole=0.7,
        marker=dict(line=dict(color='#05070a', width=2))
    )
    return fig

# --- 3. LOGIC & DATA ---
st.title("🛡️ Ops Intelligence Command")
uploaded_file = st.file_uploader("Drop Data Feed", type=["xlsx"], label_visibility="collapsed")

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        df.columns = df.columns.str.strip()
        
        cols_to_fill = ['Domain', 'Category', 'Status', 'Severity']
        df[cols_to_fill] = df[cols_to_fill].ffill()
        df['Wks'] = df['Duration'].astype(str).str.extract('(\d+)').fillna(0).astype(int)

        # --- ROW 1: KPIs ---
        k1, k2, k3, k4, k5 = st.columns(5)
        with k1: st.markdown(f"<div class='metric-container
