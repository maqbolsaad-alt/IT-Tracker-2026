import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- 1. HUD & THEME SETUP ---
st.set_page_config(page_title="Ops Executive Brief", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #05070a; color: #e6edf3; }
    
    /* High-Density Metric Cards */
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
    
    /* Section Headers */
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

# --- 2. CHART STYLING ENGINE (Fixed Overlap) ---
def apply_pro_layout(fig, title):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        # Increased top margin to t=120 to separate Title from Legend
        margin=dict(t=120, b=20, l=10, r=10),
        height=450,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=0.92,        # Positioned Legend below the Title
            xanchor="center",
            x=0.5,
            font=dict(size=10, color="#8b949e")
        ),
        title=dict(
            text=f"<b>{title}</b>",
            x=0.5,
            y=0.98,        # Positioned Title at the absolute top
            xanchor='center',
            yanchor='top',
            font=dict(size=18, color='#58a6ff')
        )
    )
    fig.update_traces(
        textinfo='value+percent', 
        textposition='inside',
        insidetextorientation='horizontal',
        hole=0.65,
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
        
        # Data Cleaning: Forward fill hierarchy
        cols_to_fill = ['Domain', 'Category', 'Status', 'Severity']
        df[cols_to_fill] = df[cols_to_fill].ffill()
        df['Wks'] = df['Duration'].astype(str).str.extract('(\d+)').fillna(0).astype(int)

        # --- ROW 1: THE KPIs ---
        k1, k2, k3, k4, k5 = st.columns(5)
        
        with k1:
            st.markdown(f"<div class='metric-container'><div class='metric-lbl'>Total Units</div><div class='metric-val'>{df['Category'].nunique()}</div></div>", unsafe_allow_html=True)
        with k2:
            st.markdown(f"<div class='metric-container'><div class='metric-lbl'>Active Tasks</div><div class='metric-val'>{len(df)}</div></div>", unsafe_allow_html=True)
        with k3:
            closed = len(df[df['Status'].str.contains('Closed|Complete', case=False, na=False)])
            rate = (closed/len(df)*100) if len(df) > 0 else 0
            st.markdown(f"<div class='metric-container'><div class='metric-lbl'>Closure Rate</div><div class='metric-val'>{rate:.1f}%</div></div>", unsafe_allow_html=True)
        with k4:
            crit = len(df[df['Severity'].str.contains('Critical', na=False)])
            st.markdown(f"<div class='metric-container' style='border-left-color:#f85149'><div class='metric-lbl'>Critical Risks</div><div class='metric-val'>{crit}</div></div>", unsafe_allow_html=True)
        with k5:
            avg_w = df[df['Wks']>0]['Wks'].mean() if len(df[df['Wks']>0]) > 0 else 0
            st.markdown(f"<div class='metric-container'><div class='metric-lbl'>Avg Longevity</div><div class='metric-val'>{avg_w:.1f}w</div></div>", unsafe_allow_html=True)

        # --- ROW 2: THE THREE DONUTS ---
        st.markdown("<div class='section-box'>Risk & Duration Analysis</div>", unsafe_allow_html=True)
        
        d1, d2, d3 = st.columns(3, gap="large")
        
        with d1:
            fig1 = px.pie(df, names='Status', color_discrete_sequence=["#58a6ff", "#2ea043", "#d29922"])
            st.plotly_chart(apply_pro_layout(fig1, "Delivery Pipeline Status"), use_container_width=True)
            
        with d2:
            fig2 = px.pie(df, names='Severity', 
                          color='Severity', 
                          color_discrete_map={'Critical': '#f85149', 'High': '#d29922', 'Medium': '#58a6ff', 'Low': '#30363d'})
            st.plotly_chart(apply_pro_layout(fig2, "Risk Distribution"), use_container_width=True)
            
        with d3:
            fig3 = px.pie(df, names='Domain', color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(apply_pro_layout(fig3, "Incident Volume"), use_container_width=True)

        # --- ROW 3: DETAILED OPERATIONS LEDGER ---
        st.markdown("<div class='section-box'>Detailed Operations Ledger</div>", unsafe_allow_html=True)
        
        def color_severity(val):
            if val == 'Critical': return 'color: #f85149; font-weight: bold'
            if val == 'High': return 'color: #d29922; font-weight: bold'
            if val in ['Closed', 'Complete']: return 'color: #2ea043; font-weight: bold'
            return 'color: #8b949e'

        st.dataframe(
            df[['Domain', 'Category', 'Status', 'Severity', 'Wks']].style.applymap(color_severity, subset=['Severity', 'Status']),
            column_config={
                "Wks": st.column_config.ProgressColumn("Longevity", min_value=0, max_value=52, format="%d weeks"),
                "Status": st.column_config.TextColumn("Current State"),
                "Severity": st.column_config.TextColumn("Risk Class")
            },
            use_container_width=True,
            hide_index=True
        )

    except Exception as e:
        st.error(f"Execution Error: {e}")
else:
    st.info("System Ready. Upload Data Feed.")
