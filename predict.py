# import findspark
# findspark.init()
import sys

from pyspark import SparkConf, SparkContext, SQLContext
from pyspark.mllib.tree import RandomForestModel
from pyspark.mllib.evaluation import MulticlassMetrics
from pyspark.mllib.regression import LabeledPoint
from pyspark.mllib.linalg import Vectors


if len(sys.argv) == 2:
    dataset_path = sys.argv[1]
else:
    print("python predict.py [dataset_path]")
    print("** please enter two parameter, the second parameter should be the validation dataset file path...")
    sys.exit(1) # 退出程序

    
conf = (SparkConf().setAppName("Predict wine app"))
sc = SparkContext("local", conf=conf)
sc.setLogLevel("ERROR")
sqlContext = SQLContext(sc)


print("==== DataSet is being Read ====")
#print(testFile)

# Read trained model
model = RandomForestModel.load(sc, "./output/pythonRandomForestModel")
# print(model)

# Reading TestValidation.csv
df = sqlContext.read.format('com.databricks.spark.csv').options(header='true', inferschema='true', sep=';').load(dataset_path)

outputRdd = df.rdd.map(lambda row: LabeledPoint(row[-1], Vectors.dense(row[:11])))

predictions = model.predict(outputRdd.map(lambda x: x.features))
# labelsAndPredictions = outputRdd.map(lambda lp: lp.label).zip(predictions)

# metrics = MulticlassMetrics(labelsAndPredictions)
# get labels
labels = outputRdd.map(lambda lp: lp.label).distinct().collect()

predictionAndLabels = predictions.zip(outputRdd.map(lambda lp: lp.label))

metrics = MulticlassMetrics(predictionAndLabels)

# Overall Statistics

print("\n\n==== Summary Statatistics ====")
for label in labels:
    try:
        f1Score = metrics.fMeasure(label)
        print("Class %s F1 Score = %s" % (label, f1Score))
    except:
        print("ERROR!!")
print("Weighted F(1) Score = %s" % metrics.weightedFMeasure())
print("Weighted precision = %s" % metrics.weightedPrecision)
