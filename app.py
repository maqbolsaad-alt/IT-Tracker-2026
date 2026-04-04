import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re

# --- 1. CONFIG & THEME ---
st.set_page_config(page_title="Ops Intelligence | Command Center", layout="wide", initial_sidebar_state="expanded")

# Unified SaaS Dark Theme CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main { background-color: #05070a; color: #e6edf3; }
    
    /* Card Container */
    .metric-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 20px;
        border-radius: 16px;
        margin-bottom: 10px;
    }
    
    /* Header Styling */
    .header-text {
        font-weight: 800;
        background: linear-gradient(90deg, #58a6ff, #bc8cff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Hide Streamlit components for cleaner look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA UTILITIES ---
def apply_modern_theme(fig):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color="#8b949e",
        title_font_size=16,
        title_font_color="#ffffff",
        margin=dict(t=50, b=10, l=10, r=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.05)', zeroline=False)
    return fig

# --- 3. SIDEBAR CONTROLS ---
with st.sidebar:
    st.markdown("<h2 class='header-text'>🛡️ Control Panel</h2>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload Ops Data", type=["xlsx"])
    st.markdown("---")
    if uploaded_file:
        st.success("Data Feed Active")
    else:
        st.info("Awaiting Data Feed...")

# --- 4. MAIN DASHBOARD LOGIC ---
if uploaded_file:
    try:
        # Data Processing
        df = pd.read_excel(uploaded_file, sheet_name=0)
        df.columns = df.columns.str.strip()
        
        # Fill hierarchies
        fill_cols = [c for c in ['Domain', 'Type', 'Category', 'Status', 'Severity'] if c in df.columns]
        df[fill_cols] = df[fill_cols].ffill()
        df = df.dropna(subset=['Category'])

        # Numeric Extraction for Duration
        df['Wks'] = df['Duration'].astype(str).str.extract('(\d+)').fillna(0).astype(int)

        # TOP ROW: EXECUTIVE KPIs
        k1, k2, k3, k4 = st.columns(4)
        
        with k1:
            st.metric("Total Scope", f"{df['Category'].nunique()} Units", "+12% vs LY")
        with k2:
            st.metric("Workload", f"{len(df)} Tasks", "Active", delta_color="off")
        with k3:
            avg_wks = df[df['Wks']>0]['Wks'].mean()
            st.metric("Avg Velocity", f"{avg_wks:.1f} Wks", "-0.8 Wks", delta_color="inverse")
        with k4:
            crit = len(df[df['Severity'].str.contains('Critical', na=False)])
            st.metric("Critical Risks", crit, f"{(crit/len(df)*100):.1f}% Total")

        st.markdown("<br>", unsafe_allow_html=True)

        # MIDDLE ROW: DISTRIBUTION & ANALYSIS
        col_left, col_right = st.columns([1, 1.2])

        with col_left:
            st.markdown("<h3 class='header-text'>Strategic Allocation</h3>", unsafe_allow_html=True)
            # Hierarchical Sunburst
            fig_sun = px.sunburst(df, path=['Domain', 'Type', 'Status'], 
                                 color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(apply_modern_theme(fig_sun), use_container_width=True)

        with col_right:
            st.markdown("<h3 class='header-text'>Risk vs. Longevity</h3>", unsafe_allow_html=True)
            # Bar Chart for Aging
            aging = df.groupby(['Category', 'Severity'])['Wks'].max().reset_index().sort_values('Wks', ascending=True)
            sev_colors = {'Critical': '#ff4b4b', 'High': '#ffa500', 'Medium': '#f1c40f', 'Low': '#00d4ff'}
            
            fig_aging = px.bar(aging.tail(10), x='Wks', y='Category', color='Severity',
                              orientation='h', color_discrete_map=sev_colors,
                              template="plotly_dark")
            st.plotly_chart(apply_modern_theme(fig_aging), use_container_width=True)

        # BOTTOM ROW: HEALTH PROGRESS & RAW DATA
        st.markdown("---")
        footer_l, footer_r = st.columns([1.5, 1])
        
        with footer_l:
            st.markdown("🔍 **Audit Log**")
            st.dataframe(df.style.background_gradient(subset=['Wks'], cmap='Blues'), height=250, use_container_width=True)
            
        with footer_r:
            st.markdown("📈 **Fleet Health**")
            closed = len(df[df['Status'].str.contains('Closed|Complete', case=False, na=False)])
            prog = (closed / len(df))
            st.write(f"Overall Completion: {prog*100:.1f}%")
            st.progress(prog)
            st.caption("Target: 85% by EOY")

    except Exception as e:
        st.error(f"Error parsing data: {e}")

else:
    # EMPTY STATE HERO
    st.markdown("""
        <div style="text-align:center; padding:120px 20px; border:2px dashed rgba(88,166,255,0.2); border-radius:30px; background:rgba(88,166,255,0.02)">
            <h1 style="font-size: 50px;">📡</h1>
            <h1 class='header-text' style="font-size: 40px; margin-bottom:10px;">Ops Command Center</h1>
            <p style="color:#8b949e; font-size:18px;">Ready to receive data uplink. Please upload the Excel tracking file via the sidebar.</p>
        </div>
        """, unsafe_allow_html=True)
