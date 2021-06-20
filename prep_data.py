import pandas as pd
import datetime as dt
import numpy as np
from tqdm import tqdm


def clean_data(df, date_cols, cat_vars):
    missing = -999999
    for col in date_cols:
        df[col] = pd.to_datetime(df[col])
        df[col] = df[col].apply(dt.datetime.toordinal)
        df[col] = df[col].replace(1, np.nan)

    df.fillna(missing, inplace=True)
    df[cat_vars] = df[cat_vars].astype('int64')

    return df


def revert_cleaned_data(df, date_cols, cat_vars):
    missing = -999999
    df = df.replace(missing, np.nan)
    for col in date_cols:
        df[col] = pd.to_datetime(df[col])
        df[col] = df[col].apply(dt.datetime.fromordinal)
    return df


def get_columns_to_explode(df):
    # columns with multiple values
    to_explode = []
    for col in tqdm(df.columns):
        if df[col].dtype == 'object':
            if df[col].str.contains('(?<!\\\\),', regex=True).any():
                to_explode.append(col)
    return to_explode


def split_values(df, to_explode, lenghts_df):
    for col in tqdm(to_explode):
        # split by comma but not when comma is after a \
        df[col] = df[col].str.split('(?<!\\\\),')
        lenghts_df[col] = df[col].str.len()
        df[col] = df[col].fillna("").apply(list)


def padding(l, n):
    return l + [''] * (n - len(l))


def explode(df, fill_value=''):
    lenghts_df = pd.DataFrame()
    to_explode = get_columns_to_explode(df)
    split_values(df, to_explode, lenghts_df)
    lens = lenghts_df.max(axis=1).fillna(0).astype('int64')

    for col in tqdm(to_explode):
        df[col] = [padding(x, lens.loc[i]) for i, x in enumerate(df[col])]

    # all columns except `lst_cols`
    idx_cols = df.columns.difference(to_explode)
    idx = np.repeat(df.index.values, lens)
    if (lens > 0).all():
        # ALL lists in cells aren't empty
        return pd.DataFrame({
            col: np.repeat(df[col].values, lens)
            for col in idx_cols
        }, index=idx).assign(**{col: np.concatenate(df[col].values) for col in to_explode}) \
            .loc[:, df.columns]
    else:
        # at least one list in cells is empty
        return pd.DataFrame({
            col: np.repeat(df[col].values, lens)
            for col in tqdm(idx_cols)
        }).assign(**{col: np.concatenate(df[col].values) for col in tqdm(to_explode)}) \
          .append(df.loc[lens == 0, idx_cols]).fillna(fill_value) \
          .loc[:, df.columns]


