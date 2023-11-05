import streamlit as st
import requests
import numpy as np
import pandas as pd

st.title("Streamlit Interface for prediction")
# if st.button("predict from data")
# Create input fields to collect data
tot_rooms_abv_grd = st.number_input("Total rooms above grade (does not include bathrooms)", min_value=0)
wood_deck_sf = st.number_input("Wood deck area in square feet  ", min_value=0)
yr_sold = st.number_input("Year Sold (YYYY)", min_value=1900, max_value=2100, value=2023, step=1)
first_flr_sf = st.number_input("First Floor square feet", min_value=0)

foundation_options = ['Brick & Tile', 'Cinder Block', 'Poured Concrete', 'Slab', 'Stone', 'Wood']
foundation = st.selectbox("Foundation", foundation_options, index=0)

kitchen_qual_options = ['Excellent', 'Good', 'Average', 'Fair', 'Poor']
kitchen_qual = st.selectbox("Kitchen Quality", kitchen_qual_options, index=0)



if st.button("Predict"):
    # Collect all radio button values
    foundation_values = {option: 1 if option == foundation else 0 for option in foundation_options}
    kitchen_qual_values = {option: 1 if option == kitchen_qual else 0 for option in kitchen_qual_options}

    # group data for API request
    data = {
        "TotRmsAbvGrd": tot_rooms_abv_grd,
        "WoodDeckSF": wood_deck_sf,
        "YrSold": yr_sold,
        "FirstFlrSF": first_flr_sf,
        **foundation_values,
        **kitchen_qual_values,
    }
    # st.write(data)
    # breakpoint()
    response = requests.post("http://127.0.0.1:8000/predict", json=data)
    # st.write(response.json())
    # breakpoint()
    
    if (response.status_code == 200 or response.status_code == 422):
        # st.write(response.json())
        # breakpoint()
        prediction = response.json()
        st.subheader("The estimated price of the house is ")
        st.write(prediction["predictions"])
        st.subheader("Based on the data received below:")
        
        single_predict_data = pd.DataFrame({
            "TotRmsAbvGrd": prediction["data"][0],
            "WoodDeckSF": prediction["data"][0],
            "YrSold": prediction["data"][0],
            "FirstFlrSF": prediction["data"][0],
            "Foundation_BrkTil": prediction["data"][0],
            "Foundation_CBlock": prediction["data"][0],
            "Foundation_PConc": prediction["data"][0],
            "Foundation_Slab": prediction["data"][0],
            "Foundation_Stone": prediction["data"][0],
            "Foundation_Wood": prediction["data"][0],
            "KitchenQual_Ex": prediction["data"][0],
            "KitchenQual_Fa": prediction["data"][0],
            "KitchenQual_Gd": prediction["data"][0],
            "KitchenQual_TA": prediction["data"][0],
        },index=[1])

        st.write(single_predict_data)

    else:
        st.write("An error occurred during prediction."+str(response.status_code))
