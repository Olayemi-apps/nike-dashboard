import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd

font_awesome = "https://use.fontawesome.com/releases/v5.10.2/css/all.css"


shoes = pd.read_csv(r'C:\Users\Admin\Desktop\Plotly_Dashboards\New_Improved\data\shoes_dataset_updated.csv')

# Best_selling_region = shoes.groupby(['Date'])[['Re_Sale_Price', 'Buyer_Region']].sum().reset_index()
best_selling_region = shoes.groupby(['year', 're_sale_price'], as_index=True).agg({'buyer_region': ' '.join})

# Best Selling Region 2020
best_selling_region['buyer_region'].iloc[-1]

# Average resell Price - Also rounded to 2 decimal places
avg_resell_price = round(shoes['re_sale_price'].mean(), 2)

# Total Reseller Sales Total
shoes_reseller_total = shoes['re_sale_price'].sum()

# Total Sales Profit
shoes_profit_total = shoes['profit'].sum()


# Map information turned into a dictionary

shoes_list = shoes[['buyer_state', 'longitude', 'latitude']]
locations_dict = shoes_list.set_index('buyer_state')[['longitude', 'latitude']].T.to_dict('dict')

# Total Re_seller Sales
shoes_reseller_total = shoes['re_sale_price'].sum()

external_stylesheets = [
    'https://fonts.googleapis.com/css2?family=Roboto&display=swap',
]


app = dash.Dash(__name__, external_stylesheets=external_stylesheets,
                meta_tags=[{"name": "viewport", "content": "width=device-width"}])


app.layout = html.Div([
    html.Div([
        html.Div([
            html.Div([
                html.H3('Nike Sneaker Dashboard', style={'fontSize': 50,'margin-bottom': '0px', 'color': '#010915'}),
                html.H6('Regional Sales from 2017 - 2020', style={'fontSize': 35,'margin-top': '5px', 'color': '#010915'})
            ])
        ], className='six column', id='title')
    ], id='header', className="row-flex-display", style={'margin-bottom': '15px'}),

    # 1st Row

    html.Div([
        html.Div([
            html.Img(src='/assets/nike_logo_v2.png'),

        ], className='logo_container three columns'),

    ], className='row flex-display'),

    # 2nd  Row
    html.Div([
        html.Div([
            html.H6('Best Region in 2020', style={'color': 'white'}),
            html.P(f"{best_selling_region['buyer_region'].iloc[-1]}",
                   style={'fontSize': 40, 'color': 'white'})

        ], className='container_2_text_box three columns'),

        html.Div([
            html.H6('Average  Re Seller Price', style={'color': 'white'}),
            html.P(f"${avg_resell_price}",
                           style={'fontSize': 40, 'color': 'white'})

        ], className='container_2_text_box three columns'),

        html.Div([
            html.H6('Total Re Seller Sales', style={'color': 'white'}),
            html.P(f"${shoes_reseller_total:,.0f}",
                   style={'fontSize': 40, 'color': 'white'})

        ], className='container_2_text_box three columns'),

        html.Div([
            html.H6('Total Sales Profit', style={'color': 'white'}),
            html.P(f"${shoes_profit_total:,.0f}",
                   style={'fontSize': 40, 'color': 'white'})

        ], className='container_2_text_box three columns')

    ], className='row flex-display'),

    # 3rd Row
    html.Div([
        html.Div([
            html.P('Select Buyer Region', className='new_label', style={'color': 'white'}),
            dcc.Dropdown(id='b_region',
                         multi=False,
                         searchable=True,
                         value='Northeast',
                         placeholder='Select Region',
                         options=[{'label': c, 'value': c}
                                  for c in (shoes['buyer_region'].unique())], className='dcc_comp'),

            html.P('Select Buyer State', className='new_label', style={'color': 'white'}),
            dcc.Dropdown(id='b_state', # Buyer_Region part of Output
                         multi=False,
                         searchable=True,
                         placeholder='Select State',
                         options=[], className='dcc_comp'), # Options part of Output

            html.P('Select Year', className='new_label', style={'color': 'white'}),
            dcc.RangeSlider(id='year_pick',
                                 min=2017,
                                 max=2020,
                                 dots=False,
                                 step=None,
                                 marks={
                                     2017: '2017',
                                     2018: '2018',
                                     2019: '2019',
                                     2020: '2020',
                                 },
                                 value=[2017, 2020]),

        ], className='container_2 three columns'),

        html.Div([
            dcc.Graph(id='stacked_chart', config={'displayModeBar': 'hover'})

        ], className='container_2 six columns'),

        html.Div([
            dcc.Graph(id='donut_chart', config={'displayModeBar': 'hover'})

        ], className='container_2 three columns')

    ], className='row flex-display'),

    html.Div([
        html.Div([
            dcc.Graph(id='usa_state_map', config={'displayModeBar': 'hover'})

        ], className='container_2 twelve columns')

    ], className='row flex-display'),

], id='mainContainer', style={'display': 'flex', 'flex-direction': 'column'})

