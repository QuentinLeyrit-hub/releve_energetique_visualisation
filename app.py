import base64
import datetime
import io
import dash
from dash.dependencies import Input, Output, State
from dash import dcc, html, dash_table
import plotly_express as px

import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

app.layout = html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '1250px',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '0px'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
    html.Div(id='output-data-upload'),
])

def preprocess(ds):
    ds = ds.iloc[3:]
    ds = ds.drop(ds.columns[2 : ], axis=1)
    ds.columns = ['Date', 'Kw']
    ds.reset_index(drop=True, inplace=True)
    ds['Kw'] = ds['Kw'].fillna(0)
    ds['Kw'] = ds['Kw'].astype('int32')
    ds['Date'] = ds['Date'].str.replace('T', ' ')
    ds['Date'] = ds['Date'].str.replace("\+01:00", "")
    ds['Date'] =  pd.to_datetime(ds['Date'], format="%Y-%m-%d %H:%M:%S")

    """
    for i in range(len(ds)):
        ds['Annee'][i] = ds['Date'][i].year
        ds['Mois'][i] = ds['Date'][i].month
        ds['Jour'][i] = ds['Date'][i].day
        ds['Heures'][i] = ds['Date'][i].hour
        ds['Minutes'][i] = ds['Date'][i].minute
        ds['Secondes'][i] = ds['Date'][i].second
    """
    return ds

def parse_contents(contents, filename, date):
    
    content_type, content_string = contents.split(',')


    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')), sep=';')
            df = preprocess(df)


            max = "Max: " + str(df['Kw'].max()) + " Kw"

            fig = px.line(df, x="Date", y="Kw", title='Consommation de Kw enregistrée toutes les 10 secondes', width=1255, height=700)

            fig.update_traces(line=dict(color="#00FA9A", width=1.2))

            fig['layout']['title']['font'] = dict(size=20)


            fig.add_hline(y=df['Kw'].max(), line_width=1, opacity=0.6,line_color="red",line_dash="dash",annotation_text= max, 
              annotation_position="top right",  annotation_font_size=12, annotation_font_color="red")

            fig.update_layout(paper_bgcolor="black", plot_bgcolor="black", title_x=0.5, title_y=0.93, title_font_color="white")




            fig.update_xaxes(showgrid=True, gridwidth=0.01, gridcolor='#303030', color = "white", showspikes=True, spikecolor="white", spikethickness=1)
            fig.update_yaxes(showgrid=True, gridwidth=0.01, gridcolor='#303030', color ="white", showspikes=True, spikecolor="white", spikethickness=1)


            

        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
            df = preprocess(df)
    except Exception as e:
        print(e)
        df = preprocess(df)
        return html.Div([
            html.H5(df),
            'There was an error processing this file.'
        ])


    return html.Div([
        html.Div("Fichier sélectionné: " + filename, id = 'filename', style={'fontSize': 15, 'color': 'grey'}),


        dcc.Graph(id ='plot', figure=fig),     


        html.Hr()  # horizontal line

        
    ])

@app.callback(Output('output-data-upload', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))

def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children

if __name__ == '__main__':
    app.run_server(debug=True)