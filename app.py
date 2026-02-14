import pandas as pd
import streamlit as st
import plotly.express as px
import pycountry

# -- Style Configuration --
st.markdown("""
<style>

/* ---- Fonts ---- */
html, body, [class*="css"]  {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* ---- Titles ---- */
h1, h2, h3 {
    font-weight: 600;
    letter-spacing: -0.3px;
}

/* ---- KPI cards ---- */
[data-testid="stMetric"] {
    background-color: #111827;
    border-radius: 12px;
    padding: 16px;
    border: 1px solid #1F2937;
}

/* Number KPI */
[data-testid="stMetricValue"] {
    font-size: 30px;
    font-weight: 700;
    color: #4f00aa;
}

/* label KPI */
[data-testid="stMetricLabel"] {
    color: #9CA3AF;
    font-weight: 500;
}

/* ---- Sidebar ---- */
section[data-testid="stSidebar"] {
    background-color: #0F172A;
    border-right: 1px solid #1F2937;
}

/* ---- Buttons ---- */
.stButton>button {
    border-radius: 10px;
    background-color: #22C55E;
    color: #020617;
    font-weight: 600;
}

/* ---- Dataframe ---- */
[data-testid="stDataFrame"] {
    border-radius: 10px;
    border: 1px solid #1F2937;
}

/* ---- Charts ---- */
.block-container {
    padding-top: 2rem;
}

</style>
""", unsafe_allow_html=True)

purple_scale = [
    "#E9D8FD",  # claro
    "#C4B5FD",
    "#A78BFA",
    "#8B5CF6",
    "#7C3AED",
    "#6D28D9",
    "#5B21B6",
    "#4C1D95",
    "#4f00aa"   # principal
]



def iso2_to_iso3(code):
    try:
        return pycountry.countries.get(alpha_2=code).alpha_3
    except:
        return None
    

# -- Load Data --
df = pd.read_csv("https://raw.githubusercontent.com/guilhermeonrails/data-jobs/refs/heads/main/salaries.csv")


# -- Data Cleaning & Transformation --

df.dropna(inplace=True)

df.rename(columns={
    'work_year':'year',
    'experience_level':'seniority',
    'job_title':'role',
    'salary_currency':'currency',
    'salary_in_usd':'usd',
    'employee_residence':'residence',
    'remote_ratio':'remote'},inplace=True)

df['year'] = df['year'].astype(int)
df['usd'] = df['usd'].astype(float)
df['salary'] = df['salary'].astype(float)

seniority_dict = {
    'SE': 'senior',
    'MI': 'full',
    'EN': 'junior',
    'EX': 'executive'
}
df['seniority'] = df['seniority'].replace(seniority_dict)

emp_type_dict = {
    'FT' : 'full-time',
    'CT' : 'temporary-contract',
    'PT' : 'part-time',
    'FL' : 'freelancer'
}
df['employment_type'] = df['employment_type'].replace(emp_type_dict)

remote_dict = {
    0 : 'in-person',
    100: 'remote',
    50: 'hybrid'
}
df['remote'] = df['remote'].replace(remote_dict)

company_size_dict = {
    'S': 'small',
    'M': 'medium',
    'L': 'large'
}
df['company_size'] = df['company_size'].replace(company_size_dict)

df['country_iso3'] = df['residence'].apply(iso2_to_iso3)


# -- Page Configuration --
# Definition of page title
st.set_page_config(
    page_title='Data Career Salaries Dashboard',
    page_icon='📊',
    layout='wide'
)

# -- Main content --
st.title('Data Career Salary Dashboard')
st.caption(
    'Dataset: Data jobs salaries | Built with Python, Pandas, Streamlit and Plotly'
)
st.markdown(
    'This dashboard explores global salary trends across data roles. '
    'Use the filters to segment the dataset by year, seniority, employment type, and company size.'
)


# -- Sidebar (Filter) ---
st.sidebar.header('🔎 Filters')

# Year Filter
available_years = sorted(df['year'].unique())
selected_years = st.sidebar.multiselect('Year', available_years, default=available_years)

# Seniority Filter
available_seniority = sorted(df['seniority'].unique())
selected_seniority = st.sidebar.multiselect('Seniority',available_seniority,default=available_seniority)

# Contract Type Filter
available_contracts = sorted(df['employment_type'].unique())
select_contracts = st.sidebar.multiselect('Contract Type',available_contracts,default=available_contracts)

# Company Size Filter
available_comp_size = sorted(df['company_size'].unique())
selected_comp_size = st.sidebar.multiselect('Company Size',available_comp_size,default=available_comp_size)


