import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objs as go
import numpy as np
from datetime import datetime

etf_tickers = [
    "SPY", "XLB", "XLE", "XLF", "XLI", "XLK", "XLP", 
    "XLU", "XLV", "XLY", "XTN", "EWJ", "EWG", "EEM", 
    "EWZ", "TLT", "GLD", "FXE"
]

opções = ['ALL',
    "SPY", "XLB", "XLE", "XLF", "XLI", "XLK", "XLP", 
    "XLU", "XLV", "XLY", "XTN", "EWJ", "EWG", "EEM", 
    "EWZ", "TLT", "GLD", "FXE", 'Personalized'
]

st.set_page_config(layout = 'wide')

col1, col2 = st.columns(2)

with col1:
    date1 = st.date_input('Data Inicial')
with col2:
    date2 = st.date_input('Data Final')

df = pd.DataFrame(yf.download(etf_tickers, start=date1, end= date2 )['Adj Close'])

st.sidebar.write('Sistema para monitoramento dos ativos investíveis no desafio JGP')

etf = st.sidebar.selectbox('Asset', opções)

df_normalized = df / df.iloc[0]

returns = df.pct_change().dropna()

rf = 0.05 / 252 
annualized_returns = returns.mean() * 252
annualized_volatility = returns.std() * np.sqrt(252)
annualized_variance = returns.var() * 252

sharpe_ratios = (annualized_returns - rf) / annualized_volatility

stats_df = pd.DataFrame({
    'Ativo': returns.columns,
    'Média': annualized_returns.round(2),
    'Volatilidade': annualized_volatility.round(2),
    'Variância': annualized_variance.round(2),
    'Sharpe Ratio': sharpe_ratios.round(2)
})

if etf == 'ALL':

    filtered_df = df_normalized.loc[date1:date2]
    fig = go.Figure()

    for column in filtered_df.columns:
        fig.add_trace(go.Scatter(
            x=filtered_df.index,
            y=filtered_df[column],
            mode='lines',
            name=column
        ))

    fig.update_layout(
        title='ETFs Performance',
        xaxis_title='Data',
        yaxis_title='Cumulative Returns',
        legend_title='ETFs',
        template='plotly_dark'
    )

    st.plotly_chart(fig, use_container_width=True)

elif etf == 'Personalized':

    cols = st.columns(len(etf_tickers))

    escolhas_selecionadas = []

    for i, col in enumerate(cols):
        if col.checkbox(etf_tickers[i]):
            escolhas_selecionadas.append(etf_tickers[i])

    col1, col2 = st.columns(2)

    with col1:

        filtered_df = df_normalized.loc[date1:date2]


        fig = go.Figure()

        for escolha in escolhas_selecionadas:
            if escolha in filtered_df.columns:
                fig.add_trace(go.Scatter(
                    x=filtered_df.index,
                    y=filtered_df[escolha],
                    mode='lines',
                    name=etf
                ))

        fig.update_layout(
            title='ETFs Performance',
            xaxis_title='Data',
            yaxis_title='Cumulative Returns',
            legend_title='ETFs',
            template='plotly_dark'
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("<h1 style='text-align: center;'>Statistics</h1>", unsafe_allow_html=True)
        html = stats_df.loc[escolhas_selecionadas].to_html(classes='dataframe', index=False)
        st.markdown(f"""
            <div style='text-align: center;'>
                {html}
            </div>
        """, unsafe_allow_html=True)

else:

    col1,col2 = st.columns(2)

    with col1:

        st.markdown("<h1 style='text-align: center;'>Chart</h1>", unsafe_allow_html=True)
    
        fig = go.Figure()
        filtered_df = df.loc[date1:date2]
        fig.add_trace(go.Scatter(
            x=filtered_df[etf].index,
            y=filtered_df[etf],
            mode='lines',
            name=etf
        ))

        fig.update_layout(
            title=etf,
            xaxis_title='Data',
            yaxis_title='Price',
            legend_title='ETFs',
            template='plotly_dark'
        )

        st.plotly_chart(fig, use_container_width=True)


    with col2:

        st.markdown("<h1 style='text-align: center;'>Statistics</h1>", unsafe_allow_html=True)            
        html = pd.DataFrame(stats_df.loc[etf]).reset_index().to_html(classes='dataframe', index=False)
        st.dataframe(stats_df.loc[etf], use_container_width=True)
        st.markdown("<h2 style='text-align: center;'>News</h2>", unsafe_allow_html=True)
        asset = yf.Ticker(etf)
        news = asset.news
    
        titles = [item['title'] for item in news]
        urls = [item['link'] for item in news]

        # Exiba os URLs
        for i in range(len(urls)):
            titles[i]
            urls[i]