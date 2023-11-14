import streamlit as st
import requests
import pandas as pd

st.title("Streamlit Interface for prediction")

def page1():
    tot_rooms_abv_grd = st.number_input("Total rooms above grade (does not include bathrooms)", min_value=0, step=1)
    wood_deck_sf = st.number_input("Wood deck area in square feet  ", min_value=0, step=1)
    yr_sold = st.number_input("Year Sold (YYYY)", min_value=1900, max_value=2100, value=2023, step=1)
    first_flr_sf = st.number_input("First Floor square feet", min_value=0, step=1)

    foundation_options = ['Foundation_BrkTil', 'Foundation_CBlock', 'Foundation_PConc', 'Foundation_Slab', 'Foundation_Stone', 'Foundation_Wood']
    foundation = st.selectbox("Foundation", foundation_options, index=0)

    kitchen_qual_options = ['KitchenQual_Ex', 'KitchenQual_Fa', 'KitchenQual_Gd', 'KitchenQual_TA']
    kitchen_qual = st.selectbox("Kitchen Quality", kitchen_qual_options, index=0)

    foundation_values = {option: 1 if option == foundation else 0 for option in foundation_options}
    kitchen_qual_values = {option: 1 if option == kitchen_qual else 0 for option in kitchen_qual_options}

    st.write("---")
    return {
        "type": "single",
        "data": {
           "TotRmsAbvGrd": tot_rooms_abv_grd,
            "WoodDeckSF": wood_deck_sf,
            "YrSold": yr_sold,
            "FirstFlrSF": first_flr_sf,
            **foundation_values,
            **kitchen_qual_values,
        }
    }

def page2():
    uploaded_file = st.file_uploader("Upload your csv file", type=["csv"])
    if uploaded_file is not None:

        st.write("---")
        return {
            "type": "multiple",
            "data": uploaded_file
        }

        if st.button("Predict"):
            # Envoyer le fichier au serveur FastAPI pour la prédiction}
            # Lire le contenu du fichier CSV
            # contenu_csv = uploaded_file.read()

            # Envoyer le fichier téléchargé à FastAPI
            files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
            # st.write(files)
            # breakpoint()
            response = requests.post("http://localhost:8000/predict_csv", files=files)
           
            if response.status_code == 200:
                from io import StringIO
                
                predictions = response.json()["predictions"]
                # Convert the csv file to a dataframe just to display datas 
                input_data = pd.read_csv(StringIO(uploaded_file.getvalue().decode("utf-8")))

                # # Add a prediction column to the dataframe
                
                input_data["Predictions"] = predictions

                # # Display all the dataframe now to the streamlit UI
                st.write(input_data)
            else:
                st.write("An error occurred during prediction.")
############################################################################################################

def main():
    st.write("---")
    pages = ["From Inputs", "From CSV"]
    selected_page = st.selectbox("Select your prediction type", pages)
    st.write("----")
    
    if selected_page == "From Inputs":
        prediction_data = page1()
    elif selected_page == "From CSV":
        prediction_data = page2()
    if st.button("Predict"):
        if prediction_data["type"] == "single":
            response = requests.post("http://localhost:8000/predict", json={"file":prediction_data["data"]})
        elif prediction_data["type"] == "multiple":
            csv_content = prediction_data["data"].read().decode("utf-8")
            rows = [list(map(int, row.split(','))) for row in csv_content.split('\n')]
            data = {"file": rows}

            response = requests.post("http://localhost:8000/predict", json=data)
        if response.status_code == 200:
            prediction = response.json()

            if prediction_data["type"] == "single":
                if "predictions" in prediction and "data" in prediction:
                    st.subheader("The estimated price of the house is ")
                    st.write(round(prediction["predictions"],2))
                    st.subheader("Based on the data received below:")
                    
                    single_predict_data = pd.DataFrame({
                        "TotRmsAbvGrd": prediction["data"][0],
                        "WoodDeckSF": prediction["data"][1],
                        "YrSold": prediction["data"][2],
                        "FirstFlrSF": prediction["data"][3],
                        "Foundation_BrkTil": prediction["data"][4],
                        "Foundation_CBlock": prediction["data"][5],
                        "Foundation_PConc": prediction["data"][6],
                        "Foundation_Slab": prediction["data"][7],
                        "Foundation_Stone": prediction["data"][8],
                        "Foundation_Wood": prediction["data"][9],
                        "KitchenQual_Ex": prediction["data"][10],
                        "KitchenQual_Fa": prediction["data"][11],
                        "KitchenQual_Gd": prediction["data"][12],
                        "KitchenQual_TA": prediction["data"][13],
                        "Result": round(prediction["predictions"],2)
                    },index=[1])

                    st.write(single_predict_data)

            elif prediction_data["type"] == "multiple":
                if "original_data" in prediction and "predictions" in prediction:
                    st.write("Original Data:")
                    df_result = pd.DataFrame(prediction["original_data"])
                    df_result["Result"] = prediction["predictions"]
                    st.write(df_result)

        else:
            st.write("An error occurred during prediction 1.")

if __name__ == "__main__":
    main()
