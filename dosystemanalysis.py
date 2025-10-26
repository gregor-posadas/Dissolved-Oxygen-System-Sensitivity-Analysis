import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from dataclasses import dataclass
from typing import Dict, List, Tuple
from io import BytesIO
from datetime import datetime

@dataclass
class AerationSystem:
    """Base class for aeration system characteristics"""
    name: str
    system_type: str
    installed_hp: float
    oxygen_transfer_efficiency: float
    energy_consumption_factor: float
    capital_cost_per_mgd: float
    maintenance_cost_annual: float
    do_delivery_capability: float
    footprint_sq_ft: float

class BioSolutionsSystem(AerationSystem):
    """BioSolutions high-concentration DO infusion system"""
    def __init__(self):
        super().__init__(
            name="BioSolutions DO Infusion",
            system_type="High-concentration DO infusion",
            installed_hp=20,
            oxygen_transfer_efficiency=2.8,
            energy_consumption_factor=0.85,
            capital_cost_per_mgd=250000,
            maintenance_cost_annual=5000,
            do_delivery_capability=40.0,
            footprint_sq_ft=100
        )
    
    def calculate_performance(self, facility_data: Dict) -> Dict:
        """Calculate expected performance metrics"""
        flow_mgd = facility_data['basic_info']['flow_rate_mgd']
        
        # Oxygen demand calculation
        bod_removal = facility_data['influent_characteristics']['bod5_mg_l'] * 0.8
        oxygen_demand_lb_day = flow_mgd * bod_removal * 8.34
        
        # Energy calculation based on Greenleaf case study
        base_kwh_per_day = 187.6
        scaling_factor = flow_mgd / 0.24
        estimated_kwh_day = base_kwh_per_day * scaling_factor ** 0.85
        
        # Nutrient removal projection
        tn_removal_improvement = 0.55
        tp_removal_improvement = 0.26
        
        current_tn = facility_data['influent_characteristics']['tn_mg_l']
        current_tp = facility_data['influent_characteristics']['tp_mg_l']
        
        projected_tn_effluent = current_tn * (1 - tn_removal_improvement)
        projected_tp_effluent = current_tp * (1 - tp_removal_improvement)
        
        # Cost calculation
        energy_cost = estimated_kwh_day * 30 * facility_data['current_aeration']['energy_cost_per_kwh']
        
        return {
            'daily_energy_kwh': estimated_kwh_day,
            'monthly_energy_kwh': estimated_kwh_day * 30,
            'monthly_cost_usd': energy_cost + self.maintenance_cost_annual/12,
            'daily_cost_usd': energy_cost/30,
            'projected_tn_effluent': projected_tn_effluent,
            'projected_tp_effluent': projected_tp_effluent,
            'do_capability': self.do_delivery_capability,
            'capital_cost': self.capital_cost_per_mgd * flow_mgd,
            'footprint': self.footprint_sq_ft
        }

class TurbineAerationSystem(AerationSystem):
    """Traditional turbine aeration system"""
    def __init__(self):
        super().__init__(
            name="Turbine Aeration",
            system_type="Mechanical surface aeration",
            installed_hp=50,
            oxygen_transfer_efficiency=2.0,
            energy_consumption_factor=1.2,
            capital_cost_per_mgd=180000,
            maintenance_cost_annual=8000,
            do_delivery_capability=5.0,
            footprint_sq_ft=200
        )
    
    def calculate_performance(self, facility_data: Dict) -> Dict:
        """Calculate expected performance for turbine system"""
        flow_mgd = facility_data['basic_info']['flow_rate_mgd']
        
        # Energy calculation based on Greenleaf baseline
        base_kwh_per_day = 166.8
        scaling_factor = flow_mgd / 0.24
        estimated_kwh_day = base_kwh_per_day * scaling_factor ** 0.85
        
        # Standard nutrient removal
        tn_removal_standard = 0.35
        tp_removal_standard = 0.20
        
        current_tn = facility_data['influent_characteristics']['tn_mg_l']
        current_tp = facility_data['influent_characteristics']['tp_mg_l']
        
        projected_tn_effluent = current_tn * (1 - tn_removal_standard)
        projected_tp_effluent = current_tp * (1 - tp_removal_standard)
        
        energy_cost = estimated_kwh_day * 30 * facility_data['current_aeration']['energy_cost_per_kwh']
        
        return {
            'daily_energy_kwh': estimated_kwh_day,
            'monthly_energy_kwh': estimated_kwh_day * 30,
            'monthly_cost_usd': energy_cost + self.maintenance_cost_annual/12,
            'daily_cost_usd': energy_cost/30,
            'projected_tn_effluent': projected_tn_effluent,
            'projected_tp_effluent': projected_tp_effluent,
            'do_capability': self.do_delivery_capability,
            'capital_cost': self.capital_cost_per_mgd * flow_mgd,
            'footprint': self.footprint_sq_ft
        }