# CALL BACKS

# USA Map

@app.callback(Output('usa_state_map', 'figure'),
              [Input('b_region', 'value')],
              [Input('b_state', 'value')],
              [Input('year_pick', 'value')])
def usa_map(b_region, b_state, year_pick):
    map = shoes.groupby(['year', 'brand', 'buyer_state', 'buyer_region', 'sales_division', 'sneaker', 'latitude',
                         'longitude'])[['retail', 're_sale_price', 'profit']].sum().reset_index()

    usa_map = map[(map['buyer_region'] == b_region) &
                      (map['buyer_state'] == b_state) &
                      (map['year'] >= year_pick[0]) & (map['year'] <= year_pick[1])]

    if b_state:
        zoom = 3
        zoom_latitude = locations_dict[b_state]['latitude']
        zoom_longitude = locations_dict[b_state]['longitude']

    return {
        'data': [go.Scattermapbox(
            lon=usa_map['longitude'],
            lat=usa_map['latitude'],
            mode='markers',
            marker=go.scattermapbox.Marker(size=usa_map['retail'],
                                           color=usa_map['retail'],
                                           colorscale='Twilight',
                                           showscale=False,
                                           sizemode='area',
                                           opacity=0.3),
            hoverinfo='text',
            hovertext=
            '<b>Buyer Region</b>: ' + usa_map['buyer_region'].astype(str) + '<br>' +
            '<b>Buyer State</b>: ' + usa_map['buyer_state'].astype(str) + '<br>' +
            '<b>Buyer Sales Division</b>: ' + usa_map['sales_division'].astype(str) + '<br>' +
            '<b>Buyer Brand</b>: ' + usa_map['brand'].astype(str) + '<br>' +
            '<b>Sneaker</b>: ' + usa_map['sneaker'].astype(str) + '<br>' +
            '<b>Year</b>: ' + usa_map['year'].astype(str) + '<br>' +
            '<b>Retail</b>: ' + [f'${x:,.0f}' for x in usa_map['retail']] + '<br>' +
            '<b>Re Sale Price</b>: ' + [f'${x:,.0f}' for x in usa_map['re_sale_price']] + '<br>' +
            '<b>Profit</b>: ' + [f'${x:,.0f}' for x in usa_map['profit']] + '<br>'

        )],

        'layout': go.Layout(
            hovermode='x',
            paper_bgcolor='#1f2c56',
            plot_bgcolor='#1f2c56',
            margin=dict(r=0, l=0, b=0, t=0),
            mapbox=dict(
                accesstoken='pk.eyJ1Ijoib2xhMjAyMiIsImEiOiJjbDc0c3dobG8wd292M25tYWh5aWR6bXl2In0.maBGd0Cjyl6G3HkpwRI-RA',
                center= go.layout.mapbox.Center(lat = zoom_latitude, lon = zoom_longitude),
                style='dark',
                zoom=zoom,
            ),
            autosize=True
        )

    }

# Chained callback

@app.callback(Output('b_state', 'options'),
             [Input('b_region', 'value')]) # From the top dropdown list
def update_buyer_info(b_region): # Key Value of the Input id
    dp_process = shoes[shoes['buyer_region'] == b_region] #  == Filters the Buyer_State column using 1st dropdown id
    return [{'label': i, 'value': i} for i in dp_process['buyer_state'].unique()]

# Chained Callback

@app.callback(Output('b_state', 'value'), # Automatically Sets Buyer State value in the first dropdown list
              [Input('b_state', 'options')])
