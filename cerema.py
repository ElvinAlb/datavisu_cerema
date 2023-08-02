import pandas as pd
import streamlit as st
import numpy as np
from bokeh.plotting import figure
from bokeh.models import DataRange1d, HoverTool
import plotly.graph_objects as go
import plotly.express as px
import datetime as dt
import seaborn as sns

st.set_page_config(page_title="Interface", page_icon=":chart_with_upwards_trend:", layout="wide")

#with open('style.css') as f:
#    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    
st.markdown(
        f"""
        <style>
            .appview-container .main .block-container{{
                padding-right: {10}rem;
                padding-left: {10}rem;
                }}
            .appview-container .main .block-container{{
                padding-top: {2}rem;
            }}

        </style>""",
        unsafe_allow_html=True,
    )

tab1, tab2 = st.tabs(["Déflexion","Température"])

with tab1:

    if 'csv_deflexion' not in st.session_state:
        st.session_state.csv_deflexion=False

    def set_csv_deflexion():
        st.session_state.csv_deflexion=True  #changer l'état du bouton

    st.button("Importer le fichier CSV de déflexion", on_click=set_csv_deflexion) 

    if st.session_state.csv_deflexion:
        df_deflexion_file = st.file_uploader("Upload CSV déflexion", type=["csv"], accept_multiple_files=False)
        if df_deflexion_file is not None:
            df_deflexion=pd.read_csv(df_deflexion_file, sep=";", engine="python")

            step=df_deflexion["step"].iloc[0]
            xmin=df_deflexion["xmin"].iloc[0]
            ymin=df_deflexion["ymin"].iloc[0]
            df_deflexion.drop(['step','xmin','ymin'], axis="columns", inplace=True)

            valeur_max=df_deflexion.values.max()
            valeur_min=df_deflexion.values.min()

            esp_x=[xmin]
            for i in range(df_deflexion.shape[0]-1):
                esp_x.append(esp_x[i]+step)
            esp_y=[ymin]
            for i in range(df_deflexion.shape[1]-1):
                esp_y.append(esp_y[i]+step)
            

            col1,col2,col3 = st.columns(3)
            with col1:
                st.write("Nombre de colonnes: ",df_deflexion.shape[0], "Nombre de lignes: ",df_deflexion.shape[1])
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
                for i in range(df_deflexion.shape[0]):
                    list_column.append(df_deflexion.iloc[:,i])

                inverser_x=st.checkbox("Inverser les courbes (selon x)", value=False)
                affichage_x=st.radio("Afficher: (selon x) ", ('Toutes les courbes (selon x)','Vue par profil (selon x)'))
                if affichage_x=='Vue par profil (selon x)':
                    slider_1 = st.slider("Sélectionner le profil à afficher", min_value=1, max_value=df_deflexion.shape[1],value=1)
                    if inverser_x == False:
                        fig = px.line(x=esp_x,y=df_deflexion.iloc[:,slider_1-1])
                        fig=go.Figure(fig,layout_yaxis_range=[valeur_min,valeur_max])
                    else:
                        fig = px.line(x=esp_x,y=df_deflexion.iloc[:,slider_1-1]*(-1))
                        fig=go.Figure(fig,layout_yaxis_range=[valeur_max*(-1),valeur_min*(-1)])
                    fig.update_traces(line=dict(color="mediumslateblue"))
                else:
                    if inverser_x == False:
                        fig=px.line(df_deflexion,x=esp_x,y=list_column)
                    else:
                        for i in range(df_deflexion.shape[0]):
                            list_column_inv.append(list_column[i]*-1)
                        fig=px.line(df_deflexion,x=esp_x,y=list_column_inv)
                    fig.update_traces(line=dict(color="mediumslateblue", width=0.5))

                
                fig.update_layout(autosize=True, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                for i in range(df_deflexion.shape[0]):
                    list_row.append(df_deflexion.iloc[i])
                inverser_y=st.checkbox("Inverser les courbes (selon y)", value=False)
                affichage_y=st.radio("Afficher: (selon y) ", ('Toutes les courbes (selon y)','Vue par profil (selon y)'))
                if affichage_y=='Vue par profil (selon y)':
                    slider_2 = st.slider("Sélectionner le profil à afficher2", min_value=1, max_value=df_deflexion.shape[0],value=1)
                    if inverser_y == False:
                        fig2=px.line(x=esp_y,y=df_deflexion.iloc[slider_2-1])
                        fig2=go.Figure(fig2,layout_yaxis_range=[valeur_min,valeur_max])
                        #fig2.update_layout(yaxis=dict(range=[valeur_min,valeur_max]))
                    else:
                        fig2=px.line(x=esp_y,y=df_deflexion.iloc[slider_2-1]*(-1))
                        fig2=go.Figure(fig2,layout_yaxis_range=[valeur_max*(-1),valeur_min*(-1)])
                        #fig2.update_layout(yaxis_range=[valeur_max*(-1),valeur_min*(-1)])
                    fig2.update_traces(line=dict(color="mediumslateblue"))
                else:
                    if inverser_y == False:
                        fig2=px.line(x=esp_y,y=list_row)
                    else:
                        for i in range(df_deflexion.shape[0]):
                            list_row_inv.append(list_row[i]*(-1))
                        fig2=px.line(x=esp_y,y=list_row_inv)
                    fig2.update_traces(line=dict(color="mediumslateblue", width=0.5))
                
                fig2.update_layout(autosize=True, showlegend=False)
                st.plotly_chart(fig2, use_container_width=True)

            
            inverser_3d=st.checkbox("Inverser la courbe (3d)")
            x = np.arange(esp_y[0],esp_y[-1]+50,50) #définition de l'axe x
            y = np.arange(esp_x[0],esp_x[-1]+50,50) #définition de l'axe y
            X, Y = np.meshgrid(x, y)
            Z = df_deflexion.to_numpy()  #définition de l'axe z

            if inverser_3d :
                fig = go.Figure(data=[go.Surface(z=Z*(-1), x=x, y=y, colorscale="Viridis")])
            else:
                fig = go.Figure(data=[go.Surface(z=Z, x=x, y=y, colorscale="Viridis")])
            fig.update_layout(title='Déflexion', autosize=False, width=1000, height=700)
            st.plotly_chart(fig)

            with st.expander("Afficher le dataframe"):
                st.dataframe(df_deflexion)

with tab2:

    color_list =["#262727","#e3342f","#f6993f","#ffed4a","#38c172","#4dc0b5","#3490dc","#6574cd","#9561e2","#f66d9b"]  #liste des couleurs des courbes

    if 'csv_temp' not in st.session_state:
        st.session_state.csv_temp=False

    def set_csv_temp():
        st.session_state.csv_temp=True  #changer l'état du bouton

    st.button("Importer le fichier CSV de température", on_click=set_csv_temp) 

    if st.session_state.csv_temp:    # après appui sur le bouton, ouverture du page pour importer un fichier csv
    
        data_file = st.file_uploader("Upload CSV température", type=["csv"], accept_multiple_files=False) #upload csv file
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
            