class DiffusedAirSystem(AerationSystem):
    """Fine bubble diffused aeration"""
    def __init__(self):
        super().__init__(
            name="Fine Bubble Diffused Air",
            system_type="Submerged diffused aeration",
            installed_hp=40,
            oxygen_transfer_efficiency=3.5,
            energy_consumption_factor=0.75,
            capital_cost_per_mgd=220000,
            maintenance_cost_annual=12000,
            do_delivery_capability=8.0,
            footprint_sq_ft=150
        )
    
    def calculate_performance(self, facility_data: Dict) -> Dict:
        """Calculate expected performance for diffused air system"""
        flow_mgd = facility_data['basic_info']['flow_rate_mgd']
        
        # Fine bubble is typically most energy efficient
        base_kwh_per_day = 150
        scaling_factor = flow_mgd / 0.24
        estimated_kwh_day = base_kwh_per_day * scaling_factor ** 0.85
        
        # Moderate nutrient removal
        tn_removal = 0.45
        tp_removal = 0.22
        
        current_tn = facility_data['influent_characteristics']['tn_mg_l']
        current_tp = facility_data['influent_characteristics']['tp_mg_l']
        
        projected_tn_effluent = current_tn * (1 - tn_removal)
        projected_tp_effluent = current_tp * (1 - tp_removal)
        
        energy_cost = estimated_kwh_day * 30 * facility_data['current_aeration']['energy_cost_per_kwh']
        
        return {
            'daily_energy_kwh': estimated_kwh_day,
            'monthly_energy_kwh': estimated_kwh_day * 30,
            'monthly_cost_usd': energy_cost + self.maintenance_cost_annual/12,
            'daily_cost_usd': energy_cost/30,
            'projected_tn_effluent': projected_tn_effluent,
            'projected_tp_effluent': projected_tp_effluent,
            'do_capability': self.do_delivery_capability,
            'capital_cost': self.capital_cost_per_mgd * flow_mgd,
            'footprint': self.footprint_sq_ft
        }

def sensitivity_analysis(facility_data: Dict, parameter: str, 
                        variation_range: Tuple[float, float]) -> pd.DataFrame:
    """
    Perform sensitivity analysis by varying a parameter
    """
    systems = [
        BioSolutionsSystem(),
        TurbineAerationSystem(),
        DiffusedAirSystem()
    ]
    
    results = []
    
    # Parse parameter path
    keys = parameter.split('.')
    
    # Get original value - need to navigate through nested dicts
    original_value = facility_data
    for key in keys:
        original_value = original_value[key]
    
    # Create range of values
    multipliers = np.linspace(variation_range[0], variation_range[1], 20)
    
    for mult in multipliers:
        # Deep copy facility data
        import copy
        modified_data = copy.deepcopy(facility_data)
        
        # Navigate to the correct nested dictionary and set value
        current_dict = modified_data
        for key in keys[:-1]:
            current_dict = current_dict[key]
        current_dict[keys[-1]] = original_value * mult
        
        # Calculate for each system
        for system in systems:
            performance = system.calculate_performance(modified_data)
            results.append({
                'parameter_value': original_value * mult,
                'multiplier': mult,
                'system': system.name,
                **performance
            })
    
    return pd.DataFrame(results)