# -- Data Filter --
# Applying user filters to dataframe data
df_filtered = df[
    (df['year'].isin(selected_years)) &
    (df['seniority'].isin(selected_seniority)) &
    (df['employment_type'].isin(select_contracts)) &
    (df['company_size'].isin(selected_comp_size))
]

# -- KPIs --
st.subheader('Key Metrics (Annual Salary in USD)')

if not df_filtered.empty:
    salary_mean = df_filtered['usd'].mean()
    salary_max = df_filtered['usd'].max()
    num_records = df_filtered.shape[0]
    most_freq_role = df_filtered['role'].mode()[0]
else:
    salary_mean,salary_max,num_records,most_freq_role = 0,0,0,0

col1, col2, col3, col4 = st.columns(4)
col1.metric('Average Salary', f"$ {salary_mean:.2f}")
col2.metric('Max Salary', f"$ {salary_max:.2f}")
col3.metric('Number of Records', f"{num_records:.0f}")
col4.metric('Most Frequent Role', most_freq_role)

st.markdown("---")

# -- Plotly Charts --

st.subheader('Charts')


col_fig1, col_fig2 = st.columns(2)

with col_fig1:
    if not df_filtered.empty:
        top_roles = df_filtered.groupby('role')['usd'].mean().nlargest(10).sort_values(ascending=True).reset_index()
        fig_roles = px.bar(
            top_roles,
            x='usd',
            y='role',
            orientation='h',
            title="Top 10 Roles for Average Salary",
            labels={'usd': 'Average Annual Salary (USD)', 'role': 'Position'},
            color='usd',
            color_continuous_scale=purple_scale
        )
        fig_roles.update_layout(title_x=0.1, yaxis={'categoryorder':'total ascending'})
        fig_roles.update_layout(
            paper_bgcolor='#0B1220',
            plot_bgcolor='#0B1220',
            font=dict(color='#E5E7EB')
        )
        st.plotly_chart(fig_roles, width='content')
    else:
        st.warning("No data available for the selected filters.")

with col_fig2:
    if not df_filtered.empty:
        fig_hist = px.histogram(
            df_filtered,
            x='usd',
            nbins=30,
            title='Annual Salary Distribution',
            labels={'usd': 'Salary Range', 'count': ''},
            color_discrete_sequence=["#4f00aa"]
        )

        fig_hist.update_layout(title_x=0.1)
        fig_hist.update_layout(
            paper_bgcolor='#0B1220',
            plot_bgcolor='#0B1220',
            font=dict(color='#E5E7EB')
        )
        st.plotly_chart(fig_hist, width='content')
    else:
        st.warning("No data available for the selected filters.")

col_fig3, col_fig4 = st.columns(2)

with col_fig3:
    if not df_filtered.empty:
        remote_count = df_filtered['remote'].value_counts().reset_index()
        remote_count.columns = ['remote','qtd']
        fig_remote = px.pie(
            remote_count,
            names='remote',
            values='qtd',
            title='Work Arrangement Distribution',
            labels={'remote': 'Work Arrangement', 'qtd': 'Count'},
            hole = 0.5,
            color_discrete_sequence=purple_scale
        )
        fig_remote.update_traces(textinfo='percent+label')
        fig_remote.update_layout(title_x=0.1)
        fig_remote.update_layout(
            paper_bgcolor='#0B1220',
            plot_bgcolor='#0B1220',
            font=dict(color='#E5E7EB')
        )
        st.plotly_chart(fig_remote, width='content')
    else:
        st.warning("No data available for the selected filters.")

with col_fig4:
    if not df_filtered.empty:
        df_ds = df_filtered[df_filtered['role'] == 'Data Scientist']
        average_ds_country = df_ds.groupby('country_iso3')['usd'].mean().reset_index()
        fig_country = px.choropleth(average_ds_country,
                                      locations='country_iso3',
                                      color='usd',
                                      color_continuous_scale=purple_scale,
                                      title='Average Data Scientist Salary by Country',
                                      labels={'usd': 'Average Salary (USD)', 'country_iso3': 'Country'})
        fig_country.update_layout(title_x=0.1)
        fig_country.update_layout(
            paper_bgcolor='#0B1220',
            plot_bgcolor='#0B1220',
            font=dict(color='#E5E7EB')
        )
        st.plotly_chart(fig_country,width='content')
    else:
        st.warning("No data available for the selected filters.")

# --- Detailed Data ---
st.subheader('Raw Data')
st.dataframe(df_filtered)
