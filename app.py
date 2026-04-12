import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- 1. HUD & ADVANCED THEME SETUP ---
st.set_page_config(page_title="Ops Intelligence Command", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@300;400;700;900&display=swap');
    
    :root {
        --primary: #58a6ff;
        --bg-dark: #0d1117;
        --card-bg: rgba(22, 27, 34, 0.7);
        --border-color: #30363d;
    }

    html, body, [class*="css"] { 
        font-family: 'Inter', sans-serif; 
        background-color: #05070a; 
        color: #e6edf3; 
    }

    /* Glassmorphic Metric Cards */
    .metric-card {
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        backdrop-filter: blur(10px);
        padding: 20px;
        border-radius: 16px;
        transition: transform 0.3s ease, border-color 0.3s ease;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        border-color: var(--primary);
    }

    .metric-val { 
        font-size: 42px; 
        font-weight: 900; 
        color: #ffffff; 
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: -2px;
    }
    
    .metric-lbl { 
        font-size: 12px; 
        color: #8b949e; 
        text-transform: uppercase; 
        letter-spacing: 1.5px; 
        font-weight: 700;
        margin-bottom: 4px;
    }

    /* Section Headers */
    .section-header {
        font-family: 'JetBrains Mono', monospace;
        color: var(--primary);
        font-size: 14px;
        letter-spacing: 3px;
        margin: 40px 0 20px 0;
        display: flex;
        align-items: center;
    }
    
    .section-header::after {
        content: "";
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg, var(--border-color), transparent);
        margin-left: 20px;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #0d1117;
        border-right: 1px solid var(--border-color);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ADVANCED CHART ENGINE ---
def apply_pro_layout(fig, title, is_bar=False):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=80, b=20, l=10, r=10),
        height=380,
        font=dict(family="Inter"),
        title=dict(
            text=f"<span style='font-size:18px; color:#8b949e; font-weight:300'>{title}</span>",
            x=0.05, y=0.95
        )
    )
    if is_bar:
        fig.update_traces(marker_color='#58a6ff', marker_line_width=0, opacity=0.8)
        fig.update_xaxes(showgrid=False, zeroline=False)
        fig.update_yaxes(showgrid=True, gridcolor="#161b22", zeroline=False)
    else:
        fig.update_traces(hole=0.7, marker=dict(line=dict(color='#05070a', width=2)))
    return fig

# --- 3. DATA PROCESSING ---
def load_and_clean(file):
    df = pd.read_excel(file)
    df.columns = df.columns.str.strip()
    cols = ['Domain', 'Category', 'Status', 'Severity', 'Type']
    df[cols] = df[cols].ffill()
    df['Severity'] = df['Severity'].astype(str).str.capitalize()
    if 'Duration' in df.columns:
        df['Wks'] = df['Duration'].astype(str).str.extract(r'(\d+)').fillna(0).astype(int)
    else:
        df['Wks'] = 0
    return df

# --- 4. MAIN INTERFACE ---
with st.sidebar:
    st.markdown("### 🎚️ CONTROL PANEL")
    uploaded_file = st.file_uploader("Upload Data Feed", type=["xlsx"])
    st.divider()
    if uploaded_file:
        df_raw = load_and_clean(uploaded_file)
        
        # Advanced Filters
        domain_filter = st.multiselect("Filter Domain", options=df_raw['Domain'].unique(), default=df_raw['Domain'].unique())
        severity_filter = st.multiselect("Filter Severity", options=df_raw['Severity'].unique(), default=df_raw['Severity'].unique())
        
        df = df_raw[(df_raw['Domain'].isin(domain_filter)) & (df_raw['Severity'].isin(severity_filter))]
        df_units = df.drop_duplicates(subset=['Category'])

if uploaded_file:
    # --- HEADER ---
    st.markdown(f"""
        <div style="padding: 20px 0px;">
            <h1 style="font-weight:900; letter-spacing:-2px; margin-bottom:0px;">OPS<span style="color:#58a6ff">INTELLIGENCE</span>.sys</h1>
            <p style="color:#8b949e; font-family:'JetBrains Mono'; font-size:14px;">TERMINAL B-4 // {len(df)} ACTIVE TASKS DETECTED</p>
        </div>
    """, unsafe_allow_html=True)

    # --- ROW 1: KPI CARDS ---
    k1, k2, k3, k4 = st.columns(4)
    
    with k1:
        st.markdown(f"""<div class="metric-card"><div class="metric-lbl">Total Categories</div><div class="metric-val">{len(df_units)}</div></div>""", unsafe_allow_html=True)
    with k2:
        closed = len(df[df['Status'].str.contains('Closed|Complete', case=False, na=False)])
        rate = (closed/len(df)*100) if len(df) > 0 else 0
        st.markdown(f"""<div class="metric-card"><div class="metric-lbl">Efficiency Rate</div><div class="metric-val">{rate:.1f}%</div></div>""", unsafe_allow_html=True)
    with k3:
        high_risk = len(df[df['Severity'] == 'High'])
        st.markdown(f"""<div class="metric-card" style="border-left: 4px solid #f85149"><div class="metric-lbl">High Risk Incidents</div><div class="metric-val">{high_risk}</div></div>""", unsafe_allow_html=True)
    with k4:
        avg_w = df['Wks'].mean()
        st.markdown(f"""<div class="metric-card"><div class="metric-lbl">Avg Cycle Time</div><div class="metric-val">{avg_w:.1f}w</div></div>""", unsafe_allow_html=True)

    # --- ROW 2: ANALYTICS GRID ---
    st.markdown('<div class="section-header">DATA VISUALIZATION LAYER</div>', unsafe_allow_html=True)
    c1, c2 = st.columns([1, 1])

    with c1:
        # Donut Chart for Status
        fig_stat = px.pie(df_units, names='Status', color_discrete_sequence=['#58a6ff', '#2ea043', '#d29922', '#30363d'])
        st.plotly_chart(apply_pro_layout(fig_stat, "DISTRIBUTION BY STATE"), use_container_width=True)

    with c2:
        # Horizontal Bar for Severity
        sev_data = df_units['Severity'].value_counts().reset_index()
        fig_sev = px.bar(sev_data, x='count', y='Severity', orientation='h')
        st.plotly_chart(apply_pro_layout(fig_sev, "INCIDENT SEVERITY SCALE", is_bar=True), use_container_width=True)

    # --- ROW 3: DATAFRAME ---
    st.markdown('<div class="section-header">REAL-TIME OPERATIONS LEDGER</div>', unsafe_allow_html=True)
    
    # Custom Styled Dataframe
    st.dataframe(
        df[['Domain', 'Category', 'Status', 'Severity', 'Wks']],
        column_config={
            "Wks": st.column_config.ProgressColumn("Aging", min_value=0, max_value=20, format="%d weeks"),
            "Severity": st.column_config.SelectboxColumn("Risk", options=["High", "Medium", "Low"]),
            "Status": st.column_config.TextColumn("State")
        },
        use_container_width=True,
        hide_index=True
    )

else:
    # Empty State
    st.markdown("""
        <div style="height: 400px; display: flex; align-items: center; justify-content: center; border: 1px dashed #30363d; border-radius: 20px;">
            <div style="text-align: center; color: #8b949e;">
                <h2 style="font-weight: 300;">Awaiting Data Feed...</h2>
                <p>Upload an .xlsx file in the sidebar to initialize command center.</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
