# NAEP AIR Summer Internship
# Elsie Lee
# July 2021

import altair as alt
import pandas as pd
from altair import datum
import streamlit as st

# Data Section
dataSection = True
if dataSection:
    # loading data
    NAEP = pd.read_csv(
        "/Data/NAEP/NAEP.csv")
    Pulse = pd.read_csv(
        "Data/CensusBureauPulseSurvey/Pulse.csv")
    Population = pd.read_csv(
        "/Data/CensusBureauPopulation/population.csv")
    EdWeek = pd.read_csv(
        "/Data/EdWeekSchoolFinance/EdWeek_SchoolFinance.csv")
    Policy = pd.read_csv(
        "/Data/Policy/policy.csv")
    PolicyCount = pd.read_csv(
        "/Data/Policy/policyCount.csv")
    hexs = pd.read_csv(
        "/Data/hexmap_plots.csv")

    # Dropping columns
    Pulse = Pulse.drop(columns=['Abbreviation'])
    EdWeek = EdWeek.drop(
        columns=['Grade', 'Total Score', 'McLoone Index', 'Coefficient of Variation', 'Restricted Range',
                 'Percent of students in districts with PPE at or above US average',
                 'Spending Index', 'Percent of total taxable resources spent on education'])
    # merging dfs
    IntAccess = pd.concat([Pulse, NAEP])
    IntHex = pd.merge(hexs, IntAccess, how="outer", on="Jurisdiction")
    NAEPHex = pd.merge(hexs, NAEP, how="outer", on="Jurisdiction")
    IntHexPolicy = pd.merge(IntHex, PolicyCount, how="outer", on="Jurisdiction")
    NAEPxEDWEEK = pd.merge(NAEPHex, EdWeek, how="outer", on="Jurisdiction")
    IntHexPolicy = pd.merge(IntHexPolicy, Population, how="outer", on=["Jurisdiction", "Year"])
    all_data = pd.merge(IntHexPolicy, EdWeek, how="outer", on=["Jurisdiction", "Year"])

def create_altair_parent(my_state):
    # Racing Internet Cable - slider over the years
    slider = alt.binding_range(min=2009, max=2021, step=2, name="Year  ")
    select_year = alt.selection_single(name="Slider", fields=['Year'],
                                       bind=slider, init={'Year': 2009})
    base = alt.Chart(all_data).mark_circle().encode(
        x=alt.Y("PercentInternet:Q", scale=alt.Scale(domain=[75, 100]),
                axis=alt.Axis(tickMinStep=0.5, title="Percent of students that have access to the internet at home")),
        opacity=alt.value(0.4),
        tooltip=["Jurisdiction", 'PercentInternet']
    ).transform_filter(select_year).transform_filter(datum.Group == "All")
    dots = base.mark_circle(size=400).encode(
        color=alt.Color("Region:N", scale=alt.Scale(scheme='viridis'))
    )
    my_dot = base.mark_circle(size=400, color='red').encode(
        opacity=alt.value(0.8)
    ).transform_filter(datum.Jurisdiction == my_state)
    text = base.mark_text(dy=-15).encode(
        text="Abbreviation"
    )
    racing_internet = (text + dots + my_dot).properties(width=700, height=100).configure_axis(
        grid=False).configure_view(
        strokeWidth=0).add_selection(select_year)

    # Racing Internet Cable - by groups
    base = alt.Chart(all_data).mark_circle().encode(
        x=alt.Y("PercentInternet:Q", scale=alt.Scale(domain=[80, 100]), axis=alt.Axis(
            tickMinStep=0.5, title="Percent of students that have access to the internet at home")),
        opacity=alt.value(1),
        tooltip=["Jurisdiction", "Group", "PercentInternet"]
    ).transform_filter(
        select_year
    ).transform_filter(datum.Group != "All")

    dots = base.mark_circle(size=400).add_selection(select_year).transform_filter(select_year)
    text = base.mark_text(dy=-15).encode(
        text="Group"
    )
    dots_LOC = dots.encode(color=alt.Color("Group", scale=alt.Scale(scheme='yellowgreen')))
    dots_NSLP = dots.encode(color=alt.Color("Group", scale=alt.Scale(scheme='inferno')))

    racing_internet_LOC = (dots_LOC + text).properties(width=700, height=100).configure_axis(
        grid=False).configure_view(strokeWidth=0).transform_filter(
        datum.Group != "Low-Income").transform_filter(datum.Group != "High-Income")
    racing_internet_NSLP = (dots_NSLP + text).properties(width=700, height=100).configure_axis(
        grid=False).configure_view(strokeWidth=0).transform_filter(
        datum.Group != "City").transform_filter(datum.Group != "Rural").transform_filter(
        datum.Group != "Suburb").transform_filter(datum.Group != "Town")

    return racing_internet, racing_internet_LOC, racing_internet_NSLP

