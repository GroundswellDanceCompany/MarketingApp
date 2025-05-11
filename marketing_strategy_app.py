
import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = st.secrets["gcp_service_account"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

campaigns_sheet = client.open("Groundswell-Business").worksheet("marketing_campaigns")
leads_sheet = client.open("Groundswell-Business").worksheet("leads")
conversions_sheet = client.open("Groundswell-Business").worksheet("conversions")
forecast_sheet = client.open("Groundswell-Business").worksheet("growth_forecast")

st.title("Marketing Strategy Dashboard")

tab1, tab2, tab3, tab4 = st.tabs(["Campaign Tracker", "Lead Tracker", "Conversion Report", "Growth Forecast"])

with tab1:
    st.header("Create & Track Campaigns")
    with st.form("add_campaign", clear_on_submit=True):
        name = st.text_input("Campaign Name")
        start = st.date_input("Start Date")
        end = st.date_input("End Date")
        platform = st.selectbox("Platform", ["Instagram", "Facebook", "Flyers", "Email", "Other"])
        budget = st.number_input("Budget (£)", min_value=0.0, step=1.0)
        status = st.selectbox("Status", ["Planned", "Running", "Completed"])
        notes = st.text_area("Notes")
        submit = st.form_submit_button("Add Campaign")
        if submit:
            campaigns_sheet.append_row([name, str(start), str(end), platform, budget, status, notes])
            st.success("Campaign added.")

    data = pd.DataFrame(campaigns_sheet.get_all_records())
    if not data.empty:
        st.subheader("All Campaigns")
        st.dataframe(data)

with tab2:
    st.header("Track New Leads")
    with st.form("add_lead", clear_on_submit=True):
        date = st.date_input("Lead Date", value=datetime.today())
        source = st.selectbox("Source", ["Website", "Social Media", "Referral", "Event", "Other"])
        interest = st.text_input("Interest (e.g. Junior Ballet)")
        status = st.selectbox("Status", ["New", "Contacted", "Converted", "Uninterested"])
        submit = st.form_submit_button("Add Lead")
        if submit:
            leads_sheet.append_row([str(date), source, interest, status])
            st.success("Lead recorded.")

    leads_df = pd.DataFrame(leads_sheet.get_all_records())
    if not leads_df.empty:
        st.dataframe(leads_df)

with tab3:
    st.header("Conversion Analysis")
    data = pd.DataFrame(conversions_sheet.get_all_records())
    if not data.empty:
        st.dataframe(data)
        total = len(data)
        successful = len(data[data["Status"] == "Converted"])
        st.metric("Total Conversions", successful)
        if total > 0:
            st.metric("Conversion Rate", f"{(successful / total) * 100:.1f}%")

with tab4:
    st.header("Growth Forecast")
    forecast = pd.DataFrame(forecast_sheet.get_all_records())
    if not forecast.empty:
        st.dataframe(forecast)
    else:
        st.info("No forecast data found yet.")
