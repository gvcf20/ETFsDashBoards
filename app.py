from dash import Dash, dash_table, dcc, callback, Output, Input, html
import dash_mantine_components as dmc
import plotly.graph_objs as go
import pandas as pd
import yfinance as yf
import numpy as np

app = Dash(__name__)

etf_tickers = [
    "SPY", "XLB", "XLE", "XLF", "XLI", "XLK", "XLP", 
    "XLU", "XLV", "XLY", "XTN", "EWJ", "EWG", "EEM", 
    "EWZ", "TLT", "GLD", "FXE"
]

df = pd.DataFrame(yf.download(etf_tickers, start='2014-01-01', end= '2024-08-29' )['Adj Close'])

df_normalized = df / df.iloc[0]

returns = df.pct_change().dropna()

# Define a taxa de retorno livre de risco (Rf)
rf = 0.05 / 252  # taxa diária, assumindo 252 dias úteis em um ano

# Calcula o retorno anualizado, a volatilidade e a variância
annualized_returns = returns.mean() * 252
annualized_volatility = returns.std() * np.sqrt(252)
annualized_variance = returns.var() * 252

# Calcula o Índice de Sharpe
sharpe_ratios = (annualized_returns - rf) / annualized_volatility

# Cria um DataFrame com as estatísticas
stats_df = pd.DataFrame({
    'Ativo': returns.columns,
    'Média': annualized_returns.round(2),
    'Volatilidade': annualized_volatility.round(2),
    'Variância': annualized_variance.round(2),
    'Sharpe Ratio': sharpe_ratios.round(2)
})

app = Dash(__name__)

app.layout = html.Div(children=[
    html.H1(children='Desempenho dos Ativos', style={'textAlign': 'center'}),

    html.Div([
        dcc.Dropdown(
            id='asset-dropdown',
            options=[{'label': 'Todos os Ativos', 'value': 'all'}] +
                    [{'label': asset, 'value': asset} for asset in df.columns] +
                    [{'label': 'Monte seu Gráfico', 'value': 'custom'}],
            value='all',  # valor padrão
            clearable=False,
            style={'width': '95%'}
        )
    ], style={'width': '90%', 'padding': '10px'}),

    html.Div([
        dcc.Checklist(
            id='custom-asset-checklist',
            options=[{'label': asset, 'value': asset} for asset in df.columns],
            value=[],
            inline=True,
            style={'display': 'none'}  # escondido por padrão
        ),
        html.Div([
            dcc.Input(id='start-date-input', type='text', value=str(df.index.min())[:10], placeholder='YYYY-MM-DD', style={'width': '45%', 'display': 'inline-block'}),
            dcc.Input(id='end-date-input', type='text', value=str(df.index.max())[:10], placeholder='YYYY-MM-DD', style={'width': '45%', 'display': 'inline-block', 'marginLeft': '10px'})
        ], style={'width': '90%', 'padding': '10px'})
    ]),

    html.Div([
        dcc.Graph(id='performance-graph', style={'width': '50%', 'display': 'inline-block', 'height': '500px'}),
        dash_table.DataTable(
            id='stats-table',
            columns=[{'name': col, 'id': col} for col in stats_df.columns],
            style_table={'height': '500px', 'overflowY': 'auto'},
            style_cell={'textAlign': 'center', 'padding': '5px'},
            style_header={'backgroundColor': 'lightgrey', 'fontWeight': 'bold'},
            style_data={'border': '1px solid grey'},
            page_size=20,
        )
    ], style={'display': 'flex', 'gap' : '30px', 'padding': '10px'})
])

@app.callback(
    [Output('performance-graph', 'figure'),
     Output('custom-asset-checklist', 'style'),
     Output('stats-table', 'data')],
    [Input('asset-dropdown', 'value'),
     Input('custom-asset-checklist', 'value'),
     Input('start-date-input', 'value'),
     Input('end-date-input', 'value')]
)
def update_graph_and_table(selected_option, selected_assets, start_date, end_date):
    filtered_df = df.loc[start_date:end_date]

    if selected_option == 'all':
        filtered_df_normalized = filtered_df / filtered_df.iloc[0]  # Normalizar
        data = [
            go.Scatter(
                x=filtered_df_normalized.index,
                y=filtered_df_normalized[asset],
                mode='lines',
                name=asset
            ) for asset in df.columns
        ]
        title = 'Desempenho Normalizado de Todos os Ativos'
        checklist_style = {'display': 'none'}
        stats_data = stats_df.to_dict('records')

    elif selected_option == 'custom':
        filtered_df_normalized = filtered_df / filtered_df.iloc[0]  # Normalizar
        if not selected_assets:
            data = []
            title = 'Selecione ativos para construir seu gráfico'
            stats_data = []
        else:
            data = [
                go.Scatter(
                    x=filtered_df_normalized.index,
                    y=filtered_df_normalized[asset],
                    mode='lines',
                    name=asset
                ) for asset in selected_assets
            ]
            title = 'Desempenho Normalizado dos Ativos Selecionados'
            stats_data = stats_df[stats_df['Ativo'].isin(selected_assets)].to_dict('records')
        checklist_style = {'display': 'block'}

    else:
        data = [
            go.Scatter(
                x=filtered_df.index,
                y=filtered_df[selected_option],
                mode='lines',
                name=selected_option
            )
        ]
        title = f'Desempenho do Ativo: {selected_option}'
        checklist_style = {'display': 'none'}
        stats_data = stats_df[stats_df['Ativo'] == selected_option].to_dict('records')

    figure = {
        'data': data,
        'layout': go.Layout(
            title=title,
            xaxis={'title': 'Data'},
            yaxis={'title': 'Valor'}
        )
    }
    return figure, checklist_style, stats_data


if __name__ == '__main__':
    app.run(debug=True)
