import dash
from dash import dash_table
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import datetime
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import base64
import yfinance as yf
import dash_auth
from stocks_import import indexes, df_symbols, df_industries
from tables_styles import style_table, style_cell, style_data, style_header, style_data_conditional_for_recomm

# Login
VALID_USERNAME_PASSWORD_PAIRS = [['naya', 'naya']]
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
auth = dash_auth.BasicAuth(app, VALID_USERNAME_PASSWORD_PAIRS)

msft = yf.Ticker('AAPL')
history_range = msft.history(period="1y")
df_history = history_range.reset_index(drop=False)
df_history['Date'] = pd.to_datetime(df_history['Date']).dt.date
first_open = df_history['Open'].iloc[0]
# Get the last close price
last_close = df_history['Close'].iloc[-1]
# Compare the first open price to the last close price
if first_open < last_close:
    fill_color = 'green'
else:
    fill_color = 'red'

# MACD Analysis
# Calculate the MACD using the close prices
fast_period = 12
slow_period = 26
signal_period = 9
# Calculate the fast and slow moving averages
fast_ma = history_range["Close"].ewm(span=fast_period, adjust=False).mean()
slow_ma = history_range["Close"].ewm(span=slow_period, adjust=False).mean()
# Calculate the MACD line
macd_line = fast_ma - slow_ma
# Calculate the MACD signal line
macd_signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
# Calculate the MACD histogram
macd_hist = macd_line - macd_signal_line
# Create a table to store the results
results = pd.DataFrame(columns=["Analysis", "Description", "Recommendation"])
# Add a row to the table with the results of the MACD analysis
macd_results = pd.concat([results, pd.DataFrame({"Analysis": "MACD",
                                                 "Description": "The MACD is a trend-following momentum indicator that shows the relationship between two moving averages of a stock's price. A bullish MACD indicates that the stock is likely to continue rising, while a bearish MACD indicates that the stock is likely to continue falling.",
                                                 "Recommendation": "Buy" if list(macd_hist)[-1] > 0 else "Sell"}, index=[0])], ignore_index=True)


# Bollinger Bands Analysis
#Calculate the Bollinger Bands using the close prices
timeperiod = 20
nbdevup = 2
nbdevdn = 2
matype = 0

# Calculate the rolling mean and standard deviation of the close prices
rolling_mean = df_history["Close"].rolling(window=timeperiod).mean()
rolling_std = df_history["Close"].rolling(window=timeperiod).std()

# Calculate the upper and lower Bollinger Bands
upper_band = rolling_mean + nbdevup * rolling_std
lower_band = rolling_mean - nbdevdn * rolling_std

# Create a table to store the results
results = pd.DataFrame(columns=["Analysis", "Description", "Recommendation"])

# Add a row to the table with the results of the Bollinger Bands analysis
if list(df_history["Close"])[-1] > list(upper_band)[-1]:
    recommendation = "Sell"
elif list(df_history["Close"])[-1] < list(lower_band)[-1]:
    recommendation = "Buy"
else:
    recommendation = "Hold"

bb_results = pd.concat([results, pd.DataFrame({"Analysis": "Bollinger Bands",
                                                "Description": "Bollinger Bands are a technical analysis tool that uses moving averages and standard deviations to indicate overbought or oversold conditions in a stock. When the stock price is above the upper band, it is considered overbought, and when the stock price is below the lower band, it is considered oversold.",
                                                "Recommendation": recommendation}, index=[0])], ignore_index=True)
# RSI Analysis
# Calculate the RSI using the close prices
timeperiod = 14

# Calculate the difference between the current close price and the previous close price
diff = df_history["Close"].diff()

# Calculate the up and down movements
up_movements = diff.where(diff > 0, 0)
down_movements = diff.where(diff < 0, 0)

# Calculate the average up and down movements over the past timeperiod periods
avg_up_movement = up_movements.rolling(timeperiod).mean()
avg_down_movement = down_movements.rolling(timeperiod).mean().abs()

# Calculate the relative strength
relative_strength = avg_up_movement / avg_down_movement

# Calculate the RSI
rsi = 100 - (100 / (1 + relative_strength))

