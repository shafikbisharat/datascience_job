import pandas as pd
import plotly.express as px
from datetime import datetime
import re

# Load data
df = pd.read_csv('Data_Science_Jobs_Israel.csv')
df['run_time'] = pd.to_datetime(df['run_time'], errors='coerce', format='mixed')
df['run_id'] = df['run_time'].dt.strftime("%Y-%m-%d %H:%M")
last_updated_time = df['run_id'].max()

html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Data Science Jobs in Israel</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{ background-color: #f8f9fa; }}
        .card {{ border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 25px; }}
        .header {{ background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%); color: white; padding: 30px 0; margin-bottom: 30px; }}
        .stat-card {{ text-align: center; padding: 20px; }}
        .stat-value {{ font-size: 2.5rem; font-weight: bold; }}
        .section-title {{ border-left: 5px solid #2575fc; padding-left: 15px; margin: 30px 0 20px; color: #2c3e50; }}
    </style>
</head>
<body>
    <div class="header">
        <div class="container">
            <h1 class="display-4">Data Science Job Market in Israel</h1>
            <div class="row mt-4">
                <div class="col-md-6">
                    <p class="lead">Total jobs collected: <strong>{len(df)}</strong></p>
                </div>
                <div class="col-md-6 text-md-end">
                    <p class="lead">Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
                </div>
            </div>
            <p>Data updated every 12 hours from LinkedIn and Google Careers</p>
        </div>
    </div>

    <div class="container">
        <!-- Time Series Section -->
        <div class="row">
            <div class="col">
                <div class="card">
                    <div class="card-body">
                        <h2 class="section-title">Job Postings Per Scraping Run</h2>
                        <div id="time-series-chart"></div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Breakdown Section -->
        <div class="row">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-body">
                        <h2 class="section-title">Top Companies Hiring</h2>
                        <div id="companies-chart"></div>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-body">
                        <h2 class="section-title">Job Sources</h2>
                        <div id="sources-chart"></div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Keywords Section -->
        <div class="row">
            <div class="col">
                <div class="card">
                    <div class="card-body">
                        <h2 class="section-title">Job Title Keywords</h2>
                        <div id="keywords-chart"></div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Recent Jobs Section -->
        <div class="row">
            <div class="col">
                <div class="card">
                    <div class="card-body">
                        <h2 class="section-title">Latest Data Science Job Postings</h2>
                        <div class="accordion" id="jobs-accordion">
"""

# Generate recent jobs accordion
latest_jobs = df.sort_values('run_time', ascending=False).head(10)
for i, row in latest_jobs.iterrows():
    html_content += f"""
    <div class="accordion-item">
        <h2 class="accordion-header" id="heading{i}">
            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapse{i}" aria-expanded="false" aria-controls="collapse{i}">
                {row['title']} - {row['company']}
            </button>
        </h2>
        <div id="collapse{i}" class="accordion-collapse collapse" aria-labelledby="heading{i}" data-bs-parent="#jobs-accordion">
            <div class="accordion-body">
                <p><strong>Location:</strong> {row['location']}</p>
                <p><strong>Source:</strong> {row['source']}</p>
                <p><strong>Posted:</strong> {row.get('posted_at', 'N/A')}</p>
                <p><strong>Scraped:</strong> {row['run_time'].strftime('%Y-%m-%d %H:%M')}</p>
                <a href="{row['link']}" class="btn btn-primary" target="_blank">Apply Here</a>
            </div>
        </div>
    </div>
    """

html_content += """
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Data Table Section -->
        <div class="row">
            <div class="col">
                <div class="card">
                    <div class="card-body">
                        <h2 class="section-title">All Job Listings</h2>
                        <div style="overflow-x: auto;">
                            <table class="table table-striped">
                                <thead>
                                    <tr>
                                        <th>Title</th>
                                        <th>Company</th>
                                        <th>Location</th>
                                        <th>Source</th>
                                        <th>Scraped At</th>
                                        <th>Link</th>
                                    </tr>
                                </thead>
                                <tbody>
"""

# Generate table rows
sorted_df = df[['title', 'company', 'location', 'source', 'run_time', 'link']].sort_values('run_time', ascending=False)
for i, row in sorted_df.iterrows():
    html_content += f"""
    <tr>
        <td>{row['title']}</td>
        <td>{row['company']}</td>
        <td>{row['location']}</td>
        <td>{row['source']}</td>
        <td>{row['run_time'].strftime('%Y-%m-%d %H:%M')}</td>
        <td><a href="{row['link']}" target="_blank">Apply</a></td>
    </tr>
    """

html_content += """
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <footer class="text-center mt-5 mb-3 text-muted">
            <p>Data Science Job Tracker | Last updated: {last_updated_time}</p>
        </footer>
    </div>

    <!-- Bootstrap & Plotly Scripts -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Time Series Chart
        Plotly.newPlot('time-series-chart', """

run_counts = df.groupby('run_id').size().reset_index(name='count')
run_counts['run_time'] = pd.to_datetime(run_counts['run_id'])
run_counts = run_counts.sort_values('run_time')

fig_time = px.scatter(
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

fig_time.update_traces(
    marker=dict(size=12, line=dict(width=2, color='DarkSlateGrey')),
    textfont=dict(size=10)
)

fig_time.update_layout(
    hovermode='x unified',
    xaxis=dict(tickformat='%Y-%m-%d %H:%M'),
    height=500
)
html_content += fig_time.to_json() + """, {});

        // Companies Chart
        Plotly.newPlot('companies-chart', """
# Top companies plot
top_companies = df['company'].value_counts().head(10)
fig_companies = px.bar(
    top_companies, 
    orientation='h',
    labels={'index': 'Company', 'value': 'Job Count'},
    title='Top Companies'
)
fig_companies.update_layout(showlegend=False, height=400)
html_content += fig_companies.to_json() + """, {});

        // Sources Chart
        Plotly.newPlot('sources-chart', """
# Sources plot
source_counts = df['source'].value_counts()
fig_sources = px.pie(
    source_counts,
    names=source_counts.index,
    values=source_counts.values,
    title='Job Sources Distribution',
    height=400
)
html_content += fig_sources.to_json() + """, {});

        // Keywords Chart
        Plotly.newPlot('keywords-chart', """
# Keywords plot
all_titles = ' '.join(df['title'].astype(str)).lower()
words = re.findall(r'\b[a-z]{4,}\b', all_titles)
word_counts = pd.Series(words).value_counts().head(20)
stop_words = ['senior', 'lead', 'israel', 'tel', 'aviv', 'and', 'for', 'with', 'team', 'developer']
word_counts = word_counts[~word_counts.index.isin(stop_words)]

fig_keywords = px.bar(
    word_counts, 
    orientation='h',
    title='Most Common Keywords in Job Titles',
    labels={'index': 'Keyword', 'value': 'Count'},
    height=500
)
fig_keywords.update_layout(showlegend=False)
html_content += fig_keywords.to_json() + """, {});
    </script>
</body>
</html>
"""

# Save HTML file
with open('jobs_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("Dashboard generated: jobs_dashboard.html")