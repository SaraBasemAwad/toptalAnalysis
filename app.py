
import pathlib
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from dash import Dash, Input, Output, dcc, html
import plotly.express as px
import calendar

PATH = pathlib.Path(__file__).parent
# DATA_PATH = PATH.joinpath("data").resolve()

df = pd.read_csv(PATH.joinpath("data.csv"))
df["Date"] = pd.to_datetime(df["created_at"], format="%Y-%m-%d")
df['Quarter'] = df['Date'].dt.quarter
df['Year'] = df['Date'].dt.year
df['Month_Num'] = df['Date'].dt.month

#Show month name for each month number
df['Month'] = ""
month_num_index = df.columns.get_loc("Month_Num")
month_index = df.columns.get_loc("Month")
for i in range(len(df)):
    df.iloc[i, month_index] = calendar.month_name[df.iloc[i, month_num_index]]
    
#Show specialization
df['Specialization'] = ""
slack_channel_index = df.columns.get_loc("slack_channel")
specialization_index = df.columns.get_loc("Specialization")
for i in range(len(df)):
    slack_channel = df.iloc[i, slack_channel_index]
    specialization = ""
    if slack_channel == "#screening-dev-no-show-bot":
        specialization = "Core"
    elif slack_channel == "#screening-dev-qa":
        specialization = "QA"
    elif slack_channel == "#screening-dev-cms":
        specialization = "CMS"
    df.iloc[i, specialization_index] = specialization

specializations = df["Specialization"].sort_values().unique()
teams = df["Team"].sort_values().unique()
screener_names = df["first_leader_name"].sort_values().unique()
years = df["Year"].sort_values().unique()
months = df["Month"].sort_values().unique()
quarter_list = df["Quarter"].sort_values().unique()

teams = np.array(teams)
teams = np.insert(teams, 0, "All", axis=0)


# years = np.array(years)
# years = np.insert(years, 0, "All", axis=0)

def group_by_columns(df, columns):
    result_dictionary = {
        i: len for i in ["id"]
    }
    df_grp = df.groupby(columns, as_index=False).agg(result_dictionary)
    return df_grp

external_stylesheets = [
    {
        "href": (
            "https://fonts.googleapis.com/css2?"
            "family=Lato:wght@400;700&display=swap"
        ),
        "rel": "stylesheet",
    },
]
app = Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Toptal Analytics"
server = app.server

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.H1(
                    children="Toptal Analytics", className="header-title"
                ),
                html.P(
                    children=(
                        "Analyze the behavior of data in years 2022-2023"
                    ),
                    className="header-description",
                ),
            ],
            className="header",
        ),
        html.Div(
            children=[
                                html.Div(
                    children=[
                        html.Div(children="Year", className="menu-title"),
                        dcc.Dropdown(
                            id="year-filter",
                            options=[
                                {"label": year, "value": year}
                                for year in years
                            ],
                            value=years[0],
                            clearable=False,
                            className="dropdown",
                        ),
                    ]
                ),
                             html.Div(
                    children=[
                        html.Div(children="Date Filter:", className="menu-title"),
                        dcc.Dropdown(
                            id="date-filter",
                            options=['Month', 'Quarter'],
                            value="Month",
                            clearable=False,
                            searchable=False,
                            className="dropdown",
                            ),
                        ],
                ),
                
                html.Div(
                    children=[
                        html.Div(children="Date Filter Value:", className="menu-title"),
                        dcc.Dropdown(
                            id="date-value-filter",
                            clearable=False,
                            searchable=False,
                            className="dropdown",
                        ),
                    ],
                ),
            ],
            className="menu",
        ),
        html.Div(
            children=[
                   html.Div(
                                children=[
                                    html.Div(children="Filter By:", className="menu-title"),
                                    dcc.Dropdown(
                                        id="names-filter",
                                        options=['Year', 'Month', 'Team', 'Specialization'],
                                        value="Year",
                                        clearable=False,
                                        searchable=False,
                                        className="dropdown",
                                    ),
                                ],
                            ),
                  html.Div(
                            dcc.Graph(id="pie-chart"),
                       className="card"
                  ),
                                html.Div(
                    children=[
                        html.Div(children="Teams", className="menu-title"),
                        dcc.Dropdown(
                            id="team-filter",
                            options=[
                                {
                                    "label": team,
                                    "value": team,
                                }
                                for team in teams
                            ],
                            value=teams[0],
                            clearable=False,
                            searchable=False,
                            className="dropdown",
                        ),
                    ],
                ),
                 html.Div(
                                children=[
                html.Div(
                    children=dcc.Graph(
                        id="date-team-line-chart",
                        config={"displayModeBar": False},
                    ),
                    className="card",
                )]),
                               
                html.Div(
                    children=[
                        html.Div(children="Screeners:", className="menu-title"),
                        dcc.Dropdown(
                            id="screener-value-filter",
                             options=[
                                {
                                    "label": screener_name,
                                    "value": screener_name,
                                }
                                for screener_name in screener_names
                            ],
                            value=screener_names[0],
                            clearable=False,
                            searchable=False,
                            className="dropdown",
                        ),
                    ],
                ),
                html.Div(
                    children=dcc.Graph(
                        id="screener-line-chart",
                        config={"displayModeBar": False},
                    ),
                    className="card",
                ),
                html.Div(
                    children=dcc.Graph(
                        id="bar-chart",
                        config={"displayModeBar": False},
                    ),
                    className="card",
                ),
            ],
            className="wrapper",
        ),
    ]
)