# Create a table to store the results
results = pd.DataFrame(columns=["Analysis", "Description", "Recommendation"])

# Add a row to the table with the results of the RSI analysis
if list(rsi)[-1] > 70:
    recommendation = "Sell"
elif list(rsi)[-1] < 30:
    recommendation = "Buy"
else:
    recommendation = "Hold"


rsi_results = pd.concat([results, pd.DataFrame({"Analysis": "Relative Strength Index (RSI)",
                                                "Description": "The Relative Strength Index (RSI) is a momentum indicator that measures the strength of a stock's price movement. A reading above 70 indicates that the stock is overbought and may be due for a correction, while a reading below 30 indicates that the stock is oversold and may be a good buying opportunity.",
                                                "Recommendation": recommendation}, index=[0])], ignore_index=True)





recomm_df = pd.concat([macd_results, bb_results,rsi_results])




selected_ind = list(df_industries[df_industries['Symbol'] == 'AZN']['Industries'])
selected_ind_symbol = list(df_industries[df_industries['Industries'].isin(selected_ind)]['Symbol'].unique())
df_second_table = df_symbols[df_symbols['Symbol'].isin(selected_ind_symbol)].reset_index(drop=True)
df_second_table = df_second_table[['Symbol', 'Company Name', 'Country']]





range_slicer = dcc.DatePickerRange(
    id='date-range-picker',
    display_format="D-M-Y",
    start_date=df_history['Date'].min(),
    end_date=df_history['Date'].max(),
    start_date_placeholder_text='Start date',
    end_date_placeholder_text='End date',
    min_date_allowed=df_history['Date'].min(),
    max_date_allowed=df_history['Date'].max(),
    initial_visible_month=df_history['Date'].min(),
    persistence=True,
    persistence_type='session',
    calendar_orientation='horizontal',
    style={'width': '90%'}
)

charts_filter = dcc.RadioItems(
    id='filter-charts',
    options=[{'label': 'Line Chart', 'value': 'line'},
             {'label': 'Candlestick Chart', 'value': 'candlestick'},
             ],
    value='line',
    labelStyle={'margin': '10px'},
    style={'font-family': 'roboto', 'font-size': 20}
)

index_dropdown = dcc.Dropdown(
                                id='index-dropdown',
                                options=[{'label': index, 'value': index} for index in indexes],
                                value='NASDAQ 100',
                                placeholder="Select Stock market index",
                                searchable=True,
                                style={'font-size': 15, 'font-family': 'roboto'}
                            )

symbol_dropdown = dcc.Dropdown(
                                id='symbol-dropdown',
                                options=[{'label': symbol, 'value': symbol} for symbol in df_symbols['Symbol'].unique()],
                                value=df_symbols['Symbol'][df_symbols['Stock Index'] == 'NASDAQ 100'].unique()[0],
                                placeholder="Search Stock by selected index",
                                searchable=True,
                                style={'font-size': 15, 'font-family': 'roboto'}
                            )

main_table = dash_table.DataTable(
                                    id='stock-table',
                                    columns=[{'name': col, 'id': col} for col in df_symbols.sort_values(by=['Symbol']).columns],
                                    page_size=12,
                                    fill_width=True,
                                    fixed_rows={'headers': False},
                                    style_table=style_table,
                                    style_data=style_data,
                                    style_cell=style_cell,
                                    style_header=style_header,
                                    style_data_conditional=[
                                        {'if': {'row_index': 'odd'},
                                         'backgroundColor': 'rgb(248, 248, 248)'},
                                        {
                                            'if': {'column_id': 'Company Name'},
                                            'textAlign': 'left'
                                        }]
)

second_table = dash_table.DataTable(
                            id='industries-table',
                            columns=[{'name': col, 'id': col} for col in df_second_table.sort_values(by=['Symbol']).columns],
                            page_size=11,
                            fill_width=True,
                            fixed_rows={'headers': False},
                            style_table=style_table,
                            style_data=style_data,
                            style_cell=style_cell,
                            style_header=style_header,
                            style_data_conditional=[
                                {'if': {'row_index': 'odd'},
                                 'backgroundColor': 'rgb(248, 248, 248)'},
                                {
                                    'if': {'column_id': 'Company Name'},
                                    'textAlign': 'left'
                                }]
)