def generate_pdf_report(facility_data, systems_data, comparison_df):
    """Generate a simple text-based report"""
    from io import StringIO
    
    report = StringIO()
    
    report.write("=" * 80 + "\n")
    report.write("WASTEWATER AERATION SYSTEM COMPARISON REPORT\n")
    report.write("Generated by BioSolutions Analysis Tool\n")
    report.write(f"Date: {datetime.now().strftime('%B %d, %Y')}\n")
    report.write("=" * 80 + "\n\n")
    
    report.write("FACILITY INFORMATION\n")
    report.write("-" * 80 + "\n")
    report.write(f"Flow Rate: {facility_data['basic_info']['flow_rate_mgd']:.2f} MGD\n")
    report.write(f"Population Served: {facility_data['basic_info']['population_served']:,}\n")
    report.write(f"Influent BOD: {facility_data['influent_characteristics']['bod5_mg_l']:.1f} mg/L\n")
    report.write(f"Influent TN: {facility_data['influent_characteristics']['tn_mg_l']:.1f} mg/L\n")
    report.write(f"Influent TP: {facility_data['influent_characteristics']['tp_mg_l']:.1f} mg/L\n")
    report.write(f"Energy Cost: ${facility_data['current_aeration']['energy_cost_per_kwh']:.5f}/kWh\n\n")
    
    report.write("SYSTEM COMPARISON SUMMARY\n")
    report.write("-" * 80 + "\n\n")
    
    for system_name, perf, _ in systems_data:
        report.write(f"{system_name.upper()}\n")
        report.write(f"  Monthly Operating Cost: ${perf['monthly_cost_usd']:,.2f}\n")
        report.write(f"  Monthly Energy: {perf['monthly_energy_kwh']:,.0f} kWh\n")
        report.write(f"  Effluent TN: {perf['projected_tn_effluent']:.1f} mg/L\n")
        report.write(f"  Effluent TP: {perf['projected_tp_effluent']:.1f} mg/L\n")
        report.write(f"  Capital Cost: ${perf['capital_cost']:,.0f}\n")
        report.write(f"  DO Capability: {perf['do_capability']:.1f} mg/L\n\n")
    
    report.write("=" * 80 + "\n")
    report.write("For detailed analysis, visit: https://biosolutions.com\n")
    report.write("=" * 80 + "\n")
    
    return report.getvalue()