def update_buyer_info(b_state):
    return [b['value'] for b in b_state][0]

# Stacked line and Barchart

@app.callback(Output('stacked_chart', 'figure'),
              [Input('b_region', 'value')],
              [Input('b_state', 'value')],
              [Input('year_pick', 'value')])
def update_stack(b_region, b_state, year_pick):
    s_barchart = shoes.groupby(['buyer_region', 'buyer_state', 'year'])[['retail',
                                                                         're_sale_price', 'profit']].sum().reset_index()
    dff = s_barchart[(s_barchart['buyer_region'] == b_region) &
                      (s_barchart['buyer_state'] == b_state) &
                      (s_barchart['year'] >= year_pick[0]) & (s_barchart['year'] <= year_pick[1])]

    return {
        'data': [go.Scatter(
            x=dff['year'],
            y=dff['retail'],
            mode='markers+lines',
            name='Retail Prices',
            line=dict(shape='spline', smoothing=1.3, width=3, color='#1f2c56'),
            marker=dict(color='white', size=10, symbol='circle',
                        line=dict(color='#E71D36', width=2)),
            hoverinfo='text',
            hovertext=
            '<b>Buyer Region</b>: ' + dff['buyer_region'].astype(str) + '<br>' +
            '<b>Buyer State</b>: ' + dff['buyer_state'].astype(str) + '<br>' +
            '<b>Year</b>: ' + dff['year'].astype(str) + '<br>' +
            '<b>Retail</b>: ' + [f'${x:,.0f}' for x in dff['retail']] + '<br>' +
            '<b>Re Sale Price</b>: ' + [f'{x:,.0f}' for x in dff['re_sale_price']] + '<br>' +
            '<b>Profit</b>: ' + [f'${x:,.0f}' for x in dff['profit']] + '<br>'

        ),
        go.Bar(
            x=dff['year'],
            y=dff['re_sale_price'],
            text=dff['re_sale_price'],
            texttemplate='%{text:,.0f}',
            textposition='auto',
            name='Total Resale Prices per Reg/State',
            marker=dict(color='white'),
            hoverinfo='text',
            hovertext=
            '<b>Buyer Region</b>: ' + dff['buyer_region'].astype(str) + '<br>' +
            '<b>Buyer State</b>: ' + dff['buyer_state'].astype(str) + '<br>' +
            '<b>Year</b>: ' + dff['year'].astype(str) + '<br>' +
            '<b>Re Sale Price</b>: ' + [f'${x:,.0f}' for x in dff['re_sale_price']] + '<br>' +
            '<b>Profit</b>: ' + [f'${x:,.0f}' for x in dff['profit']] + '<br>',
        ),

        go.Bar(
            x=dff['year'],
            y=dff['profit'],
            text=dff['profit'],
            texttemplate='%{text:,.0f}',
            textposition='auto',
            name='Total Profit per Reg/State',
            marker=dict(color='#0496FF'),
            hoverinfo='text',
            hovertext=
            '<b>Buyer Region</b>: ' + dff['buyer_region'].astype(str) + '<br>' +
            '<b>Buyer State</b>: ' + dff['buyer_state'].astype(str) + '<br>' +
            '<b>Year</b>: ' + dff['year'].astype(str) + '<br>' +
            '<b>Profit</b>: ' + [f'${x:,.0f}' for x in dff['profit']] + '<br>',
        ),

        go.Bar(
            x=dff['year'],
            y=dff['retail'],
            text=dff['retail'],
            texttemplate='%{text:,.0f}',
            textposition='auto',
            name='Total Retail Price per Reg/State',
            marker=dict(color='#E71D36'),
            hoverinfo='text',
            hovertext=
            '<b>Buyer Region</b>: ' + dff['buyer_region'].astype(str) + '<br>' +
            '<b>Buyer State</b>: ' + dff['buyer_state'].astype(str) + '<br>' +
            '<b>Year</b>: ' + dff['year'].astype(str) + '<br>' +
            '<b>Retail</b>: ' + [f'${x:,.0f}' for x in dff['retail']] + '<br>',
        ),
        ],

        'layout': go.Layout(
            barmode='stack',
            title={'text': 'Sneaker Sales Analysis by State: ' +(b_state)+ ' ' + ' '
                   + ' - ' .join([str(x) for x in year_pick]),
                   'y': 0.93,
                   'x': 0.5,
                   'xanchor': 'center',
                   'yanchor': 'top'},
            titlefont={'color': 'white',
                       'size': 16},
            font=dict(family='Roboto',
                      color='white',
                      size=12),
            hovermode='closest',
            paper_bgcolor='#006BA6',
            plot_bgcolor='#006BA6',
            legend={'orientation': 'h',
                    'bgcolor': '#006BA6',
                    'xanchor': 'center', 'x': 0.5, 'y': -0.2},
            margin=dict(b=1, r=0),
            xaxis=dict(title='<b>Year</b>',
                       # tick0 =0 and d tick=1  will take out the half values from the x axis
                       tick0=0,
                       dtick=1,
                       color='white',
                       showline=True,
                       showgrid=True,
                       showticklabels=True,
                       linecolor='white',
                       linewidth=1,
                       ticks='outside',
                       tickfont=dict(
                           family='Aerial',
                           color='white',
                           size=12
                       )),
            yaxis=dict(title="<b>Retail Price</b>",
                       color='white',
                       showline=True,
                       showgrid=True,
                       showticklabels=True,
                       linecolor='white',
                       linewidth=1,
                       ticks='outside',
                       tickfont=dict(
                           family='Aerial',
                           color='white',
                           size=12
                       ))
        )
    }

