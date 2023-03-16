import json
from flask import render_template
import pandas as pd

from typing import List


# It is assumed that the Task class has a <table_name>_id column used for merging data
def dbmodel_to_dataframe(db, dbmodel, ids: List[int] = None, columns: List[str] = None):
    if ids:
        # FIXME: Change to avoid loading all the columns!
        df = pd.read_sql(
            dbmodel.query.filter(dbmodel.id.in_(ids)).statement, 
            db.engine, 
            index_col = 'id'
        )
        if columns:
            return df[columns]
        return df
    else:
        return pd.read_sql(str(dbmodel.__table__), db.engine, index_col = 'id', columns = columns)
    


def json2str(obj):
    if type(obj) != str:
        return json.dumps(obj)
    else:
        return obj
    
def add_if_new(db, dbmodel, params: dict):
    dbmodel_obj = dbmodel.query.filter_by(**params).first()
    if not dbmodel_obj:
        dbmodel_obj = dbmodel(**params)
        db.session.add(dbmodel_obj)
        db.session.commit()
    return dbmodel_obj


def render_table(dbmodel):
    model_df = dbmodel.to_dataframe()
    html_table = model_df.to_html(index=True)
    return render_template('index.html', content=html_table)