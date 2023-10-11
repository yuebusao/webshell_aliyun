# TL;DR
本仓库记录阿里云天池WEBSHELL文本检测学习赛的提交版本。
[比赛地址](https://tianchi.aliyun.com/competition/entrance/532068/forum)
为了本地测试模拟远程环境，我把训练数据处理成测试集data/test.csv，该程序支持本地和远程两种模式运行，见dist/config.json。
#### 本地使用
1. 解压data目录下的train.zip（数据集），该数据集目录为./data/train/{1-N}。也可自行修改数据集路径(config.json)
2. python main.py -m local
#### 远程跑分
已经制作好了dockerfile，直接本地build镜像传到自己的仓库提交即可，远程镜像仓库使用阿里云免费提供的就可以
[提交地址](https://tianchi.aliyun.com/competition/entrance/532068/submission/1058)

步骤如下：
1. docker login <your docker registry url> --username your_username（登录你的镜像仓库）
2. docker build -t registry.cn-shenzhen.aliyuncs.com/test_for_tianchi/test_for_tianchi_submit:1.0 . （本地构建镜像，镜像名为你的镜像仓库地址，tag可以写版本号）
3. docker push registry.cn-shenzhen.aliyuncs.com/test_for_tianchi/test_for_tianchi_submit:1.0（推送镜像至远程仓库）
#### 提交日志
##### 第一次提交
> 完全抄的[webshell检测算法实践](https://www.ctfiot.com/121724.html)，还没抄全

**php模型：** `stacking`集成模型

**jsp模型：** `mlp`

**得分：** 0.8443
```
{eval_score:0.8443,cost_time:4804,info:"null","score_detail":{"success": true, "score": 0.8443, "scoreJson": {"score": 0.8443, "php_precision_score": 0.82309, "php_recall_score": 0.83598, "jsp_precision_score": 0.91873, "jsp_recall_score": 0.90018}}}
```
**痛点：** `php`太拉了，用训练集都能跑个95，但是测试集是训练集的十几倍。
#### 优化
1. 图神经网络等高科技
2. 提取更牛逼的特征
3. 搞更多的训练集
#### 参考文章
1. https://bbs.ichunqiu.com/thread-63425-1-1.html
2. 之后补