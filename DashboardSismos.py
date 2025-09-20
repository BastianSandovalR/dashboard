# app.py
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Superstore", layout="wide")

# -------------------------
# Función para cargar datos
# -------------------------
@st.cache(allow_output_mutation=True)
def load_data(uploaded_file):
    if uploaded_file is not None:
        # permite .csv o .xlsx
        if str(uploaded_file.name).lower().endswith('.csv'):
            df_local = pd.read_csv(uploaded_file)
        else:
            df_local = pd.read_excel(uploaded_file)
    else:
        # intenta cargar archivo local "Superstore.xlsx"
        try:
            df_local = pd.read_csv("C:/Users/basti/OneDrive/Escritorio/csv_estudio_datascience/SampleSuperstore.csv")
        except Exception as e:
            st.error("No se encontró 'Superstore.xlsx' en la carpeta. Sube el archivo con el uploader.")
            return None
    # limpieza básica de nombres de columnas
    df_local.columns = df_local.columns.str.strip()
    return df_local

# -------------------------
# Sidebar - carga y filtros
# -------------------------
st.sidebar.title("Configuración")
uploaded_file = st.sidebar.file_uploader("Sube Superstore.xlsx o .csv (opcional)", type=['xlsx','csv'])
df = load_data(uploaded_file)

if df is None:
    st.stop()

# filtros globales (sidebar)
regions = ['All'] + sorted(df['Region'].unique().tolist())
selected_region = st.sidebar.selectbox("Región", regions, index=0)

categories = ['All'] + sorted(df['Category'].unique().tolist())
selected_category = st.sidebar.selectbox("Categoría", categories, index=0)

segments = ['All'] + sorted(df['Segment'].unique().tolist())
selected_segment = st.sidebar.selectbox("Segmento", segments, index=0)

# aplicar filtros
df_filtered = df.copy()
if selected_region != 'All':
    df_filtered = df_filtered[df_filtered['Region'] == selected_region]
if selected_category != 'All':
    df_filtered = df_filtered[df_filtered['Category'] == selected_category]
if selected_segment != 'All':
    df_filtered = df_filtered[df_filtered['Segment'] == selected_segment]

# -------------------------
# KPIs
# -------------------------
st.title("📊 Dashboard - Superstore")
col1, col2, col3, col4 = st.columns(4)
total_sales = df_filtered['Sales'].sum()
total_profit = df_filtered['Profit'].sum()
total_quantity = df_filtered['Quantity'].sum()
avg_discount = df_filtered['Discount'].mean()

col1.metric("Ventas Totales", f"${total_sales:,.0f}")
col2.metric("Profit Total", f"${total_profit:,.0f}")
col3.metric("Cantidad Vendida", f"{int(total_quantity):,}")
col4.metric("Descuento Promedio", f"{avg_discount:.2%}")

st.markdown("---")

# -------------------------
# Gráficos principales
# -------------------------
# 1) Ventas por Región (agregado)
with st.container():
    st.subheader("Ventas por Región")
    sales_by_region = df.groupby('Region', as_index=False)['Sales'].sum()
    fig_reg = px.bar(sales_by_region, x='Region', y='Sales', title="Ventas por Región",
                     labels={'Sales': 'Ventas', 'Region':'Región'})
    fig_reg.update_layout(margin=dict(t=40, b=10))
    st.plotly_chart(fig_reg, use_container_width=True)

# 2) Top Sub-Categories (según filtro aplicado)
with st.container():
    st.subheader("Top Sub-Categorías por Ventas (filtro aplicado)")
    top_sub = (df_filtered.groupby('Sub-Category', as_index=False)['Sales']
               .sum().sort_values('Sales', ascending=False).head(15))
    fig_top = px.bar(top_sub, x='Sub-Category', y='Sales', text='Sales',
                     title="Top Sub-Categories", labels={'Sales':'Ventas', 'Sub-Category':'Sub-Categoría'})
    fig_top.update_layout(xaxis_tickangle=-45, margin=dict(t=40, b=150))
    st.plotly_chart(fig_top, use_container_width=True)

# 3) Discount vs Profit scatter
with st.container():
    st.subheader("Descuento vs Profit (por categoría)")
    fig_sc = px.scatter(df_filtered, x='Discount', y='Profit',
                        color='Category', hover_data=['Sub-Category', 'Sales'],
                        title="Descuento vs Profit")
    fig_sc.update_layout(margin=dict(t=40))
    st.plotly_chart(fig_sc, use_container_width=True)

st.markdown("---")

# -------------------------
# Tablas y descargas
# -------------------------
st.subheader("Datos y descarga")
st.write("Muestra de los datos filtrados")
st.dataframe(df_filtered.head(100))

# botón para descargar datos filtrados como CSV
csv = df_filtered.to_csv(index=False).encode('utf-8')
st.download_button(label="Descargar datos filtrados (CSV)", data=csv, file_name='superstore_filtered.csv', mime='text/csv')
