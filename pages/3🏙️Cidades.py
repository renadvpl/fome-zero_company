# ========== BIBLIOTECAS ======================================================================
import plotly.express as px
import pandas as pd
import streamlit as st
import folium
from streamlit_folium import folium_static
import inflection

# ========== FUNCOES ========================================================================================

def limpa_codigo( df1 ):
    ###################################################################
    # Esta funcao tem a responsabilidade de limpar o dataframe        #
    # Tipos de Limpeza:                                               #
    #    1. Remocao dos dados missing (NaN);                          #
    #    2. Renomeacao de todas as colunas do dataframe;              #
    #    3. Exclusao da coluna "switch_to_order_menu";                #
    #    4. Conversao de dados para strings;                          #
    #    5. Transformacao dos codigos dos países em nomes;            #
    ###################################################################
    title = lambda x: inflection.titleize(x)
    snakecase = lambda x: inflection.underscore(x)
    spaces = lambda x: x.replace(" ", "")
    cols_old = list(df.columns)
    cols_old = list(map(title, cols_old))
    cols_old = list(map(spaces, cols_old))
    cols_new = list(map(snakecase, cols_old))
    df1.columns = cols_new

    df1['cuisines'] = df1['cuisines'].astype('str')
    df1['cuisines'] = df1.loc[:,'cuisines'].apply(lambda x: x.split(",")[0])
    df1 = df1.drop_duplicates('restaurant_id')

    df1 = df1.loc[df1['cuisines'] != 'nan', : ].copy()
    df1 = df1.loc[df1['restaurant_id'] != 'nan', : ].copy()
    df1 = df1.loc[df1['restaurant_name'] != 'nan', : ].copy()
    df1 = df1.reset_index(drop=True)

    df1['has_table_booking'] = df1['has_table_booking'].astype('str')
    df1['has_online_delivery'] = df1['has_online_delivery'].astype('str')
    df1['is_delivering_now'] = df1['is_delivering_now'].astype('str')
    
    df1 = df1.drop('switch_to_order_menu',axis=1)
    
    # Transformacao dos codigos dos países em nomes e renomeacao da coluna:
    df1.loc[df1['country_code'] == 1   ,'country_code'] = "India"
    df1.loc[df1['country_code'] == 14  ,'country_code'] = "Australia"
    df1.loc[df1['country_code'] == 30  ,'country_code'] = "Brazil"
    df1.loc[df1['country_code'] == 37  ,'country_code'] = "Canada"
    df1.loc[df1['country_code'] == 94  ,'country_code'] = "Indonesia"
    df1.loc[df1['country_code'] == 148 ,'country_code'] = "New Zeland"
    df1.loc[df1['country_code'] == 162 ,'country_code'] = "Philippines"
    df1.loc[df1['country_code'] == 166 ,'country_code'] = "Qatar"
    df1.loc[df1['country_code'] == 184 ,'country_code'] = "Singapure"
    df1.loc[df1['country_code'] == 189 ,'country_code'] = "South Africa"
    df1.loc[df1['country_code'] == 191 ,'country_code'] = "Sri Lanka"
    df1.loc[df1['country_code'] == 208 ,'country_code'] = "Turkey"
    df1.loc[df1['country_code'] == 214 ,'country_code'] = "United Arab Emirates"
    df1.loc[df1['country_code'] == 215 ,'country_code'] = "England"
    df1.loc[df1['country_code'] == 216 ,'country_code'] = "United States of America"
    df1.rename(columns={'country_code': 'country'}, inplace = True)
    
    # Criacao da coluna "color_name":
    df1.loc[df1['rating_color'] == "3F7E00" ,'color_name'] = "darkgreen"
    df1.loc[df1['rating_color'] == "5BA829" ,'color_name'] = "green"
    df1.loc[df1['rating_color'] == "9ACD32" ,'color_name'] = "lightgreen"
    df1.loc[df1['rating_color'] == "CDD614" ,'color_name'] = "orange"
    df1.loc[df1['rating_color'] == "FFBA00" ,'color_name'] = "red"
    df1.loc[df1['rating_color'] == "CBCBC8" ,'color_name'] = "darkred"
    df1.loc[df1['rating_color'] == "FF7800" ,'color_name'] = "darkred"
    
    # Classificacao das faixas de preco e Renomeacao da coluna "price_type":
    df1.loc[df1['price_range'] == 1 ,'price_range'] = "cheap"
    df1.loc[df1['price_range'] == 2 ,'price_range'] = "normal"
    df1.loc[df1['price_range'] == 3 ,'price_range'] = "expensive"
    df1.loc[df1['price_range'] == 4 ,'price_range'] = "gourmet"
    df1.rename(columns={'price_range': 'price_type'}, inplace = True)
    
    return df1

