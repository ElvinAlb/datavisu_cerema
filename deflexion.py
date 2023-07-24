import pandas as pd
import streamlit as st
import numpy as np
from bokeh.plotting import figure
from bokeh.models import DataRange1d, HoverTool
import plotly.graph_objects as go

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

        espacement_y = []
        for i in range(data.shape[0]):
            espacement_y.append(i*50)

        espacement_x=[]
        for i in range(data.shape[1]):
            espacement_x.append(i*50)

        valeur_max=data.values.max()
        valeur_min=data.values.min()


        st.write("Nombre de colonnes: "+str(data.shape[0]), "Nombre de lignes: "+str(data.shape[1]))
        st.write("Valeur max: "+str(valeur_max),"     Valeur min: "+str(valeur_min))
        st.write("Longueur axe x: " +str(espacement_x[-1]),"Longueur axe y: " + str(espacement_y[-1]))

        col1, col2 = st.columns([0.5,0.5])
        with col1:
            plot=figure(title="Affichage", y_range=DataRange1d(start=valeur_min,end=valeur_max))
            affichage=st.radio("Afficher: ", ('Toutes les courbes','Vue par profil'))
            if affichage=='Vue par profil':
                slider_1 = st.slider("Sélectionner le profil à afficher", min_value=0, max_value=data.shape[0],value=0)
                locals()["x"+str(slider_1)]=plot.line(espacement_x,data.iloc[slider_1])
                plot.add_tools(HoverTool(tooltips=[("y", "@y"),("x","@x")], renderers=[locals()['x'+str(slider_1)]],mode="vline", name="profil"+str(slider_1)))
                
            else:
                for i in range(data.shape[0]):
                    locals()["x"+str(i)]=plot.line(espacement_x,data.iloc[i])
            st.bokeh_chart(plot,use_container_width=True)

        with col2:
            plot_y=figure(title="Affichage_y",y_range=DataRange1d(start=valeur_min,end=valeur_max))
            affichage_y=st.radio("Afficher:2 ", ('Toutes les courbes2','Vue par profil2'))
            if affichage_y=='Vue par profil2':
                slider_2 = st.slider("Sélectionner le profil à afficher", min_value=0, max_value=data.shape[1],value=0)
                locals()["y"+str(slider_2)]=plot_y.line(espacement_y,data.iloc[:,slider_2])
                plot_y.add_tools(HoverTool(tooltips=[("y", "@y"),("x","@x")], renderers=[locals()['y'+str(slider_2)]],mode="vline", name="profil"+str(slider_2)))
            else:
                for i in range(data.shape[1]):
                    locals()["y"+str(i)]=plot_y.line(espacement_y,data.iloc[:,i])
            st.bokeh_chart(plot_y,use_container_width=True)

    

        x = np.arange(0,espacement_x[-1]+50,50) #définition de l'axe x
        y = np.arange(0,espacement_y[-1]+50,50) #définition de l'axe y
        X, Y = np.meshgrid(x, y)
        Z = data.to_numpy()  #définition de l'axe z

        fig = go.Figure(data=[go.Surface(z=Z, x=x, y=y, colorscale="Viridis")])
        fig.update_layout(title='Déflexion', autosize=False, width=1000, height=700)
        st.plotly_chart(fig)

    with st.expander("Afficher le dataframe"):
            st.dataframe(data)