def create_altair_policymaker():
    ### - Bubble chart = Pre-pandemic 2017 - ###
    base = alt.Chart(all_data).mark_circle().encode(
        y=alt.Y("Initiatives:Q"),
        x=alt.Y("PercentInternet:Q", scale=alt.Scale(domain=[90, 100]),
                axis=alt.Axis(title="Percentage of students that have access to the internet at home")),
        tooltip=["Jurisdiction", "Initiatives", "PercentInternet"]
    ).transform_filter(datum.Year == 2017).transform_filter(datum.Group == "All")
    bubbles = base.mark_circle().encode(
        size=alt.Size("Population:Q", scale=alt.Scale(domain=[-10000000, 30000])),
        color=alt.Color('Initiatives_Bin:N', scale=alt.Scale(scheme='darkblue'))
    )
    text = base.mark_text().encode(text="Abbreviation")
    bubblechart_pre = (bubbles + text).properties(width=700)

    ### - Bubble chart = Pandemic 2020 - ###
    base = alt.Chart(all_data).mark_circle().encode(
        y=alt.Y("Pandemic_Funding:Q"),
        x=alt.X("PercentInternet:Q", scale=alt.Scale(domain=[90, 100]),
                axis=alt.Axis(title="Percentage of students that have access to the internet at home")),
        order=alt.Order("Pandemic_Funding:Q",sort="ascending"),
        tooltip=['Jurisdiction', 'Pandemic_Funding', "PercentInternet"]
    ).transform_filter(datum.Year == 2021).transform_filter(datum.Group == "All")
    bubbles = base.mark_circle().encode(
        size=alt.Size("Population:Q", scale=alt.Scale(domain=[-10000000, 30000])),
        color=alt.Color('Funding_Bin', scale=alt.Scale(scheme='darkblue'))
    )
    text = base.mark_text().encode(text="Abbreviation")
    bubblechart_pan = (bubbles + text).properties(width=700)

    ### - Bubble chart - by LOCALE - ###
    loc_dict = {'Group': ['City', 'Suburb', 'Town', 'Rural'],
                'Population': [30, 41, 11, 19],
                'PercentInternet': [96.7, 98.1, 95.0, 94.8]}  # 2019 data NDE
    loc_df = pd.DataFrame(data=loc_dict)
    base = alt.Chart(loc_df).mark_circle(size=400).encode(
        x=alt.Y("PercentInternet:Q", scale=alt.Scale(domain=[90, 100]),
                axis=alt.Axis(title="Percentage of students that have access to the internet at home")),
        tooltip=["Group", "PercentInternet"]
    )
    bubbles = base.mark_circle(size=400).encode(
        size=alt.Size("Population", scale=alt.Scale(domain=[0,20])),
        color=alt.Color('Group:N', scale=alt.Scale(scheme="yellowgreen"))
    )
    text = base.mark_text(dy=-20).encode(text="Group")
    bubble_LOC = (bubbles + text).properties(width=700, height=100).configure_axis(grid=False).configure_view(strokeWidth=0)

    ### - Bubble chart - by INCOME - ###
    nslp_dict = {'Group': ['Eligible', 'Noneligible'],
                 'Population': [47, 46],
                 'PercentInternet': [94.6, 98.7]}
    nslp_df = pd.DataFrame(data=nslp_dict)
    base = alt.Chart(nslp_df).mark_circle(size=400).encode(
        x=alt.X("PercentInternet:Q", scale=alt.Scale(domain=[90, 100]),
                axis=alt.Axis(title="Percentage of students that have access to the internet at home")),
        tooltip=["Group", "PercentInternet"]
    )
    bubbles = base.mark_circle(size=400).encode(
        size=alt.Size("Population", scale=alt.Scale(domain=[0,20])),
        color=alt.Color('Group:N', scale=alt.Scale(scheme="inferno"))
    )
    text = base.mark_text(dy=-20).encode(text="Group")
    bubble_NSLP = (bubbles + text).properties(width=700, height=100).configure_axis(grid=False).configure_view(strokeWidth=0)

    return bubblechart_pre, bubblechart_pan, bubble_LOC, bubble_NSLP

