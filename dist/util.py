#!/usr/bin/env python
# coding=utf-8
import argparse
import json
import os
import pandas as pd


def check_dir_and_create_it(p):
    if os.path.exists(p):
        return 1
    else:
        os.makedirs(p)
        return 1


def csv_file_read(csv_path):
    # 读取表头
    head_row = pd.read_csv(csv_path, nrows=0)
    head_row_list = list(head_row)
    # 读取
    csv_result = pd.read_csv(csv_path, usecols=head_row_list)
    row_list = csv_result.values.tolist()
    return row_list


def jsp_csv_file_read(jsp_result_csv_path):
    # 读取表头
    head_row = pd.read_csv(jsp_result_csv_path, nrows=0)
    head_row_list = list(head_row)
    # 读取
    csv_result = pd.read_csv(jsp_result_csv_path, usecols=head_row_list)
    row_list = csv_result.values.tolist()
    return row_list


def php_csv_file_read(php_result_csv_path):
    # 读取表头
    head_row = pd.read_csv(php_result_csv_path, nrows=0)
    head_row_list = list(head_row)
    # 读取
    csv_result = pd.read_csv(php_result_csv_path, usecols=head_row_list)
    row_list = csv_result.values.tolist()
    return row_list


def parse_config():
    argparser = argparse.ArgumentParser(description='config')
    argparser.add_argument(
        '-c',
        '--conf',
        default="config.json",
        # required=True,
        help='配置文件路径')
    argparser.add_argument(
        '-m',
        '--mode',
        default="remote",
        # required=True,
        help='远程运行还是本地运行')

    args = argparser.parse_args()
    config_path = args.conf
    mode = args.mode

    with open(config_path) as config_buffer:
        conf = json.loads(config_buffer.read())

    return conf[mode]


def merge_csv(result_csv_path,php_result_csv_path,jsp_result_csv_path):
    jsp_list = jsp_csv_file_read(jsp_result_csv_path)
    php_list = php_csv_file_read(php_result_csv_path)
    res_list = jsp_list + php_list
    df_jsp = pd.DataFrame(res_list, columns=['file_id', 'prediction'])
    df_jsp.to_csv(result_csv_path, index=False)
