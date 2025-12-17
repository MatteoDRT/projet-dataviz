"""
Streamlit Application - Poubelles-Propres Franchise Zone Analysis
Interactive dashboard for identifying optimal franchise zones in France
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_folium import st_folium
import config
import utils
from data_collector import get_data_collector
from zone_analyzer import ZoneAnalyzer
import map_viz


# Page configuration
st.set_page_config(
    page_title="Poubelles-Propres - Analyse de Zones",
    page_icon="🗑️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E7D32;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2E7D32;
    }
    .top-zone {
        background-color: #E8F5E9;
        padding: 0.5rem;
        border-radius: 0.3rem;
        margin-bottom: 0.5rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f2f6;
        border-radius: 4px 4px 0 0;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2E7D32;
        color: white;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    """Load and cache data"""
    collector = get_data_collector()
    data = collector.get_all_data()
    return data


@st.cache_data
def analyze_zones(_data, max_radius):
    """Analyze and score zones"""
    analyzer = ZoneAnalyzer(_data)
    zones = analyzer.create_zones(max_radius_km=max_radius)
    scored_zones = analyzer.calculate_scores()
    return scored_zones  # Only return serializable DataFrame


def main():
    """Main application"""
    
    # Header
    st.markdown('<h1 class="main-header">🗑️ Poubelles-Propres</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Analyse des Zones de Franchise Potentielles en France</p>', unsafe_allow_html=True)
    
    # Sidebar - Configuration
    st.sidebar.header("⚙️ Configuration")
    
    # Load data
    with st.spinner("Chargement des données INSEE..."):
        data = load_data()
    
    # Sidebar filters
    st.sidebar.subheader("Paramètres de Zone")
    max_radius = st.sidebar.slider(
        "Rayon maximum de zone (km)",
        min_value=10,
        max_value=50,
        value=config.MAX_ZONE_RADIUS_KM,
        step=5,
        help="Distance maximale pour regrouper les communes"
    )
    
    min_households = st.sidebar.number_input(
        "Minimum de ménages par zone",
        min_value=500,
        max_value=50000,
        value=config.MIN_HOUSEHOLDS,
        step=500,
        help="Nombre minimum de ménages requis"
    )
    
    st.sidebar.subheader("Critères de Filtrage")
    min_houses_pct = st.sidebar.slider(
        "% minimum de maisons individuelles",
        min_value=0,
        max_value=100,
        value=config.TARGET_CRITERIA['min_pct_maisons'],
        step=5,
        help="Pourcentage minimum de maisons (vs appartements)"
    )
    
    min_income_percentile = st.sidebar.slider(
        "Niveau de revenu minimum",
        min_value=0,
        max_value=100,
        value=config.TARGET_CRITERIA['min_income_percentile'],
        step=10,
        help="Percentile de revenu minimum (50 = médiane nationale)"
    )
    
    # Update config with user inputs
    config.MAX_ZONE_RADIUS_KM = max_radius
    config.MIN_HOUSEHOLDS = min_households
    config.TARGET_CRITERIA['min_pct_maisons'] = min_houses_pct
    config.TARGET_CRITERIA['min_income_percentile'] = min_income_percentile
    
    # Analyze zones
    with st.spinner("Analyse des zones en cours..."):
        scored_zones = analyze_zones(data, max_radius)
    
    # Check if we have results
    if len(scored_zones) == 0:
        st.error("Aucune zone ne correspond aux critères sélectionnés. Essayez d'assouplir les filtres.")
        return
    
    # Display number of zones filter
    st.sidebar.subheader("Affichage")
    
    # Adjust slider range based on available zones
    if len(scored_zones) >= 10:
        # Normal case: enough zones for a proper slider
        top_n = st.sidebar.slider(
            "Nombre de zones à afficher",
            min_value=10,
            max_value=min(100, len(scored_zones)),
            value=min(50, len(scored_zones)),
            step=10,
            help="Nombre de meilleures zones à visualiser"
        )
    elif len(scored_zones) > 1:
        # Few zones: use all available as range
        top_n = st.sidebar.slider(
            "Nombre de zones à afficher",
            min_value=1,
            max_value=len(scored_zones),
            value=len(scored_zones),
            step=1,
            help="Nombre de meilleures zones à visualiser"
        )
    else:
        # Only one zone or none
        top_n = len(scored_zones)
        st.sidebar.info(f"Affichage de {top_n} zone(s) disponible(s)")
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Vue d'ensemble", "🗺️ Carte Interactive", "🏆 Top Zones", "📈 Analyses"])
    
    # Tab 1: Overview
    with tab1:
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Zones identifiées",
                value=len(scored_zones),
                help="Nombre total de zones respectant les critères"
            )
        
        with col2:
            avg_score = scored_zones['score_total'].mean()
            st.metric(
                label="Score moyen",
                value=f"{avg_score:.1f}/100",
                help="Score moyen de toutes les zones"
            )
        
        with col3:
            total_households = scored_zones['nb_menages'].sum()
            st.metric(
                label="Ménages totaux",
                value=utils.format_number(total_households),
                help="Total de ménages dans toutes les zones"
            )
        
        with col4:
            total_potential = scored_zones['potential_clients'].sum()
            st.metric(
                label="Clients potentiels",
                value=utils.format_number(total_potential, 0),
                help=f"Estimation basée sur {config.TARGET_CONVERSION_RATE*100}% de conversion"
            )
        
        st.markdown("---")
        
        # Overview charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Score distribution
            fig_dist = map_viz.create_score_distribution(scored_zones)
            st.plotly_chart(fig_dist, use_container_width=True)
        
        with col2:
            # Regional distribution
            fig_regional = map_viz.create_regional_bar_chart(scored_zones, top_n=top_n)
            st.plotly_chart(fig_regional, use_container_width=True)
        
        # Top 20 zones quick view
        st.subheader("🏆 Top 20 Zones par Score")
        top_20 = scored_zones.head(20)[['rank', 'nom_commune', 'region', 'nb_communes', 
                                         'nb_menages', 'potential_clients', 'score_total']]
        top_20_display = top_20.copy()
        top_20_display['nb_menages'] = top_20_display['nb_menages'].apply(lambda x: utils.format_number(x))
        top_20_display['potential_clients'] = top_20_display['potential_clients'].apply(lambda x: utils.format_number(x, 0))
        top_20_display['score_total'] = top_20_display['score_total'].apply(lambda x: f"{x:.1f}")
        top_20_display.columns = ['Rang', 'Communes (échantillon)', 'Région', 'Nb Communes', 
                                  'Ménages', 'Clients Pot.', 'Score']
        
        st.dataframe(top_20_display, use_container_width=True, hide_index=True)
    
    # Tab 2: Interactive Map
    with tab2:
        st.subheader(f"🗺️ Carte des {top_n} Meilleures Zones")
        
        # Map type selection
        map_type = st.radio(
            "Type de carte",
            options=["Carte interactive (Folium)", "Carte scatter (Plotly)", "Heatmap"],
            horizontal=True
        )
        
        if map_type == "Carte interactive (Folium)":
            folium_map = map_viz.create_zone_map(scored_zones, top_n=top_n)
            st_folium(folium_map, width=1200, height=700)
            
        elif map_type == "Carte scatter (Plotly)":
            plotly_map = map_viz.create_plotly_scatter_map(scored_zones, top_n=top_n)
            st.plotly_chart(plotly_map, use_container_width=True)
            
        else:  # Heatmap
            heatmap = map_viz.create_heatmap(scored_zones.head(top_n))
            st_folium(heatmap, width=1200, height=700)
        
        st.info("💡 Cliquez sur les marqueurs pour voir les détails de chaque zone")
    
    # Tab 3: Top Zones Detailed View
    with tab3:
        st.subheader("🏆 Détails des Meilleures Zones")
        
        # Display top zones with detailed information
        for idx, zone in scored_zones.head(20).iterrows():
            with st.expander(f"#{int(zone['rank'])} - {zone['nom_commune']} ({zone['region']}) - Score: {zone['score_total']:.1f}/100"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("### 📍 Informations Générales")
                    st.write(f"**Région:** {zone['region']}")
                    st.write(f"**Département:** {zone['code_departement']}")
                    st.write(f"**Nombre de communes:** {int(zone['nb_communes'])}")
                    st.write(f"**Population totale:** {utils.format_number(zone['population_totale'])}")
                    st.write(f"**Nombre de ménages:** {utils.format_number(zone['nb_menages'])}")
                
                with col2:
                    st.markdown("### 🏠 Logements")
                    st.write(f"**Maisons individuelles:** {zone['pct_maisons']:.1f}%")
                    st.write(f"**Résidences principales:** {zone['pct_residences_principales']:.1f}%")
                
                with col3:
                    st.markdown("### 💰 Revenus & Potentiel")
                    st.write(f"**Revenu médian:** {utils.format_number(zone['revenu_median'], 0)}€")
                    st.write(f"**Niveau de vie médian:** {utils.format_number(zone['niveau_vie_median'], 0)}€")
                    st.write(f"**Taux de pauvreté:** {zone['taux_pauvrete']:.1f}%")
                    st.write(f"**Clients potentiels:** {utils.format_number(zone['potential_clients'], 0)}")
                
                # Score breakdown
                st.markdown("### 📊 Détail des Scores")
                score_cols = st.columns(3)
                with score_cols[0]:
                    st.metric("Logement", f"{zone['score_housing']:.1f}/100")
                with score_cols[1]:
                    st.metric("Revenus", f"{zone['score_income']:.1f}/100")
                with score_cols[2]:
                    st.metric("Taille marché", f"{zone['score_market_size']:.1f}/100")
    
    # Tab 4: Analysis
    with tab4:
        st.subheader("📈 Analyses Complémentaires")
        
        # Score components correlation
        st.markdown("### Corrélation entre les Composantes du Score")
        score_cols = ['score_housing', 'score_income', 'score_market_size', 'score_total']
        corr_matrix = scored_zones[score_cols].corr()
        
        fig_corr = px.imshow(
            corr_matrix,
            labels=dict(x="Composante", y="Composante", color="Corrélation"),
            x=['Logement', 'Revenus', 'Taille', 'Total'],
            y=['Logement', 'Revenus', 'Taille', 'Total'],
            color_continuous_scale='RdYlGn',
            aspect='auto'
        )
        fig_corr.update_layout(height=500)
        st.plotly_chart(fig_corr, use_container_width=True)
        
        # Scatter plots
        st.markdown("### Relations entre Variables Clés")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_scatter1 = px.scatter(
                scored_zones.head(50),
                x='revenu_median',
                y='score_total',
                size='nb_menages',
                color='region',
                hover_data=['nom_commune', 'rank'],
                title='Score vs Revenu Médian',
                labels={'revenu_median': 'Revenu Médian (€)', 'score_total': 'Score Total'}
            )
            st.plotly_chart(fig_scatter1, use_container_width=True)
        
        with col2:
            fig_scatter2 = px.scatter(
                scored_zones.head(50),
                x='pct_maisons',
                y='score_total',
                size='nb_menages',
                color='region',
                hover_data=['nom_commune', 'rank'],
                title='Score vs % Maisons Individuelles',
                labels={'pct_maisons': '% Maisons Individuelles', 'score_total': 'Score Total'}
            )
            st.plotly_chart(fig_scatter2, use_container_width=True)
        
        # Export data
        st.markdown("### 💾 Export des Données")
        
        # Prepare export data
        export_data = scored_zones[[
            'rank', 'zone_id', 'nom_commune', 'region', 'code_departement',
            'nb_communes', 'nb_menages', 'population_totale', 'potential_clients',
            'pct_maisons', 'pct_residences_principales', 'revenu_median',
            'score_housing', 'score_income', 'score_market_size', 'score_total',
            'latitude', 'longitude'
        ]].copy()
        
        # Download button
        csv = export_data.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Télécharger les résultats (CSV)",
            data=csv,
            file_name='poubelles_propres_zones_analyse.csv',
            mime='text/csv',
        )
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p><b>Poubelles-Propres.fr</b> - Analyse de Zones de Franchise</p>
        <p style="font-size: 0.9rem;">Données: INSEE | Scoring basé sur: Logements (40%), Revenus (30%), Taille marché (30%)</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