def top10_restaur( df1 ):
    df2 = ( df1.loc[:,['country','city','restaurant_id']]
               .groupby(['country','city']).count()
               .sort_values('restaurant_id',ascending=False).reset_index() )
    df2 = df2.head(10)
    df2.columns = ['Paises','Cidades','Quantidade de Restaurantes']
    fig = px.bar( df2 , x='Cidades', y='Quantidade de Restaurantes', color='Paises', text_auto=True )
    
    return fig

def top07( df1 , condicao_med ):
    df3 = ( df1.loc[ condicao_med ,['restaurant_id','country','city']]
               .groupby(['country','city']).count()
               .sort_values('restaurant_id',ascending=False).reset_index() )
    df3 = df3.head(7)
    df3.columns = ['Paises','Cidades','Quantidade de Restaurantes']
    fig = px.bar( df3 ,x='Cidades',y='Quantidade de Restaurantes', color='Paises', text_auto=True )

    return fig

def top10_culin( df1 ):
    df5 = ( df1.loc[ : ,['country','city','cuisines']]
               .groupby(['country','city']).nunique('cuisines')
               .sort_values('cuisines',ascending=False).reset_index() )
    df5 = df5.head(10)
    df5.columns = ['Paises','Cidades','Quantidade de Tipos de Culinarias']
    fig = px.bar( df5, x='Cidades', y='Quantidade de Tipos de Culinarias', color='Paises', text_auto=True )
    
    return fig

# ========== IMPORTACAO DO DATASET ==========================================================================
df = pd.read_csv( 'dataset/zomato.csv' )


# ========== PREPARACAO DO DATASET ==========================================================================
df1 = limpa_codigo( df )


# =========== BARRA LATERAL =================================================================================
st.set_page_config( page_title='Visão das Cidades', page_icon='🏙️', layout='wide' )
st.markdown('# 🏙️ Visão das Cidades')

# ================= Filtro dos Paises =======================================================================
st.sidebar.markdown('# Filtro')
pais_opt = st.sidebar.multiselect('Escolha os paises que deseja visualizar os restaurantes',
                          list( df1.loc[ : ,'country'].unique() ),
                          default=['Brazil','England','Qatar','South Africa','Canada','Australia'])
df1 = df1.loc[ df1['country'].isin(pais_opt) , : ]



#============ BARRA CENTRAL =================================================================================
with st.container():
    st.markdown('#### Top 10 cidades com mais restaurantes')
    fig1 = top10_restaur( df1 )
    st.plotly_chart( fig1 , use_container_width=True )

with st.container():
    st.markdown('#### Top 7 cidades com restaurantes')
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('##### Com média de avaliação acima de 4,0')
        fig2 = top07( df1 , df1['aggregate_rating'] >= 4.0 )
        st.plotly_chart( fig2 , use_container_width=True )
    with col2:
        st.markdown('##### Com média de avaliação abaixo de 2,5')
        fig3 = top07( df1 , df1['aggregate_rating'] < 2.5 )
        st.plotly_chart( fig3 , use_container_width=True )

with st.container():
    st.markdown('#### Top 10 cidades com mais restaurantes com tipos distintos de culinária')
    fig4 = top10_culin( df1 )
    st.plotly_chart( fig4 , use_container_width=True )