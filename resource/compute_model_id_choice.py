"""
Allow dynamic select of the model id in the model recipe.
"""
import dataiku
from dku_tools import process_timestamp


def do(payload, config, plugin_config, inputs):
    """
    DSS built-in interface for param loading in the form.
    Retrieve the available versions of a pretrained model in DSS.
    :param payload:
    :param config:
    :param plugin_config:
    :param inputs:
    :return:
    """
    model = None
    for input_ in inputs:
        if input_['role'] == 'model':
            model = str(input_['fullName'])
    if model is None:
        raise Exception("Did not catch the right input model")


    model_id = model.split('.')[-1]
    model = dataiku.Model(model_id)

    if model.get_info().get('type') != 'PREDICTION':
        raise ValueError('Model type {} is not supported. Please choose a regression or classifcation model.'.format(model.get_info().get('type')))


    choice_list = []
    for version in model.list_versions():
        version_detail = version.get('snippet', {})
        algorithm = version_detail.get('algorithm', '').lower().replace('_', ' ')
        active_version = version.get('active') is True
        train_date = process_timestamp(version_detail.get('trainDate'))
        version_id = version.get('versionId')

        if active_version:
            version_info = {
                'value': version_id,
                'label': 'active version, trained on {1}, {0}'.format(algorithm, train_date)
            }
        else:
            version_info = {
                'value': version_id,
                'label': 'trained on {1}, {0}'.format(algorithm, train_date)
            }
        choice_list.append((version_info, train_date))

    sorted_choice_list = sorted(choice_list, key=lambda k: k[1])
    final_choice_list = [choice[0] for choice in sorted_choice_list]

    return {"choices": final_choice_list}