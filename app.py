import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. HUD & LIGHT THEME SETUP ---
st.set_page_config(page_title="Ops Executive Brief", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
        background-color: #f8f9fb;
        color: #1e293b;
    }

    /* KPI Metric Cards */
    .metric-container {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-top: 6px solid #3b82f6;
        padding: 28px;
        border-radius: 14px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    .metric-val { 
        font-size: 64px; 
        font-weight: 300; /* Thin but big */
        color: #0f172a; 
        line-height: 1.0;
        letter-spacing: -1px;
    }
    .metric-lbl { 
        font-size: 15px; 
        color: #64748b; 
        text-transform: uppercase; 
        letter-spacing: 2px; 
        margin-bottom: 8px; 
        font-weight: 700;
    }
    
    .section-box {
        padding: 15px 0px;
        border-bottom: 4px solid #e2e8f0;
        margin-top: 50px;
        margin-bottom: 30px;
        color: #0f172a;
        font-weight: 800;
        text-transform: uppercase;
        font-size: 18px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ENHANCED CHART ENGINE (LEGEND & NUMBER FOCUS) ---
def apply_pro_layout(fig, title, chart_type="pie"):
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=100, b=160, l=20, r=20), # Extra bottom margin for larger legend
        height=600, # Increased height for better visibility
        showlegend=True,
        title=dict(
            text=f"<b>{title}</b>",
            x=0.02, y=0.98, xanchor='left',
            font=dict(size=30, color='#0f172a')
        ),
        legend=dict(
            orientation="h", 
            yanchor="top", 
            y=-0.2, # Positioned clearly below chart
            xanchor="center", 
            x=0.5,
            font=dict(size=22, color="#0f172a", family="Inter"), # Large, clear legend
            itemwidth=70
        )
    )
    
    if chart_type == "bar":
        fig.update_xaxes(showgrid=True, gridcolor="#f1f5f9", tickfont=dict(size=18))
        fig.update_yaxes(showgrid=False, tickfont=dict(size=22, family="Inter"))
        fig.update_traces(
            marker_line_width=0, 
            opacity=0.85, 
            texttemplate='<b>%{x}</b>', 
            textfont=dict(size=32, color="#0f172a", family="Inter"), # Big, clear bar numbers
            textposition='outside'
        )
    else:
        # Donut/Pie styling
        fig.update_traces(
            textinfo='percent+value', 
            hole=0.55, # Thinner donut ring looks cleaner
            # Forced white text with shadow for maximum clarity over colors
            textfont=dict(size=24, family="Inter", color="white"), 
            marker=dict(line=dict(color='#ffffff', width=4)),
            hoverinfo='label+percent',
            textposition='inside'
        )
    return fig

# --- 3. MAIN DASHBOARD LOGIC ---
st.markdown("<h1 style='color: #0f172a; font-weight: 900; letter-spacing: -2px; font-size: 42px;'>🛡️ Ops Intelligence Command</h1>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("Drop Data Feed", type=["xlsx"], label_visibility="collapsed")

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        df.columns = df.columns.str.strip()
        
        # Standardize Data
        cols = ['Domain', 'Category', 'Status', 'Severity', 'Type']
        for col in cols:
            if col in df.columns:
                df[col] = df[col].ffill()
        
        if 'Severity' in df.columns:
            df['Severity'] = df['Severity'].astype(str).str.capitalize()
        
        df['Wks'] = df['Duration'].astype(str).str.extract(r'(\d+)').fillna(0).astype(int) if 'Duration' in df.columns else 0
        df_units = df.drop_duplicates(subset=['Category']) if 'Category' in df.columns else df

        # --- EXECUTIVE HEADER ---
        st.markdown(f"""
            <div style="margin-bottom: 50px; border-left: 14px solid #3b82f6; padding-left: 35px; margin-top: 40px;">
                <h2 style="color: #0f172a; font-weight: 300; margin-bottom: 0px; font-size: 58px; letter-spacing: -2px; line-height: 1.0;">
                    IT Tracker Dashboard
                </h2>
                <p style="color: #64748b; font-size: 24px; text-transform: uppercase; letter-spacing: 5px; margin-top: 15px; font-weight: 700;">
                    Corporate Performance View ({len(df_units)} Active Categories)
                </p>
            </div>
        """, unsafe_allow_html=True)

        # --- ROW 1: KPI CARDS ---
        k1, k2, k3, k4, k5 = st.columns(5)
        with k1: st.markdown(f"<div class='metric-container'><div class='metric-lbl'>Units</div><div class='metric-val'>{len(df_units)}</div></div>", unsafe_allow_html=True)
        with k2: st.markdown(f"<div class='metric-container'><div class='metric-lbl'>Tasks</div><div class='metric-val'>{len(df)}</div></div>", unsafe_allow_html=True)
        with k3:
            closed = len(df[df['Status'].str.contains('Closed|Complete', case=False, na=False)]) if 'Status' in df.columns else 0
            rate = (closed/len(df)*100) if len(df) > 0 else 0
            st.markdown(f"<div class='metric-container'><div class='metric-lbl'>Closure</div><div class='metric-val'>{rate:.1f}%</div></div>", unsafe_allow_html=True)
        with k4:
            high_risk = len(df[df['Severity'].str.contains('High', na=False)]) if 'Severity' in df.columns else 0
            st.markdown(f"<div class='metric-container' style='border-top-color:#ef4444'><div class='metric-lbl'>High Risk</div><div class='metric-val' style='color:#ef4444'>{high_risk}</div></div>", unsafe_allow_html=True)
        with k5:
            avg_w = df[df['Wks']>0]['Wks'].mean() if len(df[df['Wks']>0]) > 0 else 0
            st.markdown(f"<div class='metric-container' style='border-top-color:#10b981'><div class='metric-lbl'>Aging</div><div class='metric-val'>{avg_w:.1f}w</div></div>", unsafe_allow_html=True)

        # --- ROW 2: VISUAL ANALYTICS ---
        st.markdown("<div class='section-box'>Analytical Breakdown</div>", unsafe_allow_html=True)
        d1, d2, d3, d4 = st.columns(4)
        
        with d1:
            fig1 = px.pie(df_units, names='Status', color_discrete_sequence=["#3b82f6", "#10b981", "#f59e0b"])
            st.plotly_chart(apply_pro_layout(fig1, "Delivery Status", "pie"), use_container_width=True)
            
        with d2:
            target_order = ['Low', 'Medium', 'High'] 
            sev_counts = df_units['Severity'].value_counts().reindex(target_order).dropna().reset_index()
            sev_counts.columns = ['Severity', 'count']
            fig2 = px.bar(sev_counts, x='count', y='Severity', orientation='h', color='Severity',
                          color_discrete_map={'High': '#ef4444', 'Medium': '#3b82f6', 'Low': '#94a3b8'})
            st.plotly_chart(apply_pro_layout(fig2, "Risk Levels", "bar"), use_container_width=True)
            
        with d3:
            fig3 = px.pie(df_units, names='Domain', color_discrete_sequence=px.colors.qualitative.Safe)
            st.plotly_chart(apply_pro_layout(fig3, "Domain Split", "pie"), use_container_width=True)

        with d4:
            type_counts = df_units['Type'].value_counts().reset_index().sort_values('count')
            fig4 = px.bar(type_counts, x='count', y='Type', orientation='h', color_discrete_sequence=['#6366f1'])
            st.plotly_chart(apply_pro_layout(fig4, "Request Type", "bar"), use_container_width=True)

    except Exception as e:
        st.error(f"Execution Error: {e}")
else:
    st.info("System Ready. Please upload your Excel Data Feed.")
