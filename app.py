import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURE LARGE FILE UPLOAD SIZE (up to 1000 MB) ---
#st.set_option('server.maxUploadSize', 1000)

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

# --- HEADER ---
st.markdown("""
    <h1 style='text-align: center; color: #003366;'>Donor Data Management and Cultivation Strategy Analysis</h1>
    <h3 style='text-align: center; color: #444444;'>MCBertyd Foundation | FY2022–FY2024 Donor Trends & Recommendations</h3>
    <p style='text-align: center; font-size: 16px; color: #555555;'>
        An analysis of donor behaviors, engagement patterns, and fundraising opportunities to support strategic decision-making.
    </p>
    <hr style='border-top: 1px solid #bbb; margin-top: 10px; margin-bottom: 20px;'>
""", unsafe_allow_html=True)

# --- SIDEBAR: DATA INPUT OPTIONS ---
st.sidebar.header("Data Input")
data_input_method = st.sidebar.radio(
    "Upload donor data:",
    ("Upload File")
)

data = None  # Initialize

# --- DATA INPUT HANDLING ---
if data_input_method == "Upload File":
    uploaded_file = st.file_uploader(
        "Drag and drop your file here",
        help="Limit 1000MB per file • Accepts XLSX, CSV, and more",
        type=None
    )

    if uploaded_file:
        try:
            file_name = uploaded_file.name.lower()

            if file_name.endswith('.xlsx') or file_name.endswith('.xls'):
                data = pd.read_excel(uploaded_file)
                st.success("Excel file uploaded successfully.")

            elif file_name.endswith('.csv'):
                data = pd.read_csv(uploaded_file)
                st.success("CSV file uploaded successfully.")

            else:
                st.warning("⚠️ Unsupported file type. Please upload an Excel (.xlsx/.xls) or CSV (.csv) file.")
                data = None

        except Exception as e:
            st.error(f"⚠️ Failed to read the uploaded file: {e}")
    else:
        st.info("Please upload a file to proceed.")

# --- PROCESS AND VISUALIZE DATA IF AVAILABLE ---
try:
    if data is not None and not data.empty:

        # PIE CHART: Gift Frequency
        gift_frequency = data["Gift Frequency"].value_counts().reset_index()
        gift_frequency.columns = ["Frequency", "Counts"]
        gift_freqplot = px.pie(
            gift_frequency, names='Frequency', values='Counts',
            title='Distribution of Yearly Gift Frequencies',
            width=500, height=500
        )

        # HISTOGRAM: Last Gift Date
        lastgiftplot = px.histogram(
            data, x="Last Gift Date", nbins=15,
            title="Timeline of Last Gifts by Date",
            width=800, height=500
        )
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
        donation_plot = px.bar(
            col_totals_df, x='Donation Year', y='Total Amount',
            title="Total Donations by Year", text='Total Amount',
            width=600, height=500
        )
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
        attendanceplot = px.pie(
            attendance, names="Event Attendance", values="Counts",
            hole=0.6, title="Event Attendance Representation",
            width=500, height=500
        )

        # --- TABS ---
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
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
                    by="TotalDonations", ascending=False).head(top_n)
                bottom = data.drop_duplicates(subset=["Donor Name"]).sort_values(
                    by="TotalDonations", ascending=True).head(top_n)

            st.markdown(f"#### Top {top_n} Donors – {year_option}")
            st.dataframe(top, use_container_width=True)

            st.markdown(f"#### Bottom {top_n} Donors – {year_option}")
            st.dataframe(bottom, use_container_width=True)

        with tab6:
            st.subheader("Actionable Insights & Recommendations")

            insights = """
            **1. Prioritize High-Value Donors**  
            Establish a major donor stewardship program with personalized engagement.

            **2. Re-Engage Dormant Donors**  
            Launch targeted re-engagement campaigns for those inactive since FY2022.

            **3. Leverage Event Attendance**  
            Track attendance to boost RSVP-to-donation conversion.

            **4. Target Recurring Givers**  
            Invite annual givers into recurring monthly/quarterly programs.

            **5. Improve Email Collection**  
            Incentivize email collection with exclusive newsletters and events.

            **6. Segment Giving Frequency**  
            Convert one-time givers into repeat donors through tailored messaging.

            **7. Use Relationship Notes**  
            Support staff in updating relationship notes to personalize outreach.

            **8. Analyze Giving Gaps**  
            Identify high-potential but irregular donors for follow-up.
            """
            st.markdown(insights)

    else:
        st.info("👆 Please upload or enter data to see visualizations and insights.")

except Exception as e:
    st.error(f"⚠️ An unexpected error occurred: {e}")
