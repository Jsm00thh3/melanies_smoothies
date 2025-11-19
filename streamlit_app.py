# Import python packages
import streamlit as st
import requests   # moved to the top as required
from snowflake.snowpark.functions import col

# Debug print to confirm secrets loaded
st.write("Loaded secrets:", st.secrets.keys())

# App title
st.title(f"Customize Your Smoothie :cup_with_straw: {st.__version__}")
st.write("Choose the fruits you want in your custom Smoothie!")

# Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# UI: Name on smoothie
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Load fruit options from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
fruit_list = my_dataframe.to_pandas()["FRUIT_NAME"].tolist()

# UI: Multiselect fruit picker
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list
)

# When ingredients selected
if ingredients_list:
    ingredients_string = ""

    # Loop through selected fruits
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

        # Lab requirement: call SmoothieFroot API for each fruit
        smoothiefroot_response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{fruit_chosen.lower()}"
        )

        # Display nutrition for each fruit
        st.subheader(f"Nutrition data for {fruit_chosen}:")
        st.write(smoothiefroot_response.json())

    # Submit button to insert order in Snowflake
    time_to_insert = st.button('Submit Order', key='submit_order')

    if time_to_insert:
        my_insert_stmt = f"""
            INSERT INTO smoothies.public.orders(ingredients, name_on_order)
            VALUES ('{ingredients_string}', '{name_on_order}')
        """
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")
