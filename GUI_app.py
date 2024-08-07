import streamlit as st
import pandas as pd
import datetime as dt
import plotly.express as px
import plotly.graph_objects as go
import os
import numpy as np
from st_files_connection import FilesConnection

planting_date_min = dt.datetime(2024,4,5)
planting_date_max = dt.datetime(2024,5,5)
#region_list_jp = ['網走市地区','網走東部地区','網走南部地区','網走西部地区北部','網走西部地区南部']
region_list_en = ['Abashiri', 'AbashiriE', 'AbashiriS', 'AbashiriW_N','AbashiriW_S']
region_group_list = list(range(1,42))

region_dict = {}
region_dict.update([('AbashiriW_N', list(range(1,4))), 
                    ('AbashiriW_S', list(range(4,11))), 
                    ('AbashiriE', list(range(11,20))), 
                    ('AbashiriS', list(range(20,34))), 
                    ('Abashiri', list(range(34,42)))])

conn = st.connection('gcs', type=FilesConnection)

scenario_date_list = pd.read_csv('date_list.csv')
scenario_date_list.Scenairo_date = pd.to_datetime(scenario_date_list.Scenario_date).dt.strftime('%Y-%m-%d')
scenario_len = len(scenario_date_list) -1

def make_boxplot(file_name):
    df_boxplot = conn.read(file_name,input_format='csv',ttl=600)
    df_boxplot['Scenario_Date'] = pd.to_datetime(scenario_date_bar).strftime('%Y/%m/%d')
    boxplot = px.box(data_frame=df_boxplot, x='Scenario_Date', y='MDAT_datetime', title='収穫日予測結果')
    boxplot.update_layout(xaxis_title='シナリオ作成日', yaxis_title='収穫日') 
    quantile_25 = pd.to_datetime(df_boxplot['MDAT'].quantile(q=0.25),format='%Y%j').strftime('%Y/%m/%d')
    quantile_75 = pd.to_datetime(df_boxplot['MDAT'].quantile(q=0.75),format='%Y%j').strftime('%Y/%m/%d')
    mean_date = pd.to_datetime(df_boxplot['MDAT'].mean(),format='%Y%j').strftime('%Y/%m/%d')
    return boxplot,quantile_25,quantile_75,mean_date

st.title('収穫時期予測アプリ(試験運用)')

with st.container():
    planting_date_calendar = st.date_input('播種日', planting_date_min, min_value=planting_date_min, max_value=planting_date_max)
    region_bar = st.selectbox('営農集団', region_group_list)
    scenario_date_bar = st.selectbox('シナリオ作成日', scenario_date_list.Scenairo_date, index=scenario_len)
    input_button = st.button('入力')

    if input_button:
    #region_en = region_list_en[region_list_jp.index(region_bar)]
        region_en = [k for k, v in region_dict.items() if region_bar in v][0]
        result_file = 'barley_storage/{0}/{2}/{0}_{1}.csv'.format(region_en, planting_date_calendar, scenario_date_bar)
        fig,quantile_25,quantile_75,mean_date = make_boxplot(result_file)
        st.plotly_chart(fig)
        st.write('収穫日は{}から{}の予測です。'.format(quantile_25,quantile_75))
        st.write('予測平均日は{}です。'.format(mean_date))
    st.divider()

st.write('"提供"  [ListenField株式会社](https://www.listenfield.com/ja/home), [サッポロビール株式会社](https://www.sapporobeer.jp/)')