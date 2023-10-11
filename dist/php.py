#!/usr/bin/env python
# coding=utf-8
import logging
import os.path
import re
import numpy as np
import pandas as pd
import joblib

import util

logger = None
f_input = None
features_len = 0


def read_file(filename):
    text = b""
    with open(filename, "rb") as f:
        for line in f:
            line = line.strip(b"\r\t")
            text += line
        result = re.compile('\"name\":.*?\]', re.S)  # 正则匹配
        theresult = re.findall(result, str(text))
        text = ''.join(theresult)
        text = text.replace('[', ' ')
        text = text.replace(']', ' ')
        text = text.replace('\\', ' ')
        text = text.replace(',', ' ')
        text = text.replace('"', ' ')
        text = text.replace('name :', ' ')
        text = re.sub('<(.*?)>', '', text)
        text = re.sub('FROM `(.*?)`', '', text)
        text = re.sub('INSERT INTO `(.*?)\)', '', text)
        text = re.sub('UPDATE `(.*?)WHERE', '', text)
        text = re.sub('REPLACE INTO `(.*?)\)', '', text)
        text = re.sub('`(.*?)`=', '', text)
        text = re.sub('SELECT `(.*?)`', '', text)
        # INSERT INTO `
        text = text.replace(':', ' ')
        text = text.replace('STMT_LIST', ' ')
        text = text.replace('ZVAL', ' ')
        text = text.replace('NULL', ' ')
        # text = text.encode("utf-8")
        text = ' '.join(text.split()).encode("utf-8")
    return text


def get_features(data, fileid):
    key_num = 0  # 黑名单数量
    capital_len = 0
    namespace_c = 0  # namespace数量
    op_c = 0  # BINARY_OP 数量
    class_c = 0  # CLASS数,结合namespace数量，区分度高
    passw_c = 0  # passw数量,区分度一般
    include_c = 0  # include数量,区分度一般
    FUNC_DECL_c = 0  # FUNC_DECL_c数量,较高
    unquote_c = 0  # 反引号`的数量
    eval_c = 0  # eval的数量
    shell_c = 0  # shell 字符串的数量
    hack_c = 0  # hack字符串的数量
    backdoor_c = 0  # backdoor字符串数量
    arg_c = 0
    post_c = 0  # _POST字符串的数量
    file_c = 0  # _FILE字符串数量
    get_c = 0  # _GET字符串数量
    b64dec_c = 0  # base64decode字符串数量
    flate_c = 0  # flate字符串数量，区分频率低，但存在即是shell
    iua_c = 0  # ignore_user_abort字符串数量，区分频率低，但存在即是shell
    stl_c = 0  # set_time_limit字符串数量，区分频率低，
    smqr_c = 0  # set_magic_quotes_runtime 高
    muf_c = 0  # move_uploaded_file 高
    sys_c = 0  # system 中
    curl_c = 0  # curl_exec 高
    funexit_c = 0  # function_exists 高
    call_c = 0  # CALL
    oppoint_c = 0  # (.)

    key_num = data.count('str_rot13') + data.count('serialize') + data.count('eval') + data.count(
        'base64_decode') + data.count('strrev')
    +data.count('assert') + data.count('file_put_contents') + data.count('fwrite') + data.count(
        'curl_exec') + data.count('passthru') + data.count('exec')
    +data.count('dl') + data.count('readlink') + data.count('popepassthru') + data.count('preg_replace') + data.count(
        'create_function') + data.count('array_map')
    +data.count('call_user_func') + data.count('array_filter') + data.count('usort') + data.count(
        'stream_socket_server') + data.count('pcntl_exec') + data.count('system')
    +data.count('chroot') + data.count('scandir') + data.count('chgrp') + data.count('shell_exec') + data.count(
        'proc_open') + data.count('proc_get_status')
    +data.count('popen') + data.count('ini_alter') + data.count('ini_restore') + data.count('ini_set') + data.count(
        'LD_PRELOAD') + data.count('_GET') + data.count('_POST') + data.count('_COOKIE')
    +data.count('_FILE') + data.count("phpinfo") + data.count("_SERVER")
    namespace_c = data.count("NAMESPACE")
    op_c = data.count("BINARY_OP")
    class_c = data.count("CLASS")
    passw_c = data.count("passw")
    # ASSIGN_REF
    include_c = data.count("INCLUDE_OR_EVAL")
    FUNC_DECL_c = data.count("FUNC_DECL")
    unquote_c = data.count("`")
    # eval_c = data.count("INCLUDE_OR_EVAL(eval)")
    eval_c = data.count(" eval ")
    shell_c = data.count("shell")
    hack_c = data.count("hack")
    backdoor_c = data.count("backdoor")
    capital_len = len(re.compile(r'[0-9]').findall(data))

    capital_f = capital_len / len(data)  # 大写字母频率
    post_c = data.count("_POST")
    file_c = data.count("_FILE")
    get_c = data.count("_GET")
    b64dec_c = data.count("base64_decode")
    flate_c = data.count("flate")
    iua_c = data.count("ignore_user_abort")
    stl_c = data.count("set_time_limit")
    smqr_c = data.count("set_magic_quotes_runtime")
    muf_c = data.count("move_uploaded_file")
    sys_c = data.count(" system ")
    curl_c = data.count(" curl_exec ")
    arg_c = data.count("ARG_LIST")
    content_list = re.split(r' ', data)
    max_length = 0
    for i in content_list:
        if len(i) > max_length:
            max_length = len(i)
        else:
            pass
    funexit_c = data.count(" function_exists ")
    call_c = data.count(" CALL ")
    oppoint_c = data.count("(.)")
    temp = data.count("passw")

    autowrite(
        len(data),
        # namespace_c,
        # class_c,
        op_c,
        arg_c,
        capital_f,
        key_num,
        passw_c,
        include_c,
        FUNC_DECL_c,
        max_length,
        unquote_c,
        eval_c,
        shell_c,
        # hack_c,
        # backdoor_c,
        call_c,
        fileid=fileid
    )


