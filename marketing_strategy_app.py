
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
campaign_ideas = client.open("Groundswell-Business").worksheet("idea_log")

st.title("Marketing Strategy Dashboard")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Campaign Tracker", "Lead Tracker", "Conversion Report", "Growth Forecast", "Campaign Ideas"])

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

with tab5:
    st.subheader("Campaign Ideas")

    campaign_ideas_dict = {
        "Meet the Dancer Series": "Weekly reels introducing students or teachers, using trending music.",
        "Countdown to Show Campaign": "Daily content leading to show day. Teasers, interviews, etc.",
        "YouTube 'Learn a Step' Series": "Short tutorials on basic dance steps to attract new students.",
        "Seasonal Mini Challenges": "Instagram/TikTok challenges with hashtags and community sharing.",
        "Google Review Drive": "Encourage reviews with incentives. Share review links via email/WhatsApp.",
        "Email Series: Why Dance?": "Automated emails about dance benefits to inform and attract.",
        "Flyer Distribution at Local Events": "QR-coded flyers handed out locally. Link to your site or Instagram.",
        "Open Day Event": "Host a free open day to showcase your classes and attract new students.",
        "Bring a Friend Week": "Encourage current students to bring friends for a trial week.",
        "Student of the Month Spotlight": "Feature outstanding students on social media and newsletters.",
        "Social Media Challenge": "Run a fun dance challenge with a hashtag to boost engagement.",
        "Mini Video Series on Class Types": "Create short videos introducing each class you offer.",
        "Behind-the-Scenes Rehearsal Stories": "Share authentic moments from your rehearsals.",
        "Parent Testimonial Campaign": "Collect and promote positive feedback from parents.",
        "Early Bird Discount for New Term": "Offer early registration incentives for the upcoming term.",
        "Seasonal Performance Promo": "Advertise shows with themed content during holidays.",
        "Instagram Giveaway or Competition": "Launch a giveaway to grow your online audience."
    }

    idea_names = list(campaign_ideas_dict.keys())

    selected_ideas = st.multiselect("Select Campaign Ideas to Plan", idea_names)

    if selected_ideas:
        for idea in selected_ideas:
            st.markdown(f"**{idea}**: {campaign_ideas_dict[idea]}")

        start_date = st.date_input("Planned Start Date")
        end_date = st.date_input("Planned End Date")

        if st.button("Add Selected Campaign Ideas"):
            if start_date > end_date:
                st.warning("Start date cannot be after end date.")
            else:
                scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
                creds_dict = st.secrets["gcp_service_account"]
                creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
                client = gspread.authorize(creds)

                ideas_log_sheet = client.open("Groundswell-Business").worksheet("campaign_ideas_log")
                campaigns_sheet = client.open("Groundswell-Business").worksheet("campaigns")

                from datetime import datetime
                now = datetime.now().strftime("%Y-%m-%d %H:%M")

                for idea in selected_ideas:
                    description = campaign_ideas_dict[idea]
                    ideas_log_sheet.append_row([now, idea, description])
                    campaigns_sheet.append_row([
                        idea,
                        start_date.strftime("%Y-%m-%d"),
                        end_date.strftime("%Y-%m-%d"),
                        "",  # Platform
                        description,
                        "",  # Metrics
                        "Planned",
                        ""   # Outcome
                    ])

                st.success("Ideas and descriptions added to campaign tracker.")



            
