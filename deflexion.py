import pandas as pd
import streamlit as st
import numpy as np
from bokeh.plotting import figure
from bokeh.models import DataRange1d, HoverTool
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="Interface", page_icon=":chart_with_upwards_trend:", layout="wide")

st.markdown(
        f"""
        <style>
            .appview-container .main {{
                padding-right: {10}rem;
                padding-left: {10}rem;
                }}
            .appview-container .main .block-container{{
                padding-top: {2}rem;
            }}

        </style>""",
        unsafe_allow_html=True,
    )

if 'clicked' not in st.session_state:
    st.session_state.clicked=False

def set_clicked():
   st.session_state.clicked=True  #changer l'état du bouton

st.button("Importer le fichier CSV", on_click=set_clicked) 

if st.session_state.clicked:
    data_file = st.file_uploader("Upload CSV", type=["csv"], accept_multiple_files=False)
    if data_file is not None:
        data=pd.read_csv(data_file, sep=";", engine="python")

        step=data["step"].iloc[0]
        xmin=data["xmin"].iloc[0]
        ymin=data["ymin"].iloc[0]
        data.drop(['step','xmin','ymin'], axis="columns", inplace=True)

        valeur_max=data.values.max()
        valeur_min=data.values.min()

        esp_x=[xmin]
        for i in range(data.shape[0]-1):
            esp_x.append(esp_x[i]+step)
        esp_y=[ymin]
        for i in range(data.shape[1]-1):
            esp_y.append(esp_y[i]+step)
        

        col1,col2,col3 = st.columns(3)
        with col1:
            st.write("Nombre de colonnes: ",data.shape[0], "Nombre de lignes: ",data.shape[1])
        with col2:
            st.write("Valeur max: ", valeur_max,"Valeur min: ",valeur_min)
        with col3:
            st.write("Longueur axe x: ",esp_x[-1]-esp_x[1],"Longueur axe y: ",esp_y[-1]-esp_y[1])


        
        col1, col2 = st.columns([0.5,0.5])
        list_row=[]
        list_column=[]
        list_column_inv = []
        list_row_inv = []
        with col1:
            for i in range(data.shape[0]):
                list_column.append(data.iloc[:,i])

            inverser_x=st.checkbox("Inverser les courbes (selon x)", value=False)
            affichage_x=st.radio("Afficher: (selon x) ", ('Toutes les courbes (selon x)','Vue par profil (selon x)'))
            if affichage_x=='Vue par profil (selon x)':
                slider_1 = st.slider("Sélectionner le profil à afficher", min_value=1, max_value=data.shape[1],value=1)
                if inverser_x == False:
                    fig = px.line(x=esp_x,y=data.iloc[:,slider_1-1])
                    fig=go.Figure(fig,layout_yaxis_range=[valeur_min,valeur_max])
                else:
                    fig = px.line(x=esp_x,y=data.iloc[:,slider_1-1]*(-1))
                    fig=go.Figure(fig,layout_yaxis_range=[valeur_max*(-1),valeur_min*(-1)])
                fig.update_traces(line=dict(color="mediumslateblue"))
            else:
                if inverser_x == False:
                    fig=px.line(data,x=esp_x,y=list_column)
                else:
                    for i in range(data.shape[0]):
                        list_column_inv.append(list_column[i]*-1)
                    fig=px.line(data,x=esp_x,y=list_column_inv)
                fig.update_traces(line=dict(color="mediumslateblue", width=0.5))

            
            fig.update_layout(height=700, showlegend=False)
            st.plotly_chart(fig)
        
        with col2:
            for i in range(data.shape[0]):
                list_row.append(data.iloc[i])
            inverser_y=st.checkbox("Inverser les courbes (selon y)", value=False)
            affichage_y=st.radio("Afficher: (selon y) ", ('Toutes les courbes (selon y)','Vue par profil (selon y)'))
            if affichage_y=='Vue par profil (selon y)':
                slider_2 = st.slider("Sélectionner le profil à afficher2", min_value=1, max_value=data.shape[0],value=1)
                if inverser_y == False:
                    fig2=px.line(x=esp_y,y=data.iloc[slider_2-1])
                    fig2=go.Figure(fig2,layout_yaxis_range=[valeur_min,valeur_max])
                    #fig2.update_layout(yaxis=dict(range=[valeur_min,valeur_max]))
                else:
                    fig2=px.line(x=esp_y,y=data.iloc[slider_2-1]*(-1))
                    fig2=go.Figure(fig2,layout_yaxis_range=[valeur_max*(-1),valeur_min*(-1)])
                    #fig2.update_layout(yaxis_range=[valeur_max*(-1),valeur_min*(-1)])
                fig2.update_traces(line=dict(color="mediumslateblue"))
            else:
                if inverser_y == False:
                    fig2=px.line(x=esp_y,y=list_row)
                else:
                    for i in range(data.shape[0]):
                        list_row_inv.append(list_row[i]*(-1))
                    fig2=px.line(x=esp_y,y=list_row_inv)
                fig2.update_traces(line=dict(color="mediumslateblue", width=0.5))
            
            fig2.update_layout(height=700, showlegend=False)
            st.plotly_chart(fig2)

        
        inverser_3d=st.checkbox("Inverser la courbe (3d)")
        x = np.arange(esp_y[0],esp_y[-1]+50,50) #définition de l'axe x
        y = np.arange(esp_x[0],esp_x[-1]+50,50) #définition de l'axe y
        X, Y = np.meshgrid(x, y)
        Z = data.to_numpy()  #définition de l'axe z

        if inverser_3d :
            fig = go.Figure(data=[go.Surface(z=Z*(-1), x=x, y=y, colorscale="Viridis")])
        else:
            fig = go.Figure(data=[go.Surface(z=Z, x=x, y=y, colorscale="Viridis")])
        fig.update_layout(title='Déflexion', autosize=False, width=1000, height=700)
        st.plotly_chart(fig)

        with st.expander("Afficher le dataframe"):
            st.dataframe(data)