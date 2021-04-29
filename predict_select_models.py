from pyspark import SparkConf, SparkContext

import sys, argparse

from predictClass import Predict

# 设置命令行参数
parser = argparse.ArgumentParser(description='Predict With Different Models')

#parser.add_argument('--model', action='store_true')
parser.add_argument('--model_type', nargs='?', default="LinearRegressionModel", help="LinearRegressionModel (default)\n LogisticRegressionModel \n RandomForestModel\n NaiveBayesModel")

parser.add_argument('model_dir', help='the directory of model')

parser.add_argument('dataset_path', help='the path of validation dataset which want to be predicted.')

args = parser.parse_args()

'''
if len(sys.argv) == 3:
    model_dir = sys.argv[1]
    model_type = "LinearRegressionModel"
    dataset_path = sys.argv[2]
elif len(sys.argv) == 4:
    model_type = sys.argv[1]
    model_dir = sys.argv[2]
    dataset_path = sys.argv[3]
else:
    print("Useage: python predict.py [model_type] <model_dir> <dataset_path>")
    print(""" 
        model_type: default LinearRegressionModel
            - LinearRegressionModel
            - LogisticRegressionModel
            - RandomForestModel
            - NaiveBayesModel
 
 model_dir: the directory of models
 dataset_path: the path of validation dataset which want to be predicted.
   """)
    sys.exit(-1) # 退出程序
 '''
    
# 创建spark 运行环境
conf = (SparkConf().setAppName("Train wine app"))
sc = SparkContext("local", conf=conf)
sc.setLogLevel("ERROR")

# 创建Predict对象进行预测
predObj = Predict(sc)

# 加载模型
predObj.load_model(args.model_type, args.model_dir)

# 数据预处理
predObj.parse_data(args.dataset_path)

# 进行预测并打印f-score结果
predObj.predict_and_print_analysis_results()