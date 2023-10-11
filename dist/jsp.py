#!/usr/bin/env python
# coding=utf-8
import logging
import joblib
import util
import pandas as pd

logger = None
check_list = []
res_list = []


class WebshellDec(object):
    def __init__(self, jsp_model_path):
        super(WebshellDec, self).__init__()
        self.cv = joblib.load(jsp_model_path["cv"])
        self.transformer = joblib.load(jsp_model_path["transformer"])
        self.mlp = joblib.load(jsp_model_path["mlp"])

    @staticmethod
    def load_file(file_path):
        t = b''
        with open(file_path, "rb") as f:
            for line in f:
                line = line.strip(b'\r\t')
                t += line
        return t

    def check(self, test_data_path, test_csv_path, jsp_result_csv_path):
        global res_list
        global logger
        logger.info("预测结果ing")
        cklist = util.csv_file_read(test_csv_path)
        for shell in cklist:
            tmplist = {}
            if shell[1] == "php":
                continue
                # tmplist["prediction"] = "white"
                # tmplist["file_id"]=shell[0]
            else:
                file_path = test_data_path + str(shell[0])
                t = self.load_file(file_path)
                t_list = list()
                t_list.append(t)
                x = self.cv.transform(t_list).toarray()
                x = self.transformer.transform(x).toarray()
                y_pred = self.mlp.predict(x)

                if y_pred[0] == 1:
                    # tmplist[1] = "black"
                    # tmplist[0] = shell[0]
                    tmplist["prediction"] = "black"
                    tmplist["file_id"] = shell[0]
                else:
                    # tmplist[1] = "white"
                    # tmplist[0] = shell[0]
                    tmplist["prediction"] = "white"
                    tmplist["file_id"] = shell[0]
                pdata = t.decode()
                # black_l = ['java.lang.Process','getRuntime','webshell','Cmd','password']
                black_l = ['java.lang.Process', 'getRuntime', 'webshell', 'Cmd', 'password', 'IDENTIFIER:defineClass',
                           'IDENTIFIER:processCmd', 'IDENTIFIER:MethodWebHell', 'IDENTIFIER:webhell',
                           'IDENTIFIER:URLClassLoader', 'IDENTIFIER:ReflectInvoker', 'IDENTIFIER:MyClassLoader']
                stack_c = 0
                for i in black_l:
                    stack_c = stack_c + pdata.count(i)
                if stack_c > 0:
                    # print("======="+str(stack_c))
                    tmplist["prediction"] = "black"
                    tmplist["file_id"] = shell[0]
            res_list.append(tmplist)
        logger.info("预测结果完毕")
        logger.info("结果已保存至:"+jsp_result_csv_path)
        df = pd.DataFrame(res_list, columns=['file_id', 'prediction'])
        df.to_csv(jsp_result_csv_path, index=False)


def start(test_data_path, test_csv_path, jsp_result_csv_path, jsp_model_path, jsp_log_path):
    global logger
    logging.basicConfig(level=logging.DEBUG,
                        filename=jsp_log_path,
                        filemode='a',
                        format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s')
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.StreamHandler())

    logger.info("加载模型ing")
    webshelldc = WebshellDec(jsp_model_path)
    logger.info("加载模型完毕")

    webshelldc.check(test_data_path, test_csv_path, jsp_result_csv_path)


if __name__ == "__main__":
    # start()
    print(1)
