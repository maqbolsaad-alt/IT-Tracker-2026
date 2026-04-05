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
        border-left: 6px solid #58a6ff;
        padding: 24px;
        border-radius: 14px;
        margin-bottom: 10px;
    }
    .metric-val { 
        font-size: 52px; 
        font-weight: 900; 
        color: #ffffff; 
        line-height: 1;
        text-shadow: 0px 0px 12px rgba(88, 166, 255, 0.25);
    }
    .metric-lbl { 
        font-size: 15px; 
        color: #8b949e; 
        text-transform: uppercase; 
        letter-spacing: 2px; 
        margin-bottom: 12px; 
        font-weight: 700;
    }
    
    .section-box {
        padding: 15px 0px;
        border-bottom: 2px solid #30363d;
        margin-top: 35px;
        margin-bottom: 25px;
        color: #58a6ff;
        font-weight: 800;
        text-transform: uppercase;
        font-size: 15px;
        letter-spacing: 1.5px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ENHANCED CHART STYLING ENGINE ---
def apply_pro_layout(fig, title, chart_type="pie"):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=70, b=30, l=10, r=50), 
        height=400, 
        showlegend=(chart_type == "pie"),
        title=dict(
            text=f"<b>{title}</b>",
            x=0.02, y=0.98, xanchor='left',
            font=dict(size=22, color='#ffffff')
        )
    )
    
    if chart_type == "bar":
        fig.update_xaxes(showgrid=True, gridcolor="#161b22", title_text="", tickfont=dict(size=14, color="#8b949e"))
        fig.update_yaxes(showgrid=False, title_text="", tickfont=dict(size=16, color="#ffffff", family="Inter-Bold"))
        fig.update_traces(
            marker_line_width=0, 
            opacity=1.0, 
            texttemplate='<b>%{x}</b>', 
            textfont=dict(size=18, color="#ffffff"), 
            textposition='outside', 
            cliponaxis=False
        )
    else:
        fig.update_traces(
            textinfo='percent', 
            hole=0.6, 
            textfont=dict(size=18, family="Inter-Black"), 
            marker=dict(line=dict(color='#05070a', width=3)),
            hoverinfo='label+percent'
        )
        fig.update_layout(
            legend=dict(
                orientation="h", 
                yanchor="bottom", 
                y=-0.25, 
                xanchor="center", 
                x=0.5, 
                font=dict(size=14)
            )
        )
    return fig

