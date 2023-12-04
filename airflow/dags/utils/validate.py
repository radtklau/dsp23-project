import great_expectations as gx
import pandas as pd
from datetime import datetime
from great_expectations.checkpoint import Checkpoint
from great_expectations.data_context.types.base import DataContextConfig
import logging

def validate(df):
    context = gx.get_context()
    now = datetime.now()

    datasource  = context.sources.add_pandas("house_datasource")
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


def log_failed_expectations(result_json) -> str:
    logging.info('LOGGING FAILED EXPECTATIONS !!!') 
    logging.info(result_json)
    run_results = result_json['run_results']
    val_result_id = list(run_results)[0]
    val_results = run_results[val_result_id]['validation_result']

    info = "" 
    for res in val_results['results']:
        if res['success'] == False:
            info += f"column -> {res['expectation_config']['kwargs']['column'] }\n"
            info += f"    expectation_config -> {res['expectation_config']['expectation_type']}\n"
            indexes_list = res['result']['partial_unexpected_index_list']
            failed_rows_id = [item['Id'] for item in indexes_list]
            info += f"    rows with errors -> {failed_rows_id}\n"

    logging.info(info)
    return info 
