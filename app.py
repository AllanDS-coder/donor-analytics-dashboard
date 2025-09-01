import streamlit as st
import pandas as pd
import plotly.express as px

# --- PAGE CONFIG ---
st.set_page_config(page_title="Donation Dashboard", layout="wide")

# --- CUSTOM CSS FOR BACKGROUND ---
st.markdown("""
    <style>
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1507525428034-b723cf961d3e");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }

    .block-container {
        background-color: rgba(255, 255, 255, 0.85);
        padding: 2rem;
        border-radius: 12px;
    }

    h1, h2, h3 {
        color: #003366;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <h1 style='text-align: center; color: #003366;'>Donor Data Management and Cultivation Strategy Analysis</h1>
    <h3 style='text-align: center; color: #444444;'>MCBertyd Foundation | FY2022–FY2024 Donor Trends & Recommendations</h3>
    <p style='text-align: center; font-size: 16px; color: #555555;'>
        An analysis of donor behaviors, engagement patterns, and fundraising opportunities to support strategic decision-making.
    </p>
    <hr style='border-top: 1px solid #bbb; margin-top: 10px; margin-bottom: 20px;'>
""", unsafe_allow_html=True)

# --- LOAD DATA ---
@st.cache_data
def load_data():
    return pd.read_excel("cleandata.xlsx")