# --- 3. MAIN INTERFACE ---
st.title("🛡️ Ops Intelligence Command")
uploaded_file = st.file_uploader("Drop Data Feed", type=["xlsx"], label_visibility="collapsed")

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        df.columns = df.columns.str.strip()
        cols = ['Domain', 'Category', 'Status', 'Severity', 'Type']
        df[cols] = df[cols].ffill()
        df['Severity'] = df['Severity'].astype(str).str.capitalize()
        
        if 'Duration' in df.columns:
            df['Wks'] = df['Duration'].astype(str).str.extract(r'(\d+)').fillna(0).astype(int)
        else:
            df['Wks'] = 0

        # --- HEADER SECTION ---
        st.markdown("""
            <div style="margin-bottom: 45px; border-left: 5px solid #58a6ff; padding-left: 30px; margin-top: 30px;">
                <h1 style="color: #ffffff; font-family: 'Inter', sans-serif; font-weight: 900; margin-bottom: 0px; font-size: 48px; letter-spacing: -1.5px;">
                    IT Tracker Dashboard
                </h1>
                <p style="color: #8b949e; font-size: 18px; text-transform: uppercase; letter-spacing: 4px; margin-top: 10px; font-weight: 500;">
                    Operational Analysis (26 Unique Units)
                </p>
            </div>
        """, unsafe_allow_html=True)

        # --- ROW 1: KPIs ---
        k1, k2, k3, k4, k5 = st.columns(5)
        total_units = df['Category'].nunique() # This should be 26
        
        with k1: st.markdown(f"<div class='metric-container'><div class='metric-lbl'>Total Units</div><div class='metric-val'>{total_units}</div></div>", unsafe_allow_html=True)
        with k2: st.markdown(f"<div class='metric-container'><div class='metric-lbl'>Total Tasks</div><div class='metric-val'>{len(df)}</div></div>", unsafe_allow_html=True)
        with k3:
            closed = len(df[df['Status'].str.contains('Closed|Complete', case=False, na=False)])
            rate = (closed/len(df)*100) if len(df) > 0 else 0
            st.markdown(f"<div class='metric-container'><div class='metric-lbl'>Closure Rate</div><div class='metric-val'>{rate:.1f}%</div></div>", unsafe_allow_html=True)
        with k4:
            high_risk = len(df[df['Severity'].str.contains('High', na=False)])
            st.markdown(f"<div class='metric-container' style='border-left-color:#f85149'><div class='metric-lbl'>High Risk Tasks</div><div class='metric-val'>{high_risk}</div></div>", unsafe_allow_html=True)
        with k5:
            avg_w = df[df['Wks']>0]['Wks'].mean() if len(df[df['Wks']>0]) > 0 else 0
            st.markdown(f"<div class='metric-container'><div class='metric-lbl'>Avg Longevity</div><div class='metric-val'>{avg_w:.1f}w</div></div>", unsafe_allow_html=True)

        # --- ROW 2: VISUALIZATIONS ---
        st.markdown("<div class='section-box'>Volume & Risk Distribution</div>", unsafe_allow_html=True)
        d1, d2, d3, d4 = st.columns(4)
        
        with d1:
            fig1 = px.pie(df, names='Status', color_discrete_sequence=["#58a6ff", "#2ea043", "#d29922"])
            st.plotly_chart(apply_pro_layout(fig1, "Task Status", "pie"), use_container_width=True)
            
        with d2:
            target_order = ['Low', 'Medium', 'High'] 
            sev_counts = df['Severity'].value_counts().reindex(target_order).dropna().reset_index()
            sev_counts.columns = ['Severity', 'count']
            fig2 = px.bar(sev_counts, x='count', y='Severity', orientation='h',
                          color='Severity',
                          color_discrete_map={'High': '#f85149', 'Medium': '#58a6ff', 'Low': '#30363d'})
            st.plotly_chart(apply_pro_layout(fig2, "Risk Levels", "bar"), use_container_width=True)
            
        with d3:
            fig3 = px.pie(df, names='Domain', color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(apply_pro_layout(fig3, "Domain Split", "pie"), use_container_width=True)

        with d4:
            # --- CRITICAL FIX: Group by Type but count UNIQUE Categories ---
            # This ensures the total sum of bars equals the "Total Units" (26)
            type_unit_counts = df.groupby('Type')['Category'].nunique().reset_index()
            type_unit_counts.columns = ['Type', 'count']
            type_unit_counts = type_unit_counts.sort_values('count')
            
            fig4 = px.bar(type_unit_counts, x='count', y='Type', orientation='h', color_discrete_sequence=['#58a6ff'])
            st.plotly_chart(apply_pro_layout(fig4, "Request Type (Units)", "bar"), use_container_width=True)

        # --- ROW 3: DETAILED LEDGER ---
        st.markdown("<div class='section-box'>Detailed Operations Ledger</div>", unsafe_allow_html=True)
        
        def color_severity(val):
            if val == 'High': return 'color: #f85149; font-weight: bold'
            if val in ['Closed', 'Complete']: return 'color: #2ea043; font-weight: bold'
            return 'color: #8b949e'

        st.dataframe(
            df[['Domain', 'Type', 'Category', 'Status', 'Severity', 'Wks']].style.map(color_severity, subset=['Severity', 'Status']),
            column_config={
                "Wks": st.column_config.ProgressColumn("Longevity", min_value=0, max_value=52, format="%d weeks"),
                "Status": st.column_config.TextColumn("Current State"),
                "Severity": st.column_config.TextColumn("Risk Class"),
                "Type": st.column_config.TextColumn("Classification")
            },
            use_container_width=True, hide_index=True
        )

    except Exception as e:
        st.error(f"System Error: {e}")
else:
    st.info("System Ready. Upload Data Feed.")