@app.callback(Output('donut_chart', 'figure'),
              [Input('b_state', 'value')],
              [Input('b_region', 'value')],
              [Input('year_pick', 'value')])
def update_pie_chart(b_state, b_region, year_pick):
    donut_chart = shoes.groupby(['buyer_region', 'buyer_state', 'year'])[['retail', 're_sale_price', 'profit']]\
        .sum().reset_index()
    # This Dataframe will give the TOTAL value for retail prices
    retail = donut_chart[(donut_chart['buyer_region'] == b_region) &
                     (donut_chart['buyer_state'] == b_state) &                          # Helps to get total value of retail
                     (donut_chart['year'] >= year_pick[0]) & (donut_chart['year'] <= year_pick[1])]['retail'].sum()

    # This Dataframe will give the TOTAL value for re sales prices
    re_sale = donut_chart[(donut_chart['buyer_region'] == b_region) &
                     (donut_chart['buyer_state'] == b_state) &  # Helps to get total value of retail
                     (donut_chart['year'] >= year_pick[0]) & (donut_chart['year'] <= year_pick[1])]['re_sale_price'].sum()

    # This Dataframe will give the TOTAL value for profit
    profit = donut_chart[(donut_chart['buyer_region'] == b_region) &
                          (donut_chart['buyer_state'] == b_state) &  # Helps to get total value of profit
                          (donut_chart['year'] >= year_pick[0]) & (donut_chart['year'] <= year_pick[1])]['profit'].sum()

    # Colors for slices
    colors = ['#E71D36', '#F2743C', 'yellow']

    return {
        'data': [go.Pie(
            labels=['Total retail prices', 'Total re sale prices', ' Total profits'],
            values=[retail, re_sale, profit],
            marker=dict(colors=colors),
            texttemplate="%{label}:<br> %{value:$,.0f}<br>(%{percent})",
            hoverinfo='label+value+percent',
            textinfo='label+value',
            hole=.7,
            rotation=45,

        )],

        'layout': go.Layout(
            title={'text': 'Total Sales Analysis for all States: ' + (b_state) + ' ' + ' '
                           + ' - '.join([str(x) for x in year_pick]),
                   'y': 0.93,
                   'x': 0.5,
                   'xanchor': 'center',
                   'yanchor': 'top'},
            titlefont={'color': 'white',
                       'size': 14},
            font=dict(family='Roboto',
                      color='white',
                      size=12),
            hovermode='closest',
            paper_bgcolor='#006BA6',
            plot_bgcolor='#006BA6',
            legend={'orientation': 'h',
                    'bgcolor': '#006BA6',
                    'xanchor': 'center', 'x': 0.5, 'y': -0.7},

       ),
    }

if __name__ == '__main__':
    app.run_server(debug=False, host="0.0.0.0", port=8080)   # For Production Debug=False


