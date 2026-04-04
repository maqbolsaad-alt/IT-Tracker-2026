import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="Ops Intelligence | Executive", layout="wide", initial_sidebar_state="collapsed")

# --- 2. ADVANCED STYLING ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main { background-color: #05070a; }
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 15px !important;
        border-radius: 16px;
        backdrop-filter: blur(10px);
    }
    .section-header {
        background: linear-gradient(90deg, #58a6ff 0%, rgba(88, 166, 255, 0) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 20px; font-weight: 800;
        margin: 20px 0 10px 0;
        letter-spacing: -0.5px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. THEME HELPER ---
def apply_modern_theme(fig):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color="#8b949e",
        title_font_size=16,
        title_font_color="#ffffff",
        margin=dict(t=50, b=20, l=10, r=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig

st.title("🛡️ Ops Intelligence")
st.markdown("<p style='color:#8b949e; margin-top:-15px;'>Strategic Portfolio Analysis & Resource Allocation</p>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload IT Track Data", type=["xlsx"])

if uploaded_file:
    try:
        # DATA ENGINE
        df = pd.read_excel(uploaded_file, sheet_name="Sheet1")
        df.columns = df.columns.str.strip()
        fill_cols = [c for c in ['Domain', 'Type', 'Category', 'Status', 'Duration', 'Severity'] if c in df.columns]
        df[fill_cols] = df[fill_cols].ffill()
        df_clean = df.dropna(subset=['Category']).copy()

        def get_wks(x):
            match = re.search(r'(\d+)', str(x))
            return int(match.group(1)) if match else 0
        df_clean['Weeks_Open'] = df_clean['Duration'].apply(get_wks)

        # KPI ROW
        k1, k2, k3, k4 = st.columns(4)
        avg_age = df_clean[df_clean['Weeks_Open'] > 0]['Weeks_Open'].mean()
        crit_count = len(df_clean[df_clean['Severity'].str.contains('Critical', na=False)])

        k1.metric("Portfolio Scale", f"{df_clean['Category'].nunique()} Units")
        k2.metric("Total Initiatives", len(df_clean))
        k3.metric("Avg Cycle Time", f"{avg_age:.1f} Wks")
        k4.metric("Critical Risks", crit_count)

        # --- LAYOUT START ---
        st.markdown("---")
        c1, c2 = st.columns([1, 1.2])

        with c1:
            st.markdown("<div class='section-header'>Strategic Distribution</div>", unsafe_allow_html=True)
            
            # TREEMAP: Hierarchical view of where effort is spent
            fig_tree = px.treemap(df_clean, 
                                  path=[px.Constant("Portfolio"), 'Domain', 'Type'], 
                                  color='Domain',
                                  color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_tree.update_traces(textinfo="label+value")
            st.plotly_chart(apply_modern_theme(fig_tree), use_container_width=True)
            
            # DOMAIN MIX: Stacked Bar for composition
            domain_mix = df_clean.groupby(['Domain', 'Type']).size().reset_index(name='count')
            fig_mix = px.bar(domain_mix, y='Domain', x='count', color='Type', 
                             orientation='h', barmode='stack',
                             title="Domain Effort Composition",
                             color_discrete_sequence=px.colors.sequential.Agsunset)
            st.plotly_chart(apply_modern_theme(fig_mix), use_container_width=True)

        with c2:
            st.markdown("<div class='section-header'>Risk & Aging Analysis</div>", unsafe_allow_html=True)
            
            # AGING BAR
            aging_data = df_clean.groupby(['Category', 'Severity'])['Weeks_Open'].max().reset_index().sort_values('Weeks_Open')
            sev_map = {'Critical': '#FF3131', 'High': '#FF914D', 'Medium': '#FFDE59', 'Low': '#00BF63'}
            
            fig_bar = px.bar(aging_data.tail(12), x='Weeks_Open', y='Category', color='Severity',
                             orientation='h', color_discrete_map=sev_map,
                             text_auto=True, title="Project Longevity (Top 12 Aging)")
            st.plotly_chart(apply_modern_theme(fig_bar), use_container_width=True)

            # HEALTH PROGRESS
            st.markdown("<div style='padding:20px; background:rgba(255,255,255,0.02); border-radius:12px;'>", unsafe_allow_html=True)
            closed_rate = (len(df_clean[df_clean['Status'] == 'Closed']) / len(df_clean)) * 100
            st.write(f"🚀 **Execution Velocity:** {closed_rate:.1f}%")
            st.progress(closed_rate / 100)
            st.markdown("</div>", unsafe_allow_html=True)

        with st.expander("🔍 Audit Inventory"):
            st.dataframe(df_clean.drop_duplicates(), use_container_width=True)

    except Exception as e:
        st.error(f"Critical Error: {e}")
else:
    st.info("System Ready. Please upload 'Track with IT.xlsx'.")