def main():
    st.set_page_config(
        page_title="Aeration System Comparison Tool",
        page_icon="💧",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Enhanced CSS for better UI
    st.markdown("""
        <style>
        .main {
            background-color: #ffffff;
        }
        .stApp {
            max-width: 1400px;
            margin: 0 auto;
        }
        .comparison-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 20px;
            padding: 25px;
            margin: 15px 0;
            box-shadow: 0 8px 16px rgba(0,0,0,0.1);
            color: white;
        }
        .metric-card {
            background-color: #f8f9fa;
            border-radius: 12px;
            padding: 15px;
            margin: 8px 0;
            border-left: 4px solid #667eea;
        }
        .system-name {
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 15px;
            color: white;
        }
        .big-number {
            font-size: 42px;
            font-weight: 700;
            color: #1a1a1a;
        }
        .savings-box {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            border-radius: 15px;
            padding: 20px;
            color: white;
            margin: 20px 0;
        }
        .warning-box {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            border-radius: 15px;
            padding: 20px;
            color: white;
            margin: 20px 0;
        }
        h1 {
            color: #1a1a1a;
            font-weight: 700;
        }
        h2 {
            color: #2c3e50;
            font-weight: 600;
            margin-top: 30px;
        }
        h3 {
            color: #34495e;
            font-weight: 600;
        }
        .stButton>button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 12px 24px;
            font-weight: 600;
            transition: transform 0.2s;
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(102, 126, 234, 0.4);
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Header with logo placeholder
    col1, col2 = st.columns([1, 4])
    with col1:
        st.markdown("### 💧")
    with col2:
        st.title("Wastewater Aeration System Comparison Tool")
        st.markdown("**Powered by BioSolutions** | Compare aeration systems and optimize your facility")
    
    st.markdown("---")
    
    # Sidebar for inputs
    with st.sidebar:
        st.image("https://via.placeholder.com/200x80/667eea/ffffff?text=BioSolutions", use_container_width=True)
        st.markdown("## 📊 Facility Input Parameters")
        
        with st.expander("🏭 Basic Information", expanded=True):
            flow_rate = st.number_input("Flow Rate (MGD)", min_value=0.1, value=0.24, step=0.1, 
                                       help="Million gallons per day")
            population = st.number_input("Population Served", min_value=100, value=920, step=100)
        
        with st.expander("💧 Influent Characteristics", expanded=True):
            bod5 = st.number_input("BOD₅ (mg/L)", min_value=50.0, value=200.0, step=10.0)
            cod = st.number_input("COD (mg/L)", min_value=100.0, value=400.0, step=10.0)
            tn = st.number_input("Total Nitrogen (mg/L)", min_value=10.0, value=40.0, step=5.0)
            tp = st.number_input("Total Phosphorus (mg/L)", min_value=2.0, value=10.0, step=1.0)
            temp = st.slider("Temperature (°C)", min_value=5, max_value=30, value=15)
        
        with st.expander("⚡ Current System", expanded=True):
            current_system = st.selectbox("Current Aeration Type", 
                                         ["Turbine", "Diffused Air", "Surface", "None"])
            current_kwh = st.number_input("Current Monthly kWh", min_value=0, value=5000, step=100)
            energy_cost = st.number_input("Energy Cost ($/kWh)", min_value=0.01, value=0.054658, 
                                         step=0.001, format="%.5f")
        
        with st.expander("✅ Effluent Requirements", expanded=True):
            tn_limit = st.number_input("TN Limit (mg/L)", min_value=5.0, value=15.0, step=1.0)
            tp_limit = st.number_input("TP Limit (mg/L)", min_value=0.5, value=2.0, step=0.5)
    
    # Prepare facility data
    facility_data = {
        'basic_info': {
            'flow_rate_mgd': flow_rate,
            'population_served': int(population)
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
    st.markdown("## 🔍 Select Systems to Compare")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        compare_bio = st.checkbox("✨ BioSolutions DO Infusion", value=True)
    with col2:
        compare_turb = st.checkbox("🌊 Turbine Aeration", value=True)
    with col3:
        compare_diff = st.checkbox("💨 Fine Bubble Diffused Air", value=False)
    
    # Create comparison layout
    selected_systems = []
    if compare_bio:
        selected_systems.append(("BioSolutions", bio_perf, "#667eea"))
    if compare_turb:
        selected_systems.append(("Turbine", turb_perf, "#f093fb"))
    if compare_diff:
        selected_systems.append(("Diffused Air", diff_perf, "#38ef7d"))
    
    if len(selected_systems) == 0:
        st.warning("⚠️ Please select at least one system to display.")
        return
    
    # Beautiful comparison cards
    st.markdown("## 💎 System Comparison at a Glance")
    
    cols = st.columns(len(selected_systems))
    
    for idx, (name, perf, color) in enumerate(selected_systems):
        with cols[idx]:
            st.markdown(f"""
                <div style="background: linear-gradient(135deg, {color} 0%, {color}dd 100%); 
                            border-radius: 20px; padding: 25px; color: white; 
                            box-shadow: 0 8px 16px rgba(0,0,0,0.1);">
                    <h3 style="color: white; margin: 0 0 20px 0;">{name}</h3>
                    <div style="background: rgba(255,255,255,0.2); border-radius: 10px; padding: 15px; margin: 10px 0;">
                        <div style="font-size: 32px; font-weight: 700;">${perf['monthly_cost_usd']:.0f}</div>
                        <div style="font-size: 14px; opacity: 0.9;">Monthly Cost</div>
                    </div>
                    <div style="background: rgba(255,255,255,0.2); border-radius: 10px; padding: 15px; margin: 10px 0;">
                        <div style="font-size: 32px; font-weight: 700;">{perf['monthly_energy_kwh']:.0f}</div>
                        <div style="font-size: 14px; opacity: 0.9;">kWh/month</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
            
            # Key metrics in cleaner format
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("TN Effluent", f"{perf['projected_tn_effluent']:.1f} mg/L")
                st.metric("Capital Cost", f"${perf['capital_cost']/1000:.0f}K")
            with col_b:
                st.metric("TP Effluent", f"{perf['projected_tp_effluent']:.1f} mg/L")
                st.metric("DO Max", f"{perf['do_capability']:.0f} mg/L")
            
            # Compliance check
            tn_compliant = perf['projected_tn_effluent'] <= tn_limit
            tp_compliant = perf['projected_tp_effluent'] <= tp_limit
            
            if tn_compliant and tp_compliant:
                st.success("✅ Meets All Limits")
            else:
                st.error("❌ Exceeds Limits")
    
    # Enhanced visualizations
    st.markdown("## 📊 Performance Comparison")
    
    # Create comparison dataframe
    comparison_df = pd.DataFrame([
        {
            'System': name,
            'Monthly Cost': perf['monthly_cost_usd'],
            'Monthly Energy': perf['monthly_energy_kwh'],
            'TN Effluent': perf['projected_tn_effluent'],
            'TP Effluent': perf['projected_tp_effluent'],
            'Capital Cost': perf['capital_cost'],
            'Footprint': perf['footprint']
        }
        for name, perf, _ in selected_systems
    ])
    
    # Tab-based organization for clarity
    tab1, tab2, tab3, tab4 = st.tabs(["💰 Costs", "⚡ Energy", "🌊 Water Quality", "📈 ROI Analysis"])
    
    with tab1:
        st.markdown("### Operating vs Capital Costs")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Monthly operating cost - horizontal bar for easy comparison
            fig_cost = go.Figure()
            fig_cost.add_trace(go.Bar(
                y=comparison_df['System'],
                x=comparison_df['Monthly Cost'],
                orientation='h',
                marker=dict(
                    color=[color for _, _, color in selected_systems],
                    pattern_shape="/"
                ),
                text=[f"${x:,.0f}" for x in comparison_df['Monthly Cost']],
                textposition='outside',
            ))
            fig_cost.update_layout(
                title="Monthly Operating Cost",
                xaxis_title="Cost ($/month)",
                height=300,
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
            )
            st.plotly_chart(fig_cost, use_container_width=True)
        
        with col2:
            # Capital cost comparison
            fig_capital = go.Figure()
            fig_capital.add_trace(go.Bar(
                y=comparison_df['System'],
                x=comparison_df['Capital Cost'],
                orientation='h',
                marker=dict(
                    color=[color for _, _, color in selected_systems],
                ),
                text=[f"${x/1000:,.0f}K" for x in comparison_df['Capital Cost']],
                textposition='outside',
            ))
            fig_capital.update_layout(
                title="Capital Investment Required",
                xaxis_title="Cost ($)",
                height=300,
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
            )
            st.plotly_chart(fig_capital, use_container_width=True)
    
    with tab2:
        st.markdown("### Energy Consumption Analysis")
        
        # Gauge-style visualization for energy
        fig_energy = go.Figure()
        
        for idx, (name, perf, color) in enumerate(selected_systems):
            fig_energy.add_trace(go.Indicator(
                mode="gauge+number+delta",
                value=perf['monthly_energy_kwh'],
                domain={'row': 0, 'column': idx},
                title={'text': name},
                delta={'reference': current_kwh, 'relative': True, 'valueformat': '.1%'},
                gauge={
                    'axis': {'range': [None, max(comparison_df['Monthly Energy']) * 1.2]},
                    'bar': {'color': color},
                    'steps': [
                        {'range': [0, max(comparison_df['Monthly Energy']) * 0.5], 'color': "lightgray"},
                        {'range': [max(comparison_df['Monthly Energy']) * 0.5, max(comparison_df['Monthly Energy'])], 'color': "gray"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': current_kwh
                    }
                }
            ))
        
        fig_energy.update_layout(
            grid={'rows': 1, 'columns': len(selected_systems), 'pattern': "independent"},
            height=350
        )
        
        st.plotly_chart(fig_energy, use_container_width=True)
        
        st.info(f"🔴 Red line shows your current consumption: {current_kwh:,.0f} kWh/month")
    
    with tab3:
        st.markdown("### Nutrient Removal Performance")
        
        # Stacked comparison with limit lines
        fig_nutrients = go.Figure()
        
        fig_nutrients.add_trace(go.Bar(
            name='Total Nitrogen',
            x=[name for name, _, _ in selected_systems],
            y=[perf['projected_tn_effluent'] for _, perf, _ in selected_systems],
            marker=dict(color='#667eea'),
            text=[f"{perf['projected_tn_effluent']:.1f}" for _, perf, _ in selected_systems],
            textposition='outside',
        ))
        
        fig_nutrients.add_trace(go.Bar(
            name='Total Phosphorus',
            x=[name for name, _, _ in selected_systems],
            y=[perf['projected_tp_effluent'] for _, perf, _ in selected_systems],
            marker=dict(color='#f093fb'),
            text=[f"{perf['projected_tp_effluent']:.1f}" for _, perf, _ in selected_systems],
            textposition='outside',
        ))
        
        # Add limit lines
        fig_nutrients.add_hline(y=tn_limit, line_dash="dash", line_color="red", 
                               annotation_text=f"TN Limit: {tn_limit} mg/L")
        fig_nutrients.add_hline(y=tp_limit, line_dash="dash", line_color="orange", 
                               annotation_text=f"TP Limit: {tp_limit} mg/L")
        
        fig_nutrients.update_layout(
            title="Effluent Nutrient Concentrations",
            yaxis_title="Concentration (mg/L)",
            barmode='group',
            height=450,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig_nutrients, use_container_width=True)
        
        # Show removal percentages
        st.markdown("#### Removal Efficiency")
        cols = st.columns(len(selected_systems))
        for idx, (name, perf, color) in enumerate(selected_systems):
            with cols[idx]:
                tn_removal = ((tn - perf['projected_tn_effluent']) / tn) * 100
                tp_removal = ((tp - perf['projected_tp_effluent']) / tp) * 100
                st.markdown(f"""
                    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 4px solid {color};">
                        <h4 style="margin: 0 0 10px 0;">{name}</h4>
                        <p style="margin: 5px 0;">TN Removal: <strong>{tn_removal:.1f}%</strong></p>
                        <p style="margin: 5px 0;">TP Removal: <strong>{tp_removal:.1f}%</strong></p>
                    </div>
                """, unsafe_allow_html=True)
    
    with tab4:
        st.markdown("### Return on Investment Calculator")
        
        if compare_bio and (compare_turb or compare_diff):
            baseline_system = "Turbine" if compare_turb else "Diffused Air"
            baseline_perf = turb_perf if compare_turb else diff_perf
            
            monthly_savings = baseline_perf['monthly_cost_usd'] - bio_perf['monthly_cost_usd']
            annual_savings = monthly_savings * 12
            capital_difference = bio_perf['capital_cost'] - baseline_perf['capital_cost']
            
            if annual_savings > 0:
                payback_years = capital_difference / annual_savings if annual_savings != 0 else float('inf')
                
                st.markdown(f"""
                    <div class="savings-box">
                        <h2 style="color: white; margin: 0;">💰 Cost Savings</h2>
                        <h1 style="color: white; margin: 10px 0;">${monthly_savings:.2f}/month</h1>
                        <p style="color: white; font-size: 18px; margin: 0;">${annual_savings:.2f} per year</p>
                    </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                    <div style="background-color: #e3f2fd; padding: 20px; border-radius: 15px; border-left: 5px solid #2196f3;">
                        <h3 style="margin: 0 0 10px 0;">⏱️ Payback Period</h3>
                        <h1 style="color: #1976d2; margin: 0;">{payback_years:.1f} years</h1>
                        <p style="margin: 10px 0 0 0; color: #666;">
                            Additional capital investment of ${capital_difference:,.0f} pays back through operating savings
                        </p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class="warning-box">
                        <h3 style="color: white; margin: 0;">⚠️ Higher Operating Costs</h3>
                        <p style="color: white; font-size: 18px; margin: 10px 0 0 0;">
                            Operating costs are ${abs(monthly_savings):.2f}/month higher with BioSolutions
                        </p>
                    </div>
                """, unsafe_allow_html=True)
            
            # Show additional benefits
            st.markdown("#### Environmental Benefits")
            tn_improvement = baseline_perf['projected_tn_effluent'] - bio_perf['projected_tn_effluent']
            tp_improvement = baseline_perf['projected_tp_effluent'] - bio_perf['projected_tp_effluent']
            
            col1, col2 = st.columns(2)
            with col1:
                tn_pct = (tn_improvement / baseline_perf['projected_tn_effluent']) * 100
                st.metric(
                    "Additional TN Reduction", 
                    f"{tn_improvement:.1f} mg/L",
                    f"{tn_pct:.1f}% improvement",
                    delta_color="normal"
                )
            with col2:
                tp_pct = (tp_improvement / baseline_perf['projected_tp_effluent']) * 100
                st.metric(
                    "Additional TP Reduction", 
                    f"{tp_improvement:.1f} mg/L",
                    f"{tp_pct:.1f}% improvement",
                    delta_color="normal"
                )
        else:
            st.info("Select BioSolutions and at least one other system to see ROI analysis")
    
    # Sensitivity Analysis
    st.markdown("## 🔬 Sensitivity Analysis")
    st.markdown("See how system performance changes with different operating conditions")
    
    # Parameter selection with helpful descriptions
    param_descriptions = {
        "Flow Rate": {
            "desc": "How does changing facility size affect performance?",
            "affects": ["Cost", "Energy", "Nutrients"],
            "icon": "🌊"
        },
        "Energy Cost": {
            "desc": "What if electricity prices change?",
            "affects": ["Cost only"],
            "icon": "💰"
        },
        "Influent BOD": {
            "desc": "Higher pollution = more treatment needed",
            "affects": ["Energy", "Cost"],
            "icon": "🧪"
        },
        "Influent TN": {
            "desc": "How does nitrogen loading affect removal?",
            "affects": ["TN Effluent"],
            "icon": "🔬"
        },
        "Temperature": {
            "desc": "Seasonal temperature effects on biology",
            "affects": ["Nutrients", "Energy"],
            "icon": "🌡️"
        }
    }
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        sens_param = st.selectbox(
            "What do you want to analyze?",
            ["Flow Rate", "Energy Cost", "Influent BOD", "Influent TN", "Temperature"],
            help="Select which parameter to vary"
        )
        
        # Show what this parameter affects
        param_info = param_descriptions[sens_param]
        st.info(f"{param_info['icon']} **{param_info['desc']}**\n\nAffects: {', '.join(param_info['affects'])}")
    
    with col2:
        range_min = st.slider("Min % of current", 50, 100, 70)
    
    with col3:
        range_max = st.slider("Max % of current", 100, 200, 130)
    
    param_map = {
        "Flow Rate": ("basic_info.flow_rate_mgd", ["monthly_cost_usd", "monthly_energy_kwh", "projected_tn_effluent"]),
        "Energy Cost": ("current_aeration.energy_cost_per_kwh", ["monthly_cost_usd"]),
        "Influent BOD": ("influent_characteristics.bod5_mg_l", ["monthly_cost_usd", "monthly_energy_kwh"]),
        "Influent TN": ("influent_characteristics.tn_mg_l", ["projected_tn_effluent"]),
        "Temperature": ("influent_characteristics.temperature_celsius", ["projected_tn_effluent", "projected_tp_effluent"])
    }
    
    if st.button("🚀 Run Sensitivity Analysis", use_container_width=True):
        with st.spinner("Running analysis..."):
            param_path, relevant_metrics = param_map[sens_param]
            sens_results = sensitivity_analysis(
                facility_data, 
                param_path,
                (range_min/100, range_max/100)
            )
            
            # Define all possible metrics
            all_metrics = {
                'monthly_cost_usd': ('💰 Monthly Operating Cost', '$/month', 'LightGreen'),
                'monthly_energy_kwh': ('⚡ Monthly Energy Consumption', 'kWh/month', 'LightBlue'),
                'projected_tn_effluent': ('🌊 Total Nitrogen in Effluent', 'mg/L', 'LightCoral'),
                'projected_tp_effluent': ('🌊 Total Phosphorus in Effluent', 'mg/L', 'LightSalmon')
            }
            
            # Only plot metrics that actually change with this parameter
            st.markdown(f"### Results: How {sens_param} Affects Performance")
            
            for metric in relevant_metrics:
                if metric in all_metrics:
                    title, unit, area_color = all_metrics[metric]
                    
                    fig = go.Figure()
                    
                    # Get min/max for setting reference lines
                    all_values = []
                    
                    for system_name in sens_results['system'].unique():
                        system_data = sens_results[sens_results['system'] == system_name]
                        all_values.extend(system_data[metric].tolist())
                        
                        color_map = {
                            "BioSolutions DO Infusion": "#667eea", 
                            "Turbine Aeration": "#f093fb",
                            "Fine Bubble Diffused Air": "#38ef7d"
                        }
                        color = color_map.get(system_name, "#000000")
                        
                        # Convert hex to rgba for transparency
                        def hex_to_rgba(hex_color, opacity=0.2):
                            hex_color = hex_color.lstrip('#')
                            r = int(hex_color[0:2], 16)
                            g = int(hex_color[2:4], 16)
                            b = int(hex_color[4:6], 16)
                            return f'rgba({r},{g},{b},{opacity})'
                        
                        # Add area fill for better visibility
                        fig.add_trace(go.Scatter(
                            x=system_data['parameter_value'], 
                            y=system_data[metric],
                            name=system_name,
                            line=dict(color=color, width=4),
                            mode='lines',
                            fill='tonexty' if system_name != "BioSolutions DO Infusion" else None,
                            fillcolor=hex_to_rgba(color, 0.2) if system_name != "BioSolutions DO Infusion" else None
                        ))
                    
                    # Add current value marker
                    param_keys = param_path.split('.')
                    current_value = facility_data
                    for key in param_keys:
                        current_value = current_value[key]
                    
                    fig.add_vline(
                        x=current_value, 
                        line_dash="dash", 
                        line_color="red",
                        annotation_text="Current",
                        annotation_position="top"
                    )
                    
                    fig.update_layout(
                        title=f"<b>{title}</b>",
                        xaxis_title=f"{sens_param} {'($/kWh)' if 'Cost' in sens_param else ''}",
                        yaxis_title=unit,
                        height=450,
                        hovermode='x unified',
                        legend=dict(
                            orientation="h", 
                            yanchor="bottom", 
                            y=1.02, 
                            xanchor="right", 
                            x=1
                        ),
                        plot_bgcolor='rgba(240,240,240,0.5)',
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Add interpretation help
                    min_val, max_val = min(all_values), max(all_values)
                    change_pct = ((max_val - min_val) / min_val) * 100
                    
                    if change_pct > 5:  # Only show if there's meaningful change
                        st.markdown(f"""
                        <div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px; border-left: 4px solid #667eea;">
                            <strong>💡 What this means:</strong> 
                            If {sens_param.lower()} varies from {range_min}% to {range_max}% of current, 
                            this metric changes by up to <strong>{abs(change_pct):.1f}%</strong>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.success(f"✅ This metric is stable - not significantly affected by {sens_param}")
            
            # Show comparison table at current conditions
            st.markdown("### 📊 Quick Comparison at Current Conditions")
            
            current_comparison = sens_results[
                (sens_results['multiplier'] >= 0.99) & 
                (sens_results['multiplier'] <= 1.01)
            ][['system', 'monthly_cost_usd', 'monthly_energy_kwh', 
               'projected_tn_effluent', 'projected_tp_effluent']]
            
            if not current_comparison.empty:
                current_comparison.columns = ['System', 'Monthly Cost ($)', 'Energy (kWh/mo)', 
                                             'TN (mg/L)', 'TP (mg/L)']
                st.dataframe(
                    current_comparison.style.format({
                        'Monthly Cost ($)': '${:,.2f}',
                        'Energy (kWh/mo)': '{:,.0f}',
                        'TN (mg/L)': '{:.2f}',
                        'TP (mg/L)': '{:.2f}'
                    }),
                    use_container_width=True,
                    hide_index=True
                )
    
    # Summary table
    st.markdown("## 📋 Summary Table")
    
    summary_display = comparison_df.copy()
    summary_display.columns = ['System', 'Monthly Cost ($)', 'Monthly Energy (kWh)', 
                               'TN (mg/L)', 'TP (mg/L)', 'Capital Cost ($)', 'Footprint (sq ft)']
    
    st.dataframe(
        summary_display.style.format({
            'Monthly Cost ($)': '${:,.2f}',
            'Monthly Energy (kWh)': '{:,.0f}',
            'TN (mg/L)': '{:.2f}',
            'TP (mg/L)': '{:.2f}',
            'Capital Cost ($)': '${:,.0f}',
            'Footprint (sq ft)': '{:,.0f}'
        }),
        use_container_width=True,
        height=200
    )
    
    # Export section
    st.markdown("## 📥 Export Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Generate text report
        report_text = generate_pdf_report(facility_data, selected_systems, comparison_df)
        st.download_button(
            label="📄 Download Text Report",
            data=report_text,
            file_name=f"aeration_comparison_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    with col2:
        # CSV export
        csv = comparison_df.to_csv(index=False)
        st.download_button(
            label="📊 Download Data (CSV)",
            data=csv,
            file_name=f"aeration_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: #6e6e73; padding: 20px;'>
            <p style='margin: 5px 0;'>
                <strong>Developed by BioSolutions</strong> | 
                Data based on Greenleaf WWTP case study
            </p>
            <p style='margin: 5px 0;'>
                📧 <a href='mailto:info@biosolutions.com' style='color: #667eea;'>info@biosolutions.com</a> | 
                🌐 <a href='https://biosolutions.com' style='color: #667eea;'>www.biosolutions.com</a>
            </p>
            <p style='margin: 15px 0 5px 0; font-size: 12px; color: #999;'>
                © 2025 BioSolutions. All rights reserved. | Version 1.0
            </p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