try:
    data = load_data()

    # PIE CHART: Gift Frequency
    gift_frequency = data["Gift Frequency"].value_counts().reset_index()
    gift_frequency.columns = ["Frequency", "Counts"]
    gift_freqplot = px.pie(gift_frequency, names='Frequency', values='Counts',
                           title='Distribution of Yearly Gift Frequencies',
                           width=500, height=500)

    # HISTOGRAM: Last Gift Date
    lastgiftplot = px.histogram(data, x="Last Gift Date", nbins=15,
                                 title="Timeline of Last Gifts by Date",
                                 width=800, height=500)
    lastgiftplot.update_layout(
        title={'x': 0.5, 'xanchor': 'center'},
        xaxis_title="Date of Last Gift",
        yaxis_title="Number of Gifts",
        xaxis=dict(showgrid=True, gridcolor='lightgrey'),
        yaxis=dict(showgrid=True, gridcolor='lightgrey')
    )

    # BAR CHART: Total Donations
    col_totals = data[['Donations 2022', 'Donations 2023', 'Donations 2024', 'TotalDonations']].sum()
    col_totals_df = col_totals.reset_index()
    col_totals_df.columns = ['Donation Year', 'Total Amount']
    donation_plot = px.bar(col_totals_df, x='Donation Year', y='Total Amount',
                           title="Total Donations by Year", text='Total Amount',
                           width=600, height=500)
    donation_plot.update_layout(
        title={'x': 0.5},
        xaxis_title="Year",
        yaxis_title="Donation Amount",
        yaxis=dict(showgrid=True, gridcolor='lightgrey'),
        xaxis=dict(showgrid=True, gridcolor='lightblue')
    )

    # DONUT CHART: Event Attendance
    attendance = data["Event Attendance"].value_counts().reset_index()
    attendance.columns = ("Event Attendance", "Counts")
    attendanceplot = px.pie(attendance, names="Event Attendance", values="Counts",
                            hole=0.6, title="Event Attendance Representation",
                            width=500, height=500)

    # --- TABS ---
    tab1, tab2, tab3, tab4, tab5,tab6 = st.tabs([
        "Gift Frequency",
        "Last Gift Timeline",
        "Donations",
        "Event Attendance",
        "Donor Cultivation Analysis",
	"Actionable Insights and Recommendations"
    ])

    with tab1:
        st.subheader("Gift Frequency Distribution")
        st.plotly_chart(gift_freqplot, use_container_width=True)

    with tab2:
        st.subheader("Timeline of Last Gift Dates")
        st.plotly_chart(lastgiftplot, use_container_width=True)

    with tab3:
        st.subheader("Total Donations by Year")
        st.plotly_chart(donation_plot, use_container_width=True)

    with tab4:
        st.subheader("Event Attendance Representation")
        st.plotly_chart(attendanceplot, use_container_width=True)

    with tab5:
        st.subheader("Donor Cultivation & Giving Trends")

        # Average Donations
        st.markdown("### Average Donations (2022–2024)")
        ave_donation = round(data[["Donations 2022", "Donations 2023", "Donations 2024", "TotalDonations"]].mean(), 2)
        st.dataframe(
            ave_donation.reset_index().rename(columns={'index': 'Year', 0: 'Average Donation ($)'}),
            use_container_width=True
        )

        # --- TOP DONORS BY AVERAGE DONATION ---
        st.markdown("### Top Donors by Average Annual Donation (2022–2024)")

        avg_top_n = st.slider(
            "Select number of top average donors to view",
            min_value=5, max_value=50, value=10, key="avg_donors_slider"
        )

        data_avg = data.copy()
        data_avg["Average Donation"] = data_avg[["Donations 2022", "Donations 2023", "Donations 2024"]].mean(axis=1)

        avg_top_donors = data_avg.drop_duplicates(subset=["Donor Name"]).sort_values(
            by="Average Donation", ascending=False
        )

        avg_top_donors = avg_top_donors[[
            "Donor Name", "Average Donation", "Donations 2022", "Donations 2023", "Donations 2024",
            "Last Gift Date", "Gift Frequency", "Event Attendance", "Relationship Notes", "TotalDonations"
        ]]

        st.dataframe(avg_top_donors.head(avg_top_n), use_container_width=True)

        # --- TOP & BOTTOM DONORS ---
        st.markdown("### Explore Top & Bottom Donors")

        year_option = st.selectbox("Select Year", ["2022", "2023", "2024", "All Years"])
        top_n = st.slider("Number of donors to show", min_value=5, max_value=50, value=10)

        def get_donor_slice(year_col, donation_label):
            donors_sorted = data.drop_duplicates(subset=["Donor Name"]).sort_values(by=year_col, ascending=False)
            top_donors = donors_sorted.head(top_n)[[
                'Donor Name', year_col, 'Last Gift Date', 'Gift Frequency',
                'Event Attendance', 'Relationship Notes', 'TotalDonations'
            ]].rename(columns={year_col: donation_label})

            bottom_donors = donors_sorted.sort_values(by=year_col, ascending=True).head(top_n)[[
                'Donor Name', year_col, 'Last Gift Date', 'Gift Frequency',
                'Event Attendance', 'Relationship Notes', 'TotalDonations'
            ]].rename(columns={year_col: donation_label})

            return top_donors, bottom_donors

        if year_option == "2022":
            top, bottom = get_donor_slice("Donations 2022", "Donations 2022")
        elif year_option == "2023":
            top, bottom = get_donor_slice("Donations 2023", "Donations 2023")
        elif year_option == "2024":
            top, bottom = get_donor_slice("Donations 2024", "Donations 2024")
        else:
            top = data.drop_duplicates(subset=["Donor Name"]).sort_values(
                by="TotalDonations", ascending=False).head(top_n)[[
                    'Donor Name', 'TotalDonations', 'Last Gift Date', 'Gift Frequency',
                    'Event Attendance', 'Relationship Notes'
                ]]
            bottom = data.drop_duplicates(subset=["Donor Name"]).sort_values(
                by="TotalDonations", ascending=True).head(top_n)[[
                    'Donor Name', 'TotalDonations', 'Last Gift Date', 'Gift Frequency',
                    'Event Attendance', 'Relationship Notes'
                ]]

        st.markdown(f"####  Top {top_n} Donors – {year_option}")
        st.dataframe(top, use_container_width=True)

        st.markdown(f"####  Bottom {top_n} Donors – {year_option}")
        st.dataframe(bottom, use_container_width=True)

    with tab6:
        st.subheader(" Actionable Insights & Recommendations")

        insights = """
        **1. Prioritize High-Value Donors**  
        A small group of donors consistently contributes the highest average annual donations.  
        _Recommendation:_ Establish a major donor stewardship program to engage these top donors with personalized updates, events, and recognition opportunities.

        **2. Re-Engage Dormant Donors**  
        A notable percentage of donors have not given since FY2022.  
        _Recommendation:_ Launch a re-engagement campaign (email, phone, or in-person) to reconnect and understand their reasons for inactivity.

        **3. Leverage Event Attendance Behavior**  
        Event attendees tend to have higher total donations than non-attendees.  
        _Recommendation:_ Expand donor event opportunities and track RSVP vs. gift conversion to better plan future engagements.

        **4. Target Consistent Givers for Recurring Programs**  
        Donors who give every year exhibit high loyalty and reliability.  
        _Recommendation:_ Invite them to join monthly or quarterly giving programs to increase retention and lifetime value.

        **5. Improve Email Communication**  
        Many donors lack recorded email addresses, limiting digital engagement.  
        _Recommendation:_ Prioritize email collection in all interactions. Use incentives like newsletters or early-access event invites to encourage sign-ups.

        **6. Segment by Giving Frequency**  
        One-time donors dominate the database but contribute less overall.  
        _Recommendation:_ Use segmentation to craft specific messaging for one-time, occasional, and frequent donors, aiming to convert one-time givers into repeat supporters.

        **7. Capture and Utilize Relationship Notes**  
        Some donor profiles include valuable personal notes.  
        _Recommendation:_ Encourage staff to regularly update relationship notes to support personalized outreach, especially for stewardship or planned giving.

        **8. Analyze Giving Gaps**  
        A few high-potential donors show irregular giving patterns.  
        _Recommendation:_ Identify these gaps and investigate if internal or external factors (e.g. lack of follow-up, change in contact info) contributed.
        """

        st.markdown(insights)
   


# --- ERROR HANDLING ---
except FileNotFoundError:
    st.error("❌ File 'cleandata.xlsx' not found in this directory.")
except Exception as e:
    st.error(f"⚠️ An error occurred: {e}")