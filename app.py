with c1:
            st.markdown("<div class='section-header'>Strategic Distribution</div>", unsafe_allow_html=True)
            
            # --- IMPROVED HIERARCHY: ICICLE CHART ---
            # Icicles are easier to read than sunbursts in narrow columns
            fig_hierarchy = px.icicle(
                df_clean, 
                path=[px.Constant("Portfolio"), 'Domain', 'Type'], 
                color='Domain',
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            
            fig_hierarchy.update_traces(
                textinfo="label+percent entry",
                tiling=dict(orientation='v') # Vertical orientation looks modern
            )
            
            st.plotly_chart(apply_modern_theme(fig_hierarchy), use_container_width=True)
            
            # --- REFINED STATUS DONUT ---
            # Added custom styling to make the donut look "glowy" and professional
            fig_donut = go.Figure(data=[go.Pie(
                labels=df_clean['Status'], 
                values=[1]*len(df_clean), 
                hole=.75,
                marker=dict(colors=['#58a6ff', '#2EB67D', '#FFD700'], line=dict(color='#05070a', width=2))
            )])
            
            fig_donut.update_layout(
                title=dict(text="Delivery Velocity", font=dict(size=14)),
                showlegend=True,
                margin=dict(t=30, b=0, l=0, r=0)
            )
            
            st.plotly_chart(apply_modern_theme(fig_donut), use_container_width=True)
