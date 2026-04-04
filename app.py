import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="Ops Intelligence | Executive", layout="wide", initial_sidebar_state="collapsed")

# --- 2. ADVANCED STYLING (SaaS Dark Theme) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main { background-color: #05070a; }
    
    /* Metric Card Styling */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 15px !important;
        border-radius: 16px;
        backdrop-filter: blur(10px);
    }
    
    /* Header Polish */
    .section-header {
        background: linear-gradient(90deg, #58a6ff 0%, rgba(88, 166, 255, 0) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 20px; font-weight: 800;
        margin: 20px 0 10px 0;
        letter-spacing: -0.5px;
    }
    
    /* File Uploader Polish */
    section[data-testid="stFileUploadDropzone"] {
        background: rgba(88, 166, 255, 0.05);
        border: 1px dashed #58a6ff;
        border-radius: 12px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CUSTOM PLOTLY THEME ---
def apply_modern_theme(fig):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color="#8b949e",
        title_font_size=18,
        title_font_color="#ffffff",
        margin=dict(t=40, b=20, l=0, r=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.05)', zeroline=False)
    return fig

# --- 4. APP LOGIC ---
st.title("🛡️ Ops Intelligence")
st.markdown("<p style='color:#8b949e; margin-top:-15px;'>Real-time IT Infrastructure & Delivery Performance</p>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, sheet_name="Sheet1")
        df.columns = df.columns.str.strip()
        
        # Data Pipeline
        fill_cols = [c for c in ['Domain', 'Type', 'Category', 'Status', 'Duration', 'Severity'] if c in df.columns]
        df[fill_cols] = df[fill_cols].ffill()
        df_clean = df.dropna(subset=['Category']).copy()

        def get_wks(x):
            match = re.search(r'(\d+)', str(x))
            return int(match.group(1)) if match else 0
        df_clean['Weeks_Open'] = df_clean['Duration'].apply(get_wks)

        # --- KPI GRID ---
        k1, k2, k3, k4 = st.columns(4)
        avg_age = df_clean[df_clean['Weeks_Open'] > 0]['Weeks_Open'].mean()
        crit_count = len(df_clean[df_clean['Severity'].str.contains('Critical', na=False)])

        k1.metric("Portfolio Scale", f"{df_clean['Category'].nunique()} Units", "+2")
        k2.metric("Sub-Task Depth", len(df_clean), "Active")
        k3.metric("Cycle Time", f"{avg_age:.1f} Wks", "-0.4", delta_color="inverse")
        k4.metric("Risk Density", crit_count, f"{crit_count/len(df_clean)*100:.1f}%", delta_color="off")

        # --- VISUALIZATION LAYER ---
        st.markdown("---")
        c1, c2 = st.columns([1, 1.2])

        with c1:
            st.markdown("<div class='section-header'>Strategic Distribution</div>", unsafe_allow_html=True)
            
            # Sunburst for Domain > Type Hierarchy
            fig_sun = px.sunburst(df_clean, path=['Domain', 'Type'], 
                                  color_discrete_sequence=px.colors.sequential.Blues_r)
            st.plotly_chart(apply_modern_theme(fig_sun), use_container_width=True)
            
            # Status Donut
            fig_donut = go.Figure(data=[go.Pie(labels=df_clean['Status'], 
                                               values=[1]*len(df_clean), 
                                               hole=.7,
                                               marker=dict(colors=['#00D1FF', '#2EB67D']))])
            fig_donut.update_layout(title="Delivery Velocity (Status)")
            st.plotly_chart(apply_modern_theme(fig_donut), use_container_width=True)

        with c2:
            st.markdown("<div class='section-header'>Risk & Aging Analysis</div>", unsafe_allow_html=True)
            
            # Advanced Aging Bar Chart
            aging_data = df_clean.groupby(['Category', 'Severity'])['Weeks_Open'].max().reset_index().sort_values('Weeks_Open')
            sev_map = {'Critical': '#FF3131', 'High': '#FF914D', 'Medium': '#FFDE59', 'Low': '#00BF63'}
            
            fig_bar = px.bar(aging_data.tail(12), x='Weeks_Open', y='Category', color='Severity',
                             orientation='h', color_discrete_map=sev_map,
                             text_auto=True, title="Project Longevity (Wks)")
            st.plotly_chart(apply_modern_theme(fig_bar), use_container_width=True)

            # Severity Heatmap / Indicator
            st.markdown("<div style='padding:20px; background:rgba(255,255,255,0.02); border-radius:12px;'>", unsafe_allow_html=True)
            st.write("📈 **Portfolio Health Insight:**")
            health_perc = (len(df_clean[df_clean['Status'] == 'Closed']) / len(df_clean)) * 100
            st.progress(health_perc / 100)
            st.caption(f"Portfolio completion rate: {health_perc:.1f}% against quarterly targets.")
            st.markdown("</div>", unsafe_allow_html=True)

        # --- RAW DATA VIEW ---
        with st.expander("🔍 Explore Full Audit Trail"):
            st.dataframe(df_clean.style.background_gradient(subset=['Weeks_Open'], cmap='Blues'), use_container_width=True)

    except Exception as e:
        st.error(f"System Error: {e}")
else:
    # Empty State
    st.markdown("""
        <div style="text-align:center; padding:100px; border:1px dashed rgba(255,255,255,0.1); border-radius:20px;">
            <h2 style="color:#58a6ff;">Waiting for Data...</h2>
            <p style="color:#8b949e;">Upload the 'Track with IT' spreadsheet to initialize the dashboard.</p>
        </div>
    """, unsafe_allow_html=True)
