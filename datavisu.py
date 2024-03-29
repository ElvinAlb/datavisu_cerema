import pandas as pd
import streamlit as st
import numpy as np
from bokeh.plotting import figure
from bokeh.models import DataRange1d, HoverTool
import datetime as dt
import seaborn as sns



st.set_page_config(page_title="Interface", page_icon=":thermometer:", layout="wide")

color_list =["#262727","#e3342f","#f6993f","#ffed4a","#38c172","#4dc0b5","#3490dc","#6574cd","#9561e2","#f66d9b"]  #liste des couleurs des courbes

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
 # block markdown pour utiliser du code html dans la page
 # ce block permet de modifier le layout

if 'clicked' not in st.session_state:
    st.session_state.clicked=False

def set_clicked():
   st.session_state.clicked=True  #changer l'état du bouton

st.button("Importer le fichier CSV", on_click=set_clicked) 

if st.session_state.clicked:    # après appui sur le bouton, ouverture du page pour importer un fichier csv

    data_file = st.file_uploader("Upload CSV", type=["csv"], accept_multiple_files=False) #upload csv file
    if data_file is not None:
        file_details = {"filename":data_file.name, "filesize":data_file.size}
        data=pd.read_csv(data_file, index_col=2)#read csv
    
        nb_columns= len(data.columns)
        date=pd.to_datetime(data.index, dayfirst=True)
        
        for i in range(1,nb_columns-3):
            locals()["temp"+str(i)] = data["t_sonde_"+str(i)]
        
        temp_corps_noir=data['t_corps_noir']
        temp_ambiante=data['t_ambiante']

        nb_data=data.shape[0] #nombre de données récupérées par sonde 
        nb_data_tot=data.size #nombre total de données

        latitude=data['latitude'][0]
        longitude=data['longitude'][0]
        data.drop('longitude',axis="columns",inplace=True)
        data.drop('latitude',axis="columns",inplace=True)
        cols = list(data.columns)
        #------------------ Sidebar ---------------------------------------
            
        checkbox_list = []   #définition de la liste des checkbox.
        st.sidebar.write("Choix des sondes")
        for i in range(1,9):
            checkbox_list.append(st.sidebar.checkbox("Sonde " + str(i), value=False)) #variables checkbox1,2,3...
        checkbox_list.append(st.sidebar.checkbox("Corps Noir", value=False))
        checkbox_list.append(st.sidebar.checkbox("Température ambiante", value=False))

        #------------------- Range selection ------------------------------------------
    
        start_date_slider = date[0].to_pydatetime()      #redéfinition range date
        end_date_slider= date[len(date)-1].to_pydatetime()

        slider_range=st.slider("Sélectionner l'intervalle de temps",min_value=start_date_slider, max_value=end_date_slider, value=[start_date_slider,end_date_slider])

    #---------------- Plot Bokeh ----------------------------

        plot_x_range=DataRange1d(start=slider_range[0], end=slider_range[1]) # Echelle de l'axe des abscisses à partir des valeurs du slider


        plot=figure(title='Températures des sondes', x_axis_type='datetime', x_range=plot_x_range)        #définition du plot bokeh des températures
        plot_mg=figure(title='Moyenne glissante des température', x_axis_type='datetime')    #définition du plot bokeh des moyennes glissantes

        for i in range(1,nb_columns-3):
            locals()["l"+str(i)]=plot.line(date,locals()["temp"+str(i)], line_color=color_list[i], legend_label="sonde "+str(i)) #variables l1,l2,l3...

        l9=plot.line(date,temp_corps_noir, legend_label='température corps noir', line_color=color_list[0])
        l10=plot.line(date,temp_ambiante, legend_label='température ambiante', line_color=color_list[9])


        for i in range(1,nb_columns-2):
            if checkbox_list[i-1]:
                plot.add_tools(HoverTool(tooltips="y: @y", renderers=[locals()['l'+str(i)]],mode="vline", name="sonde"+str(i)))
        if checkbox_list[-1]:
            plot.add_tools(HoverTool(tooltips="y: @y", renderers=[l10],mode="vline", name="Température ambiante"))
        if checkbox_list[-2]:
            plot.add_tools(HoverTool(tooltips="y: @y", renderers=[l9],mode="vline", name="Température corps noir"))

    #Cocher une checkbox permet d'afficher un hover donnant la valeur de température précise pour la sonde sélectionnée
        
        plot.legend.click_policy='hide'

        st.bokeh_chart(plot,use_container_width=True)   #affichage de la courbe bokeh

#--------------------------------- Moyenne glissante -----------------------------------
        with st.expander("Graphique des moyennes glissantes"):
                    #définition du plot bokeh des moyennes glissantes des températures
            if 'moyenne_glissante' not in st.session_state:
                st.session_state.moyenne_glissante=False
        
            def set_mg():
                st.session_state.moyenne_glissante=True
 
            st.button("Afficher le graphique des moyennes glissantes", on_click=set_mg)

            if st.session_state.moyenne_glissante:
                pas=st.number_input("Rentrer le pas de la moyenne glissante", min_value=1,value=5, step=1)
                for i in range(1,nb_columns-3):
                    locals()["mg"+str(i)]=plot_mg.line(date,locals()["temp"+str(i)].rolling(pas).mean(), line_color=color_list[i], legend_label="sonde "+str(i)) #variables mg1,mg2,mg3...

                m9=plot_mg.line(date,temp_corps_noir.rolling(pas).mean(), legend_label='température corps noir', line_color=color_list[0])
                m10=plot_mg.line(date,temp_ambiante.rolling(pas).mean(), legend_label='température ambiante', line_color=color_list[9])
                st.bokeh_chart(plot_mg,use_container_width=True) #affichage des moyennes glissantes

