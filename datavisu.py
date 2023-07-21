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


        nb_data=len(temp1) #nombre de données récupérées par sonde 
        nb_data_tot=data.size #nombre total de données

        #------------------ Sidebar ---------------------------------------
            
        checkbox_list = []   #définition de la liste des checkbox.
        st.sidebar.write("Choix des sondes")
        for i in range(1,9):
            checkbox_list.append(st.sidebar.checkbox("Sonde " + str(i), value=False)) #variables checkbox1,2,3...
        checkbox_list.append(st.sidebar.checkbox("Corps Noir", value=False))
        checkbox_list.append(st.sidebar.checkbox("Température ambiante", value=False))

        #------------------- Range selection ------------------------------------------
    
        start_date = pd.to_datetime(date[0])       #redéfinition range date
        end_date= pd.to_datetime(date[len(date)-1])
        
        col1, col2, col3 = st.columns([0.15,0.7,0.15])
        with col1 :
            start_date_box = st.date_input("start_date",value=start_date,min_value=start_date,max_value=end_date, label_visibility="hidden")
            start_date_slider=dt.datetime.combine(start_date_box, dt.time(date[0].hour,date[0].minute))
        with col3:
            end_date_box = st.date_input("end_date",value=end_date,min_value=start_date,max_value=end_date, label_visibility='hidden')
            end_date_slider = dt.datetime.combine(end_date_box, dt.time(date[len(date)-1].hour,date[len(date)-1].minute))

        with col2:
            slider_range=st.slider("Sélectionner l'intervalle de temps",min_value=start_date, max_value=end_date, value=[start_date_slider,end_date_slider])

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
    #Cocher une checkbox permet d'afficher un hover donnant la valeur de température précise pour la sonde sélectionnée
        
        plot.legend.click_policy='hide'

        st.bokeh_chart(plot,use_container_width=True)   #affichage de la courbe bokeh

#--------------------------------- Moyenne glissante -----------------------------------
        with st.expander("Graphique des moyennes glissantes"):
                    #définition du plot bokeh des moyennes glissantes des températures
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
        localisation={'latitude': [data['latitude'][0]], 'longitude': [data['longitude'][0]]}
        df_localisation= pd.DataFrame(data=localisation)
        st.dataframe(df_localisation)
        

        with st.expander("Localisation"):
            col1,col2,col3,col4 = st.columns([0.25,0.25,0.25,0.25])

            with col2:
                st.info(f"Latitude : **{str(data['latitude'][0])}**")
            with col3:
                st.info(f"Longitude :  **{str(data['longitude'][0])}**")

            st.map(df_localisation, zoom=14)
#----------------------------- Slicing des données -------------------------------------------
        with st.expander("Slicing"):
            pas_slice=int(st.number_input("Selectionner le pas pour réduire le dataframe", min_value=1, value=1))
            data_clear=data.iloc[::pas_slice]
            data_clear.drop(columns=['longitude','latitude'])

            date_slice=pd.to_datetime(data_clear.index, dayfirst=True)    

            range_date=st.date_input("Intervalle de temps", (date_slice[0], date_slice[len(date_slice)-1]))
            range_date_start=dt.datetime.combine(range_date[0], dt.time(date_slice[0].hour,date_slice[0].minute))
            range_date_end=dt.datetime.combine(range_date[1], dt.time(date_slice[len(date_slice)-1].hour,date_slice[len(date_slice)-1].minute))

            data_clear=data_clear[range_date_start.strftime("%d/%m/%Y %H:%M"):range_date_end.strftime("%d/%m/%Y %H:%M")]
            data_clear=data_clear.reset_index()
            list_date = data_clear['date_heure'].tolist()
            data_clear.drop('longitude',axis="columns",inplace=True)
            data_clear.drop('latitude',axis="columns",inplace=True)

            st.dataframe(data_clear)

#------------------------------------ Valeurs aberrantes --------------------------------------------
        """with st.expander("Valeurs aberrantes"):
            for i in range(1,9):
                for x in ['t_sonde_'+str(i)]:
                    q75,q25 = np.percentile(data.loc[:,x],[75,25])
                    intr_qr = q75-q25
                
                    max = q75+(1.5*intr_qr)
                    min = q25-(1.5*intr_qr)
                
                    data_clear.loc[data_clear[x] < min,x] = np.nan
                    data_clear.loc[data_clear[x] > max,x] = np.nan
            for x in ['t_ambiante']:
                    q75,q25 = np.percentile(data_clear.loc[:,x],[75,25])
                    intr_qr = q75-q25
                
                    max = q75+(1.5*intr_qr)
                    min = q25-(1.5*intr_qr)
                
                    data_clear.loc[data_clear[x] < min,x] = np.nan
                    data_clear.loc[data_clear[x] > max,x] = np.nan
            for x in ['t_corps_noir']:
                    q75,q25 = np.percentile(data_clear.loc[:,x],[75,25])
                    intr_qr = q75-q25
                
                    max = q75+(1.5*intr_qr)
                    min = q25-(1.5*intr_qr)
                    st.write(max,min,q75,q25,intr_qr)
                    data_clear.loc[data_clear[x] < min,x] = np.nan
                    data_clear.loc[data_clear[x] > max,x] = np.nan
            
            #data_clear[(np.abs(stats.zscore(data_clear)) < 3).all(axis=1)]
            data_outliers = data_clear[(data_clear["t_ambiante"]> data_clear["t_ambiante"].quantile(0.01))]

            st.dataframe(data_outliers)
            plot_test_outliers=figure(title="Outliers")
            plot_test_outliers.line(date, data_outliers["t_ambiante"])

            st.bokeh_chart(plot_test_outliers,use_container_width=True)"""

#------------------------- Gradient de température -----------------------------------------
        depth=[10,20,30,40,50,60,70,80]

        palette=sns.color_palette("hls",len(list_date))
        palette=palette.as_hex()


        if 'gradient' not in st.session_state:
            st.session_state.gradient=False
        
        def set_gradient():
            st.session_state.gradient=True

        st.button("Afficher le gradient", on_click=set_gradient)

        if st.session_state.gradient:
            plot_gradient=figure(title='Gradient de température')
            data_clear.drop('date_heure',axis="columns",inplace=True)
            data_clear.drop('t_corps_noir',axis="columns",inplace=True)
            data_clear.drop('t_ambiante',axis="columns",inplace=True)
            

            for i in range(len(list_date)):
                locals()["grad"+str(i)]=plot_gradient.line(depth,data_clear.loc[i], legend_label=str(list_date[i]),line_color=palette[i])
                
            plot_gradient.legend.visible=False


            st.bokeh_chart(plot_gradient,use_container_width=True)
    