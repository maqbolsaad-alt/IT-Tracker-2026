import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- 1. CONFIG & HUD STYLING ---
st.set_page_config(page_title="Ops Intelligence | Command Center", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;800&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #05070a; }
    
    /* Executive Metric Tiles */
    .metric-tile {
        background: rgba(255, 255, 255, 0.03);
        border-left: 4px solid #58a6ff;
        padding: 20px;
        border-radius: 8px;
        text-align: left;
    }
    .metric-value { font-size: 28px; font-weight: 800; color: #ffffff; }
    .metric-label { font-size: 12px; color: #8b949e; text-transform: uppercase; letter-spacing: 1px; }
    
    /* Status Tags */
    .status-tag {
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 10px;
        font-weight: bold;
        margin-right: 4px;
    }
    
    .section-title {
        font-size: 14px;
        font-weight: 800;
        color: #58a6ff;
        margin-bottom: 15px;
        text-transform: uppercase;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THEME UTILS ---
def apply_hud_theme(fig, title=""):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=30, b=10, l=10, r=10),
        height=300,
        title={'text': title, 'font': {'size': 14, 'color': '#8b949e'}}
    )
    return fig

# --- 3. APP HEADER ---
t1, t2 = st.columns([3, 1])
with t1:
    st.markdown("<h1 style='margin-bottom:0;'>🛡️ Ops Intel: Executive Brief</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#8b949e;'>Infrastructure Performance & Risk Distribution</p>", unsafe_allow_html=True)
with t2:
    uploaded_file = st.file_uploader("Upload Data Feed", type=["xlsx"], label_visibility="collapsed")

# --- 4. DASHBOARD CONTENT ---
if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        df.columns = df.columns.str.strip()
        
        # Data Cleansing
        fill_cols = ['Domain', 'Type', 'Category', 'Status', 'Severity']
        df[fill_cols] = df[fill_cols].ffill()
        df['Wks'] = df['Duration'].astype(str).str.extract('(\d+)').fillna(0).astype(int)
        
        # --- ROW 1: THE NUMBERS (KPIs) ---
        k1, k2, k3, k4, k5 = st.columns(5)
        
        with k1:
            st.markdown(f"<div class='metric-tile'><div class='metric-label'>Total Units</div><div class='metric-value'>{df['Category'].nunique()}</div></div>", unsafe_allow_html=True)
        with k2:
            st.markdown(f"<div class='metric-tile'><div class='metric-label'>Active Tasks</div><div class='metric-value'>{len(df)}</div></div>", unsafe_allow_html=True)
        with k3:
            closed = len(df[df['Status'].str.contains('Closed|Complete', case=False, na=False)])
            st.markdown(f"<div class='metric-tile'><div class='metric-label'>Closure Rate</div><div class='metric-value'>{(closed/len(df)*100):.1f}%</div></div>", unsafe_allow_html=True)
        with k4:
            crit = len(df[df['Severity'].str.contains('Critical', na=False)])
            color = "#ff3131" if crit > 0 else "#58a6ff"
            st.markdown(f"<div class='metric-tile' style='border-left-color:{color}'><div class='metric-label'>Critical Risks</div><div class='metric-value'>{crit}</div></div>", unsafe_allow_html=True)
        with k5:
            avg_age = df[df['Wks']>0]['Wks'].mean()
            st.markdown(f"<div class='metric-tile'><div class='metric-label'>Avg Longevity</div><div class='metric-value'>{avg_age:.1f}w</div></div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # --- ROW 2: CATEGORY & STATUS SEVERITY ---
        c1, c2, c3 = st.columns([1.2, 1, 1.2])

        with c1:
            st.markdown("<div class='section-title'>Workload by Category</div>", unsafe_allow_html=True)
            cat_data = df.groupby('Category').size().reset_index(name='Count').sort_values('Count')
            fig_cat = px.bar(cat_data, x='Count', y='Category', orientation='h', color_discrete_sequence=['#58a6ff'])
            st.plotly_chart(apply_hud_theme(fig_cat), use_container_width=True)

        with c2:
            st.markdown("<div class='section-title'>Status Distribution</div>", unsafe_allow_html=True)
            fig_pie = px.pie(df, names='Status', hole=0.7, color_discrete_sequence=['#00D1FF', '#2EB67D', '#FFD700'])
            st.plotly_chart(apply_hud_theme(fig_pie), use_container_width=True)

        with c3:
            st.markdown("<div class='section-title'>Severity Heatmap</div>", unsafe_allow_html=True)
            # Matrix of Category vs Severity
            sev_matrix = df.groupby(['Category', 'Severity']).size().unstack(fill_value=0)
            fig_heat = px.imshow(sev_matrix, color_continuous_scale='Blues', aspect="auto")
            st.plotly_chart(apply_hud_theme(fig_heat), use_container_width=True)

        # --- ROW 3: DOMAIN DRILLDOWN ---
        st.markdown("<div class='section-title'>Domain Operations Detail</div>", unsafe_allow_html=True)
        
        # Formatting the dataframe to look like an app
        st.dataframe(
            df[['Domain', 'Type', 'Category', 'Status', 'Severity', 'Wks']],
            column_config={
                "Wks": st.column_config.ProgressColumn("Longevity", min_value=0, max_value=20, format="%d wks"),
                "Severity": st.column_config.TextColumn("Risk Level"),
                "Status": st.column_config.SelectboxColumn("State", options=["Open", "Closed", "Pending"])
            },
            use_container_width=True,
            hide_index=True
        )

    except Exception as e:
        st.error(f"Integrity Error: Ensure Excel columns match 'Domain, Type, Category, Status, Severity, Duration'. Detail: {e}")

else:
    st.info("💡 Dashboard Idle. Please upload the spreadsheet to generate the visual report.")
