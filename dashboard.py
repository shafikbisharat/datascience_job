import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import streamlit as st
import re

# MUST BE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="Data Science Jobs in Israel",
    layout="wide",
    page_icon="📊"
)

# Load data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('Data_Science_Jobs_Israel.csv')
        
        # Convert run_time to datetime
        df['run_time'] = pd.to_datetime(df['run_time'], errors='coerce', format='mixed')
        
        # Create run identifier
        df['run_id'] = df['run_time'].dt.strftime('%Y-%m-%d %H:00')
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

df = load_data()

# Dashboard content
st.title('Data Science Job Market in Israel')
st.markdown(f"**Total data science jobs collected:** {len(df)}")
st.markdown("Data updated every 12 hours from LinkedIn and Google Careers")

# Time series chart
st.subheader('Job Postings Per Scraping Run')
if not df.empty:
    # Group by scraping run
    run_counts = df.groupby('run_id').size().reset_index(name='count')
    run_counts['run_time'] = pd.to_datetime(run_counts['run_id'])
    run_counts = run_counts.sort_values('run_time')
    
    # Create plot
    fig = px.scatter(
        run_counts,
        x='run_time',
        y='count',
        title='Data Science Jobs Per Scraping Run',
        labels={'run_time': 'Scraping Time', 'count': 'Jobs Found'},
        size='count',
        color='count',
        trendline='lowess',
        hover_data={'run_time': '|%Y-%m-%d %H:%M'}
    )
    
    # Add labels
    fig.update_traces(
        marker=dict(size=12, line=dict(width=2, color='DarkSlateGrey')),
        textfont=dict(size=10)
    )
    
    # Improve layout
    fig.update_layout(
        hovermode='x unified',
        xaxis=dict(tickformat='%Y-%m-%d %H:%M'),
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No data available for time series")

# Breakdown analysis
st.subheader('Data Science Job Market Breakdown')
col1, col2 = st.columns(2)

with col1:
    st.markdown("**Top Companies Hiring**")
    if not df.empty:
        top_companies = df['company'].value_counts().head(10)
        fig = px.bar(
            top_companies, 
            orientation='h',
            labels={'index': 'Company', 'value': 'Job Count'},
            title='Top Companies'
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No company data")

with col2:
    st.markdown("**Job Sources**")
    if not df.empty:
        source_counts = df['source'].value_counts()
        fig = px.pie(
            source_counts,
            names=source_counts.index,
            values=source_counts.values,
            title='Job Sources Distribution'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No source data")

# Job title analysis
st.subheader('Job Title Keywords')
if not df.empty:
    # Extract keywords from titles
    all_titles = ' '.join(df['title'].astype(str)).lower()
    
    # Clean and tokenize
    words = re.findall(r'\b[a-z]{4,}\b', all_titles)
    word_counts = pd.Series(words).value_counts().head(20)
    
    # Filter out common non-relevant words
    stop_words = ['senior', 'lead', 'israel', 'tel', 'aviv', 'and', 'for', 'with', 'team', 'developer']
    word_counts = word_counts[~word_counts.index.isin(stop_words)]
    
    fig = px.bar(
        word_counts, 
        orientation='h',
        title='Most Common Keywords in Job Titles',
        labels={'index': 'Keyword', 'value': 'Count'}
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No data for keyword analysis")

# Recent jobs
st.subheader('Latest Data Science Job Postings')
if not df.empty:
    latest_jobs = df.sort_values('run_time', ascending=False).head(10)
    for i, row in latest_jobs.iterrows():
        with st.expander(f"{row['title']} - {row['company']}"):
            st.markdown(f"**Location:** {row['location']}")
            st.markdown(f"**Source:** {row['source']}")
            st.markdown(f"**Posted:** {row.get('posted_at', 'N/A')}")
            st.markdown(f"**Scraped:** {row['run_time'].strftime('%Y-%m-%d %H:%M')}")
            st.markdown(f"[Apply Here]({row['link']})")
else:
    st.info("No recent jobs")

# Full data table
st.subheader('All Data Science Job Listings')
if not df.empty:
    st.dataframe(
        df[['title', 'company', 'location', 'source', 'run_time', 'link']].sort_values('run_time', ascending=False),
        column_config={
            "link": st.column_config.LinkColumn("Job Link"),
            "run_time": st.column_config.DatetimeColumn("Scraped At")
        },
        hide_index=True,
        height=500,
        use_container_width=True
    )
else:
    st.info("No job data available")

# Footer
st.markdown("---")
st.caption(f"Data Science Job Tracker | Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")