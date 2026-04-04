with c1:
    st.markdown("<div class='section-header'>Resource Allocation Analysis</div>", unsafe_allow_html=True)
    
    # 1. TREEMAP: Much better than Sunburst for "at-a-glance" understanding
    # It shows Domain as the main box, and Types as sub-boxes.
    fig_tree = px.treemap(df_clean, 
                          path=[px.Constant("All Projects"), 'Domain', 'Type'], 
                          color='Domain',
                          color_discrete_sequence=px.colors.qualitative.Prism,
                          title="<b>Where is the Effort Going?</b>")
    
    fig_tree.update_traces(textinfo="label+value")
    fig_tree.update_layout(margin=dict(t=50, b=10, l=10, r=10))
    st.plotly_chart(apply_modern_theme(fig_tree), use_container_width=True)
    
    # 2. HORIZONTAL STACKED BAR: Shows the "Mix" of work within each domain
    # This answers: "In the Security domain, how much is 'Support' vs 'New Feature'?"
    domain_mix = df_clean.groupby(['Domain', 'Type']).size().reset_index(name='count')
    fig_mix = px.bar(domain_mix, 
                     y='Domain', x='count', color='Type', 
                     orientation='h',
                     title="<b>Domain Composition by Work Type</b>",
                     color_discrete_sequence=px.colors.sequential.Agsunset)
    
    fig_mix.update_layout(barmode='stack', showlegend=True)
    st.plotly_chart(apply_modern_theme(fig_mix), use_container_width=True)
