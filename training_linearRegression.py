"""
Linear Regression With SGD.
"""
from pyspark import SparkConf, SparkContext, SQLContext
from pyspark import SparkFiles
from pyspark.mllib.regression import LabeledPoint, LinearRegressionWithSGD
from pyspark.mllib.regression import LabeledPoint
from pyspark.ml.feature import VectorAssembler
from pyspark.mllib.linalg import Vectors
from pyspark.mllib.evaluation import MulticlassMetrics

import shutil

conf = (SparkConf().setAppName("Train wine app"))
sc = SparkContext("local", conf=conf)
sc.setLogLevel("ERROR")

training_dataset_url = "https://my-project-dataset.s3.amazonaws.com/TrainingDataset.csv"
validation_dataset_url = "https://my-project-dataset.s3.amazonaws.com/ValidationDataset.csv"

sc.addFile(training_dataset_url)
sc.addFile(validation_dataset_url)

sqlContext = SQLContext(sc)
# sc = SparkContext(appName="PythonLinearRegressionWithSGDExample")
# sqlContext = SQLContext(sc)

train_df = sqlContext.read.format('com.databricks.spark.csv').options(header='true', inferschema='true', sep=';').load("file://"+SparkFiles.get("TrainingDataset.csv"))

# parsed data
parsedData = train_df.rdd.map(lambda row: LabeledPoint(row[-1], Vectors.dense(row[:11])))

# 定义线性回归模型
model = LinearRegressionWithSGD.train(parsedData, iterations=1000, step=0.001)

# Evaluate the model on training data
print("\n\n===Evaluate the model on training data===")
valuesAndPreds = parsedData.map(lambda p: (p.label, model.predict(p.features)))
MSE = valuesAndPreds \
    .map(lambda vp: (vp[0] - vp[1])**2) \
    .reduce(lambda x, y: x + y) / valuesAndPreds.count()
print("Linear Regression With SGD")
print("Mean Squared Error = " + str(MSE))


# 使用验证集进行验证
# 读取验证集数据
validatedataFrame = sqlContext.read.format('com.databricks.spark.csv').options(header='true', inferschema='true', sep=';').load("file://"+SparkFiles.get("TrainingDataset.csv"))

# 数据预处理
validationOutputRdd = validatedataFrame.rdd.map(lambda row: LabeledPoint(row[-1], Vectors.dense(row[:11])))

# 获取不重复的labels
labels = validationOutputRdd.map(lambda lp: lp.label).distinct().collect()

# 使用模型对验证集数据进行预测
predictions = model.predict(validationOutputRdd.map(lambda x: x.features))

# 将预测结果进行四舍五入
round_predictions = predictions.map(lambda x: float(round(x)))

# 将label与预测结果打包到一起
predictionAndLabels = round_predictions.zip(validationOutputRdd.map(lambda lp: lp.label))

# 创建MulticlassMetrics对象，以获得预测准确度相关信息
metrics = MulticlassMetrics(predictionAndLabels)

# Overall statistics
print("==== Summary Statistics ====")
for label in sorted(labels):
        print("Class %s precision = %s" % (label, metrics.precision(label)))
        print("Class %s recall = %s" % (label, metrics.recall(label)))
        print("Class %s F1 Measure = %s \n\n" % (label, metrics.fMeasure(label, beta=1.0)))
        

# Weighted stats
print("=== Weighted staus ===")
print("Weighted recall = %s" % metrics.weightedRecall)
print("Weighted precision = %s" % metrics.weightedPrecision)
print("Weighted F(1) Score = %s" % metrics.weightedFMeasure())
print("Weighted F(0.5) Score = %s" % metrics.weightedFMeasure(beta=0.5))
print("Weighted false positive rate = %s" % metrics.weightedFalsePositiveRate)

print("\n\n==== Saving model ====")

output_dir = "./output/pythonLinearRegressionModel"

shutil.rmtree(output_dir, ignore_errors=True) 
# Save and load model
model.save(sc, output_dir)
print("Model Saved successfully")