def create_altair_policy(my_state):
    policy_text = alt.Chart(Policy.reset_index()).mark_text(align='left', lineBreak='\n',size=15).encode(
        y=alt.Y('State_index:O', axis=None, scale=alt.Scale(zero=False)),
        x=alt.X('Start:Q', scale=alt.Scale(domain=[0, 1]), axis=None),
        text=alt.Text('Formatted_Text'),
        order=alt.Order('State_index', sort='ascending')
    ).transform_filter(datum.Jurisdiction==my_state).transform_filter(datum.State_index>0
    ).properties(width=800).configure_axis(grid=False).configure_view(strokeWidth=0)
    return policy_text

def create_altair_stacked():
    pulse_week1 = {
        'Response': ['Always', 'Usually', 'Sometimes', 'Rarely', 'Never', 'Unknown'],
        'Value': [46713712, 11020451, 4887743, 1987773, 1096152, 855810],
        'I': [1, 2, 3, 4, 5, 6]
    }
    pulse_df = pd.DataFrame(data=pulse_week1)

    naep_2019 = {
        'Response': ['Yes', 'No'],
        'Value': [.9672, .0328],
        'I': [1, 2]
    }
    naep_df = pd.DataFrame(data=naep_2019)

    pulse_stacked = alt.Chart(pulse_df).mark_bar().encode(
        # x='variety',
        x=alt.X('sum(Value)', stack="normalize", title="Percentage of students who have access to internet"),
        color=alt.Color('Response', sort=['Always', 'Usually', 'Sometimes', 'Rarely', 'Never', 'Unknown'],
                        # sort=['Unknown', 'Never', 'Rarely', 'Sometimes', 'Usually', 'Always'],
                        scale=alt.Scale(scheme='darkblue')),
        order=alt.Order('I'),
        tooltip=['Response']
    ).properties(width=700, title="Census Bureau Household Pulse, 2020")

    naep_stacked = alt.Chart(naep_df).mark_bar(color='#ff8c00').encode(
        x=alt.X('sum(Value)', stack="normalize", title="Percentage of students who have access to internet"),
        tooltip='Value'
    ).properties(width=700, title='National Assessment of Educational Progress, 2019')
    stacked = pulse_stacked & naep_stacked
    return stacked

def state_list():
    hexs = pd.read_csv(
        "//dc3fs1/DC4Work/ESSIN Task 14/05_RAPS/Z_Misc/Interns/2021 Summer/Sandbox/Lee/Data/hexmap_plots.csv")
    states = hexs['Jurisdiction'].to_list()
    states.remove('National')
    return states

