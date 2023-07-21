import pandas as pd
import streamlit as st
import numpy as np
from bokeh.plotting import figure
from bokeh.models import DataRange1d, HoverTool
import datetime as dt

from bokeh.core.properties import Instance, String
from bokeh.io import show
from bokeh.models import ColumnDataSource, LayoutDOM
from bokeh.util.compiler import TypeScript

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
        
        #data = data.fillna('')

        #data.drop(data.columns[-1], axis="columns",inplace=True)
        st.dataframe(data)

        espacement_y = []
        for i in range(data.shape[0]):
            espacement_y.append(i*50)

        espacement_x=[]
        for i in range(data.shape[1]):
            espacement_x.append(i*50)

        st.write("Nombre de colonnes: "+str(data.shape[0]), "Nombre de lignes: "+str(data.shape[1]))

        valeur_max=data.values.max()
        valeur_min=data.values.min()

        st.write("Valeur max: "+str(valeur_max),"     Valeur min: "+str(valeur_min))
        st.write(espacement_y[-1],espacement_x[-1])
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

    
    if 'graph3d' not in st.session_state:
        st.session_state.graph3d=False

    def set_graph3d():
        st.session_state.graph3d=True


    st.button("Afficher le graphe 3d ", on_click=set_graph3d)
    if st.session_state.graph3d:

        TS_CODE = """
        // This custom model wraps one part of the third-party vis.js library:
        //
        //     http://visjs.org/index.html
        //
        // Making it easy to hook up python data analytics tools (NumPy, SciPy,
        // Pandas, etc.) to web presentations using the Bokeh server.

        import {LayoutDOM, LayoutDOMView} from "models/layouts/layout_dom"
        import {ColumnDataSource} from "models/sources/column_data_source"
        import {LayoutItem} from "core/layout"
        import * as p from "core/properties"

        declare namespace vis {
        class Graph3d {
            constructor(el: HTMLElement, data: object, OPTIONS: object)
            setData(data: vis.DataSet): void
        }

        class DataSet {
            add(data: unknown): void
        }
        }

        // This defines some default options for the Graph3d feature of vis.js
        // See: http://visjs.org/graph3d_examples.html for more details.
        const OPTIONS = {
        width: '600px',
        height: '600px',
        style: 'surface',
        showPerspective: true,
        showGrid: true,
        keepAspectRatio: true,
        verticalRatio: 1.0,
        legendLabel: 'stuff',
        cameraPosition: {
            horizontal: -0.35,
            vertical: 0.22,
            distance: 1.8,
        },
        }
        // To create custom model extensions that will render on to the HTML canvas
        // or into the DOM, we must create a View subclass for the model.
        //
        // In this case we will subclass from the existing BokehJS ``LayoutDOMView``
        export class Surface3dView extends LayoutDOMView {
        model: Surface3d

        private _graph: vis.Graph3d

        initialize(): void {
            super.initialize()

            const url = "https://cdnjs.cloudflare.com/ajax/libs/vis/4.16.1/vis.min.js"
            const script = document.createElement("script")
            script.onload = () => this._init()
            script.async = false
            script.src = url
            document.head.appendChild(script)
        }

        private _init(): void {
            // Create a new Graph3s using the vis.js API. This assumes the vis.js has
            // already been loaded (e.g. in a custom app template). In the future Bokeh
            // models will be able to specify and load external scripts automatically.
            //
            // BokehJS Views create <div> elements by default, accessible as this.el.
            // Many Bokeh views ignore this default <div>, and instead do things like
            // draw to the HTML canvas. In this case though, we use the <div> to attach
            // a Graph3d to the DOM.
            this._graph = new vis.Graph3d(this.el, this.get_data(), OPTIONS)

            // Set a listener so that when the Bokeh data source has a change
            // event, we can process the new data
            this.connect(this.model.data_source.change, () => {
            this._graph.setData(this.get_data())
            })
        }

        // This is the callback executed when the Bokeh data has an change. Its basic
        // function is to adapt the Bokeh data source to the vis.js DataSet format.
        get_data(): vis.DataSet {
            const data = new vis.DataSet()
            const source = this.model.data_source
            for (let i = 0; i < source.get_length()!; i++) {
            data.add({
                x: source.data[this.model.x][i],
                y: source.data[this.model.y][i],
                z: source.data[this.model.z][i],
            })
            }
            return data
        }

        get child_models(): LayoutDOM[] {
            return []
        }

        _update_layout(): void {
            this.layout = new LayoutItem()
            this.layout.set_sizing(this.box_sizing())
        }
        }

        // We must also create a corresponding JavaScript BokehJS model subclass to
        // correspond to the python Bokeh model subclass. In this case, since we want
        // an element that can position itself in the DOM according to a Bokeh layout,
        // we subclass from ``LayoutDOM``
        export namespace Surface3d {
        export type Attrs = p.AttrsOf<Props>

        export type Props = LayoutDOM.Props & {
            x: p.Property<string>
            y: p.Property<string>
            z: p.Property<string>
            data_source: p.Property<ColumnDataSource>
        }
        }

        export interface Surface3d extends Surface3d.Attrs {}

        export class Surface3d extends LayoutDOM {
        properties: Surface3d.Props
        __view_type__: Surface3dView

        constructor(attrs?: Partial<Surface3d.Attrs>) {
            super(attrs)
        }

        // The ``__name__`` class attribute should generally match exactly the name
        // of the corresponding Python class. Note that if using TypeScript, this
        // will be automatically filled in during compilation, so except in some
        // special cases, this shouldn't be generally included manually, to avoid
        // typos, which would prohibit serialization/deserialization of this model.
        static __name__ = "Surface3d"

        static {
            // This is usually boilerplate. In some cases there may not be a view.
            this.prototype.default_view = Surface3dView

            // The @define block adds corresponding "properties" to the JS model. These
            // should basically line up 1-1 with the Python model class. Most property
            // types have counterparts, e.g. ``bokeh.core.properties.String`` will be
            // ``String`` in the JS implementatin. Where the JS type system is not yet
            // as rich, you can use ``p.Any`` as a "wildcard" property type.
            this.define<Surface3d.Props>(({String, Ref}) => ({
            x:            [ String ],
            y:            [ String ],
            z:            [ String ],
            data_source:  [ Ref(ColumnDataSource) ],
            }))
        }
        }
        """

        # This custom extension model will have a DOM view that should layout-able in
        # Bokeh layouts, so use ``LayoutDOM`` as the base class. If you wanted to create
        # a custom tool, you could inherit from ``Tool``, or from ``Glyph`` if you
        # wanted to create a custom glyph, etc.
        class Surface3d(LayoutDOM):

            # The special class attribute ``__implementation__`` should contain a string
            # of JavaScript code that implements the browser side of the extension model.
            __implementation__ = TypeScript(TS_CODE)

            # Below are all the "properties" for this model. Bokeh properties are
            # class attributes that define the fields (and their types) that can be
            # communicated automatically between Python and the browser. Properties
            # also support type validation. More information about properties in
            # can be found here:
            #
            #    https://docs.bokeh.org/en/latest/docs/reference/core/properties.html#bokeh-core-properties

            # This is a Bokeh ColumnDataSource that can be updated in the Bokeh
            # server by Python code
            data_source = Instance(ColumnDataSource)

            # The vis.js library that we are wrapping expects data for x, y, and z.
            # The data will actually be stored in the ColumnDataSource, but these
            # properties let us specify the *name* of the column that should be
            # used for each field.
            x = String()

            y = String()

            z = String()


        x = np.arange(0,espacement_x[-1]+50,50)
        y = np.arange(0,espacement_y[-1]+50,50)
        xx, yy = np.meshgrid(x, y)
        xx = xx.ravel()
        yy = yy.ravel()
        value = data.to_numpy()
        source = ColumnDataSource(data=dict(x=xx, y=yy, z=value))

        surface = Surface3d(x="x", y="y", z="z", data_source=source, width=10000, height=10000)

        show(surface)
        st.session_state.graph3d=False