def autowrite(*features, fileid):
    global f_input
    global features_len
    features_len = len(features)
    wtf = "%f" + ",%f" * (len(features) - 1) + ",%i"
    features = features + (fileid,)
    f_input.write(wtf % features + '\n')


def generate(test_data_path, test_csv_path):
    global logger

    logger.info("提取特征中")
    row_list = util.csv_file_read(test_csv_path)
    for line in row_list:
        if line[1] == "jsp":
            continue
        else:
            data = read_file(test_data_path + str(line[0])).decode('utf-8')
            if len(data) == 0:
                data = ""
            get_features(data, line[0])
    logger.info("特征提取完毕")



def online_extract_feature(test_data_path, test_csv_path):
    generate(test_data_path, test_csv_path)


def online_predict(php_feature_path, php_result_csv_path, php_model_path):
    global logger
    logger.info("预测结果ing")
    clf = joblib.load(php_model_path)
    feature_max = pd.read_csv(php_feature_path,header=None)
    arr = feature_max.values
    test_data = np.delete(arr, -1, axis=1)  # 删除最后一列
    # test_data = np.array(arr)
    id = arr[:, features_len]

    y_pred = clf.predict(test_data)
    res_list = []
    for i in range(0, len(id)):
        tmplist = {}
        if y_pred[i] == 0:
            tmplist["prediction"] = "white"
        else:
            tmplist["prediction"] = "black"
        tmplist["file_id"] = int(id[i])
        res_list.append(tmplist)
    logger.info("预测结果完毕")
    logger.info("结果已保存至:" + php_result_csv_path)
    df = pd.DataFrame(res_list, columns=['file_id', 'prediction'])
    df.to_csv(php_result_csv_path, index=False)


def start(test_data_path, test_csv_path, php_feature_path, php_result_csv_path, php_model_path, php_log_path):
    global logger
    logging.basicConfig(level=logging.DEBUG,
                        filename=php_log_path,
                        filemode='a',
                        format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s')
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.StreamHandler())

    global f_input
    f_input = open(php_feature_path, 'w+')
    online_extract_feature(test_data_path, test_csv_path)
    f_input.flush()
    f_input.close()
    # exit()
    online_predict(php_feature_path, php_result_csv_path, php_model_path)


if __name__ == "__main__":
    start("asd")
