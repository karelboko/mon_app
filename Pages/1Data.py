import streamlit as st
import pandas as pd
import io

def load_sheet_data(uploaded_file, sheet_name):
    data = pd.read_excel(uploaded_file, sheet_name=sheet_name)
    return data

def setup_streamlit_app():
    st.set_page_config(page_title="Investor Dashboard", page_icon="📊", layout="wide")
    st.markdown("<h1 style='text-align: center;'>Data 📊</h1>", unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Importer les données (.xlsm)", type=['xlsm'])
    if uploaded_file is not None:
        st.session_state['uploaded_file'] = io.BytesIO(uploaded_file.getvalue())
        xl = pd.ExcelFile(st.session_state['uploaded_file'])
        sheet_names = xl.sheet_names

        # Chargement des noms de colonnes de la feuille "MAX" pour utilisation ultérieure
        if "MAX" in sheet_names:
            max_data = pd.read_excel(st.session_state['uploaded_file'], sheet_name="MAX")
            st.session_state['max_columns'] = max_data.columns.tolist()  # Stockage des noms des colonnes

        selected_sheet = st.selectbox('Visualisation des données', sheet_names, index=sheet_names.index('MAX') if 'MAX' in sheet_names else 0)
        data = load_sheet_data(st.session_state['uploaded_file'], selected_sheet)
        
        st.session_state['df'] = data
        st.session_state['selected_sheet_index'] = sheet_names.index(selected_sheet)
        
        st.dataframe(data)

def main():
    if 'uploaded_file' in st.session_state:
        setup_streamlit_app()
    else:
        setup_streamlit_app()

if __name__ == "__main__":
    main()
