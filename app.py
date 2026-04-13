# --- UPDATED ENHANCED CHART STYLING ENGINE ---
def apply_pro_layout(fig, title, chart_type="pie"):
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=80, b=100, l=10, r=10), # Increased bottom margin for legend
        height=500, # Increased height slightly for clarity
        showlegend=(chart_type == "pie"),
        title=dict(
            text=f"<b>{title}</b>",
            x=0.02, y=0.98, xanchor='left',
            font=dict(size=24, color='#0f172a') # Bigger Title
        )
    )
    
    if chart_type == "bar":
        fig.update_xaxes(
            showgrid=True, 
            gridcolor="#f1f5f9", 
            title_text="", 
            tickfont=dict(size=16, color="#64748b") # Bigger X-axis labels
        )
        fig.update_yaxes(
            showgrid=False, 
            title_text="", 
            tickfont=dict(size=18, color="#1e293b", family="Inter-SemiBold") # Bigger Y-axis labels
        )
        fig.update_traces(
            marker_line_width=0, 
            opacity=0.9, 
            texttemplate='<b>%{x}</b>', 
            textfont=dict(size=20, color="#1e293b"), # Much bigger numbers on bars
            textposition='outside'
        )
    else:
        # Pie/Donut Chart specific logic
        fig.update_traces(
            textinfo='percent+value', 
            hole=0.5, 
            textfont=dict(size=18, family="Inter-Bold"), # Much bigger numbers inside/around pie
            marker=dict(line=dict(color='#ffffff', width=3)),
            hoverinfo='label+percent',
            textposition='auto'
        )
        fig.update_layout(
            legend=dict(
                orientation="h", 
                yanchor="top", 
                y=-0.15, # Moved lower to avoid overlap
                xanchor="center", 
                x=0.5,
                font=dict(size=16, color="#1e293b"), # Bigger Legend Text
                itemwidth=40
            )
        )
    return fig