recommend_table = dash_table.DataTable(
                            id='recommend-table',
                            columns=[{'name': col, 'id': col} for col in recomm_df.columns],
                            data=macd_results.to_dict('records'),
                            #page_size=11,
                            fill_width=True,
                            fixed_rows={'headers': False},
                            style_table=style_table,
                            style_data=style_data,
                            style_cell=style_cell,
                            style_header=style_header,
                            style_data_conditional=style_data_conditional_for_recomm,
                            style_cell_conditional=[
                                {
                                'if': {'column_id': 'Analysis'},
                                'width': '150px'},
                                {
                                    'if': {'column_id': 'Recommendation'},
                                    'width': '150px'}
                            ],

)

logo_png = 'stock-market-image.png'
logo_base64 = base64.b64encode(open(logo_png, 'rb').read()).decode('ascii')

# Define the layout of the app
app.layout = html.Div([
    # Row 1
    dbc.Row([
        # Row 1 - Col 1
        dbc.Col([html.Img(src='data:image/png;base64,{}'.format(logo_base64), style={'height': '90%',
                                                                                     'width': '40%'})], width=3),
        # Row 1 - Col 2
        dbc.Col([
                html.Div([
                    html.H3('Stock Market Overview', style={'text-align': 'center', 'font-family': 'roboto',
                                                            'fontSize': 40}),
                    html.H5('Naya Python Middle Project', style={'text-align': 'center', 'font-family': 'roboto',
                                                                 'fontSize': 15}),
                ])
                ], style={'font-weight': 'bold', 'font-family': 'sans-serif', 'fontSize': 40}, width=3),

        # Row 1 - Col 3
        dbc.Col([], width=2),
        # Row 1 - Col 4
        dbc.Col([
            html.Div([
                html.H1('Select Stock Market Index', style={'text-align': 'center',
                                                            'backgroundColor': '#2c3e50',
                                                            'color': '#ffffff',
                                                            'font-family': 'roboto',
                                                            'fontSize': 15}),
                index_dropdown])
        ], width=2),
        # Row 1 - Col 5
        dbc.Col([
            html.Div([
                html.H1('Select Ticker in the selected index', style={'text-align': 'center',
                                                                      'backgroundColor': '#2c3e50',
                                                                      'color': '#ffffff',
                                                                      'font-family': 'roboto',
                                                                      'fontSize': 15}),
                symbol_dropdown])
        ], width=2),
    ], justify="center", className="h-10", style={'margin-bottom': 10,
                                                  'margin-top': 5,
                                                  'margin-left': 10,
                                                  'margin-right': 10}),
    # Row 2
    # dbc.Row([html.Hr(style={'backgroundColor': '#2c3e50', 'height': '2px', 'border': 'none'})
    #          ], style={'margin-bottom': 2,
    #                    'margin-top': 5,
    #                    'margin-left': 10,
    #                    'margin-right': 10}),

    # Row 2
    dbc.Row([
        html.H1(id='main_header', style={'text-align': 'center', 'font-family': 'roboto',
                                         'fontSize': 20, 'backgroundColor': '#ffffff',
                                         'color': 'red'}),
    ], style={'margin-bottom': 5}),
    # Row 3
    dbc.Row([
        # Row 3 - Col 1
        dbc.Col([
            html.Div([
                html.H1(id='header_1', style={'text-align': 'center', 'font-family': 'roboto',
                                                            'fontSize': 15, 'backgroundColor': '#2c3e50',
                                                            'color': '#ffffff',  'fontWeight': 'bold'}),
                second_table
                ])
        ], width=4),
        # Row 3 - Col 2
        dbc.Col([
            # Row 3 - Col 1 - Row 1
            dbc.Row([
                # Row 3 - Col 1 - Row 1 - Col 1
                dbc.Col([], width=2),
                dbc.Col([charts_filter], width=4),
                dbc.Col([], width=2),
                # Row 3 - Col 1 - Row 1 - Col 2
                dbc.Col([range_slicer], width=4)
            ], justify="center"),
            # Row 3 - Col 1 - Row 2
            dbc.Row([dcc.Graph(id='chart')])
        ], width=8),
    ], style={'margin-left': 10}),
    # Row 4
    dbc.Row([html.Hr(style={'backgroundColor': '#2c3e50', 'height': '1px'})
             ], style={'margin-bottom': 10, 'margin-left': 10, 'margin-right': 10}),
    # Row 5
    dbc.Row([
        # Row 5 - Col 1
        dbc.Col([
            html.Div([
                html.H1(id='header_2', style={'text-align': 'center', 'font-family': 'roboto',
                                                            'fontSize': 15, 'backgroundColor': '#2c3e50',
                                                            'color': '#ffffff',  'fontWeight': 'bold'}),
                main_table
            ])
        ], width=4),
        # Row 5 - Col 2
        #dbc.Col([], width=1),
        # Row 5 - Col 3
        dbc.Col([
            html.Div([
                html.H1(id='header_3', style={'text-align': 'center', 'font-family': 'roboto',
                                                            'fontSize': 15, 'backgroundColor': '#2c3e50',
                                                            'color': '#ffffff',  'fontWeight': 'bold'}),
                recommend_table
            ])
        ], width=8),
             ], style={'margin-bottom': 10, 'margin-left': 10, 'margin-right': 10})
])
# Define the callback function to update the table based on the selected index
@app.callback(
    [Output(component_id='stock-table', component_property='data'),
     Output(component_id='symbol-dropdown', component_property='options'),
     Output(component_id='symbol-dropdown', component_property='value'),
     Output(component_id='chart', component_property='figure'),
     Output(component_id='industries-table', component_property='data'),
     Output(component_id='header_1', component_property='children'),
     Output(component_id='header_2', component_property='children'),
     Output(component_id='main_header', component_property='children'),
     Output(component_id='recommend-table', component_property='data'),
     Output(component_id='header_3', component_property='children'),
     ],
    [Input(component_id='index-dropdown', component_property='value'),
     Input(component_id='filter-charts', component_property='value'),
     Input(component_id='symbol-dropdown', component_property='value'),
     Input(component_id='date-range-picker', component_property='start_date'),
     Input(component_id='date-range-picker', component_property='end_date')
     ]
)

