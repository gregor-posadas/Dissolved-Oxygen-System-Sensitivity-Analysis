import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

def main():
    st.set_page_config(
        page_title="Aeration System Comparison Tool",
        page_icon="💧",
        layout="wide"
    )
    
    # Custom CSS for Apple-style comparison
    st.markdown("""
        <style>
        .comparison-card {
            background-color: #f5f5f7;
            border-radius: 18px;
            padding: 20px;
            margin: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .metric-value {
            font-size: 48px;
            font-weight: 600;
            color: #1d1d1f;
        }
        .metric-label {
            font-size: 14px;
            color: #6e6e73;
            margin-top: 4px;
        }
        .system-name {
            font-size: 24px;
            font-weight: 600;
            margin-bottom: 20px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("🌊 Wastewater Aeration System Comparison Tool")
    st.markdown("### Powered by BioSolutions")
    
    # Sidebar for inputs
    with st.sidebar:
        st.header("Facility Specifications")
        
        st.subheader("Basic Information")
        flow_rate = st.number_input("Flow Rate (MGD)", min_value=0.1, value=0.24, step=0.1)
        population = st.number_input("Population Served", min_value=100, value=920, step=100)
        
        st.subheader("Influent Characteristics")
        bod5 = st.number_input("BOD₅ (mg/L)", min_value=50.0, value=200.0, step=10.0)
        cod = st.number_input("COD (mg/L)", min_value=100.0, value=400.0, step=10.0)
        tn = st.number_input("Total Nitrogen (mg/L)", min_value=10.0, value=40.0, step=5.0)
        tp = st.number_input("Total Phosphorus (mg/L)", min_value=2.0, value=10.0, step=1.0)
        temp = st.slider("Temperature (°C)", min_value=5, max_value=30, value=15)
        
        st.subheader("Current System")
        current_system = st.selectbox("Current Aeration Type", 
                                     ["Turbine", "Diffused Air", "Surface", "None"])
        current_kwh = st.number_input("Current Monthly kWh", min_value=0, value=5000, step=100)
        energy_cost = st.number_input("Energy Cost ($/kWh)", min_value=0.01, value=0.054658, step=0.01, format="%.5f")
        
        st.subheader("Effluent Requirements")
        tn_limit = st.number_input("TN Limit (mg/L)", min_value=5.0, value=15.0, step=1.0)
        tp_limit = st.number_input("TP Limit (mg/L)", min_value=0.5, value=2.0, step=0.5)
    
    # Prepare facility data
    facility_data = {
        'basic_info': {
            'flow_rate_mgd': flow_rate,
            'population_served': population
        },
        'influent_characteristics': {
            'bod5_mg_l': bod5,
            'cod_mg_l': cod,
            'tn_mg_l': tn,
            'tp_mg_l': tp,
            'temperature_celsius': temp
        },
        'current_aeration': {
            'system_type': current_system,
            'monthly_kwh': current_kwh,
            'energy_cost_per_kwh': energy_cost
        },
        'effluent_requirements': {
            'tn_limit_mg_l': tn_limit,
            'tp_limit_mg_l': tp_limit
        }
    }
    
    # Calculate performance for all systems
    biosolutions = BioSolutionsSystem()
    turbine = TurbineAerationSystem()
    diffused = DiffusedAirSystem()
    
    bio_perf = biosolutions.calculate_performance(facility_data)
    turb_perf = turbine.calculate_performance(facility_data)
    diff_perf = diffused.calculate_performance(facility_data)
    
    # System selection for comparison
    st.header("Select Systems to Compare")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        compare_bio = st.checkbox("BioSolutions DO Infusion", value=True)
    with col2:
        compare_turb = st.checkbox("Turbine Aeration", value=True)
    with col3:
        compare_diff = st.checkbox("Fine Bubble Diffused Air", value=False)
    
    # Create comparison layout
    selected_systems = []
    if compare_bio:
        selected_systems.append(("BioSolutions", bio_perf, "#007AFF"))
    if compare_turb:
        selected_systems.append(("Turbine", turb_perf, "#FF3B30"))
    if compare_diff:
        selected_systems.append(("Diffused Air", diff_perf, "#34C759"))
    
    if len(selected_systems) == 0:
        st.warning("Please select at least one system to display.")
        return
    
    # Apple-style comparison cards
    st.header("System Comparison")
    
    cols = st.columns(len(selected_systems))
    
    for idx, (name, perf, color) in enumerate(selected_systems):
        with cols[idx]:
            st.markdown(f"""
                <div class="comparison-card" style="border-left: 4px solid {color}">
                    <div class="system-name">{name}</div>
                </div>
            """, unsafe_allow_html=True)
            
            # Key metrics
            st.metric("Monthly Cost", f"${perf['monthly_cost_usd']:.2f}")
            st.metric("Monthly Energy", f"{perf['monthly_energy_kwh']:.0f} kWh")
            st.metric("Effluent TN", f"{perf['projected_tn_effluent']:.1f} mg/L")
            st.metric("Effluent TP", f"{perf['projected_tp_effluent']:.1f} mg/L")
            st.metric("DO Capability", f"{perf['do_capability']:.1f} mg/L")
            st.metric("Capital Cost", f"${perf['capital_cost']:,.0f}")
            
            # Compliance check
            tn_compliant = perf['projected_tn_effluent'] <= tn_limit
            tp_compliant = perf['projected_tp_effluent'] <= tp_limit
            
            if tn_compliant and tp_compliant:
                st.success("✅ Meets Effluent Limits")
            else:
                st.error("❌ Exceeds Effluent Limits")
    
    # Detailed comparison charts
    st.header("Detailed Performance Analysis")
    
    # Create comparison dataframe
    comparison_df = pd.DataFrame([
        {
            'System': name,
            'Monthly Cost ($)': perf['monthly_cost_usd'],
            'Monthly Energy (kWh)': perf['monthly_energy_kwh'],
            'TN Effluent (mg/L)': perf['projected_tn_effluent'],
            'TP Effluent (mg/L)': perf['projected_tp_effluent'],
            'Capital Cost ($)': perf['capital_cost'],
            'Footprint (sq ft)': perf['footprint']
        }
        for name, perf, _ in selected_systems
    ])
    
    # Cost comparison chart
    fig_cost = go.Figure()
    fig_cost.add_trace(go.Bar(
        x=comparison_df['System'],
        y=comparison_df['Monthly Cost ($)'],
        marker_color=[color for _, _, color in selected_systems],
        text=comparison_df['Monthly Cost ($)'].round(2),
        textposition='auto',
    ))
    fig_cost.update_layout(
        title="Monthly Operating Cost Comparison",
        yaxis_title="Cost ($/month)",
        showlegend=False,
        height=400
    )
    st.plotly_chart(fig_cost, use_container_width=True)
    
    # Energy comparison
    fig_energy = go.Figure()
    fig_energy.add_trace(go.Bar(
        x=comparison_df['System'],
        y=comparison_df['Monthly Energy (kWh)'],
        marker_color=[color for _, _, color in selected_systems],
        text=comparison_df['Monthly Energy (kWh)'].round(0),
        textposition='auto',
    ))
    fig_energy.update_layout(
        title="Monthly Energy Consumption Comparison",
        yaxis_title="Energy (kWh/month)",
        showlegend=False,
        height=400
    )
    st.plotly_chart(fig_energy, use_container_width=True)
    
    # Nutrient removal comparison
    fig_nutrients = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Total Nitrogen Removal", "Total Phosphorus Removal")
    )
    
    for system_name, perf, color in selected_systems:
        fig_nutrients.add_trace(
            go.Bar(name=system_name, x=[system_name], y=[perf['projected_tn_effluent']],
                  marker_color=color, showlegend=False),
            row=1, col=1
        )
        fig_nutrients.add_trace(
            go.Bar(name=system_name, x=[system_name], y=[perf['projected_tp_effluent']],
                  marker_color=color, showlegend=False),
            row=1, col=2
        )
    
    # Add limit lines
    fig_nutrients.add_hline(y=tn_limit, line_dash="dash", line_color="red", 
                           annotation_text="Limit", row=1, col=1)
    fig_nutrients.add_hline(y=tp_limit, line_dash="dash", line_color="red", 
                           annotation_text="Limit", row=1, col=2)
    
    fig_nutrients.update_yaxes(title_text="mg/L as N", row=1, col=1)
    fig_nutrients.update_yaxes(title_text="mg/L as P", row=1, col=2)
    fig_nutrients.update_layout(height=400, title_text="Effluent Nutrient Concentrations")
    
    st.plotly_chart(fig_nutrients, use_container_width=True)
    
    # Capital cost vs operating cost
    fig_capex_opex = go.Figure()
    
    for system_name, perf, color in selected_systems:
        annual_opex = perf['monthly_cost_usd'] * 12
        fig_capex_opex.add_trace(go.Scatter(
            x=[perf['capital_cost']],
            y=[annual_opex],
            mode='markers+text',
            name=system_name,
            marker=dict(size=20, color=color),
            text=[system_name],
            textposition="top center"
        ))
    
    fig_capex_opex.update_layout(
        title="Capital Cost vs Annual Operating Cost",
        xaxis_title="Capital Cost ($)",
        yaxis_title="Annual Operating Cost ($/year)",
        height=500
    )
    st.plotly_chart(fig_capex_opex, use_container_width=True)
    
    # Sensitivity Analysis Section
    st.header("Sensitivity Analysis")
    
    st.markdown("""
    Explore how changes in key parameters affect system performance. 
    Select a parameter to vary and see how each system responds.
    """)
    
    sens_param = st.selectbox(
        "Parameter to Analyze",
        ["Flow Rate", "Energy Cost", "Influent BOD", "Influent TN", "Temperature"]
    )
    
    param_map = {
        "Flow Rate": "basic_info.flow_rate_mgd",
        "Energy Cost": "current_aeration.energy_cost_per_kwh",
        "Influent BOD": "influent_characteristics.bod5_mg_l",
        "Influent TN": "influent_characteristics.tn_mg_l",
        "Temperature": "influent_characteristics.temperature_celsius"
    }
    
    col1, col2 = st.columns(2)
    with col1:
        range_min = st.slider("Minimum (% of current)", 50, 100, 70)
    with col2:
        range_max = st.slider("Maximum (% of current)", 100, 200, 130)
    
    if st.button("Run Sensitivity Analysis"):
        with st.spinner("Calculating..."):
            sens_results = sensitivity_analysis(
                facility_data, 
                param_map[sens_param],
                (range_min/100, range_max/100)
            )
            
            # Plot results
            fig_sens = make_subplots(
                rows=2, cols=2,
                subplot_titles=("Monthly Cost", "Monthly Energy", 
                              "TN Effluent", "TP Effluent")
            )
            
            for system_name in sens_results['system'].unique():
                system_data = sens_results[sens_results['system'] == system_name]
                color_map = {"BioSolutions DO Infusion": "#007AFF", 
                           "Turbine Aeration": "#FF3B30",
                           "Fine Bubble Diffused Air": "#34C759"}
                color = color_map.get(system_name, "#000000")
                
                fig_sens.add_trace(
                    go.Scatter(x=system_data['parameter_value'], 
                             y=system_data['monthly_cost_usd'],
                             name=system_name, line=dict(color=color),
                             showlegend=True),
                    row=1, col=1
                )
                fig_sens.add_trace(
                    go.Scatter(x=system_data['parameter_value'], 
                             y=system_data['monthly_energy_kwh'],
                             name=system_name, line=dict(color=color),
                             showlegend=False),
                    row=1, col=2
                )
                fig_sens.add_trace(
                    go.Scatter(x=system_data['parameter_value'], 
                             y=system_data['projected_tn_effluent'],
                             name=system_name, line=dict(color=color),
                             showlegend=False),
                    row=2, col=1
                )
                fig_sens.add_trace(
                    go.Scatter(x=system_data['parameter_value'], 
                             y=system_data['projected_tp_effluent'],
                             name=system_name, line=dict(color=color),
                             showlegend=False),
                    row=2, col=2
                )
            
            fig_sens.update_xaxes(title_text=sens_param, row=2, col=1)
            fig_sens.update_xaxes(title_text=sens_param, row=2, col=2)
            fig_sens.update_yaxes(title_text="$/month", row=1, col=1)
            fig_sens.update_yaxes(title_text="kWh/month", row=1, col=2)
            fig_sens.update_yaxes(title_text="mg/L", row=2, col=1)
            fig_sens.update_yaxes(title_text="mg/L", row=2, col=2)
            
            fig_sens.update_layout(height=700, title_text=f"Sensitivity to {sens_param}")
            st.plotly_chart(fig_sens, use_container_width=True)
    
    # Summary table
    st.header("Summary Table")
    st.dataframe(comparison_df.style.format({
        'Monthly Cost ($)': '${:,.2f}',
        'Monthly Energy (kWh)': '{:,.0f}',
        'TN Effluent (mg/L)': '{:.2f}',
        'TP Effluent (mg/L)': '{:.2f}',
        'Capital Cost ($)': '${:,.0f}',
        'Footprint (sq ft)': '{:,.0f}'
    }), use_container_width=True)
    
    # ROI Calculator
    st.header("Return on Investment Calculator")
    
    if compare_bio and (compare_turb or compare_diff):
        baseline_system = "Turbine" if compare_turb else "Diffused Air"
        baseline_perf = turb_perf if compare_turb else diff_perf
        
        monthly_savings = baseline_perf['monthly_cost_usd'] - bio_perf['monthly_cost_usd']
        annual_savings = monthly_savings * 12
        capital_difference = bio_perf['capital_cost'] - baseline_perf['capital_cost']
        
        if annual_savings > 0:
            payback_years = capital_difference / annual_savings
            st.success(f"💰 Switching to BioSolutions saves **${monthly_savings:.2f}/month** (${annual_savings:.2f}/year)")
            st.info(f"⏱️ Simple payback period: **{payback_years:.1f} years**")
        else:
            st.warning(f"Operating costs are ${abs(monthly_savings):.2f}/month higher with BioSolutions")
        
        # Additional benefits
        tn_improvement = baseline_perf['projected_tn_effluent'] - bio_perf['projected_tn_effluent']
        tp_improvement = baseline_perf['projected_tp_effluent'] - bio_perf['projected_tp_effluent']
        
        st.subheader("Additional Benefits")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("TN Reduction", f"{tn_improvement:.1f} mg/L", 
                     f"{(tn_improvement/baseline_perf['projected_tn_effluent']*100):.1f}%")
        with col2:
            st.metric("TP Reduction", f"{tp_improvement:.1f} mg/L",
                     f"{(tp_improvement/baseline_perf['projected_tp_effluent']*100):.1f}%")
    
    # Download report
    st.header("Export Results")
    
    if st.button("Generate PDF Report"):
        st.info("PDF generation feature coming soon!")
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: #6e6e73;'>
            <p>Developed by BioSolutions | Data based on Greenleaf WWTP case study</p>
            <p>For more information, contact: <a href='mailto:info@biosolutions.com'>info@biosolutions.com</a></p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
```

## 4. DEPLOYMENT INSTRUCTIONS

Create a `requirements.txt` file:
```
streamlit==1.28.0
pandas==2.0.3
numpy==1.24.3
plotly==5.17.0
