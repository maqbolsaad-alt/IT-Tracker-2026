with c1:
    st.markdown("<div class='section-header'>Strategic Resource Allocation</div>", unsafe_allow_html=True)
    
    # --- 1. ENHANCED TREEMAP ---
    # We aggregate data to ensure the boxes are sized by the number of projects
    tree_data = df_clean.groupby(['Domain', 'Type']).size().reset_index(name='Project Count')
    
    fig_tree = px.treemap(
        tree_data, 
        path=[px.Constant("Portfolio"), 'Domain', 'Type'], 
        values='Project Count',
        color='Domain',
        color_discrete_sequence=px.colors.qualitative.Bold,
        hover_data=['Project Count']
    )
    
    # Clean up the look: Remove the root 'Portfolio' box text for a cleaner look
    fig_tree.update_traces(
        textinfo="label+value",
        hovertemplate='<b>%{label}</b><br>Total Projects: %{value}',
        marker_line_width=2
    )
    fig_tree.update_layout(title="<b>Workload Distribution by Domain</b>")
    st.plotly_chart(apply_modern_theme(fig_tree), use_container_width=True)
    
    # --- 2. 100% STACKED BAR (Normalized Mix) ---
    # This is "better looking" because it aligns all bars to the same width (100%)
    # making it easier to compare the work 'flavor' across domains.
    mix_data = df_clean.groupby(['Domain', 'Type']).size().reset_index(name='count')
    
    fig_mix = px.bar(
        mix_data, 
        y='Domain', 
        x='count', 
        color='Type', 
        orientation='h',
        title="<b>Work Type Composition (%)</b>",
        color_discrete_sequence=px.colors.sequential.Viridis,
        # 'percent' makes it a 100% stacked bar
        barnorm='percent' 
    )
    
    fig_mix.update_layout(
        barmode='stack', 
        xaxis_title="Contribution Percentage",
        yaxis_title=None,
        legend_title="Work Type",
        showlegend=True
    )
    
    # Add percentage labels inside the bars
    fig_mix.update_traces(texttemplate='%{x:.1f}%', textposition='inside')
    
    st.plotly_chart(apply_modern_theme(fig_mix), use_container_width=True)

    st.info("💡 **Insight:** Larger boxes in the Treemap indicate higher project volume. The Bar Chart shows the balance between Support, Growth, and Innovation.")
