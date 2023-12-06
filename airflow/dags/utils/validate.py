import os
import great_expectations as gx
import pandas as pd
from datetime import datetime
from great_expectations.checkpoint import Checkpoint
from great_expectations.data_context.types.base import DataContextConfig
import logging

def validate(df: pd.DataFrame):
    context = gx.get_context()
    now = datetime.now()

    datasource = context.sources.add_pandas("house_datasource")
    data_asset = datasource.add_dataframe_asset(name="house_asset")
    batch_request = data_asset.build_batch_request(dataframe=df)

    context.add_or_update_expectation_suite(expectation_suite_name='expectation_house')
    validator = context.get_validator(
        batch_request=data_asset.build_batch_request(dataframe=df),
        expectation_suite_name='expectation_house',
    )
    
    validator.expect_column_values_to_not_be_null('TotRmsAbvGrd')
    validator.expect_column_values_to_be_between('TotRmsAbvGrd', min_value=1, max_value=30)
    validator.expect_column_values_to_not_be_null('WoodDeckSF')
    validator.expect_column_values_to_not_be_null('YrSold')
    validator.expect_column_values_to_not_be_null('1stFlrSF')
    validator.expect_column_values_to_not_be_null('Foundation')
    validator.expect_column_values_to_be_in_set(column='Foundation', value_set = [
        'BrkTil',
        'CBlock',
        'PConc',
        'Slab',
        'Stone',
        'Wood',
    ])
    validator.expect_column_values_to_not_be_null('KitchenQual')
    validator.expect_column_values_to_be_in_set(column='KitchenQual', value_set = [
        'Ex',
        'Gd',
        'TA',
        'Fa',
        'Po',
    ])
    validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = Checkpoint(
        name="house_checkpoint",
        run_name_template="housing_checkpoint",
        data_context=context,
        batch_request=batch_request,
        expectation_suite_name='expectation_house',
        action_list=[
            {
                "name": "store_validation_result",
                "action": {"class_name": "StoreValidationResultAction"},
            },
                {"name": "update_data_docs", "action": {"class_name": "UpdateDataDocsAction"}},
            ],
        )

    context.add_or_update_checkpoint(checkpoint=checkpoint)
    result_format: dict = {
        "result_format": "COMPLETE",
        "unexpected_index_column_names": ["Id"],
    }
    return checkpoint.run(result_format=result_format)


def filter_expectations_result(result_json):
    logging.info(result_json)
    run_results = result_json['run_results']
    val_result_id = list(run_results)[0]
    val_results = run_results[val_result_id]['validation_result']

    info = '' 
    failed_rows = []
    failed_cols = []
    failed_conf = []

    for res in val_results['results']:
        if res['success'] == False:
            _col = res['expectation_config']['kwargs']['column'] 
            _exp_conf = res['expectation_config']['expectation_type']
            info += f'column -> {_col}\n'
            info += f'    expectation_config -> {_exp_conf}\n'
            indexes_list = res['result']['partial_unexpected_index_list']
            failed_rows_id = [item['Id'] for item in indexes_list]
            failed_rows = list(set(failed_rows + failed_rows_id))
            failed_conf = list(set(failed_conf + [_exp_conf]))
            failed_cols = list(set(failed_cols + [_col]))
            info += f'    rows with errors -> {failed_rows_id}\n'

    desc = f'Validation Error on Rows {failed_rows} of file _FILENAME_ !'
    desc += f'Columns {failed_cols} failed on the following expectations : {failed_conf}'
 
    logging.info(info)
    return failed_rows, desc


def move_dirs(src_folder_name,dst_folder_name, file_name):
    if not os.path.exists(dst_folder_name):
        os.makedirs(dst_folder_name)
    logging.info(f'Saving file {file_name} in folder {dst_folder_name}')
    src_path = os.path.join(src_folder_name, file_name)
    dst_path = os.path.join(dst_folder_name, file_name)
    os.rename(src_path,dst_path)


def save_df_to_folder(df,folder_name,file_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_nae)

    path = os.path.join(folder_name, file_name)

    logging.info(f'Saving file {file_name} in folder {folder_name}')
    df.to_csv(path, index=False, header=False)
