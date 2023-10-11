#!/usr/bin/env python
# coding=utf-8
import jsp, php, util

if __name__ == "__main__":
    conf = util.parse_config()
    # 测试数据路径
    test_csv_path = conf["test_csv_path"]
    test_data_path = conf["test_data_path"]
    # php生成的特征文件路径
    php_feature_path = conf["php_feature_path"]
    # 模型预测输出文件路径
    php_result_csv_path = conf["result_csv_path"]["php"]
    jsp_result_csv_path = conf["result_csv_path"]["jsp"]
    result_csv_path = conf["result_csv_path"]["result"]
    # 模型路径
    php_model_path = conf["model_path"]["php"]
    jsp_model_path = conf["model_path"]["jsp"]
    # 日志路径
    php_log_path = conf["log_path"]["php"]
    jsp_log_path = conf["log_path"]["jsp"]

    php.start(test_data_path, test_csv_path, php_feature_path, php_result_csv_path, php_model_path, php_log_path)
    jsp.start(test_data_path, test_csv_path,jsp_result_csv_path, jsp_model_path, jsp_log_path)
    util.merge_csv(result_csv_path, php_result_csv_path, jsp_result_csv_path)