@app.callback(
    Output("pie-chart", "figure"), 
    Input("names-filter", "value")
)
def generate_chart(names):
    pie_figure = px.pie(df, values='id', names=names, hole=.3)
    return pie_figure


@app.callback(
    Output("date-value-filter", "options"),
    Input("year-filter", "value"),
    Input("date-filter", "value")
)
def update_date_value_options(selected_year, selected_date_filter):
    filtered_df = df[df["Year"] == selected_year]
    if selected_date_filter == "Month":
        months_list = np.array(filtered_df["Month"].sort_values().unique())
        months_list = np.insert(months_list, 0, "All", axis=0)
        options = months_list
    elif selected_date_filter == "Quarter":
        quarter_list = np.array(filtered_df["Quarter"].sort_values().unique())
        options = quarter_list
    return [
        {
            'label': option, 'value': option
        }
        for option in options
    ]

@app.callback(
    Output("date-team-line-chart", "figure"),
    Input("year-filter", "value"),
    Input("date-filter", "value"),
    Input("date-value-filter", "value"),
    Input("team-filter", "value")
)
def update_line_graph(selected_year, selected_date_name, selected_date_value, selected_team):
    filtered_data = df
    if selected_team == "All" and selected_date_value != "All":
        filtered_data = filtered_data[(filtered_data[selected_date_name] == selected_date_value) & (filtered_data["Year"] == selected_year)]
    elif selected_date_value == "All" and selected_team != "All":
        filtered_data = filtered_data[(filtered_data["Year"] == selected_year) & (filtered_data["Team"] == selected_team)]
    elif selected_team == "All" and selected_date_value == "All":
         filtered_data = filtered_data[(filtered_data["Year"] == selected_year)]
    else:
        filtered_data = filtered_data[(filtered_data[selected_date_name] == selected_date_value) & (filtered_data["Team"] == selected_team) & (filtered_data["Year"] == selected_year)]
    line_figure = px.line(filtered_data,
                       x="Date",
                       y="id",
                       color="Team",
                       hover_data = [selected_date_name],
                       title="Count per Date Filter per Team"
                      )
    return line_figure


@app.callback(
    Output("screener-line-chart", "figure"),
    Input("year-filter", "value"),
    Input("date-filter", "value"),
    Input("date-value-filter", "value"),
    Input("screener-value-filter", "value")
)

def update_screener_line_graph(selected_year, selected_date_name, selected_date_value, selected_screener):
    filtered_data = df
    if selected_date_value == "All":
        filtered_data = filtered_data[(filtered_data["Year"] == selected_year) & (filtered_data["first_leader_name"] == selected_screener)]
    else:
        filtered_data = filtered_data[(filtered_data[selected_date_name] == selected_date_value) & (filtered_data["first_leader_name"] == selected_screener) & (filtered_data["Year"] == selected_year)]
    line_figure = px.line(filtered_data,
                       x="Date",
                       y="id",
                       color="first_leader_name",
                       hover_data = [selected_date_name],
                       title="Count per Date Filter per Screener"
                      )
    return line_figure




@app.callback(
    Output("bar-chart", "figure"),
    Input("year-filter", "value")
)
def update_bar_graph(selected_year):
    filtered_data = df[df["Year"] == selected_year]
    filtered_data.rename(columns={'id': 'Count'}, inplace = True)
    filtered_data = filtered_data.sort_values(by='Count', ascending=False)

    bar_figure = px.bar(filtered_data,
                     x="Team",
                     y="Count",
                     color="Team",
                     hover_data=['Count'])

    return bar_figure

if __name__ == '__main__':
    app.run_server(debug=False)
    # application.run(host='0.0.0.0', port='8080')