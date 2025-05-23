import streamlit as st
import pandas as pd
import plotly.express as px
from ta.trend import SMAIndicator, EMAIndicator
from ta.momentum import RSIIndicator, StochasticOscillator
import plotly.graph_objects as go
from ta.volatility import BollingerBands
from ta.trend import MACD
from ta.momentum import ROCIndicator, StochRSIIndicator
from ta.trend import CCIIndicator

# Configuration de la page
st.set_page_config(page_title="Investor Dashboard", page_icon="💰", layout="wide")
st.markdown("""
<style>
    /* Styles globaux */
    body {
        font-family: 'Arial', sans-serif;
        background-color: #f9f9f9;
    }
    .main-container {
        padding: 20px;
    }
    .section {
        border: 1px solid #e6e6e6;
        border-radius: 8px;
        padding: 20px;
        margin: 20px 0;
        background-color: #fff;
    }
    .section-title {
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 10px;
        color: #2e7d32;
    }
    .section-content {
        display: flex;
        flex-wrap: wrap;
        gap: 20px;
    }
    .indicator-card {
        border: 1px solid #e6e6e6;
        border-radius: 8px;
        padding: 10px;
        width: 30%;
        background-color: #f5f5f5;
    }
    .indicator-card h5 {
        margin: 0;
        color: #333;
    }
    .indicator-card p {
        margin: 5px 0;
    }
    .eval-card {
        border: 1px solid #e6e6e6;
        border-radius: 8px;
        padding: 10px;
        background-color: #fff;
    }
    .executive-summary {
        border: 2px solid #4CAF50;
        border-radius: 8px;
        padding: 20px;
        margin: 20px 0;
        background-color: #e8f5e9;
        color: #2e7d32;
    }
    .exec-summary-title {
        font-size: 24px;
        font-weight: bold;
        color: #2e7d32;
    }
    .exec-summary-content {
        font-size: 18px;
    }
    footer {
        position: fixed;
        width: 100%;
        bottom: 0;
        background-color: white;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>💰Tableau de Bord de l'investisseur 💰</h1>", unsafe_allow_html=True)

# Zone de sélection du marché
st.markdown("#### Sélectionnez le marché")
market = st.selectbox("Marché:", ["BRVM"], index=0, help="Sélectionnez le marché pour afficher les données correspondantes.")

# Section de sélection de l'action
st.markdown("#### Sélectionnez l'action à analyser")
if 'max_columns' in st.session_state:
    # Exclure la colonne 'Date' des options
    options = [col for col in st.session_state['max_columns'] if col != 'Date']
    action = st.selectbox("Action :", options, help="Sélectionnez le marché pour afficher les données correspondantes")
else:
    st.error("Les noms des colonnes n'ont pas été chargés. Veuillez d'abord charger le fichier sur la page de données.")

# Définition des proportions pour les colonnes : les trois colonnes sont de même taille
col1, col2, col3 = st.columns([1, 1, 1])

# Ajout d'un contenu dans la première colonne : Analyse Technique
with col1:
    st.markdown("<div class='section-title'>📈 Analyse Technique</div>", unsafe_allow_html=True)
    if 'max_columns' in st.session_state and action:
        # Chargement et préparation des données
        data = pd.read_excel(st.session_state['uploaded_file'], sheet_name='COURS')
        data = data[::-1]  # Inverser si nécessaire
        data['Date'] = pd.to_datetime(data['Date'])
        filtered_data = data[data['Date'].dt.year >= 2021]

        ouverture_data = pd.read_excel(st.session_state['uploaded_file'], sheet_name='OUVERTURE')
        ouverture_data['Date'] = pd.to_datetime(ouverture_data['Date'])

        max_data = pd.read_excel(st.session_state['uploaded_file'], sheet_name='MAX')
        max_data['Date'] = pd.to_datetime(max_data['Date'])

        min_data = pd.read_excel(st.session_state['uploaded_file'], sheet_name='MIN')
        min_data['Date'] = pd.to_datetime(min_data['Date'])

        # Supprimer les valeurs nulles dans la colonne Date
        filtered_data.dropna(subset=['Date'], inplace=True)
        ouverture_data.dropna(subset=['Date'], inplace=True)
        max_data.dropna(subset=['Date'], inplace=True)
        min_data.dropna(subset=['Date'], inplace=True)

        # Aligner les données par date
        merged_data = pd.merge(filtered_data, ouverture_data, on='Date', suffixes=('', '_open'))
        merged_data = pd.merge(merged_data, max_data, on='Date', suffixes=('', '_max'))
        merged_data = pd.merge(merged_data, min_data, on='Date', suffixes=('', '_min'))

        # Renommer les colonnes pour plus de clarté
        merged_data.rename(columns={
            action: 'Close',
            f'{action}_open': 'Open',
            f'{action}_max': 'High',
            f'{action}_min': 'Low'
        }, inplace=True)

        # Vérifier et nettoyer les données
        valid_indices = (
            (merged_data['High'] >= merged_data['Low']) &
            (merged_data['Open'].between(merged_data['Low'], merged_data['High'])) &
            (merged_data['Close'].between(merged_data['Low'], merged_data['High']))
        )

        valid_data = merged_data[valid_indices]

    # Utilisation des onglets pour différents indicateurs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs(["Cours", "Volume", "RSI", "MACD", "Moyennes Mobiles", "Bandes de Bollinger", "EMA", "ROC", "Momentum"])

    with tab1:
        # Tracer le graphique de l'action sélectionnée en bougie
        fig = go.Figure(data=[go.Candlestick(
            x=valid_data['Date'],
            open=valid_data['Open'],
            high=valid_data['High'],
            low=valid_data['Low'],
            close=valid_data['Close'],
            increasing_line_color='green',
            decreasing_line_color='red'
        )])
        fig.update_layout(
            xaxis_title='Date',
            yaxis_title='Prix',
            height=400,
            margin=dict(l=10, r=10, t=10, b=10),  # Réduire les marges
            xaxis=dict(
                rangeslider=dict(visible=False),  # Supprimer le petit graphique avant la date
            ),
            template='plotly_white'
        )
        st.plotly_chart(fig, use_container_width=True)


    with tab2:
        # Tracer le graphique du volume
        volume_data = pd.read_excel(st.session_state['uploaded_file'], sheet_name='VOLUME')
        volume_data['Date'] = pd.to_datetime(volume_data['Date'])
        filtered_volume_data = volume_data[volume_data['Date'].dt.year >= 2018]
        fig = px.bar(filtered_volume_data, x='Date', y=action, color_discrete_sequence=['red'], labels={action: "Volume"}, height=400)
        fig.update_layout(margin=dict(l=10, r=10, t=10, b=10))  # Réduire les marges
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        # Calculer le RSI pour la période de 14 jours
        rsi = RSIIndicator(filtered_data[action], window=14).rsi()

        # Tracer le RSI sur un nouveau graphique
        fig_rsi = px.line(filtered_data, x='Date', y=rsi)
        fig_rsi.update_layout(
            xaxis_title='Date',
            yaxis_title='RSI ',
            yaxis=dict(
                range=[0, 100],  # Typique pour RSI pour voir les niveaux de surachat (>70) et de survente (<30)
                title='RSI (14)'
            ),
            template='plotly_white', height=400,
            margin=dict(l=10, r=10, t=10, b=10)  # Réduire les marges
        )
        st.plotly_chart(fig_rsi, use_container_width=True)

    with tab4:
        # Calculer le MACD
        macd_indicator = MACD(close=filtered_data[action], window_slow=26, window_fast=12, window_sign=9)
        macd_line = macd_indicator.macd()
        signal_line = macd_indicator.macd_signal()
        histogram = macd_indicator.macd_diff()

        # Créer un nouveau graphique pour le MACD
        fig = go.Figure()

        # Ajouter la ligne MACD
        fig.add_trace(go.Scatter(x=filtered_data['Date'], y=macd_line, mode='lines', name='MACD Line', line=dict(color='blue')))

        # Ajouter la ligne de signal
        fig.add_trace(go.Scatter(x=filtered_data['Date'], y=signal_line, mode='lines', name='Signal Line', line=dict(color='red')))

        # Ajouter l'histogramme avec des couleurs conditionnelles
        colors = ['red' if val < 0 else 'green' for val in histogram]
        fig.add_trace(go.Bar(x=filtered_data['Date'], y=histogram, name='Histogram', marker_color=colors))

        # Configurer la légende pour qu'elle soit en haut et horizontale
        fig.update_layout(
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,  # Légèrement au-dessus du haut du graphique
                xanchor='right',
                x=1
            ),
            xaxis_title='Date',
            yaxis_title='MACD and Signal',
            yaxis=dict(
                title='MACD and Signal'
            ),
            yaxis2=dict(
                title='Histogram',
                overlaying='y',
                side='right',
                showgrid=False,  # Désactiver la grille pour l'axe secondaire
            ),
            template='plotly_white', height=400,
            margin=dict(l=10, r=10, t=10, b=10)  # Réduire les marges
        )

        # Afficher le graphique dans Streamlit
        st.plotly_chart(fig, use_container_width=True)

    with tab5:
        # Calculer les Moyennes Mobiles
        sma_7 = SMAIndicator(valid_data['Close'], window=7).sma_indicator()
        sma_21 = SMAIndicator(valid_data['Close'], window=21).sma_indicator()
        sma_100 = SMAIndicator(valid_data['Close'], window=100).sma_indicator()

        # Tracer le graphique de l'action sélectionnée en bougie avec les Moyennes Mobiles
        fig = go.Figure(data=[go.Candlestick(
            x=valid_data['Date'],
            open=valid_data['Open'],
            high=valid_data['High'],
            low=valid_data['Low'],
            close=valid_data['Close'],
            increasing_line_color='green',
            decreasing_line_color='red',
            name=action
        )])

        # Ajouter les Moyennes Mobiles avec des lignes plus épaisses et des couleurs plus visibles
        #fig.add_trace(go.Scatter(x=valid_data['Date'], y=sma_7, mode='lines', name='SMA 7', line=dict(color='blue', width=1)))
        fig.add_trace(go.Scatter(x=valid_data['Date'], y=sma_21, mode='lines', name='SMA 21', line=dict(color='purple', width=1)))
        fig.add_trace(go.Scatter(x=valid_data['Date'], y=sma_100, mode='lines', name='SMA 100', line=dict(color='orange', width=1)))

        # Mise à jour de la mise en page pour inclure une légende horizontale en haut et supprimer le graphique en miniature
        fig.update_layout(
            legend=dict(
                title='Indicateurs',
                orientation='h',
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            xaxis_title='Date',
            yaxis_title='Prix',
            template='plotly_white',
            height=400,
            xaxis=dict(
                rangeslider=dict(visible=False)  # Supprimer le graphique en miniature en bas
            ),
            margin=dict(l=10, r=10, t=10, b=10)  # Réduire les marges
        )

        # Afficher le graphique final avec les moyennes mobiles
        st.plotly_chart(fig, use_container_width=True)

    with tab6:
        # Calculer les Bandes de Bollinger pour la fenêtre de 20 jours et 2 écarts-types
        bb_indicator = BollingerBands(close=filtered_data[action], window=20, window_dev=2)
        bb_high_band = bb_indicator.bollinger_hband()
        bb_low_band = bb_indicator.bollinger_lband()
        bb_mid_band = bb_indicator.bollinger_mavg()

        # Tracer le graphique de l'action sélectionnée en bougie avec les Bandes de Bollinger
        fig_bb = go.Figure(data=[go.Candlestick(
            x=valid_data['Date'],
            open=valid_data['Open'],
            high=valid_data['High'],
            low=valid_data['Low'],
            close=valid_data['Close'],
            increasing_line_color='green',
            decreasing_line_color='red',
            name=action
        )])

        # Ajouter les Bandes de Bollinger avec des lignes plus épaisses et des couleurs plus visibles
        fig_bb.add_trace(go.Scatter(x=filtered_data['Date'], y=bb_high_band, name='Bande Supérieure', line=dict(color='blue', width=1)))
        fig_bb.add_trace(go.Scatter(x=filtered_data['Date'], y=bb_low_band, name='Bande Inférieure', line=dict(color='purple', width=1)))
        fig_bb.add_trace(go.Scatter(x=filtered_data['Date'], y=bb_mid_band, name='Bande Moyenne', line=dict(color='orange', width=1)))

        # Mise à jour de la mise en page pour inclure une légende horizontale en haut et supprimer le graphique en miniature
        fig_bb.update_layout(
            legend=dict(
                title='Indicateurs',
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='right',
                x=1
            ),
            xaxis_title='Date',
            yaxis_title='Prix',
            template='plotly_white',
            height=400,
            xaxis=dict(
                rangeslider=dict(visible=False)  # Supprimer le graphique en miniature en bas
            ),
            margin=dict(l=10, r=10, t=10, b=10)  # Réduire les marges
        )

        # Afficher le graphique final avec les Bandes de Bollinger
        st.plotly_chart(fig_bb, use_container_width=True)

    with tab7:
        # Calculer les Moyennes Mobiles Exponentielles (EMA)
        ema_14 = EMAIndicator(valid_data['Close'], window=14).ema_indicator()
        ema_100 = EMAIndicator(valid_data['Close'], window=100).ema_indicator()

        # Tracer le graphique de l'action sélectionnée en bougie avec les Moyennes Mobiles Exponentielles
        fig = go.Figure(data=[go.Candlestick(
            x=valid_data['Date'],
            open=valid_data['Open'],
            high=valid_data['High'],
            low=valid_data['Low'],
            close=valid_data['Close'],
            increasing_line_color='green',
            decreasing_line_color='red',
            name=action
        )])

        # Ajouter les Moyennes Mobiles Exponentielles avec des lignes plus épaisses et des couleurs plus visibles
        fig.add_trace(go.Scatter(x=valid_data['Date'], y=ema_14, mode='lines', name='EMA 14', line=dict(color='blue', width=1)))
        fig.add_trace(go.Scatter(x=valid_data['Date'], y=ema_100, mode='lines', name='EMA 100', line=dict(color='purple', width=1)))

        # Mise à jour de la mise en page pour inclure une légende horizontale en haut et supprimer le graphique en miniature
        fig.update_layout(
            legend=dict(
                title='Indicateurs',
                orientation='h',
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1 
            ),
            xaxis_title='Date',
            yaxis_title='Prix',
            template='plotly_white',
            height=400,
            xaxis=dict(
                rangeslider=dict(visible=False)  # Supprimer le graphique en miniature en bas
            ),
            margin=dict(l=10, r=10, t=10, b=10)  # Réduire les marges
        )

        # Afficher le graphique final avec les moyennes mobiles exponentielles
        st.plotly_chart(fig, use_container_width=True)


    with tab8:
        # Calculer le ROC pour une période de 12 jours
        roc_indicator = ROCIndicator(close=filtered_data[action], window=12)
        roc = roc_indicator.roc()

        # Tracer le ROC sur un nouveau graphique
        fig_roc = px.line(filtered_data, x='Date', y=roc)
        fig_roc.update_layout(
            xaxis_title='Date',
            yaxis_title='ROC',
            template='plotly_white',
            height=400,
            margin=dict(l=10, r=10, t=10, b=10)  # Réduire les marges
        )
        st.plotly_chart(fig_roc, use_container_width=True)

    with tab9:
        # Calculer le Momentum pour une période de 10 jours
        momentum_indicator = SMAIndicator(filtered_data[action], window=10)  # Utilisation de SMA comme proxy pour le momentum
        momentum = momentum_indicator.sma_indicator()

        # Tracer le Momentum sur un nouveau graphique
        fig_momentum = px.line(filtered_data, x='Date', y=momentum)
        fig_momentum.update_layout(
            xaxis_title='Date',
            yaxis_title='Momentum',
            template='plotly_white',
            height=400,
            margin=dict(l=10, r=10, t=10, b=10)  # Réduire les marges
        )
        st.plotly_chart(fig_momentum, use_container_width=True)

with col2:
    st.markdown("<div class='section-title'>📊 Analyse Fondamentale</div>", unsafe_allow_html=True)
    if 'uploaded_file' in st.session_state and action:
        indices_data = pd.read_excel(st.session_state['uploaded_file'], sheet_name='INDICES')
        
        if action in indices_data.columns:
            indices_list = indices_data[action].dropna().tolist()
            
            if indices_list:
                # Utilisation des onglets pour les indices
                tab1, *tabs = st.tabs(["Indice vs Action"] + [str(idx) for idx in indices_list])
                
                with tab1:
                    # Comparaison de l'action avec les indices associés
                    indices_data = pd.read_excel(st.session_state['uploaded_file'], sheet_name='INDICES')
                    if action in indices_data.columns:
                        indices_list = indices_data[action].dropna().tolist()
                        
                        if indices_list:
                            # Trouver la date de début la plus récente parmi les indices
                            latest_start_date = filtered_data['Date'].min()
                            for idx in indices_list:
                                if idx in filtered_data.columns:
                                    idx_start_date = filtered_data[['Date', idx]].dropna()['Date'].min()
                                    if idx_start_date > latest_start_date:
                                        latest_start_date = idx_start_date
                            
                            # Filtrer les données pour commencer à la date de début la plus récente
                            filtered_data = filtered_data[filtered_data['Date'] >= latest_start_date]

                            fig = go.Figure()
                            fig.add_trace(go.Scatter(x=filtered_data['Date'], y=filtered_data[action], mode='lines', name=action, line=dict(color='blue')))

                            for idx in indices_list:
                                if idx in filtered_data.columns:
                                    fig.add_trace(go.Scatter(x=filtered_data['Date'], y=filtered_data[idx], mode='lines', name=idx, yaxis="y2"))
                            
                            fig.update_layout(
                                xaxis_title='Date',
                                yaxis_title='Prix de l\'action',
                                yaxis2=dict(
                                    title='Valeur des indices',
                                    overlaying='y',
                                    side='right'
                                ),
                                template='plotly_white',
                                height=400,
                                margin=dict(l=10, r=10, t=10, b=10),  # Réduire les marges
                                legend=dict(
                                    orientation='h',
                                    yanchor='bottom',
                                    y=1.02,
                                    xanchor='right',
                                    x=1
                                )
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.write(f"Aucun indice trouvé pour l'action {action}.")
                    else:
                        st.write(f"L'action {action} n'est pas trouvée dans la feuille 'INDICES'.")
                
                for i, tab in enumerate(tabs):
                    with tab:
                        selected_index = indices_list[i]
                        cours_data = pd.read_excel(st.session_state['uploaded_file'], sheet_name='COURS')
                        cours_data['Date'] = pd.to_datetime(cours_data['Date'])
                        
                        if selected_index in cours_data.columns:
                            valid_dates = cours_data[cours_data[selected_index].notna()]['Date']
                            if not valid_dates.empty:
                                date_debut = valid_dates.min()
                                filtered_data = cours_data[cours_data['Date'] >= date_debut]

                                indice_cours = filtered_data[selected_index]
                                df_to_plot = pd.DataFrame({
                                    'Date': filtered_data['Date'],
                                    selected_index: indice_cours
                                })

                                fig = px.line(df_to_plot, x='Date', y=selected_index, height=340)
                                fig.update_layout(height=400,
                                    margin=dict(l=10, r=10, t=10, b=10)  # Réduire les marges
                                )
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.error(f"Aucune donnée valide trouvée pour l'indice {selected_index}.")
                        else:
                            st.error(f"L'indice {selected_index} n'est pas trouvé dans la feuille 'COURS'.")
            else:
                st.write(f"Aucun indice trouvé pour l'action {action}.")
        else:
            st.write(f"L'action {action} n'est pas trouvée dans la feuille 'INDICES'.")

with col3:     
    # Section Profil
    st.markdown("<div class='section-title'>🏢 Profil</div>", unsafe_allow_html=True)
    if 'uploaded_file' in st.session_state and action:
        profile_data = pd.read_excel(st.session_state['uploaded_file'], sheet_name='Profil', header=0)
        
        # Ensure the first column is the index
        profile_data.set_index(profile_data.columns[0], inplace=True)
        
        # Find the column for the selected action
        if action in profile_data.columns:
            # Display the second row (Company Profile)
            profile_info = profile_data.iloc[0]
            company_profile = profile_info[action]
            
            # Add space before displaying the profile text
            st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: justify;'>{company_profile}</p>", unsafe_allow_html=True)
        else:
            st.error(f"L'action {action} n'est pas trouvée dans la feuille 'Profil'.")

        st.markdown("""
    <div class='section-title' style='text-align: center; color: black; font-size: 20px;'>📋 Informations</div>
    """, unsafe_allow_html=True)
    
    if 'uploaded_file' in st.session_state and action:
        profile_data = pd.read_excel(st.session_state['uploaded_file'], sheet_name='Profil 1', header=0)
        profile_data.set_index(profile_data.columns[0], inplace=True)
        
        if action in profile_data.columns:
            # Split the dataframe into two halves
            stats_for_action = profile_data[[action]].dropna()
            stats_for_action_first_half = stats_for_action.iloc[:4]
            stats_for_action_second_half = stats_for_action.iloc[4:]
            
            col1, col2 = st.columns(2)
            
            # Display the first half of the stats in the first column
            with col1:
                for stat_name, value in stats_for_action_first_half[action].items():
                    st.markdown(f"<div style='margin-bottom: 10px;'><strong>{stat_name}</strong>: {value if pd.notna(value) else '-'}</div>", unsafe_allow_html=True)
            
            # Display the second half of the stats in the second column
            with col2:
                for stat_name, value in stats_for_action_second_half[action].items():
                    st.markdown(f"<div style='margin-bottom: 10px;'><strong>{stat_name}</strong>: {value if pd.notna(value) else '-'}</div>", unsafe_allow_html=True)
        else:
            st.error(f"L'action {action} n'est pas trouvée dans la feuille 'Profil 1'.")

# Ajout de contenu dans les colonnes: Indicateurs Techniques, Statistiques Clés et Méthodes d'Évaluation
indicateurs_tech_col, stats_cle_col, eval_methods_col = st.columns(3)

with indicateurs_tech_col:
    st.markdown("<div class='section-title'>🧩 Indicateurs Techniques</div>", unsafe_allow_html=True)

    # Création d'une liste pour contenir les signaux
    signals = []

    # Moyennes Mobiles
    sma_7 = SMAIndicator(filtered_data[action], window=7).sma_indicator()
    sma_21 = SMAIndicator(filtered_data[action], window=21).sma_indicator()
    sma_100 = SMAIndicator(filtered_data[action], window=100).sma_indicator()
    last_price = filtered_data[action].iloc[-1]
        
    # Signaux pour les moyennes mobiles
    signals.extend([
            {
                'Nom': 'Moyenne Mobile (7)',
                'Valeur': round(sma_7.iloc[-1],2),
                'Action': 'Acheter' if sma_7.iloc[-1] < last_price else 'Vendre' if sma_7.iloc[-1] > last_price else 'Neutre'
            },
            {
                'Nom': 'Moyenne Mobile (21)',
                'Valeur': round(sma_21.iloc[-1],2),
                'Action': 'Acheter' if sma_21.iloc[-1] < last_price else 'Vendre' if sma_21.iloc[-1] > last_price else 'Neutre'
            },
            {
                'Nom': 'Moyenne Mobile (100)',
                'Valeur': round(sma_100.iloc[-1],2),
                'Action': 'Acheter' if sma_100.iloc[-1] < last_price else 'Vendre' if sma_100.iloc[-1] > last_price else 'Neutre'
            }
        ])

    # RSI
    rsi = RSIIndicator(filtered_data[action], window=14).rsi()
    last_rsi = round(rsi.iloc[-1], 2)
    signals.append({
            'Nom': 'Indice de force relative (14)',
            'Valeur': last_rsi,
            'Action': 'Acheter' if last_rsi < 30 else 'Vendre' if last_rsi > 70 else 'Neutre'
        })

    # MACD
    macd_indicator = MACD(close=filtered_data[action], window_slow=26, window_fast=12, window_sign=9)
    macd_diff = round(macd_indicator.macd_diff().iloc[-1],2)
    signals.append({
            'Nom': 'MACD (12,26)',
            'Valeur': macd_diff,
            'Action': 'Acheter' if macd_diff > 0 else 'Vendre' if macd_diff < 0 else 'Neutre'
        })


    # Ajout du signal de Bandes de Bollinger
    indicator_bb = BollingerBands(close=filtered_data[action], window=20, window_dev=2)
    bb_upper = indicator_bb.bollinger_hband_indicator().iloc[-1]
    bb_lower = indicator_bb.bollinger_lband_indicator().iloc[-1]
        
    # La logique de signal pour les Bandes de Bollinger peut être basée sur le croisement des prix avec les bandes
    if filtered_data[action].iloc[-1] > bb_upper:
            bb_action = 'Vendre'  # Prix au-dessus de la bande supérieure
    elif filtered_data[action].iloc[-1] < bb_lower:
            bb_action = 'Acheter'  # Prix en dessous de la bande inférieure
    else:
            bb_action = 'Neutre'
        
    signals.append({
            'Nom': 'Bandes de Bollinger (20, 2)',
            'Valeur': f"Upper: {bb_upper}, Lower: {bb_lower}",
            'Action': bb_action
        })
        # EMA
    ema_indicator = EMAIndicator(close=filtered_data[action], window=14)
    ema = ema_indicator.ema_indicator()
    last_ema = round(ema.iloc[-1], 2)
    signals.append({
            'Nom': 'EMA (14)',
            'Valeur': last_ema,
            'Action': 'Acheter' if last_price > last_ema else 'Vendre' if last_price < last_ema else 'Neutre'
        })

    ema_indicator = EMAIndicator(close=filtered_data[action], window=100)
    ema = ema_indicator.ema_indicator()
    last_ema = round(ema.iloc[-1], 2)
    signals.append({
            'Nom': 'EMA (100)',
            'Valeur': last_ema,
            'Action': 'Acheter' if last_price > last_ema else 'Vendre' if last_price < last_ema else 'Neutre'
        })

    # Momentum
    momentum_indicator = SMAIndicator(filtered_data[action], window=10).sma_indicator()
    last_momentum = round(momentum_indicator.iloc[-1], 2)
    signals.append({
            'Nom': 'Momentum (10)',
            'Valeur': last_momentum,
            'Action': 'Acheter' if last_momentum > 0 else 'Vendre' if last_momentum < 0 else 'Neutre'
        })

    # Rate of Change (ROC)
    roc_indicator = ROCIndicator(filtered_data[action], window=12)
    last_roc = round(roc_indicator.roc().iloc[-1], 2)
    signals.append({
            'Nom': 'ROC (12)',
            'Valeur': last_roc,
            'Action': 'Acheter' if last_roc > 0 else 'Vendre' if last_roc < 0 else 'Neutre'
        })

    def display_signals(signals):
            # En-têtes des colonnes
            col1, col2, col3 = st.columns([5, 5, 2])
            with col1:
                st.markdown("**Nom**")
            with col2:
                st.markdown("**Valeur**")
            with col3:
                st.markdown("**Action**")

            # Données des signaux
            for signal in signals:
                col1, col2, col3 = st.columns([5, 5, 2])
                with col1:
                    st.write(signal['Nom'])
                with col2:
                    st.write(f"{signal['Valeur']}")

                # Utilisation du HTML pour colorer les actions en rouge ou vert
                action_color = "red" if signal['Action'] == "Vendre" else "blue" if signal['Action'] == "Acheter" else "black"
                with col3:
                    st.markdown(f"<span style='color: {action_color};'>{signal['Action']}</span>", unsafe_allow_html=True)

    # Affichage conditionnel des signaux
    #if 'show_signals' in st.session_state and st.session_state['show_signals']:
    display_signals(signals)
    st.markdown("</div>", unsafe_allow_html=True)

with stats_cle_col:
    st.markdown("<div class='section-title'>🔍 Indicateurs fondatemtaux </div>", unsafe_allow_html=True)
    if 'uploaded_file' in st.session_state and action:
        # Charger les données de la feuille correspondant à l'action sélectionnée
        sheet_data = pd.read_excel(st.session_state['uploaded_file'], sheet_name=action, header=None)
        
        # Utiliser les colonnes D et E (indices 3 et 4) pour le pie chart
        pie_data = sheet_data.iloc[:, [3, 4]].dropna()
        pie_data.columns = ['Actionnaire', 'Pourcentage']
        
        # Remplacer les virgules par des points et convertir en float
        pie_data['Pourcentage'] = pie_data['Pourcentage'].str.replace(',', '.').str.rstrip('%').astype(float)
        
        # Créer le pie chart
        fig = px.pie(pie_data, names='Actionnaire', values='Pourcentage', title='Répartition des Actionnaires')
        
        # Afficher le pie chart
        st.plotly_chart(fig, use_container_width=True)


    if 'uploaded_file' in st.session_state and action:
        profile_data = pd.read_excel(st.session_state['uploaded_file'], sheet_name='Profil', header=0)
        profile_data.set_index(profile_data.columns[0], inplace=True)
        if action in profile_data.columns:
            stats_for_action = profile_data[[action]].dropna().iloc[1:]
            col_label, col_value = st.columns([1, 1])
            with col_label:
                for stat_name in stats_for_action.index:
                    st.markdown(f"<div style='margin-bottom: 10px;'><strong>{stat_name}</strong></div>", unsafe_allow_html=True)
            with col_value:
                for value in stats_for_action[action]:
                    st.markdown(f"<div style='margin-bottom: 10px;'>{value if pd.notna(value) else '-'}</div>", unsafe_allow_html=True)
        else:
            st.error(f"L'action {action} n'est pas trouvée dans la feuille 'Profil'.")

with eval_methods_col:
    st.markdown("<div class='section-title'>📝 Méthodes d'évaluation</div>", unsafe_allow_html=True)
    if 'uploaded_file' in st.session_state and action:
        stats_data = pd.read_excel(st.session_state['uploaded_file'], sheet_name='Statistique', header=0)
        stats_data.set_index(stats_data.columns[0], inplace=True)
        if action in stats_data.columns:
            stats_data[action] = pd.to_numeric(stats_data[action], errors='coerce')
            eval_methods = stats_data.iloc[-4:][[action]].dropna()
            eval_signals = []
            cours_data = pd.read_excel(st.session_state['uploaded_file'], sheet_name='COURS')
            cours_data['Date'] = pd.to_datetime(cours_data['Date'])
            filtered_data = cours_data[cours_data['Date'].dt.year >= 2018]
            last_price = filtered_data[action].iloc[-1]
            for method_name, value in eval_methods[action].items():
                if pd.notna(value):
                    action_signal = 'Acheter' if value > last_price else 'Vendre' if value < last_price else 'Neutre'
                    eval_signals.append({'Nom': method_name, 'Valeur': round(value, 2), 'Action': action_signal})
            for signal in eval_signals:
                action_color = "blue" if signal['Action'] == "Acheter" else "red" if signal['Action'] == "Vendre" else "black"
                st.markdown(
                    f"""
                    <div class="eval-card">
                        <h6 style="margin: 0; color: #333;">{signal['Nom']}</h5>
                        <p style="margin: 5px 0;"><strong>Valeur:</strong> {signal['Valeur']}</p>
                        <p style="margin: 5px 0;"><strong>Action:</strong> <span style="color: {action_color};">{signal['Action']}</span></p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.error(f"L'action {action} n'est pas trouvée dans la feuille 'Statistique'.")
