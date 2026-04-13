# --- 2. ENHANCED CHART STYLING ENGINE (Updated for High Visibility) ---
def apply_pro_layout(fig, title, chart_type="pie"):
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=100, b=80, l=10, r=10), # Added more bottom margin for larger legend
        height=500, # Increased height slightly
        showlegend=(chart_type == "pie"),
        title=dict(
            text=f"<b>{title}</b>",
            x=0.02, y=0.95, xanchor='left',
            font=dict(size=26, color='#0f172a') # Larger title
        )
    )
    
    if chart_type == "bar":
        fig.update_xaxes(
            showgrid=True, 
            gridcolor="#f1f5f9", 
            title_text="", 
            tickfont=dict(size=16, color="#64748b") # Larger X-axis labels
        )
        fig.update_yaxes(
            showgrid=False, 
            title_text="", 
            tickfont=dict(size=18, color="#1e293b", family="Inter-SemiBold") # Larger Y-axis labels
        )
        fig.update_traces(
            marker_line_width=0, 
            opacity=0.9, 
            texttemplate='<b>%{x}</b>', 
            textfont=dict(size=20, color="#1e293b"), # Larger numbers on bar ends
            textposition='outside'
        )
    else:
        # Pie / Donut Chart adjustments
        fig.update_traces(
            textinfo='percent+value', 
            hole=0.5, 
            textfont=dict(size=18, family="Inter-Bold"), # Much larger numbers inside slices
            marker=dict(line=dict(color='#ffffff', width=3)),
            hoverinfo='label+percent'
        )
        fig.update_layout(
            legend=dict(
                orientation="h", 
                yanchor="bottom", 
                y=-0.3, # Moved lower to prevent overlapping
                xanchor="center", 
                x=0.5,
                font=dict(size=18) # Larger legend text
            )
        )
    return fig
