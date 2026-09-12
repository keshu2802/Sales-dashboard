import streamlit as st
import pandas as pd
import datetime
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go

# Set page config as the very first Streamlit command
st.set_page_config(layout="wide", page_title="Sales Dashboard")

# Slightly bigger sidebar for better slicer visibility
st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            min-width: 270px;
            max-width: 270px;
        }
        [data-testid="stSidebarContent"] {
            padding: 1rem;
        }
        div.block-container {
            padding-top: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

# Load data
df = pd.read_csv("C:\\salessss\\train.csv")

# Sidebar Filters (Slicers)
st.sidebar.header("Filter Data \n Atleast select one filter ")

category_options = df['Category'].unique().tolist()
selected_categories = st.sidebar.multiselect("Select Category", category_options, default=category_options)

region_options = df['Region'].unique().tolist()
selected_regions = st.sidebar.multiselect("Select Region", region_options, default=region_options)

segment_options = df['Segment'].unique().tolist()
selected_segments = st.sidebar.multiselect("Select Segment", segment_options, default=segment_options)

# Apply Filters
df = df[df['Category'].isin(selected_categories)]
df = df[df['Region'].isin(selected_regions)]
df = df[df['Segment'].isin(selected_segments)]

# Header
image = Image.open("C:\\salessss\\Sales.jpg")
col1, col2 = st.columns([0.2, 0.8])
with col1:
    st.image(image, width=150)

html_title = """
<style>
  .title-test {
    font-weight: bold;
    padding: 5px;
    border-radius: 6px;
    text-align: center;
  }
</style>
<h1 class="title-test">Sales Dashboard</h1>
"""
with col2:
    st.markdown(html_title, unsafe_allow_html=True)

col3, col4, col5 = st.columns([0.1, 0.45, 0.45])
with col3:
    box_date = str(datetime.datetime.now().strftime("%d %B %Y"))
    st.write(f"Last updated by: \n {box_date}")

# Category Bar Chart
with col4:
    fig = px.bar(df, x="Category", y="Sales", labels={"Sales": "Sales ($)"},
                 title="Total Sales by Category", hover_data=["Sales"],
                 template="gridon", height=500)
    st.plotly_chart(fig, use_container_width=True)

# Region Pie Chart
with col5:
    fig1 = px.pie(df, values="Sales", names="Region", title="Total Sales Distribution by Region")
    fig1.update_layout(width=400, height=400)
    st.plotly_chart(fig1, use_container_width=True)

# Expanders and download buttons
_, view1, dwn1, view2, dwn2 = st.columns([0.15, 0.20, 0.20, 0.20, 0.20])
with view1:
    expander = st.expander("Category wise Sales")
    data = df[["Category", "Sales"]].groupby("Category")["Sales"].sum()
    expander.write(data)
with dwn1:
    st.download_button("Get Data", data=data.to_csv().encode("utf-8"), file_name="CategorySales.csv", mime="text/csv")

with view2:
    expander = st.expander("Region wise Sales")
    data = df[["Region", "Sales"]].groupby("Region")["Sales"].sum()
    expander.write(data)
with dwn2:
    st.download_button("Get Data", data=data.to_csv().encode("utf-8"), file_name="RegionSales.csv", mime="text/csv")

st.divider()

# Monthly Sales Trend
_, col6, col7 = st.columns([0.1, 0.45, 0.45])
with col6:
    st.subheader("Monthly Sales Trend")
    df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")
    df = df.dropna(subset=["Order Date"])
    df["Month"] = df["Order Date"].dt.to_period("M").astype(str)
    monthly_sales = df.groupby("Month")["Sales"].sum().reset_index()
    fig3 = px.line(monthly_sales, x="Month", y="Sales", title="Monthly Sales Trend", markers=True,
                   labels={"Sales": "Total Sales", "Month": "Month"}, template="plotly")
    fig3.update_traces(line=dict(color="green"))
    fig3.update_layout(width=500, height=500)
    st.plotly_chart(fig3, use_container_width=False)

_, view3, dwn3, view4, dwn4 = st.columns([0.15, 0.20, 0.20, 0.20, 0.20])
with view3:
    expander = st.expander("Monthly Sales")
    data = df[["Month", "Sales"]].groupby("Month")["Sales"].sum()
    expander.write(data)
with dwn3:
    st.download_button("Get Data", data=data.to_csv().encode("utf-8"), file_name="MonthlySales.csv", mime="text/csv")

# Treemap Region-State
treemap = df[["Region", "State", "Sales"]].groupby(["Region", "State"])["Sales"].sum().reset_index()
def format_sales(value):
    return '{:.2f} Lakh'.format(value / 1_00_000) if pd.notnull(value) else '0'
treemap["Sales (Formatted)"] = treemap["Sales"].apply(format_sales)
fig4 = px.treemap(treemap, path=["Region", "State"], values="Sales", hover_name="State",
                  hover_data={"Sales (Formatted)": True, "Sales": False}, color="State", height=600, width=500)
fig4.update_traces(textinfo="label+value")
with col7:
    st.subheader("Region-State Wise Sales Treemap")
    st.plotly_chart(fig4, use_container_width=False)

with view4:
    expander = st.expander("Region-State Wise Sales (Lakhs)")
    view_data = treemap[["Region", "State", "Sales"]].copy()
    view_data["Sales (Lakhs)"] = view_data["Sales"].apply(lambda x: round(x))
    expander.write(view_data[["Region", "State", "Sales (Lakhs)"]])
with dwn4:
    st.download_button("Get Data", data=view_data.to_csv(index=False).encode("utf-8"),
                       file_name="RegionStateSales.csv", mime="text/csv")

st.divider()

# Segment and Top Products Charts
_, col8, col9 = st.columns([0.1, 0.45, 0.45])
with col8:
    fig = px.bar(df, x="Segment", y="Sales", labels={"Sales": "Sales ($)"},
                 title="Total Sales by Segments", hover_data=["Sales"],
                 template="gridon", height=500)
    st.plotly_chart(fig, use_container_width=True)

with col9:
    top_products = df.groupby("Product Name")["Sales"].sum().reset_index()
    top_products = top_products.sort_values(by="Sales", ascending=False).head(10)
    fig = px.bar(top_products, x="Sales", y="Product Name", orientation="h",
                 title="Top 10 Products by Sales",
                 labels={"Sales": "Total Sales ($)", "Product Name": "Product"},
                 template="gridon", height=500)
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig, use_container_width=True)

_, view5, dwn5, view6, dwn6 = st.columns([0.15, 0.20, 0.20, 0.20, 0.20])
with view5:
    expander = st.expander("Segment wise Sales")
    data = df[["Segment", "Sales"]].groupby("Segment")["Sales"].sum()
    expander.write(data)
with dwn5:
    st.download_button("Get Data", data=data.to_csv().encode("utf-8"), file_name="SegmentSales.csv", mime="text/csv")

with view6:
    expander = st.expander("Top 10 Products Data")
    expander.write(top_products)
with dwn6:
    st.download_button("Download Top 10 Products",
                       data=top_products.to_csv(index=False).encode("utf-8"),
                       file_name="Top_10_Products.csv", mime="text/csv")