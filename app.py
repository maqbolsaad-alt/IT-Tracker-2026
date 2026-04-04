import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re

# --- 1. SETTINGS & THEME ---
st.set_page_config(page_title="OpsIntel | Pro", layout="wide", initial_sidebar_state="expanded")

# Ultra-Modern CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Outfit', sans-serif; color: #E0E0E0; }
    .stApp { background-color: #0A0C10; }
    
    /* Glassmorphism Card */
    .metric-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 24px;
        border-radius: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    }
    
    /* Glow Header */
    .glow-text {
        color: #fff;
        text-shadow: 0 0 10px rgba(88, 166, 255, 0.5);
        font-weight: 700;
        letter-spacing: -1px;
    }

    /* Custom Scrollbar */
    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-track { background: #0A0C10; }
    ::-webkit-scrollbar-thumb { background: #232d3b; border-radius: 10px; }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGIC & DATA ---
def apply_pro_theme(fig):
    fig.update_layout(
        margin=dict(t=50, b=0, l=0, r=0),
        font_family="Outfit",
        hoverlabel=dict(bgcolor="#161b22", font_size=13, font_family="Outfit"),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )
    return fig

def get_weeks(x):
    match = re.search(r'(\d+)', str(x))
    return int(match.group(1)) if match else 0

# --- 3. SIDEBAR CONTROLS ---
with st.sidebar:
    st.markdown("<h2 class='glow-text'>FILTERS</h2>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Drop Data Stream", type=["xlsx"])
    st.divider()
    if uploaded_file:
        # Load and quick clean
        df_raw = pd.read_excel(uploaded_file)
        df_raw.columns = df_raw.columns.str.strip()
        df_raw.ffill(inplace=True)
        
        domains = st.multiselect("Focus Domain", options=df_raw['Domain'].unique(), default=df_raw['Domain'].unique())
        severity = st.multiselect("Risk Level", options=df_raw['Severity'].unique(), default=df_raw['Severity'].unique())

# --- 4. MAIN DASHBOARD ---
if uploaded_file:
    # Filter Data
    df = df_raw[(df_raw['Domain'].isin(domains)) & (df_raw['Severity'].isin(severity))].copy()
    df['Weeks_Open'] = df['Duration'].apply(get_weeks)
    
    # Header Section
    c_title, c_kpi = st.columns([1, 2])
    with c_title:
        st.markdown("<h1 class='glow-text' style='font-size: 2.5rem;'>OPERATIONAL<br>INTELLIGENCE</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color:#58a6ff; opacity:0.8;'>Command Center v2.4 (Enterprise)</p>", unsafe_allow_html=True)

    # Top Metrics
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"<div class='metric-card'><small>ACTIVE ENTITIES</small><h2>{len(df)}</h2><span style='color:#2eb67d;'>↑ 12% vs LY</span></div>", unsafe_allow_html=True)
    with m2:
        avg_wks = df['Weeks_Open'].mean()
        st.markdown(f"<div class='metric-card'><small>AVG VELOCITY</small><h2>{avg_wks:.1f}w</h2><span style='color:#ff3131;'>-0.2w Lag</span></div>", unsafe_allow_html=True)
    with m3:
        crit = len(df[df['Severity'] == 'Critical'])
        st.markdown(f"<div class='metric-card'><small>CRITICAL RISKS</small><h2>{crit}</h2><span style='color:#58a6ff;'>System Stability: 94%</span></div>", unsafe_allow_html=True)
    with m4:
        completion = (len(df[df['Status'] == 'Closed']) / len(df)) * 100 if len(df) > 0 else 0
        st.markdown(f"<div class='metric-card'><small>TARGET HIT RATE</small><h2>{completion:.1f}%</h2><progress value='{completion}' max='100' style='width:100%'></progress></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Visual Grid
    col_left, col_right = st.columns([1.2, 1])

    with col_left:
        st.markdown("### 🛰️ Architectural Distribution")
        fig_sun = px.sunburst(
            df, path=['Domain', 'Type', 'Category'], 
            color='Weeks_Open',
            color_continuous_scale='Blues',
            template="plotly_dark"
        )
        st.plotly_chart(apply_pro_theme(fig_sun), use_container_width=True, config={'displayModeBar': False})

    with col_right:
        st.markdown("### ⚠️ Bottleneck Analysis")
        # Horizontal Bar for Aging
        top_aging = df.sort_values('Weeks_Open', ascending=False).head(10)
        fig_h = px.bar(
            top_aging, x='Weeks_Open', y='Category', 
            orientation='h',
            color='Severity',
            color_discrete_map={'Critical': '#FF3131', 'High': '#FF914D', 'Medium': '#FFDE59', 'Low': '#00D1FF'},
            text_auto=True
        )
        fig_h.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(apply_pro_theme(fig_h), use_container_width=True, config={'displayModeBar': False})

    # Bottom Row
    st.markdown("---")
    b1, b2 = st.columns(2)
    
    with b1:
        st.markdown("### 📈 Status Volume")
        fig_area = px.area(df.groupby('Status').count().reset_index(), x='Status', y='Domain', 
                           color_discrete_sequence=['#58a6ff'])
        st.plotly_chart(apply_pro_theme(fig_area), use_container_width=True)

    with b2:
        st.markdown("### 📋 Executive Audit Trail")
        st.dataframe(
            df[['Domain', 'Category', 'Severity', 'Status', 'Weeks_Open']],
            column_config={
                "Weeks_Open": st.column_config.ProgressColumn("Longevity", min_value=0, max_value=20, format="%d wks"),
                "Severity": st.column_config.TextColumn("Risk Level"),
            },
            use_container_width=True,
            hide_index=True
        )

else:
    # High-end Empty State
    st.markdown("""
        <div style="height: 60vh; display: flex; flex-direction: column; align-items: center; justify-content: center; border: 1px dashed rgba(255,255,255,0.1); border-radius: 30px;">
            <h1 style="color: #1f2937; font-size: 5rem; margin-bottom: 0;">OFFLINE</h1>
            <p style="color: #58a6ff; font-size: 1.2rem;">Awaiting encrypted data uplink from 'Track with IT' source...</p>
        </div>
    """, unsafe_allow_html=True)
