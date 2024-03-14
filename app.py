import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from dash_daq import Gauge
 
import plotly.express as px
import pandas as pd
import numpy as np
import json
import requests
import base64
 
 
app = dash.Dash(__name__, title='Sun Safety',suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP, "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css"])
 
uv_image_path ='./UV-recommend.png'

weather_app_key = "your_api_key_here"
 
with open("./postcodes.json", "r") as f:
    dict_postcode = json.load(f)
 
sunscreen_df = pd.read_csv('sunscreen_data.csv')
cancer_df = pd.read_csv('cancer_data.csv')
uv_df = pd.read_csv('uv_data.csv')
 
def b64_image(img):
    with open(img, 'rb') as f:
        image = f.read()
    return 'data:image/png;base64,' + base64.b64encode(image).decode('utf-8')
 
def home_page_content():
    return html.Div([
        dbc.Row([
           html.Div([
                html.H1("Welcome to the Sun Safety App", className='text-center'),
                html.P("Get informed about UV levels and learn how to protect yourself.", className='text-center')
           ])
        ]),
        dbc.Row([
            dbc.Col(html.Div([
                html.Img(src=b64_image('sunsafe.png'), style={'max-width': '100%', 'height': 'auto', 'padding': '20px'}),
            ]), width=6, style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'}),
            dbc.Col(html.Div([
                html.Div([
                    dcc.Input(id='postcode-input', type='text', placeholder='Enter postcode...', className='mb-2',
                              style={'border': '2px solid #007bff', 'borderRadius': '4px', 'padding': '10px', 'height': '38px', 'display': 'inline-block', 'verticalAlign': 'middle'}),
                    dbc.Button('Submit', id='submit-postcode', n_clicks=0, color='primary', className='mb-2 ml-2',
                               style={
                                   'background-color': '#020008',
                                   'color': 'white',
                                   'border': 'none',
                                   'padding': '7px 20px',
                                   'cursor': 'pointer',
                                   'borderRadius': '4px',
                                   'height': '38px',
                                   'display': 'inline-block', 'verticalAlign': 'middle'}),
                ], style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center', 'marginTop': '150px'}),
                html.Div(id='uv-index-output', className='mt-3')
            ]), width=6),
        ])
    ])
 
 
gender_options = [{'label': 'Male', 'value': 'male'}, {'label': 'Female', 'value': 'female'}, {'label': 'Prefer not to say', 'value': 'both'}]
water_resistent_options = [{'label': 'Yes', 'value': 'yes'}, {'label': 'No', 'value': 'no'}]
sensitive_skin_options = [{'label': 'Yes', 'value': 'yes'}, {'label': 'No', 'value': 'no'}]
 
 
app.layout = html.Div([
    dbc.NavbarSimple(
        children=[
            # Your navbar children here
            dbc.NavItem(html.Img(src=b64_image('logo.png'), height="47px", style={'marginRight': '10px'})),
            dbc.NavItem(dbc.NavLink([html.I(className="fas fa-home mr-1"), "  Home"], href="#", id='home')),
            dbc.NavItem(dbc.NavLink([html.I(className='fas fa-shield-alt mr-1'), "  Recommendations"], href="#", id='recommendations')),
            dbc.NavItem(dbc.NavLink([html.I(className='fas fa-info-circle mr-1'), "  More Information"], href="#", id='more-info'))
        ],
        brand="Sun Safety App",
        brand_href="#",
        color="dark",
        dark=True,
        className='navbar',  # Apply custom class for styling
        style={'height': '80px'}  # Increase navbar height
    ),
    html.Div(id='content', children=home_page_content(), style={'margin-top': '20px'}),  # Initialize with home_page_content
    html.Div(id='stored-uv-index', style={'display': 'none'})  # Hidden div for storing UV index
])

@app.callback(
    Output('content', 'children'),
    [Input('home', 'n_clicks'), Input('recommendations', 'n_clicks'), Input('more-info', 'n_clicks')],
    prevent_initial_call=True
)
def render_page_content(home_clicks, recommendations_clicks, more_info_clicks):
    ctx = dash.callback_context
 
    if not ctx.triggered:
        return home_page_content()
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
 
        if button_id == "home":
            return home_page_content()
        elif button_id == "recommendations":
            return dbc.Row([
                dbc.Col(html.Div([
                    html.Img(src=b64_image(uv_image_path))
                ]), width=6, style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'}),
                dbc.Col([
                    html.Div(id='recommendation-icons'),
                    html.H3('Enter your details to get recommendations:'),
                    html.Label("Gender:"),
                    dcc.Dropdown(id='gender-dropdown', options=gender_options, value='male'),
                    html.Label("Water Resistant:"),
                    dcc.Dropdown(id='water-dropdown', options=water_resistent_options, value='yes'),
                    html.Label("Sensitive Skin:"),
                    dcc.Dropdown(id='skin-dropdown', options=sensitive_skin_options, value='no'),
                    html.Label("Age:"),
                    dcc.Input(id='age-input', type='number', placeholder='Enter your age...'),
                    html.Button('Get Recommendations', id='get-recommendations', n_clicks=0),
                    html.Div(id='recommendations-output')
                ], width=6)  # Adjusted width for balance
            ])
        elif button_id == "more-info":
            return html.Div([
                # Contents of the more information page
                html.H1("More Information", className='text-center'),
                html.P("Learn more about UV radiation and why sun protection is crucial.", className='text-center'),
                html.P("Australia faces a critical challenge with its high levels of ultraviolet (UV) radiation, directly impacting the health of its residents. This region's unique geographic and atmospheric conditions expose individuals to some of the highest UV radiation levels worldwide, significantly increasing the risk of skin cancer. Statistics reveal a stark reality: two in three Australians will be diagnosed with skin cancer by the age of 70, a rate that far surpasses many other countries. The correlation between prolonged UV exposure and the prevalence of skin cancer types, such as melanoma, basal cell carcinoma, and squamous cell carcinoma, underscores the urgent need for heightened awareness and preventive measures. As Australians grapple with this pervasive health issue, adopting comprehensive sun protection strategies, including the use of broad-spectrum sunscreen, wearing protective clothing, and seeking shade, becomes imperative to mitigate the risks associated with the nation's high UV radiation levels", className='text-auto'),
                html.P("PBJ",className='text-auto')

            ])
    return html.Div("Page content")
 
@app.callback(
    [Output('uv-index-output', 'children'),
     Output('stored-uv-index', 'children')],
    [Input('submit-postcode', 'n_clicks')],
    [State('postcode-input', 'value')]
)
def update_uv_index(n_clicks, postcode):
    if n_clicks > 0 and postcode:
        uv_index = get_uv_index(postcode)
        return (
            html.Div([
                html.H4(f'UV Index for {postcode}: {uv_index}', style={'textAlign': 'center'}),
                html.Div([  # Wrap the Gauge in a div and apply text-align style to center it
                    Gauge(color={"gradient": True, "ranges": {"green": [0, 3], "yellow": [3, 6], "orange": [6, 8], "red": [8, 12]}},
                          value=uv_index, max=12, min=0),
                    # html.P("Would you like recommendations for this UV index?"),
                    dcc.Link("Would you like recommendations for this UV index?", href='/recommendations', style={'display': 'block', 'textAlign': 'center'})
                ], style={'textAlign': 'center'}),
            ]),
            str(uv_index)  # Store UV index as a string
        )
    return None, None
 
 
@app.callback(
    Output('recommendation-icons', 'children'),
    [Input('uv-index-output', 'children')],
    prevent_initial_call=True
)
def display_recommendation_icons(uv_index):
    if uv_index:
        icons = []
 
        uvi = float(uv_index)
        # Define the common base class for Font Awesome 5 solid icons
        base_class = "fas fa-"
       
        # Common icons
        icons.extend([
            dbc.Col(html.I(className=f"{base_class}sunglasses", style={"fontSize": "24px"}), width="auto"),
            dbc.Col(html.I(className=f"{base_class}cloud-sun", style={"fontSize": "24px"}), width="auto")
        ])
       
        # UV Index-specific icons
        if uvi < 3:
            pass  # No extra icons for UVI < 3
        elif uvi < 6:
            icons.append(dbc.Col(html.I(className=f"{base_class}sun", style={"fontSize": "24px"}), width="auto"))
        elif uvi < 9:
            icons.extend([
                dbc.Col(html.I(className=f"{base_class}sun", style={"fontSize": "24px"}), width="auto"),
                dbc.Col(html.I(className=f"{base_class}umbrella", style={"fontSize": "24px"}), width="auto")
            ])
        else:
            icons.extend([
                dbc.Col(html.I(className=f"{base_class}sun", style={"fontSize": "24px"}), width="auto"),
                dbc.Col(html.I(className=f"{base_class}umbrella", style={"fontSize": "24px"}), width="auto"),
                dbc.Col(html.I(className=f"{base_class}home", style={"fontSize": "24px"}), width="auto")
            ])
       
        # Return a row with all icons as columns
        return dbc.Row(icons, className="gy-4", align="center", justify="start")
       
    return "UV index not available"
 
 
@app.callback(
    Output('recommendations-output', 'children'),
    [Input('get-recommendations', 'n_clicks')],
    [State('gender-dropdown', 'value'), State('water-dropdown', 'value'),
     State('skin-dropdown', 'value'), State('stored-uv-index', 'children'),
     State('age-input', 'value')]
)
def update_recommendations(n_clicks, gender, water_resistant, sensitive_skin, uv_index, age):
    if n_clicks > 0:
        if uv_index is None:
            return "Please calculate UV index in Tab 1 first."
       
        uv_index = float(uv_index)  # Convert the uv_index to float since it's passed as a string
        age = int(age)  # Ensure age is treated as an integer for comparison
   
        if age in np.arange(0, 13, 1):
            age_group = 'kid'
        elif age in np.arange(13, 25, 1) :
            age_group = 'young adult'
        elif age in np.arange(25, 51, 1):
            age_group = 'adult'
        else:
            age_group = 'old'
   
        if sensitive_skin == 'yes':
            formulation = ['mineral']
        elif sensitive_skin == 'no':
            formulation = ['mineral', 'chemical']
 
        spf = 50
        if uv_index in np.arange(0, 3, 1):
            spf = None
            return "No sunscreen required!"
        elif uv_index in np.arange(3, 6, 1):
            spf = 15
        elif uv_index in np.arange(6, 9, 1):
            spf = 30
        elif uv_index in np.arange(9, 12, 1):
            spf = 50
       
        if gender == 'male':
            filtered_gender = ['male']
        elif gender == 'female':
            filtered_gender = ['female']
        elif gender == 'both':
            filtered_gender = ['male', 'female']
   
        filtered_df = sunscreen_df[(sunscreen_df['gender'].isin(filtered_gender)) &
                        (sunscreen_df['water_resistant'] == water_resistant) &
                        (sunscreen_df['formulation'].isin(formulation)) &
                        (sunscreen_df['age_group'] == age_group) &
                        (sunscreen_df['spf'] >= spf)]  # Filter based on UV index
   
        if filtered_df.empty:
            return "No sunscreen matches the selected criteria."
        else:
            sunscreen_names = filtered_df['sunscreen'].unique()
            return html.Ul([html.Li(sunscreen_name) for sunscreen_name in sunscreen_names], style={'padding-left': '20px'})
       
    return "Please calculate UV index in Tab 1 and enter all information."
 
@app.callback(
    [Output('cancer-analysis', 'figure'), Output('uv-analysis', 'figure')],
    [Input('tabs', 'value')]
)
def update_analysis(tab):
    if tab == 'tab-3':
        fig1 = px.line(cancer_df, x="Year", y="Count", title="Cancer Cases Over Time")
        fig2 = px.line(uv_df, x="Year", y="Mean UV Index", title="UV Index Over Time")
        return fig1, fig2
    return {}, {}
 
def get_uv_index(postcode):
    # Placeholder for the actual API call to get UV index
    # You need to replace this with the real API call
    import random
    return round(random.uniform(0, 10), 2)
 
if __name__ == '__main__':
    app.run_server(debug=True)
