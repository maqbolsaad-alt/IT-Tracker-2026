# --- ROW 1: THE KPIs (From your screenshot) ---
        k1, k2, k3, k4, k5 = st.columns(5)
        with k1: 
            st.markdown(f"<div class='metric-container'><div class='metric-lbl'>Total Units</div><div class='metric-val'>{df['Category'].nunique()}</div></div>", unsafe_allow_html=True)
        with k2: 
            st.markdown(f"<div class='metric-container'><div class='metric-lbl'>Active Tasks</div><div class='metric-val'>{len(df)}</div></div>", unsafe_allow_html=True)
        with k3:
            closed = len(df[df['Status'].str.contains('Closed|Complete', case=False, na=False)])
            rate = (closed/len(df)*100) if len(df) > 0 else 0
            st.markdown(f"<div class='metric-container'><div class='metric-lbl'>Closure Rate</div><div class='metric-val'>{rate:.1f}%</div></div>", unsafe_allow_html=True)
        with k4:
            crit = len(df[df['Severity'].str.contains('Critical', na=False)])
            st.markdown(f"<div class='metric-container'><div class='metric-lbl'>Critical Risks</div><div class='metric-val'>{crit}</div></div>", unsafe_allow_html=True)
        with k5:
            avg_w = df[df['Wks']>0]['Wks'].mean() if len(df[df['Wks']>0]) > 0 else 0
            st.markdown(f"<div class='metric-container'><div class='metric-lbl'>Avg Longevity</div><div class='metric-val'>{avg_w:.1f}w</div></div>", unsafe_allow_html=True)

        # --- ROW 2: THE THREE DONUTS (Next to each other) ---
        st.markdown("<div class='section-box'>Risk & Duration Analysis</div>", unsafe_allow_html=True)
        
        d1, d2, d3 = st.columns(3)
        
        with d1:
            # Chart 1: Delivery Pipeline
            fig1 = px.pie(df, names='Status', hole=0.75, title="Delivery Pipeline Status")
            fig1.update_traces(textinfo='none') # Keep it clean/minimal
            st.plotly_chart(apply_executive_theme(fig1), use_container_width=True)
            
        with d2:
            # Chart 2: Risk Distribution
            fig2 = px.pie(df, names='Severity', hole=0.75, title="Risk Distribution",
                          color='Severity', 
                          color_discrete_map={'Critical': '#f85149', 'High': '#d29922', 'Medium': '#58a6ff', 'Low': '#30363d'})
            fig2.update_traces(textinfo='none')
            st.plotly_chart(apply_executive_theme(fig2), use_container_width=True)
            
        with d3:
            # Chart 3: Incident Volume
            fig3 = px.pie(df, names='Domain', hole=0.75, title="Incident Volume")
            fig3.update_traces(textinfo='none')
            st.plotly_chart(apply_executive_theme(fig3), use_container_width=True)

        # --- ROW 3: DETAILED LEDGER ---
        st.markdown("<div class='section-box'>Detailed Operations Ledger</div>", unsafe_allow_html=True)
        
        def color_severity(val):
            if val == 'Critical': return 'color: #f85149; font-weight: bold'
            if val == 'High': return 'color: #d29922; font-weight: bold'
            if val in ['Closed', 'Complete']: return 'color: #2ea043; font-weight: bold'
            return 'color: #8b949e'

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
