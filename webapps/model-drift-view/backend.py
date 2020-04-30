import numpy as np
import traceback
import logging
from flask import request
import json
import dataiku
from dku_data_drift import DriftAnalyzer, ModelAccessor
from model_metadata import get_model_handler
logger = logging.getLogger(__name__)

MAX_NUM_ROW = 100000 # heuristic choice


def convert(o):
    if isinstance(o, np.int64): return int(o)  
    raise TypeError

@app.route('/list-datasets')
def list_datasets():
    project_key = dataiku.default_project_key()
    client = dataiku.api_client()
    project = client.get_project(project_key)
    dataset_list = [{"name": dataset_dict['name']} for dataset_dict in project.list_datasets()]
    return json.dumps({'dataset_list': dataset_list})

@app.route('/get-drift-metrics')
def get_drift_metrics():
    try:
        model_id = request.args.get('model_id')
        version_id = request.args.get('version_id')
        test_set = request.args.get('test_set')
        new_test_df = dataiku.Dataset(test_set).get_dataframe(bool_as_str=True, limit=MAX_NUM_ROW)

        model = dataiku.Model(model_id)
        model_handler = get_model_handler(model, version_id=version_id)
        model_accessor = ModelAccessor(model_handler)

        drifter = DriftAnalyzer()
        drifter.fit(new_test_df, model_accessor=model_accessor)
        return json.dumps(drifter.get_drift_metrics_for_webapp(), allow_nan=False, default=convert)
    except:
        logger.error(traceback.format_exc())
        return traceback.format_exc(), 500
