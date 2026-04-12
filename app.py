import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. PREMIUM LIGHT HUD SETUP ---
st.set_page_config(page_title="Ops Executive Brief", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800;900&display=swap');
    
    /* Global Reset */
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
        background-color: #fcfcfd;
        color: #0f172a;
    }

    /* Extra-Large Metric Containers */
    .metric-container {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-bottom: 6px solid #2563eb; /* Cobalt Accent */
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.04);
        margin-bottom: 20px;
    }
    
    .metric-val { 
        font-size: 64px; /* Massive Font */
        font-weight: 900; 
        color: #1e293b; 
        line-height: 0.9;
        letter-spacing: -3px;
    }
    
    .metric-lbl { 
        font-size: 16px; /* Bigger Label */
        color: #64748b; 
        text-transform: uppercase; 
        letter-spacing: 2.5px; 
        margin-bottom: 15px; 
        font-weight: 800;
    }
    
    /* Giant Section Headers */
    .section-box {
        padding: 20px 0px;
        border-bottom: 3px solid #1e293b;
        margin-top: 50px;
        margin-bottom: 30px;
        color: #1e293b;
        font-weight: 900;
        text-transform: uppercase;
        font-size: 20px;
        letter-spacing: 2px;
    }

    /* Clean Table Styling */
    .stDataFrame {
        border-radius: 15px;
        overflow: hidden;
        border: 1px solid #e2e8f0;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. HIGH-CONTRAST CHART ENGINE ---
def apply_pro_layout(fig, title, chart_type="pie"):
    # Using a clean, bold color palette
    COBALT_PALETTE = ["#2563eb", "#3b82f6", "#60a5fa", "#93c5fd", "#dbeafe"]
    
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=100, b=40, l=10, r=10), 
        height=450, 
        showlegend=(chart_type == "pie"),
        title=dict(
            text=f"<span style='font-size:26px; font-weight:900; color:#0f172a'>{title}</span>",
            x=0.02, y=0.95, xanchor='left'
        )
    )
    
    if chart_type == "bar":
        fig.update_xaxes(showgrid=True, gridcolor="#f1f5f9", title_text="", tickfont=dict(size=14, color="#475569", weight='bold'))
        fig.update_yaxes(showgrid=False, title_text="", tickfont=dict(size=16, color="#0f172a", family="Inter-Bold"))
        fig.update_traces(
            marker_color='#2563eb',
            marker_line_width=0, 
            opacity=1.0, 
            texttemplate='<b>%{x}</b>', 
            textfont=dict(size=18, color="#ffffff"), 
            textposition='inside'
        )
    else:
        fig.update_traces(
            palette=COBALT_PALETTE,
            textinfo='percent+value', 
            hole=0.55, 
            textfont=dict(size=16, family="Inter-Bold"), 
            marker=dict(line=dict(color='#ffffff', width=3)),
            hoverinfo='label+percent'
        )
        fig.update_layout(
            legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5, font=dict(size=14))
        )
    return fig

# --- 3. MAIN INTERFACE ---
st.markdown("<h1 style='color: #0f172a; font-weight: 900; font-size: 56px; letter-spacing: -3px; margin-bottom: 20px;'>Ops Intelligence</h1>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload Data Feed", type=["xlsx"], label_visibility="collapsed")

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        df.columns = df.columns.str.strip()
        
        # Data Normalization
        cols = ['Domain', 'Category', 'Status', 'Severity', 'Type']
        df[cols] = df[cols].ffill()
        df['Severity'] = df['Severity'].astype(str).str.capitalize()
        
        if 'Duration' in df.columns:
            df['Wks'] = df['Duration'].astype(str).str.extract(r'(\d+)').fillna(0).astype(int)
        else:
            df['Wks'] = 0

        df_units = df.drop_duplicates(subset=['Category']).copy()

        # --- ROW 1: GIANT KPIs ---
        k1, k2, k3, k4 = st.columns(4)
        
        with k1:
            st.markdown(f"""<div class='metric-container'>
                <div class='metric-lbl'>Total Units</div>
                <div class='metric-val'>{len(df_units)}</div>
            </div>""", unsafe_allow_html=True)
            
        with k2:
            closed = len(df[df['Status'].str.contains('Closed|Complete', case=False, na=False)])
            rate = (closed/len(df)*100) if len(df) > 0 else 0
            st.markdown(f"""<div class='metric-container'>
                <div class='metric-lbl'>Velocity</div>
                <div class='metric-val'>{rate:.0f}%</div>
            </div>""", unsafe_allow_html=True)
            
        with k3:
            high_risk = len(df[df['Severity'].str.contains('High', na=False)])
            st.markdown(f"""<div class='metric-container' style='border-bottom-color:#dc2626'>
                <div class='metric-lbl'>Critical</div>
                <div class='metric-val' style='color:#dc2626'>{high_risk}</div>
            </div>""", unsafe_allow_html=True)
            
        with k4:
            avg_w = df[df['Wks']>0]['Wks'].mean() if len(df[df['Wks']>0]) > 0 else 0
            st.markdown(f"""<div class='metric-container' style='border-bottom-color:#059669'>
                <div class='metric-lbl'>Avg Aging</div>
                <div class='metric-val'>{avg_w:.1f}w</div>
            </div>""", unsafe_allow_html=True)

        # --- ROW 2: ANALYTICS ---
        st.markdown("<div class='section-box'>Statistical Analysis</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        
        with c1:
            fig1 = px.pie(df_units, names='Status', color_discrete_sequence=["#1e293b", "#2563eb", "#64748b", "#cbd5e1"])
            st.plotly_chart(apply_pro_layout(fig1, "Operations Status"), use_container_width=True)
            
        with c2:
            type_counts = df_units['Type'].value_counts().reset_index()
            fig2 = px.bar(type_counts, x='count', y='Type', orientation='h')
            st.plotly_chart(apply_pro_layout(fig2, "Volume by Classification", "bar"), use_container_width=True)

        # --- ROW 3: DATAFRAME ---
        st.markdown("<div class='section-box'>Full Incident Log</div>", unsafe_allow_html=True)
        
        st.dataframe(
            df[['Domain', 'Type', 'Category', 'Status', 'Severity', 'Wks']],
            column_config={
                "Wks": st.column_config.ProgressColumn("Longevity", min_value=0, max_value=52, format="%d weeks"),
                "Severity": st.column_config.TextColumn("Risk"),
            },
            use_container_width=True, hide_index=True
        )

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("Ready for Data Upload.")
