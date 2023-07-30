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

def top_culin( df1 , cozinha ):    
    aux = ( df1.loc[df1['cuisines'] == cozinha , ['restaurant_name','aggregate_rating']]
               .groupby('restaurant_name').mean()
               .sort_values(by='aggregate_rating',ascending=False).reset_index() )
    return aux

def top_rest_culin( df1 , lOrdem ):
    dfx = ( df1.loc[ : ,['cuisines','aggregate_rating']].groupby('cuisines').mean()
               .sort_values(by='aggregate_rating', ascending=lOrdem).reset_index() )
    dfx = dfx.head(data_slider)
    dfx.columns = ['Tipos de culinária','Média da Avaliação Média']
    fig = px.bar( dfx, x='Tipos de culinária',y='Média da Avaliação Média' , text_auto='.2f' )
    
    return fig

# ========== IMPORTACAO DO DATASET ================================================================
df = pd.read_csv( 'dataset/zomato.csv' )


# ========== PREPARACAO DO DATASET ================================================================
df1 = limpa_codigo( df )


#=========== BARRA LATERAL=========================================================================
st.set_page_config( page_title='Visão das Cozinhas', page_icon='🍽️', layout='wide' )
st.markdown('# 🍽️ Visão das Cozinhas')

st.sidebar.markdown('# Filtros')
# =============== Filtro dos Paises ===============================================================
pais_opt = st.sidebar.multiselect('Escolha os paises que deseja visualizar os restaurantes',
                          list( df1.loc[ : ,'country'].unique() ),
                          default=['Brazil','England','Qatar',
                                   'South Africa','Canada','Australia'])
df1 = df1.loc[ df1['country'].isin(pais_opt) , : ]

st.sidebar.markdown("""---""")
# =============== Filtro da Quantidade de Restaurantes ============================================
data_slider = st.sidebar.slider('Selecione a quantidade de restaurantes que deseja visualizar?',
                                value=10, min_value=0, max_value=20 )

st.sidebar.markdown("""---""")
# =============== Filtro das Culinarias ===========================================================
coz_opt = st.sidebar.multiselect('Escolha os tipos de culinária',
                          list( df1.loc[ : ,'cuisines'].unique() ),
                          default=['BBQ','Japanese','Brazilian',
                                   'Arabian','American','Italian'])
df1 = df1.loc[ df1['cuisines'].isin(coz_opt) , : ]


#=======================BARRA CENTRAL==============================================================

with st.container():
    st.markdown('#### Melhores restaurantes dos principais tipos culinários')
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        df1_ita = top_culin( df1 , 'Italian' )
        col1.metric( label='Italiana: '+df1_ita.iloc[0,0], value=str(df1_ita.iloc[0,1])+'/5.0' )
    with col2:
        df1_ame = top_culin( df1 , 'American' )
        col2.metric( label='Americana: '+df1_ame.iloc[0,0], value=str(df1_ame.iloc[0,1])+'/5.0' )
    with col3:
        df1_ara = top_culin( df1 , 'Arabian' )
        col3.metric( label='Arabe: '+df1_ara.iloc[0,0], value=str(df1_ara.iloc[0,1])+'/5.0' )
    with col4:
        df1_jap = top_culin( df1 , 'Japanese' )
        col4.metric( label='Japonesa: '+df1_jap.iloc[0,0], value=str(df1_jap.iloc[0,1])+'/5.0' )
    with col5:
        df1_bra = top_culin( df1 , 'Brazilian' )
        col5.metric( label='Brasileira: '+df1_bra.iloc[0,0], value=str(df1_bra.iloc[0,1])+'/5.0' )
        
with st.container():
    st.markdown('#### Top '+str(data_slider)+' restaurantes')
    df2 = ( df1.loc[ : ,['restaurant_id','restaurant_name','country','city',
                         'cuisines','average_cost_for_two','aggregate_rating','votes'] ]
               .groupby(['restaurant_id','restaurant_name','country','city',
                         'cuisines','average_cost_for_two','votes']).mean()
               .sort_values(by='aggregate_rating',ascending=False).reset_index() )
    st.dataframe( df2.head(data_slider) )
    
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('##### Top '+str(data_slider)+' melhores tipos de culinarias')
        fig = top_rest_culin( df1 , False )
        st.plotly_chart( fig , use_container_width=True )
        
    with col2:
        st.markdown('##### Top '+str(data_slider)+' piores tipos de culinarias')
        fig = top_rest_culin( df1 , True )
        st.plotly_chart( fig , use_container_width=True )