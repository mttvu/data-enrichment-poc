import requests
import pandas as pd


def get_topic_data(topic):
    if topic == 'activity':
        return get_activities()
    elif topic == 'budgets':
        return get_budgets()
    elif topic == 'transactions':
        return get_transactions()
    elif topic == 'planned_disbursements':
        return get_planned_disbursements()


def get_activities():
    # columns = [
    #     'activity_status_code', 'activity_scope_code',
    #     'activity_date_start_planned', 'activity_date_end_planned',
    #     'activity_date_start_actual', 'activity_date_end_actual',
    #     'collaboration_type_code', 'default_flow_type_code', 'default_finance_type_code',
    #     'default_tied_status_code', 'humanitarian']
    #
    # columns = ','.join(columns)
    # url = f'https://iatidatastore.iatistandard.org/search/activity?q=*:*&fl={columns}&wt=csv&rows=10000'
    # return pd.read_csv(url)
    return pd.read_csv('activities.csv')


def get_budgets():
    columns = ['budget_period_end_iso_date', 'budget_status', 'budget_period_start_iso_date', 'budget_value_usd']
    columns = ','.join(columns)
    url = f'https://iatidatastore.iatistandard.org/search/activity?q=*:*&fl={columns}&wt=csv&rows=50'
    return pd.read_csv(url)


def get_transactions():
    return ''


def get_planned_disbursements():
    return ''

