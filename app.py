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

# --- 2. IMPROVED CHART STYLING ENGINE ---
def apply_pro_layout(fig, title, is_bar=False):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=60, b=40, l=10, r=10),
        height=350,
        showlegend=not is_bar, # Hide legend for bars as colors are self-explanatory
        title=dict(
            text=f"<b>{title}</b>",
            x=0.5, y=0.98, xanchor='center',
            font=dict(size=16, color='#58a6ff')
        )
    )
    
    if is_bar:
        fig.update_xaxes(showgrid=False, title_text="", tickfont=dict(color="#8b949e"))
        fig.update_yaxes(showgrid=True, gridcolor="#30363d", title_text="", tickfont=dict(color="#8b949e"))
        fig.update_traces(marker_line_width=0, opacity=0.9)
    else:
        fig.update_traces(
            textinfo='percent',
            hole=0.7,
            marker=dict(line=dict(color='#05070a', width=2))
        )
        fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
        
    return fig

# --- 3. LOGIC & DATA ---
st.title("🛡️ Ops Intelligence Command")
uploaded_file = st.file_uploader("Drop Data Feed", type=["xlsx"], label_visibility="collapsed")

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        df.columns = df.columns.str.strip()
        
        cols = ['Domain', 'Category', 'Status', 'Severity', 'Type']
        df[cols] = df[cols].ffill()
        df['Wks'] = df['Duration'].astype(str).str.extract('(\d+)').fillna(0).astype(int)

        # --- ROW 1: KPIs ---
        k1, k2, k3, k4, k5 = st.columns(5)
        with k1: st.markdown(f"<div class='metric-container'><div class='metric-lbl'>Total Units</div><div class='metric-val'>{df['Category'].nunique()}</div></div>", unsafe_allow_html=True)
        with k2: st.markdown(f"<div class='metric-container'><div class='metric-lbl'>Active Tasks</div><div class='metric-val'>{len(df)}</div></div>", unsafe_allow_html=True)
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

        # --- ROW 2: VISUALIZATIONS ---
        st.markdown("<div class='section-box'>Risk & Distribution Analysis</div>", unsafe_allow_html=True)
        d1, d2, d3, d4 = st.columns(4)
        
        with d1:
            fig1 = px.pie(df, names='Status', color_discrete_sequence=["#58a6ff", "#2ea043", "#d29922"])
            st.plotly_chart(apply_pro_layout(fig1, "Delivery Status"), use_container_width=True)
            
        with d2:
            # BAR CHART: Severity (Ordered)
            sev_order = ['Critical', 'High', 'Medium', 'Low']
            sev_counts = df['Severity'].value_counts().reindex(sev_order).fillna(0).reset_index()
            fig2 = px.bar(sev_counts, x='Severity', y='count', color='Severity',
                          color_discrete_map={'Critical': '#f85149', 'High': '#d29922', 'Medium': '#58a6ff', 'Low': '#30363d'})
            st.plotly_chart(apply_pro_layout(fig2, "Risk Levels", is_bar=True), use_container_width=True)
            
        with d3:
            fig3 = px.pie(df, names='Domain', color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(apply_pro_layout(fig3, "Domain Split"), use_container_width=True)

        with d4:
            # BAR CHART: Request Type
            type_counts = df['Type'].value_counts().reset_index()
            fig4 = px.bar(type_counts, x='Type', y='count', color_discrete_sequence=['#58a6ff'])
            st.plotly_chart(apply_pro_layout(fig4, "Request Type", is_bar=True), use_container_width=True)

        # --- ROW 3: DETAILED LEDGER ---
        st.markdown("<div class='section-box'>Detailed Operations Ledger</div>", unsafe_allow_html=True)
        
        def color_severity(val):
            if val == 'Critical': return 'color: #f85149; font-weight: bold'
            if val == 'High': return 'color: #d29922; font-weight: bold'
            if val in ['Closed', 'Complete']: return 'color: #2ea043; font-weight: bold'
            return 'color: #8b949e'

        st.dataframe(
            df[['Domain', 'Type', 'Category', 'Status', 'Severity', 'Wks']].style.applymap(color_severity, subset=['Severity', 'Status']),
            column_config={
                "Wks": st.column_config.ProgressColumn("Longevity", min_value=0, max_value=52, format="%d weeks"),
                "Status": st.column_config.TextColumn("Current State"),
                "Severity": st.column_config.TextColumn("Risk Class"),
                "Type": st.column_config.TextColumn("Classification")
            },
            use_container_width=True, hide_index=True
        )

    except Exception as e:
        st.error(f"Error Processing Data: {e}")
else:
    st.info("System Ready. Upload Data Feed.")
