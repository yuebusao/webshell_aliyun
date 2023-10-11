# Base Images
## 从天池基础镜像构建(from的base img 根据自己的需要更换，建议使用天池open list镜像链接：https://tianchi.aliyun.com/forum/postDetail?postId=67720)
FROM registry.cn-shanghai.aliyuncs.com/tcc_public/python:3.10

WORKDIR /
COPY ./model/ /tmp/
COPY ./dist/ /
COPY run.sh run.sh
##安装python依赖包
RUN python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --upgrade pip \
pip install pandas -i https://pypi.tuna.tsinghua.edu.cn/simple \
pip install numpy -i https://pypi.tuna.tsinghua.edu.cn/simple \
pip install joblib -i https://pypi.tuna.tsinghua.edu.cn/simple \
pip install scikit-learn -i https://pypi.tuna.tsinghua.edu.cn/simple \
pip install xgboost -i https://pypi.tuna.tsinghua.edu.cn/simple
## 镜像启动后统一执行 sh run.sh

CMD ["sh", "run.sh"]