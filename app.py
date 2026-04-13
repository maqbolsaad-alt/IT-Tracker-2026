# --- 1. UPDATED CHART ENGINE (WITH CLIPPING FIX) ---
def apply_pro_layout(fig, title, chart_type="pie"):
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        # Increased right margin (r=60) to give numbers room to breathe
        margin=dict(t=100, b=160, l=20, r=60), 
        height=600,
        showlegend=True,
        title=dict(
            text=f"<b>{title}</b>",
            x=0.02, y=0.98, xanchor='left',
            font=dict(size=30, color='#0f172a')
        ),
        legend=dict(
            orientation="h", 
            yanchor="top", 
            y=-0.2, 
            xanchor="center", 
            x=0.5,
            font=dict(size=22, color="#0f172a", family="Inter"),
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
            textfont=dict(size=32, color="#0f172a", family="Inter"),
            textposition='outside',
            cliponaxis=False # THIS PREVENTS NUMBERS FROM BEING CUT OFF
        )
    else:
        fig.update_traces(
            textinfo='percent+value', 
            hole=0.55,
            textfont=dict(size=24, family="Inter", color="white"), 
            marker=dict(line=dict(color='#ffffff', width=4)),
            hoverinfo='label+percent',
            textposition='inside'
        )
    return fig

# --- 2. THE SPECIFIC CHART CALL ---
# Use this for your "Request Type" chart to ensure the axis range is wide enough
with d4:
    if 'Type' in df.columns:
        type_counts = df_units['Type'].value_counts().reset_index().sort_values('count')
        fig4 = px.bar(type_counts, x='count', y='Type', orientation='h', color_discrete_sequence=['#6366f1'])
        
        # Explicitly extend the x-axis range by 15% so the number fits
        max_val = type_counts['count'].max()
        fig4.update_xaxes(range=[0, max_val * 1.15]) 
        
        st.plotly_chart(apply_pro_layout(fig4, "Request Type", "bar"), use_container_width=True)