#---------------------------------- Dataset et températures max et min ---------------------------

        with st.expander('Dataset et Températures Max et Min'):
        
            st.write("Max et Min sur l'ensemble des données")
            tempmax=data.max()
            tempmin=data.min()
            tempminmax=pd.concat([tempmax,tempmin], axis=1)
            tempminmax=tempminmax.set_axis(['Max','Min'], axis=1)
            tempminmax=tempminmax.transpose()
            st.write(tempminmax)
            
            st.write("Max et Min sur l'intervalle sélectionné")
            temp_intervalle=data[start_date_slider.strftime("%d/%m/%Y %H:%M"):end_date_slider.strftime("%d/%m/%Y %H:%M")]
            temp_intervalle_max=temp_intervalle.max()
            temp_intervalle_min=temp_intervalle.min()
            temp_intervalle_minmax=pd.concat([temp_intervalle_max,temp_intervalle_min], axis=1)
            temp_intervalle_minmax=temp_intervalle_minmax.set_axis(['Max','Min'],axis=1)
            temp_intervalle_minmax=temp_intervalle_minmax.transpose()
            st.write(temp_intervalle_minmax)
    
            st.write("Dataset")
            st.dataframe(data)
            st.write("Nombre de mesures : " + str(nb_data))
            st.write("Nombre total de données : " + str(nb_data_tot))

#------------------------- Localisation GPS ----------------------------------------------
        #localisation={'latitude': [data['latitude'][0]], 'longitude': [data['longitude'][0]]}       

        with st.expander("Localisation"):
            col1,col2,col3,col4 = st.columns([0.25,0.25,0.25,0.25])

            with col2:
                #st.info(f"Latitude : **{str(data['latitude'][0])}**")
                st.info("Latitude : " +str(latitude))
            with col3:
                st.info("Longitude : " +str(longitude))
            
            map_data={'latitude':[latitude],'longitude':[longitude]}    

            st.map(map_data, zoom=14)
#----------------------------- Slicing des données -------------------------------------------
        with st.expander("Réduction du nombre de données"):
            pas_slice=int(st.number_input("Selectionner le pas pour réduire le dataframe", min_value=1, value=1))
            data_clear=data.iloc[::pas_slice]

            date_slice=pd.to_datetime(data_clear.index, dayfirst=True)    

            range_date=st.date_input("Intervalle de temps", (date_slice[0], date_slice[len(date_slice)-1]))
            range_date_start=dt.datetime.combine(range_date[0], dt.time(date_slice[0].hour,date_slice[0].minute))
            range_date_end=dt.datetime.combine(range_date[1], dt.time(date_slice[len(date_slice)-1].hour,date_slice[len(date_slice)-1].minute))

            data_clear=data_clear[range_date_start.strftime("%d/%m/%Y %H:%M"):range_date_end.strftime("%d/%m/%Y %H:%M")]
            data_clear=data_clear.reset_index()
            list_date = data_clear['date_heure'].tolist()

            st.dataframe(data_clear)

#------------------------------------ Valeurs aberrantes --------------------------------------------
        with st.expander("Valeurs aberrantes"):
            
            data_zscore = (data-data.mean())/data.std()
            outliers = data.where(np.abs(data_zscore.values)>5)
            
            outliers.dropna(inplace=True, how="all")
            outliers.dropna(inplace=True, axis="columns" )
            outliers.reset_index(inplace=True)
            data_filter=data_clear[~data_clear["date_heure"].isin(outliers["date_heure"])]
            data_outliers=data_clear[data_clear["date_heure"].isin(outliers["date_heure"])]
            st.write("Dataframe des valeurs aberrantes écartées")
            st.write(data_outliers)
            st.write("Dataframe sans les valeurs aberrantes")
            st.write(data_filter)
            plot_test_outliers=figure(title="Outliers")

            if 'outliers' not in st.session_state:
                st.session_state.outliers=False
        
            def set_outliers():
                st.session_state.outliers=True

            st.button("Afficher le graphe sans valeurs aberrantes", on_click=set_outliers)

            if st.session_state.outliers:
                i=0
                for x in cols:
                    plot_test_outliers.line(date, data_filter[x], line_color=color_list[i])
                    i+=1
                st.bokeh_chart(plot_test_outliers,use_container_width=True)
#------------------------- Gradient de température -----------------------------------------
        with st.expander("Gradient"):
            depth=[-10,-20,-30,-40,-50,-60,-70,-80]

            palette=sns.color_palette("hls",len(list_date))
            palette=palette.as_hex()


            if 'gradient' not in st.session_state:
                st.session_state.gradient=False
            
            def set_gradient():
                st.session_state.gradient=True

            st.button("Afficher le gradient", on_click=set_gradient)
            
            st.write("Penser à réduire le nombre de données avant d'afficher le gradient")

            if st.session_state.gradient:
                plot_gradient=figure(title='Gradient de température')
                data_clear.drop('date_heure',axis="columns",inplace=True)
                data_clear.drop('t_corps_noir',axis="columns",inplace=True)
                data_clear.drop('t_ambiante',axis="columns",inplace=True)
                

                for i in range(len(list_date)):
                    locals()["grad"+str(i)]=plot_gradient.line(data_clear.loc[i],depth, legend_label=str(list_date[i]),line_color=palette[i])
                    
                plot_gradient.legend.visible=False


                st.bokeh_chart(plot_gradient,use_container_width=True)
        