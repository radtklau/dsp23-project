import os
import great_expectations as gx
import logging
from shutil import copyfile

def create_validator(path, context):
    validator = context.sources.pandas_default.read_csv(path)

    validator.expect_column_values_to_not_be_null('TotRmsAbvGrd')
    validator.expect_column_values_to_be_between('TotRmsAbvGrd', min_value=1, max_value=30)
    validator.expect_column_values_to_not_be_null('WoodDeckSF')
    validator.expect_column_values_to_not_be_null('YrSold')
    validator.expect_column_values_to_not_be_null('1stFlrSF')
    validator.expect_column_values_to_not_be_null('Foundation_BrkTil')
    validator.expect_column_values_to_not_be_null('Foundation_CBlock')
    validator.expect_column_values_to_not_be_null('Foundation_PConc')
    validator.expect_column_values_to_not_be_null('Foundation_Slab')
    validator.expect_column_values_to_not_be_null('Foundation_Stone')
    validator.expect_column_values_to_not_be_null('Foundation_Wood')
    validator.expect_column_values_to_not_be_null('KitchenQual_Ex')
    validator.expect_column_values_to_not_be_null('KitchenQual_Fa')
    validator.expect_column_values_to_not_be_null('KitchenQual_Gd')
    validator.expect_column_values_to_not_be_null('KitchenQual_TA')
    validator.save_expectation_suite(discard_failed_expectations=False)
    return validator


def validate(path):
    context = gx.get_context()

    validator = create_validator(path, context)

    checkpoint = context.add_or_update_checkpoint(name='housing_checkpoint',
                                                  validator=validator)
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

    # info = ''
    failed_rows = []
    failed_cols = []
    failed_conf = []

    for res in val_results['results']:
        if res['success'] == False:
            _col = res['expectation_config']['kwargs']['column']
            _exp_conf = res['expectation_config']['expectation_type']
            # info += f'column -> {_col}\n'
            # info += f'    expectation_config -> {_exp_conf}\n'
            indexes_list = res['result']['partial_unexpected_index_list']
            failed_rows_id = [item['Id'] for item in indexes_list]
            failed_rows = list(set(failed_rows + failed_rows_id))
            failed_conf = list(set(failed_conf + [_exp_conf]))
            failed_cols = list(set(failed_cols + [_col]))
            # info += f'    rows with errors -> {failed_rows_id}\n'

    desc = f'Validation Error on Rows {failed_rows} of file _FILENAME_ !'
    desc += f'Columns {failed_cols} failed on the following expectations : {failed_conf}'
    desc = desc.replace('[', '')
    desc = desc.replace(']', '')
    # logging.info(info)
    return failed_rows, desc


def move_dirs(src_folder_name, dst_folder_name, file_name):
    if not os.path.exists(dst_folder_name):
        os.makedirs(dst_folder_name)
    logging.info(f'Saving file {file_name} in folder {dst_folder_name}')
    src_path = os.path.join(src_folder_name, file_name)
    dst_path = os.path.join(dst_folder_name, file_name)
    os.rename(src_path, dst_path)

def copy_dirs(src_folder_name, dst_folder_name, file_name):
    if not os.path.exists(dst_folder_name):
        os.makedirs(dst_folder_name)
    logging.info(f'Copying file {file_name} to folder {dst_folder_name}')
    src_path = os.path.join(src_folder_name, file_name)
    dst_path = os.path.join(dst_folder_name, file_name)
    copyfile(src_path, dst_path)

def save_df_to_folder(df, folder_name, file_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    path = os.path.join(folder_name, file_name)

    logging.info(f'Saving file {file_name} in folder {folder_name}')
    df.to_csv(path, index=False, header=False)

