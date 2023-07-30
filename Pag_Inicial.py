# ========== BIBLIOTECAS ===============================================
import pandas as pd
import streamlit as st
import folium
from PIL import Image
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static
import inflection

# =========== FUNCOES =============================================================================

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
    
    return ( df1 )


def mapa_mundi( df1 ):
    data_plot = df1.loc[:, ['latitude','longitude'] ]
    mapa = folium.Map()
    locais = data_plot.values.tolist()
    MarkerCluster( locations=locais ).add_to( mapa )                     
    folium_static( mapa , width=1024 , height=600 )
    
    return ( df1 )


# ========== IMPORTACAO DO DATASET ================================================================
st.set_page_config( page_title='Pagina Inicial', page_icon='📊', layout='wide' )
df = pd.read_csv( 'dataset/zomato.csv' )


# ========== PREPARACAO DO DATASET ================================================================
df1 = limpa_codigo( df )


# =========== BARRA LATERAL =======================================================================
image = Image.open('fome-zero-tech.jpg')
st.sidebar.image( image, width=300 )

# ================= Filtro dos Paises =============================================================
st.sidebar.markdown('# Filtro')
pais_opt = st.sidebar.multiselect('Escolha os paises que deseja visualizar os restaurantes',
                          list( df1.loc[ : ,'country'].unique() ),
                          default=['Brazil','England','Qatar','South Africa','Canada','Australia'])
df1 = df1.loc[ df1['country'].isin(pais_opt) , : ]

st.sidebar.markdown("""---""")

# ================= Botao p/ baixar o arquivo tratado =============================================
st.sidebar.markdown('# Dados Tratados')
st.sidebar.download_button( label='Download',
                            data=df1.to_csv( index=False , sep=';' ).encode( "utf-8" ),
                            file_name='data.csv',mime='text/csv' )


#============ BARRA CENTRAL ========================================================================

st.markdown('# Fome Zero')
st.markdown('## O Melhor lugar para encontrar seu mais novo restaurante favorito!')

with st.container():
    st.markdown('#### Temos as seguintes marcas dentro da nossa plataforma:')
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        col1.metric('Restaurantes Cadastrados', df1.loc[:,"restaurant_id"].nunique() )
    with col2:
        col2.metric('Paises Cadastrados', df1.loc[:,'country'].unique().shape[0] )
    with col3:
        col3.metric('Cidades Cadastradas', df1.loc[:,'city'].unique().shape[0] )
    with col4:
        col4.metric('Avaliações Feitas na Plataforma', df1.loc[:,"votes"].sum() )
    with col5:
        col5.metric('Tipos de Culinária Oferecidos', df1.loc[:,'cuisines'].unique().shape[0] )

st.markdown("""---""")

with st.container():
    fig02 = mapa_mundi( df1 )