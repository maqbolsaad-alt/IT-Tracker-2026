# --- ROW 3: DETAILED OPERATIONS LEDGER ---
        st.markdown("<div class='section-box'>Detailed Operations Ledger</div>", unsafe_allow_html=True)
        
        # Triple Column Layout for Donut Charts
        d1, d2, d3 = st.columns(3)
        
        with d1:
            # Delivery Pipeline Status
            status_counts = df.groupby('Status').size().reset_index(name='Count')
            fig_status_dn = px.pie(status_counts, values='Count', names='Status', hole=0.7,
                                   title="Delivery Pipeline Status")
            st.plotly_chart(apply_executive_theme(fig_status_dn), use_container_width=True)
            
        with d2:
            # Risk (Severity)
            severity_counts = df.groupby('Severity').size().reset_index(name='Count')
            fig_sev_dn = px.pie(severity_counts, values='Count', names='Severity', hole=0.7,
                                   title="Risk Distribution",
                                   color='Severity',
                                   color_discrete_map={'Critical': '#f85149', 'High': '#d29922', 'Medium': '#58a6ff', 'Low': '#30363d'})
            st.plotly_chart(apply_executive_theme(fig_sev_dn), use_container_width=True)

        with d3:
            # Incident Volume (Domain)
            domain_counts = df.groupby('Domain').size().reset_index(name='Count')
            fig_dom_dn = px.pie(domain_counts, values='Count', names='Domain', hole=0.7, 
                             title="Incident Volume by Domain")
            st.plotly_chart(apply_executive_theme(fig_dom_dn), use_container_width=True)

        # --- DATA TABLE ---
        def color_severity(val):
            color = '#8b949e'
            if val == 'Critical': color = '#f85149'
            elif val == 'High': color = '#d29922'
            elif val in ['Closed', 'Complete']: color = '#2ea043'
            return f'color: {color}; font-weight: bold'

        st.dataframe(
            df[['Domain', 'Category', 'Status', 'Severity', 'Wks']].style.applymap(color_severity, subset=['Severity', 'Status']),
            column_config={
                "Wks": st.column_config.ProgressColumn("Longevity", min_value=0, max_value=52, format="%d weeks"),
                "Status": st.column_config.TextColumn("Current State"),
                "Severity": st.column_config.TextColumn("Risk Class")
            },
            use_container_width=True,
            hide_index=True
        )
