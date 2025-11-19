# Import python packages
import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col

st.write("Loaded secrets:", st.secrets.keys())

# Title
st.title(f"Customize Your Smoothie :cup_with_straw: {st.__version__}")
st.write("Choose the fruits you want in your custom Smoothie!")

# Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# Name input
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Load FRUIT_NAME + SEARCH_ON
my_dataframe = session.table("smoothies.public.fruit_options") \
                     .select(col('FRUIT_NAME'), col('SEARCH_ON'))

# Convert Snowpark DF → Pandas
pd_df = my_dataframe.to_pandas()

# Ingredient selector (show FRUIT_NAME only)
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

# When user selects fruits
if ingredients_list:
    ingredients_string = ""

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

        # Use SEARCH_ON instead of FRUIT_NAME
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]

        st.subheader(f"{fruit_chosen} Nutrition Information")

        # API call using SEARCH_ON value
        smoothiefroot_response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{search_on}"
        )

        st.dataframe(
            data=smoothiefroot_response.json(),
            use_container_width=True
        )

    # Insert into orders table
    my_insert_stmt = f"""
        insert into smoothies.public.orders(ingredients, name_on_order)
        values ('{ingredients_string}', '{name_on_order}')
    """

    # Submit button
    if st.button("Submit Order"):
        session.sql(my_insert_stmt).collect()
        st.success("Your Smoothie is ordered!", icon="✅")