# Writing to the Streamlit App
### - TITLE AND INTRODUCTION - ###
st.title('Access to Internet in the United States')
st.write('Access to broadband internet at home is an important resource for education, whether it\'s for completing homework, practicing digital skills, or distance learning. However, not everyone has access to this essential resource. The digital divide refers to the gap between people who do not have access to the internet or digital devices and those that do. Students in rural areas and low-income students are disproportionately denied access to the internet for a variety of reasons. In rural areas, the infrastructure of internet cables might not not run to students\' houses. In low-income households, broadband internet might be too expensive to afford. Increasing digital equity has been a goal for many states over the years, and this effort has been galvanized by the pandemic and the need to move education to distance learning.')
states = state_list()
sidebar_selectbox = st.sidebar.selectbox(
    'I am a...',
    ('Parent or Teacher', 'Policymaker or Researcher')
)
if sidebar_selectbox == 'Parent or Teacher':
    racing_int_sources = "Sources: National Assessment of Educational Progress (NAEP) Mathematics Assessment, Census Bureau Household Pulse Survey."

    ### - ACCESS BY STATE - ###
    st.header('What percentage of students have access to internet at home in my state?')
    st.write('From 2009 to 2021, the percentage of students who have access to internet at home has increased for all states. The gap between the bottom and top states has narrowed over time. The range in 2009 was from New Mexico at 79.8% to New Jersey at 96.2% and the range in 2021 was from Missisippi at 93.3% to Hawaii at 100%. The pandemic has galvanized efforts to increase digital equity, with three jurisdictions achieving 100% of students with access to internet and the 2021 National average at 97.9% of students with access to internet.')
    st.write('_Alt Text: This visualization shows the percentage of students in each state who have access to internet at home. Each state is represented as a circle that is "racing" up an internet cable as more students gain access to internet over time._')
    st.write("Choose your state below to see how it compares to the national average and similar states. Color indicates region and your state is highlighted in red.")
    my_state = st.selectbox('', states, index=22)
    [racing_internet, racing_internet_LOC, racing_internet_NSLP] = create_altair_parent(my_state)
    st.image('racinginternet.png')
    st.video('SW.mp4')
    #racing_internet
    st.write(racing_int_sources)
    st.write('Note: Missing state-level data from 2009-2019 is due to reporting standards not met through the NDE. Laptop Icon created by Olga from the Noun Project.')
    my_expander = st.beta_expander(label="Data Analysis Details")
    with my_expander:
        'The 2009-2019 data in the racing internet cable visualization is from NAEP 8th grade Mathematics. Students that participated in NAEP answered a question about if they had access to internet at home. The options they could choose were either a "Yes" or a "No". The 2021 data is from the Census Bureau Household Pulse data, which surveyed adults. If the adult had a child that was in public or private school, they answered a question about the availability of internet for educational purposes in their household. The responses to this question were on a scale of "Always Available", "Usually available", "Sometimes Available", "Rarely Available", or "Never Available." In order to match the NAEP data to the Census Bureau data, I aggregated "Always", "Usually", "Sometimes", and "Rarely" into one "Yes" category and used "Never" as the "No" category. '

    ### - ACCESS BY LOCALE - ###
    st.header('How does access to internet vary by urban and rural areas?')
    st.write('There is a smaller percentage of rural students that have access to internet at home. One reason for this is that in rural areas, the infrastructure of internet cables might not run to students\' houses. In 2009, the gap between suburban students and rural students was 5%, with 93% of suburban students and 88% of rural students with access to internet. Over time, all of the locales (city, suburb, town, and rural) have increased percentages of students that have access to the internet. In 2019, 95% of rural students had access to internet and 98% of suburban students had access to internet.')
    st.write('_Alt Text: This visualization shows the percentage of students who have access to internet at home. Students in four locales (rural, town, suburb, and city) are represented as circles with a slider over time that shows that more students gain access to internet from 2009-2021._')
    racing_internet_LOC
    st.write(racing_int_sources)
    st.write("Note: Data by locale (city, suburb, town, rural) was not available for the 2020 Household Pulse data. The data in this visualization is at the National level.")

    ### - ACCESS BY SES - ###
    st.header('How does access to internet vary between low-income and high-income families?')
    st.write('There is a smaller percentage of low-income students that have access to internet at home. In low-income households, broadband internet might be too expensive to afford. In 2009, the gap between low-income students and high-income students was 14%, with 81% of low-income students and 95% of high-income students with access to internet. Over time, this gap has decreased to 4%, with 95% of low-income students and 99% of high-income students with access to internet.')
    st.write('_Alt Text: This visualization shows the percentage of students in each state who have access to internet at home. Low-income students and high-income students are both represented as circles with a slider over time that shows that more students gain access to internet from 2009-2021._')
    racing_internet_NSLP
    st.write(racing_int_sources)
    st.write("Note: Income levels (low, high) for 2009-2019 data is by NSLP eligibility (eligible, noneligible). Income levels for 2021 data is by resources used to meet spending needs (SNAP, Regular Income sources). The data in this visualization is at the National level.")

    ### - POLICY - ###
    st.header('What is my state doing to increase access to broadband internet?')
    st.write('Listed below are pre-pandemic and pandemic initiatives that your state is taking to increase access to broadband internet. Pre-pandemic data from Pew Charitable Trust includes state agencies, task forces, plans, maps, goals, and funds that are dedicated to increasing access to broadband internet. Pandemic data is a non-exhaustive list of funds that states are allocating for broadband access.')
    st.write("**" + my_state + "'s Policy Initiatives:**")
    policy_text = create_altair_policy(my_state)
    policy_text
    if my_state == "Illinois":
        st.write(" - **Connect Illinois** is a state-wide initiative to expand broadband access.  \n - **The Department of Commerce and Economic Opportunity** funds Rebuild Illinois, and infrastructure program that supports broadband projects.  \n - **Illinois Century Network** supports repairing and expanding broadband network for schools K-12 and higher education.   \n - **The Broadband Advisory Council** developed an action plan to achieve broadband access across the state.  \n - **Illinois K-12 Broadband Initiative** allocated state funding for broadband access for all K-12 public schools.  \n Learn more at https://www2.illinois.gov/dceo/ConnectIllinois/Pages/default.aspx ")
    elif my_state == "Michigan":
        st.write(" - **Connected Nation** is an organization that partner's with states to close the digital divide. https://connectednation.org/  \n - **Connecting Michigan Communities grants** fund projects to expand broadband infrastructure across Michigan. https://www.michigan.gov/dtmb/0,5552,7-358-82547_56345_91154---,00.html  \n - **The Michigan Broadband Roadmap** details a plan, goals, and maps to address access to broadband internet across Michigan. https://connectednation.org/wp-content/uploads/sites/13/2019/01/Final-Roadmap-8-8-18.pdf")
    st.write("Sources: Pew Charitable Trust, National Governor\'s Association.")
