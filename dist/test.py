import re

import joblib
import numpy as np
import pandas as pd
from sklearn import metrics
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.ensemble import AdaBoostClassifier, VotingClassifier, StackingClassifier
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
# from mlxtend.classifier import StackingClassifier
from xgboost import XGBClassifier

from online_version.dist import util

php_result_csv_path = "../result.csv"
test_feature_path = "../../data/3space.csv"
features_len = 13


# tmpcsv = "./data/3space.csv"  # 提取到的特征


def create_models():
    models = [
        AdaBoostClassifier(base_estimator=DecisionTreeClassifier(max_depth=26), n_estimators=101),
        GradientBoostingClassifier(n_estimators=101),
        RandomForestClassifier(n_estimators=101),
        XGBClassifier(),
        DecisionTreeClassifier(max_depth=26)
    ]
    estimators = []
    i = 1
    for m in models:
        estimators.append(((str(i)), m))
        i += 1

    stack = StackingClassifier(estimators)

    return stack


def train():
    feature_max = pd.read_csv(test_feature_path)
    arr = feature_max.values
    data = np.delete(arr, -1, axis=1)  # 删除最后一列

    target = arr[:, len(arr[0]) - 1]  # 标签
    # 随机划分训练集和测试集
    # train_data, test_data, train_target, test_target = train_test_split(data, target, test_size=0.3, random_state=10)
    model = create_models()
    model.fit(data, target)
    # y_pred2 = model.predict(test_data)  # 预测
    # print("y_pred:%s" % y_pred2)
    # print("test_target:%s" % test_target)
    # # Verify
    # print('Precision:%.3f' % metrics.precision_score(y_true=test_target, y_pred=y_pred2))  # 查全率
    # print('Recall:%.3f' % metrics.recall_score(y_true=test_target, y_pred=y_pred2))  # 查准率
    # print(metrics.confusion_matrix(y_true=test_target, y_pred=y_pred2))  # 混淆矩阵
    #
    # print("features_len:" + str(features_len))
    joblib.dump(model, '../model/php_pred1.model')


def metric(y_pred2, test_target):
    print("y_pred:%s" % y_pred2)
    print("test_target:%s" % test_target)
    # Verify
    print('Precision:%.3f' % metrics.precision_score(y_true=test_target, y_pred=y_pred2))  # 查全率
    print('Recall:%.3f' % metrics.recall_score(y_true=test_target, y_pred=y_pred2))  # 查准率
    print(metrics.confusion_matrix(y_true=test_target, y_pred=y_pred2))  # 混淆矩阵

    print("features_len:" + str(features_len))


def online_predict():
    clf = joblib.load('../model/php_pred1.model')
    feature_max = pd.read_csv("../../data/feature.csv", header=None)#没有表头
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
    # metric(y_pred, id)
    df = pd.DataFrame(res_list, columns=['file_id', 'prediction'])
    df.to_csv(php_result_csv_path, index=False)

online_predict()

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



# f_input = open("../../data/feature.csv", 'w+')
#
# print("提取特征中")
# head_row = pd.read_csv('../../train.csv', nrows=0)
# head_row_list = list(head_row)
# # 读取
# csv_result = pd.read_csv('../../train.csv', usecols=head_row_list)
# row_list = csv_result.values.tolist()
# for line in row_list:
#     if line[1] == "jsp":
#         continue
#     else:
#         data = read_file("../../train/train/" + str(line[0])).decode('utf-8')
#         if len(data) == 0:
#             data = ""
#         get_features(data, line[0])
# print("特征提取完毕")
# f_input.flush()
# f_input.close()
