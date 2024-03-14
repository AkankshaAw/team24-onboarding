import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from dash_iconify import DashIconify
from dash_daq import Gauge
 
import plotly.express as px
import pandas as pd
import numpy as np
import json
import requests
import base64
 
 
app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP, "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css"])
 
server = app.server

weather_app_key = "d276224e3f71ea68e06ef05e77dee585"
 
with open("./postcodes 2.json", "r") as f:
    dict_postcode = json.load(f)
 
sunscreen_df = pd.read_csv('sunscreen_data 3.csv')
cancer_df = pd.read_csv('cancer_data 2.csv')
cancer_df['Count'] = cancer_df['Count'].str.replace(',', '').astype(float)
uv_df = pd.read_csv('uv_data 2.csv')
 
def b64_image(img):
    with open(img, 'rb') as f:
        image = f.read()
    return 'data:image/png;base64,' + base64.b64encode(image).decode('utf-8')
 
def home_page_content():
    return html.Div([
        dbc.Row([
           html.Div([
                html.H1("Welcome to the Sun Safety App", className='text-center'),
                html.P("Get informed about UV levels and learn how to protect yourself.", className='text-center'),
           ],style={'margin-top': '80px'})
        ]),
        dbc.Row([
            dbc.Col(html.Div([
                html.Img(src=b64_image('sunsafe.png'), style={'max-width': '100%', 'height': 'auto', 'padding': '20px'}),
            ]), width=6, style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'}),
            dbc.Col(html.Div([
                html.Div([
                    html.P("Please enter your postcode below to see the current UV index:", className='mb-1 text-center'),  # Instructional text
                ], style={'textAlign': 'center','marginTop': '150px'}),
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
                ], style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center'}),
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
        style={'position': 'fixed',
        'top': 0,
        'left': 0,
        'width': '100%',
        'zIndex': 1020,  # Typically enough to stay above other content, adjust if necessary
        'height': '80px'}  # Increase navbar height
    ),
    html.Div(id='content', style={'margin-top': '20px'}),  # Adjust margin-top for content
    html.Div(id='stored-uv-index', style={'display': 'none'}),  # Hidden div for storing UV index
    html.Div(id='navigate-to-recommendations', style={'display': 'none'})
])

def recommendations_page_content():
    return html.Div([
        dbc.Row([
            dbc.Col(html.Div([
                html.H3("Personalized Sunscreen Recommendations", className='text-center'),
                html.P("Fill out the form below to get sunscreen recommendations tailored to your specific needs.", className='text-center mb-4'),
            ],style={'margin-top': '80px'})),
        ]),
        dbc.Row([
            dbc.Col(html.Div(id='icons-output', className='icons-container'), style={'display': 'flex',
                'justify-content':'center',
                'align-items': 'center',
                'padding': '20px'
            })
        ]),
        dbc.Row([
            dbc.Col(width=2), 
            dbc.Col([
                dbc.Form([
                    dbc.Row([
                        dbc.Label("Gender:", className="mt-2"),
                        dcc.Dropdown(id='gender-dropdown', options=gender_options, value='male'),
                    ]),
                    dbc.Row([
                        dbc.Label("Water Resistant:", className="mt-2"),
                        dcc.Dropdown(id='water-dropdown', options=water_resistent_options, value='yes'),
                    ]),
                    dbc.Row([
                        dbc.Label("Sensitive Skin:", className="mt-2"),
                        dcc.Dropdown(id='skin-dropdown', options=sensitive_skin_options, value='no'),
                    ]),
                    dbc.Row([
                        dbc.Label("Age:", className="mt-2"),
                        dcc.Input(id='age-input', type='number', placeholder='Enter your age...', className="form-control"),
                    ]),
                    dbc.Row([
                        html.Button('Get Recommendations', id='get-recommendations', n_clicks=0, className="btn btn-primary mt-3"),
                    ]),
                ]),
            ]),
            dbc.Col(width=2),  # Spacer
        ]),
        dbc.Row([
            dbc.Col(html.Div(id='recommendations-output', className="mt-3"), width={"size": 6, "offset": 3}),
        ])
    ])

sunsmart_title_style = {
    'textAlign': 'center',
    'marginTop': '20px',
    'marginBottom': '40px',
    'color': '#333',
    'margin-top': '80px'
}

recommendation_title_style = {
    'textAlign': 'center',
    'marginBottom': '30px',
    'color': '#555'
}

sunsmart_container_style = {
    'display': 'flex',
    'flexDirection': 'column',
    'alignItems': 'center',
    'margin': 'auto',
    'padding': '20px'
}

sunsmart_section_style = {
    'display': 'flex',
    'flexDirection': 'row',
    'alignItems': 'center',
    'marginBottom': '30px',
    'maxWidth': '800px',
    'border': '1px solid #ddd',
    'borderRadius': '8px',
    'padding': '20px',
    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
}

sunsmart_image_style = {
    'width': '150px',
    'height': 'auto',
    'marginRight': '20px'
}

sunsmart_text_style = {
    'fontSize': '16px',
    'color': '#666',
    'flexGrow': '1'
}

sunsmart_mark_style = {
    'fontSize': '16px',
    'color': '#666',
    'flexGrow': '1',
    'padding': '150px'
}


def more_information_content():
    fig = px.bar(cancer_df, x='Year', y='Count', title='Count of Melanoma Each Year In Victoria')
    

    
    return html.Div([
        html.H1("Understanding SunSmart and UV Protection", style=sunsmart_title_style),
        dbc.Row([
            dbc.Col(html.Div([
                # Display the local GIF file using html.Img
                html.Img(src='/assets/Hello-sun-gif.gif', style={'width': '200px',  # Adjust width as needed
                                'height': 'auto'}),  # Keeps the aspect ratio intact
            ]), width=12, style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'}),
        ]),
        dcc.Markdown('''
            **SunSmart Practices and UV Radiation**
            
            Ultraviolet (UV) radiation from the sun is the main cause of skin cancer. UV damage also causes sunburn, tanning, premature ageing, and eye damage. Understanding and adopting SunSmart practices from a young age is crucial in minimizing these risks.
            
            **The Impact of UV on Younger Individuals**
            
            Young skin is more susceptible to UV damage, which can lead to serious skin conditions in later life. It's important to educate children and young adults about the risks of UV exposure and the importance of sun protection.
        ''', style=sunsmart_mark_style),
        html.Div([
            html.Img(src=b64_image('umberlla_img.png'), style=sunsmart_image_style),
            dcc.Markdown('''
                **Seek Shade:** Limit direct sun exposure during peak UV times, usually between 10 AM and 4 PM.
            ''', style=sunsmart_text_style),
        ], style=sunsmart_section_style),
        html.Div([
            html.Img(src=b64_image('clothes_protective.png'), style=sunsmart_image_style),
            dcc.Markdown('''
                **Wear Protective Clothing:** Long-sleeved shirts, pants, and broad-brimmed hats offer good protection.
            ''', style=sunsmart_text_style),
        ], style=sunsmart_section_style),
        html.Div([
            html.Img(src=b64_image('sunscreen_img.png'), style=sunsmart_image_style),
            dcc.Markdown('''
                **Apply Sunscreen:** Use broad-spectrum sunscreen with an SPF of 30 or higher. Reapply every two hours, or more often if swimming or sweating.
            ''', style=sunsmart_text_style),
        ], style=sunsmart_section_style),
        html.Div([
            html.Img(src=b64_image('sunglasses_img.png'), style=sunsmart_image_style),
            dcc.Markdown('''
                **Wear Sunglasses:** Protect your eyes with sunglasses that block out 99% to 100% of both UVA and UVB radiation.
            ''', style=sunsmart_text_style),
        ], style=sunsmart_section_style),
        html.Div([
            html.Img(src=b64_image('sand_water.png'), style=sunsmart_image_style),
            dcc.Markdown('''
                **Be Extra Careful Near Water, Sand, and Snow:** These surfaces can reflect the sun’s rays and increase the chance of sunburn.
            ''', style=sunsmart_text_style),
        ], style=sunsmart_section_style),
        dcc.Markdown('''
            **Educational Resources:**

            For more information on SunSmart practices and resources for education and prevention, visit [Cancer Council's SunSmart Website](https://www.sunsmart.com.au).

            **Visualizing the Impact of UV Exposure:**

            The following graph shows the annual count of skin cancer cases, highlighting the critical need for effective sun protection strategies from a young age.
        ''', style=sunsmart_text_style),
        dcc.Graph(figure=fig, className='sunsmart-graph'),
    ], style=sunsmart_container_style)
     
@app.callback(
    Output('content', 'children'),
    [Input('home', 'n_clicks'), Input('recommendations', 'n_clicks'), Input('more-info', 'n_clicks'),
     Input('navigate-to-recommendations', 'children')],  
    prevent_initial_call=False
)

def render_page_content(home_clicks, recommendations_clicks, more_info_clicks, navigate_flag):
    ctx = dash.callback_context
 
    if not ctx.triggered:
        return home_page_content()
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
 
        if button_id == "home":
            return home_page_content()
        elif button_id == "recommendations":
            return recommendations_page_content()
        elif button_id == "more-info":
            return more_information_content()
        elif navigate_flag == "recommendations":
            return recommendations_page_content()
    return html.Div("Page content")

@app.callback(
    Output('navigate-to-recommendations', 'children'),
    [Input('navigate-recommendations-btn', 'n_clicks')]
)
def trigger_navigation(n_clicks):
    if n_clicks and n_clicks > 0:
        return "recommendations"  
    return dash.no_update


def update_uv_index(n_clicks, postcode):
    if n_clicks > 0 and postcode:
        uv_index = get_uv_index(postcode)
        return (
            html.Div([
                html.H4(f'UV Index for {postcode}: {uv_index}', style={'textAlign': 'center'}),
                html.Div([
                    Gauge(color={"gradient": True, "ranges": {"green": [0, 3], "yellow": [3, 6], "orange": [6, 8], "red": [8, 12]}},
                          value=uv_index, max=12, min=0),
                    dbc.Button("Would you like recommendations for this UV index?", id="navigate-recommendations-btn", className="mt-3", color="primary", style={'display': 'block', 'margin': 'auto'})
                ], style={'textAlign': 'center'}),
            ]),
            str(uv_index)
        )
    return None, None
 
@app.callback(
    [Output('uv-index-output', 'children'),
     Output('stored-uv-index', 'children')],
    [Input('submit-postcode', 'n_clicks')],
    [State('postcode-input', 'value')]
)
def update_uv_index(n_clicks, postcode):
    if n_clicks > 0 and postcode:
        uv_index = get_uv_index(postcode)
        if uv_index == "Invalid postcode":
            return (
                html.Div("Invalid postcode!", style={'textAlign': 'center', 'color': 'red'}),
                None
            )
        else:
            return (
                html.Div([
                    html.H4(f'UV Index for {postcode}: {uv_index}', style={'textAlign': 'center'}),
                    html.Div([
                        Gauge(color={"gradient": True, "ranges": {"green": [0, 3], "yellow": [3, 6], "orange": [6, 8], "red": [8, 12]}},
                              value=uv_index, max=12, min=0),
                        dbc.Button("Would you like recommendations for this UV index?", id="navigate-recommendations-btn", className="mt-3", color="primary", style={'display': 'block', 'margin': 'auto'})
                    ], style={'textAlign': 'center'}),
                ]),
                str(uv_index)
            )
    return None, None
 
 
@app.callback(
    Output('icons-output', 'children'),  
    [Input('stored-uv-index', 'children')] 
)

def display_recommendation_icons(uv_index):
    if uv_index:
        uvi = float(uv_index)
        if uvi < 3:
            return [DashIconify(icon="bi:sunglasses", width=50), DashIconify(icon="bi:cloud-sun", width=50)]
        elif uvi < 6:
            return [DashIconify(icon="bi:sunglasses", width=50), DashIconify(icon="bi:cloud-sun", width=50), DashIconify(icon="bi:brightness-high", width=50)]
        elif uvi < 9:
            return [DashIconify(icon="bi:sunglasses", width=50), DashIconify(icon="bi:cloud-sun", width=50), DashIconify(icon="bi:brightness-high", width=50), DashIconify(icon="bi:umbrella", width=50)]
        else:
            return [DashIconify(icon="bi:sunglasses", width=50), DashIconify(icon="bi:cloud-sun", width=50), DashIconify(icon="bi:brightness-high", width=50), DashIconify(icon="bi:umbrella", width=50), DashIconify(icon="bi:house", width=50)]
    return " "

def update_icons(uv_index):
    if uv_index is not None:
        return display_recommendation_icons(uv_index)
    return []
 
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
    postcode = str(postcode)
    if postcode not in dict_postcode:
        return "Invalid postcode"
    lat = dict_postcode.get(postcode, {}).get("lat")
    long = dict_postcode.get(postcode, {}).get("long")
    
    uvi_response = requests.get(f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={long}&exclude=hourly,daily&appid={weather_app_key}").json()
    # Extract the UV index from the response and return it
    uvi = uvi_response.get("current", {}).get("uvi")
    return uvi
 
if __name__ == '__main__':
    app.run_server(debug=True)