def update_table(selected_index, selected_chart, selected_symbol,start_date, end_date):

    header_1 = f'Stocks {selected_index} from Same Industry'
    header_2 = f'All Stocks in {selected_index}'
    header_3 = f'Trade Recommendations for {selected_symbol}'

    # Get the stock data for the selected index
    new_df = df_symbols[df_symbols['Stock Index'] == selected_index]
    new_main_table_df = new_df[['Symbol', 'Company Name', 'Country', 'Stock Index', 'Year of Founded', '#Employees']]
    table_data = new_main_table_df.to_dict('records')

    symbol_options = [{'label': symbol, 'value': symbol} for symbol in new_df['Symbol'].unique()]
    value = new_df['Symbol'].unique()[0]

    selected_ind = list(df_industries[df_industries['Symbol'] == selected_symbol]['Industries'])
    selected_ind_symbol = list(df_industries[df_industries['Industries'].isin(selected_ind)]['Symbol'].unique())
    df_second_table = new_main_table_df[new_main_table_df['Symbol'].isin(selected_ind_symbol)].reset_index(drop=True)
    second_table_data = df_second_table.to_dict('records')


    msft_new = yf.Ticker(selected_symbol)
    history_range = msft_new.history(period="1y")
    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()

    df_history = history_range.reset_index(drop=False)
    df_history['Date'] = pd.to_datetime(df_history['Date']).dt.date
    df_history = df_history[(df_history['Date'] >= start_date) & (df_history['Date'] <= end_date)]
    # Add a column to the DataFrame that indicates the trend
    first_open = df_history['Open'].iloc[0]
    # Get the last close price
    last_close = df_history['Close'].iloc[-1]
    # Compare the first open price to the last close price
    if first_open < last_close:
        trend_fill_color = 'green'
    else:
        trend_fill_color = 'red'

    result = new_main_table_df[new_main_table_df['Symbol'] == selected_symbol]
    if result.size > 0:
        selected_stock_info = 'Selected Stock: (' + selected_symbol + ') ' + \
                              new_main_table_df[new_main_table_df['Symbol'] == selected_symbol]['Company Name'].values[
                                  0] + \
                              '  |  Industries: ' + ', '.join(selected_ind) + ' |  Country Origin: ' + \
                              new_main_table_df[new_main_table_df['Symbol'] == selected_symbol]['Country'].values[0]
    else:
        selected_stock_info = 'Selected Stock: (' + selected_symbol + ') ' + \
                              'Not Found' + \
                              '  |  Industries: ' + ', '.join(selected_ind) + '  |  Country Origin: ' + \
                              'Not Found'


    stok_info_header = html.H1(selected_stock_info, style={'text-align': 'center', 'font-family': 'roboto',
                                     'fontSize': 20, 'backgroundColor': '#ffffff',
                                     'color': trend_fill_color}),


    if selected_chart == 'line':
        # Find the minimum and maximum values in the y data series
        y_min = min(df_history['Close'])
        y_max = max(df_history['Close'])
        fig = px.line(df_history, x="Date", y="Close", range_y=[y_min*0.9, y_max*1.2])
        fig.update_traces(fill='tozeroy', line=dict(color=trend_fill_color))
        fig.update_layout(title='Stock Price Trend',
                          title_x=0.5,
                          template="plotly_white",
                          colorway=['#f44336', '#3f51b5', '#2196f3', '#009688', '#4caf50'],
                          font=dict(family='roboto', size=12),
                          #paper_bgcolor='#F5F5F5',
                          plot_bgcolor='#F5F5F5',
                          margin=dict(l=50, r=50, b=50, t=50, pad=4))
        # Add an annotation for the minimum value
        fig.add_annotation(x=df_history['Date'][df_history['Close'].idxmin()], y=y_min,
                           text=f"Min: {y_min:.2f}", showarrow=True, arrowhead=7, arrowsize=1, font=dict(family='roboto', size=16, color='red'))
        # Add an annotation for the maximum value
        fig.add_annotation(x=df_history['Date'][df_history['Close'].idxmax()], y=y_max,
                           text=f"Max: {y_max:.2f}", showarrow=True, arrowhead=7, arrowsize=1, font=dict(family='roboto', size=16, color='green'))
    else:
        # Find the minimum and maximum values in the y data series
        y_min = min(df_history['Close'])
        y_max = max(df_history['Close'])
        fig = go.Figure(data=[go.Candlestick(x=df_history['Date'],
                                             open=df_history['Open'],
                                             high=df_history['High'],
                                             low=df_history['Low'],
                                             close=df_history['Close'],
                                             visible=True
                                             )])
        fig.update_layout(title='Stock Price History',
                          title_x=0.5,
                          yaxis=dict(range=[y_min*0.9, y_max*1.1]),
                          template="plotly_white",
                          colorway=['#f44336', '#3f51b5', '#2196f3', '#009688', '#4caf50'],
                          font=dict(family='roboto', size=12),
                          #paper_bgcolor='#F5F5F5',
                          plot_bgcolor='#F5F5F5',
                          #plot_bgcolor='black',
                          xaxis_rangeslider_visible=False,
                          margin=dict(l=50, r=50, b=50, t=50, pad=4))
        # Add an annotation for the minimum value
        fig.add_annotation(x=df_history['Date'][df_history['Close'].idxmin()], y=y_min,
                           text=f"Min: {y_min:.2f}", showarrow=True, arrowhead=7, arrowsize=2, font=dict(family='roboto', size=16, color='red'))
        # Add an annotation for the maximum value
        fig.add_annotation(x=df_history['Date'][df_history['Close'].idxmax()], y=y_max,
                           text=f"Max: {y_max:.2f}", showarrow=True, arrowhead=7, arrowsize=2, font=dict(family='roboto', size=16, color='green'))

    # MACD Analysis
    # Calculate the MACD using the close prices
    fast_period = 12
    slow_period = 26
    signal_period = 9

    # Calculate the fast and slow moving averages
    fast_ma = df_history["Close"].ewm(span=fast_period, adjust=False).mean()
    slow_ma = df_history["Close"].ewm(span=slow_period, adjust=False).mean()

    # Calculate the MACD line
    macd_line = fast_ma - slow_ma

    # Calculate the MACD signal line
    macd_signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()

    # Calculate the MACD histogram
    macd_hist = macd_line - macd_signal_line

    # Create a table to store the results
    results = pd.DataFrame(columns=["Analysis", "Description", "Recommendation"])

    # Add a row to the table with the results of the MACD analysis
    macd_results = pd.concat([results, pd.DataFrame({"Analysis": "MACD",
                                                     "Description": "The MACD is a trend-following momentum indicator that shows the relationship between two moving averages of a stock's price. A bullish MACD indicates that the stock is likely to continue rising, while a bearish MACD indicates that the stock is likely to continue falling.",
                                                     "Recommendation": "Buy" if list(macd_hist)[-1] > 0 else "Sell"},
                                                    index=[0])], ignore_index=True)

    # Bollinger Bands Analysis
    # Calculate the Bollinger Bands using the close prices
    timeperiod = 20
    nbdevup = 2
    nbdevdn = 2
    matype = 0

    # Calculate the rolling mean and standard deviation of the close prices
    rolling_mean = df_history["Close"].rolling(window=timeperiod).mean()
    rolling_std = df_history["Close"].rolling(window=timeperiod).std()

    # Calculate the upper and lower Bollinger Bands
    upper_band = rolling_mean + nbdevup * rolling_std
    lower_band = rolling_mean - nbdevdn * rolling_std

    # Create a table to store the results
    results = pd.DataFrame(columns=["Analysis", "Description", "Recommendation"])

    # Add a row to the table with the results of the Bollinger Bands analysis
    if list(df_history["Close"])[-1] > list(upper_band)[-1]:
        recommendation = "Sell"
    elif list(df_history["Close"])[-1] < list(lower_band)[-1]:
        recommendation = "Buy"
    else:
        recommendation = "Hold"

    bb_results = pd.concat([results, pd.DataFrame({"Analysis": "Bollinger Bands",
                                                   "Description": "Bollinger Bands are a technical analysis tool that uses moving averages and standard deviations to indicate overbought or oversold conditions in a stock. When the stock price is above the upper band, it is considered overbought, and when the stock price is below the lower band, it is considered oversold.",
                                                   "Recommendation": recommendation}, index=[0])], ignore_index=True)

    # RSI Analysis
    # Calculate the RSI using the close prices
    timeperiod = 14

    # Calculate the difference between the current close price and the previous close price
    diff = df_history["Close"].diff()

    # Calculate the up and down movements
    up_movements = diff.where(diff > 0, 0)
    down_movements = diff.where(diff < 0, 0)

    # Calculate the average up and down movements over the past timeperiod periods
    avg_up_movement = up_movements.rolling(timeperiod).mean()
    avg_down_movement = down_movements.rolling(timeperiod).mean().abs()

    # Calculate the relative strength
    relative_strength = avg_up_movement / avg_down_movement

    # Calculate the RSI
    rsi = 100 - (100 / (1 + relative_strength))

    # Create a table to store the results
    results = pd.DataFrame(columns=["Analysis", "Description", "Recommendation"])

    # Add a row to the table with the results of the RSI analysis
    if list(rsi)[-1] > 70:
        recommendation = "Sell"
    elif list(rsi)[-1] < 30:
        recommendation = "Buy"
    else:
        recommendation = "Hold"

    rsi_results = pd.concat([results, pd.DataFrame({"Analysis": "Relative Strength Index (RSI)",
                                                    "Description": "The Relative Strength Index (RSI) is a momentum indicator that measures the strength of a stock's price movement. A reading above 70 indicates that the stock is overbought and may be due for a correction, while a reading below 30 indicates that the stock is oversold and may be a good buying opportunity.",
                                                    "Recommendation": recommendation}, index=[0])], ignore_index=True)

    recomm_df = pd.concat([macd_results, bb_results, rsi_results])

    recommend_table_data = recomm_df.to_dict('records')

    return table_data, symbol_options, value,  fig, second_table_data, header_1, header_2, stok_info_header,\
           recommend_table_data, header_3

if __name__ == '__main__':
    app.run_server(debug=True)
    #app.run_server(debug=True, port=8150)