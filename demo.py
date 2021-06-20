import dash
from dash.dependencies import Input, Output
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import data
import pandas as pd
import joblib
import prep_data

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.MINTY])

df = data.get_activities()

controls = dbc.Card(
    [
        dbc.FormGroup(
            [
                dbc.Label("Topic"),
                dcc.Dropdown(
                    id="topic-dropdown",
                    options=[
                        {'label': 'Activity', 'value': 'activity'},
                        {'label': 'Budgets', 'value': 'budgets'},
                        {'label': 'Transactions', 'value': 'transactions'},
                        {'label': 'Planned disbursements', 'value': 'planned_disbursements'}
                    ],
                    value='activity'
                ),
            ]
        ),
        dbc.Button("Impute", id='impute-btn', color="primary", className="mr-1", style={"margin-bottom": "15px"}),
        dbc.Button("Detect Outliers", id='outlier-btn', color="primary", className="mr-1", style={"margin-bottom": "15px"}),
        dbc.Button("Download CSV file", id='export-btn', color="primary", className="mr-1")
    ],
    body=True,
)

app.layout = html.Div([
    dbc.NavbarSimple(brand='IATI Data Enrichment', color='primary', dark=True, style={"margin-bottom": "15px"}),
    dbc.Container(children=[
        dbc.Row(children=[
            dbc.Col(id='table-col', children=[
                dash_table.DataTable(
                    id='topic-table',
                    columns=[
                        {"name": i, "id": i, "selectable": True} for i in df.columns
                    ],
                    data=df.to_dict('records'),
                    editable=True,
                    filter_action="native",
                    sort_action="native",
                    sort_mode="multi",
                    column_selectable="single",
                    row_selectable="multi",
                    selected_columns=[],
                    selected_rows=[],
                    page_action="native",
                    page_current=0,
                    page_size=10,
                    style_table={'overflowX': 'auto'}
                )
            ], width=9),
            dbc.Col(children=[
                controls
            ], width=3)
        ])

    ])])


@app.callback(
    [dash.dependencies.Output('table-col', 'children')],
    [dash.dependencies.Input('topic-dropdown', 'value'),
     dash.dependencies.Input('topic-table', 'data'),
     dash.dependencies.Input('topic-table', 'columns'),
     dash.dependencies.Input('impute-btn', 'n_clicks')])
def impute_data(topic, table_data, columns, n_clicks):
    if n_clicks is not None:
        print(n_clicks)
        df_missing = pd.DataFrame(table_data, columns=[c['name'] for c in columns])
        df_missing = prep_data.clean_data(df_missing,
                                          date_cols=["activity_date_start_planned", "activity_date_end_planned",
                                                     "activity_date_start_actual", "activity_date_end_actual"],
                                          cat_vars=["activity_status_code", "activity_scope_code",
                                                    "collaboration_type_code",
                                                    "default_flow_type_code", "default_finance_type_code",
                                                    "default_tied_status_code", "humanitarian"]
                                          )
        model = joblib.load('missforest_activity.joblib')
        imputed = model.transform(df_missing)
        df_imputed = pd.DataFrame(imputed, columns=[c['name'] for c in columns])
        print(df_imputed.head())
    else:
        return dash.no_update


def detect_outliers():
    print('')

@app.callback(
    [dash.dependencies.Output('table-col', 'children')],
    [dash.dependencies.Input('topic-dropdown', 'value'),
     dash.dependencies.Input('topic-table', 'data'),
     dash.dependencies.Input('topic-table', 'columns'),
     dash.dependencies.Input('impute-btn', 'n_clicks')])
def download_csv():
    print('')


@app.callback(
    [dash.dependencies.Output('topic-table', 'data'),
     dash.dependencies.Output('topic-table', 'columns')],
    [dash.dependencies.Input('topic-dropdown', 'value')])
def update_datatable(topic):
    topic_df = data.get_topic_data(topic)
    columns = [
        {"name": i, "id": i, "selectable": True} for i in topic_df.columns
    ]
    return topic_df.to_dict('records'), columns


if __name__ == '__main__':
    app.run_server(debug=True)
