# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests   # ← NEW for API requests

st.write("Loaded secrets:", st.secrets.keys())

# Write directly to the app
st.title(f"Customize Your Smoothie :cup_with_straw: {st.__version__}")
st.write(
  """Choose the fruits you want in your custom Smoothie!
  """
)

# NEW SniS CONNECTION (correct)
cnx = st.connection("snowflake")
session = cnx.session()

# UI input
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Read data from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

# Convert to pandas list
fruit_list = my_dataframe.to_pandas()["FRUIT_NAME"].tolist()

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list
)

# Insert order when submitted
if ingredients_list:
    ingredients_string = ' '.join(ingredients_list)

    my_insert_stmt = f"""
        insert into smoothies.public.orders(ingredients, name_on_order)
        values ('{ingredients_string}', '{name_on_order}')
    """

    time_to_insert = st.button('Submit Order', key='submit_order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")


# -------------------------------------------------
# 🍉 SmoothieFroot Nutrition API Section (NEW)
# -------------------------------------------------

st.header("Fruit Nutrition Info 🍓")

fruit_choice = st.text_input("Enter a fruit to look up nutrition info:")

if fruit_choice:
    url = f"https://my.smoothiefroot.com/api/fruit/{fruit_choice.lower()}"
    response = requests.get(url)

    if response.status_code == 200:
        st.subheader(f"Nutrition for: {fruit_choice.capitalize()}")
        st.json(response.json())
    else:
        st.error("Fruit not found or API error. Try another fruit.")