elif sidebar_selectbox == 'Policymaker or Researcher':
    [bubblechart_pre, bubblechart_pan, bubble_LOC, bubble_NSLP] = create_altair_policymaker()
    stacked = create_altair_stacked()
    bubble_sources = "Sources: National Assessment of Educational Progress (NAEP) Mathematics Assessment, Census Bureau Household Pulse Survey, Pew Charitable Trust, National Governor\'s Association."

    ### - ACCESS - ###
    st.header('What percentage of students have access to internet at home in my state?')
    st.write('The national average rose from 96% in 2019 to 98% in 2021. The states that improved the most were Kentucky, Arkansas, and Oklahoma, all increasing by 7%. These three states ranked in the bottom four states in 2020, leaving room for improvement. The top jurisdications in 2021 were Hawaii, Montana, and the District of Columbia, all reaching virtually 100% of students with access to internet. Many states have high percentages of students with access to internet, with 13 more states achieving more than 99%. The states that are falling behind the most in 2021 are Mississippi (93%), Maine (94%), Georgia (94%), Pennslyvania (95%), and Rhode Island (95%). All other states have at least 96% access.')
    st.write('This chart below shows the percentage of students that have access to the internet at home in each state. Size represents population. In the pre-pandemic chart, color represents the number of policy initiatives to increase access to broadband internet in action as of 2019. In the pandemic chart, color represents the amount of funding that states have dedicated from the CARES act to increasing access to broadband internet. ')
    #st.image('bubblechart.png', caption='Sketch of bubble chart. The scatterplot below will be edited in Adobe Illustrator to be a bubble chart.')
    time_radio = st.radio("Time periods",
             ["Pre-pandemic (2019)", "Pandemic (2020-2021)"], index=0)
    if time_radio == "Pre-pandemic (2019)":
        #bubblechart_pre
        st.image("PRE-midline.png")
        #st.image("PRE-baseline.png")
    elif time_radio == "Pandemic (2020-2021)":
        #bubblechart_pan
        st.image("POST-midline.png")
        #st.image("POST-baseline.png")
    st.write("Sources: Pre-pandemic data is from the National Assessment of Educational Progress (NAEP) Mathematics Assessment. Pandemic  access to internet data is from the 2021 Census bureau Household Pulse survey. Population data is from the Census Bureau. Pandemic population data is from 2020. Policy data is form Pew Charitable Trust and the National Governor's Association.")
    my_expander = st.beta_expander(label="Data Analysis Details")
    with my_expander:
        'The 2019 data in the packed bubble chart is from NAEP 8th grade Mathematics. Students that participated in NAEP answered a question about if they had access to internet at home. The options they could choose were either a "Yes" or a "No". The 2021 data is from the Census Bureau Household Pulse data, which surveyed adults. If the adult had a child that was in public or private school, they answered a question about the availability of internet for educational purposes in their household. The responses to this question were on a scale from "Always Available", "Usually available", "Sometimes Available", "Rarely Available", or "Never Available." In order to match the NAEP data to the Census Bureau data, I aggregated "Always", "Usually", "Sometimes", and "Rarely" into one "Yes" category and used "Never" as the "No" category. '

    ### - BY GROUPS - ###
    st.header("How does access to internet vary by income levels and urban and rural areas?")
    st.write("There is a smaller percentage of rural students that have access to internet at home. One reason for this is that in rural areas, the infrastructure of internet cables might not run to students\' houses. In 2019, 95% of rural students and 98% of suburban students had access to internet. ")
    bubble_LOC
    st.write("There is also a smaller percentage of low-income students that have access to internet at home. In low-income households, broadband internet might be too expensive to afford. Over time, this gap has decreased to 4%, with NSLP eligible students at 95% and noneligible students at 99%.")
    bubble_NSLP
    st.write(bubble_sources)

    ### - DATA DETAILS - ###
    st.header('How does the Household Pulse survey provide a more detailed look at NAEP data?')
    st.write('The NAEP student questionnaire asks students if they have access to internet at home, with two response options: Yes or No. The Household Pulse survey provides a more detailed look at this measure. This survey asks adults about the availability of internet in their home for their children\'s educational purposes. These parents responded on a scale, from Always available, Usually, Sometimes, Rarely, and Never. This provides more granularity to the measure.')
    st.write("This is important because access to internet is reaching the maximum possible value, 100%. As of 2019, 97% of students have access to the internet. But, when looking at the Household Pulse data, we see that there are varying levels of availability. Only 70% of students always have access to the internet. Grouping together all of the categories that indicate some type of access - Always, Usually, Sometimes and Rarely - we reach 97% access, on par with the NAEP data. Lower levels of availability, such as Sometimes available or Rarely available, could interfere with a students' education. Partial availability could be the result of unafforable or low bandwidth internet. Policy and funding can focus on these issues, such as the FCC's Emergency Broadband Benefit program that provides funds to low-income households to pay for broadband internet services. ")
    #stacked
    st.image("StackedBar.png")
    st.write('Sources: National Assessment of Educational Progress (NAEP) Mathematics Assessment, Census Bureau Household Pulse Survey')

    ### - POLICY DETAILS - ###
    st.header('Explore state policies to increase access to broadband internet')
    st.write('Listed below are pre-pandemic and pandemic initiatives that states are taking to increase digital equity. Pre-pandemic data from Pew Charitable Trust includes state agencies, task forces, plans, maps, goals, and funds that are dedicated to increasing access to broadband internet.')
    st.write('As of 2019, Virginia had the most policy initiatives, coming in at 16. Virginia had seven agencies, one task force, one plan, one goal, and five funds to increase access to the internet. Other top states for policy initiatives were California and Massachusettes, each with 9 initiatives. Several states did not have any policy initiatives before the pandemic: Missisippi, Texas, South Carolina, Ohio, and New Jersey. But, the pandemic galvanized efforts to increase access to internet. Many states allocated funds from the CARES Act to this cause. Missisippi allocated 275 million dollars, Texas allocated 200 million dollars, and South Carolina and Ohio both allocated 50 million dollars.')
    my_state = st.selectbox(
        'Choose a state.', states, index=22)
    policy_text = create_altair_policy(my_state)
    policy_text
    if my_state == "Illinois":
        st.write(" - **Connect Illinois** is a state-wide initiative to expand broadband access.  \n - **The Department of Commerce and Economic Opportunity** funds Rebuild Illinois, and infrastructure program that supports broadband projects.  \n - **Illinois Century Network** supports repairing and expanding broadband network for schools K-12 and higher education.   \n - **The Broadband Advisory Council** developed an action plan to achieve broadband access across the state.  \n - **Illinois K-12 Broadband Initiative** allocated state funding for broadband access for all K-12 public schools.  \n Learn more at https://www2.illinois.gov/dceo/ConnectIllinois/Pages/default.aspx ")
    elif my_state == "Michigan":
        st.write(" - **Connected Nation** is an organization that partner's with states to close the digital divide. https://connectednation.org/  \n - **Connecting Michigan Communities grants** fund projects to expand broadband infrastructure across Michigan. https://www.michigan.gov/dtmb/0,5552,7-358-82547_56345_91154---,00.html  \n - **The Michigan Broadband Roadmap** details a plan, goals, and maps to address access to broadband internet across Michigan. https://connectednation.org/wp-content/uploads/sites/13/2019/01/Final-Roadmap-8-8-18.pdf")
    st.write("Sources: Pew Charitable Trust, National Governor\'s Association.")


