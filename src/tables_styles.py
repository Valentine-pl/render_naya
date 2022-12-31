style_table = {
                  'maxHeight': '500',
                  'overflowY': 'auto'
              }
style_data = {
                 'whiteSpace': 'normal',
                 'text-align': 'center',
             }
style_cell = {'textAlign': 'center', 'fontSize': 12, 'font-family': 'roboto', 'border': '1px solid black'}

style_header = {'backgroundColor': '#2c3e50', 'color': '#ffffff', 'fontWeight': 'bold',
                'textAlign': 'center', 'border': '1px solid black'}

style_data_conditional_for_recomm = [
    {'if': {'row_index': 'odd'},
     'backgroundColor': 'rgb(248, 248, 248)'},
    {
        'if': {'column_id': 'Description'},
        'textAlign': 'left'
    },
    {
        'if': {'column_id': 'Analysis'},
        'textAlign': 'left'
    },
    {
        'if': {
            'filter_query': '{Recommendation} = Sell',
            'column_id': 'Recommendation'
        },
        'backgroundColor': 'tomato',
    },
    {
        'if': {
            'filter_query': '{Recommendation} = Hold',
            'column_id': 'Recommendation'
        },
        'backgroundColor': 'yellow'
    },
    {
        'if': {
            'filter_query': '{Recommendation} = Buy',
            'column_id': 'Recommendation'
        },
        'backgroundColor': 'green'
    }
]