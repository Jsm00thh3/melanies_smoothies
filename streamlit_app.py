# Import python packages
import streamlit as st
import requests
from snowflake.snowpark.functions import col

st.write("Loaded secrets:", st.secrets.keys())

# Title
st.title(f"Customize Your Smoothie :cup_with_straw: {st.__version__}")
st.write(
    """Choose the fruits you want in your custom Smoothie!
    """
)

# Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# Name input
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Load fruit list
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
fruit_list = my_dataframe.to_pandas()["FRUIT_NAME"].tolist()

# Pick ingredients
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list
)

# Process selection
if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        # SmoothieFroot API call (inside loop — per lab instructions)
        smoothiefroot_response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{fruit_chosen}"
        )

        sf_df = st.dataframe(
            data=smoothiefroot_response.json(),
            use_container_width=True
        )

    # Insert record when button clicked
    my_insert_stmt = f"""
        insert into smoothies.public.orders(ingredients, name_on_order)
        values ('{ingredients_string}', '{name_on_order}')
    """

    time_to_insert = st.button('Submit Order', key='submit_order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")
