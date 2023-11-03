import streamlit as st
import pandas as pd
import datetime
import requests


st.markdown("# Past Predictions 🎈")
st.sidebar.markdown("# Here you can see all the past predictions")

today = datetime.datetime.now()
next_year = datetime.date(today.year + 1, today.month, today.day)
prediction_dates = st.date_input("Select the predictions start and end date",
                                 (today, next_year),
                                 format="DD/MM/YYYY")

prediction_options = ["all", "webapp", "scheduled predictions"]
prediction_source = st.selectbox("Select the prediction source",
                                 prediction_options)

if st.button("Get Predictions"):

    data = {
        "start_date": prediction_dates[0].strftime("%d/%m/%Y"),
        "end_date": prediction_dates[1].strftime("%d/%m/%Y"),
        "prediction_source": prediction_source
    }

    response = requests.get("http://127.0.0.1:8080/past-predictions", json=data)

    if (response.status_code == 200 or response.status_code == 422):
        db_contents = response.json()
        df = pd.DataFrame(db_contents)
        st.dataframe(df)
    else:
        st.write("An error occurred during prediction.")
