from pyspark import SparkConf, SparkContext, SQLContext
from pyspark.mllib.tree import RandomForest
from pyspark.mllib.regression import LabeledPoint
from pyspark.ml.feature import VectorAssembler
from pyspark.mllib.linalg import Vectors
from pyspark.mllib.evaluation import MulticlassMetrics

import shutil

conf = (SparkConf().setAppName("Train wine app"))
sc = SparkContext("local", conf=conf)
sc.setLogLevel("ERROR")
sqlContext = SQLContext(sc)

# prediction dataframe
dataFrame = sqlContext.read.format('com.databricks.spark.csv').options(header='true', inferschema='true', sep=';').load('TrainingDataset.csv')
# validation datarame
validatedataFrame = sqlContext.read.format('com.databricks.spark.csv').options(header='true', inferschema='true', sep=';').load('ValidationDataset.csv')

# dropping quality column
# newDf = dataFrame.select(dataFrame.columns[:11])

outputRdd = dataFrame.rdd.map(lambda row: LabeledPoint(row[-1], Vectors.dense(row[:11])))

model = RandomForest.trainClassifier(outputRdd,numClasses=10,categoricalFeaturesInfo={}, numTrees=60, maxBins=32, maxDepth=4, seed=42)

# Evaluate model on test instances and compute test error
print("\n\n===Evaluate model on test instances and compute test error===")
predictions = model.predict(outputRdd.map(lambda x: x.features))
labelsAndPredictions = outputRdd.map(lambda lp: lp.label).zip(predictions)
testMSE = labelsAndPredictions.map(lambda lp: (lp[0] - lp[1]) * (lp[0] - lp[1])).sum() /\
        float(labelsAndPredictions.count())
print('Test Mean Squared Error = ' + str(testMSE))
print('Learned regression forest model:')
print(model.toDebugString())


validationOutputRdd = validatedataFrame.rdd.map(lambda row: LabeledPoint(row[-1], Vectors.dense(row[:11])))

# get labels
labels = validationOutputRdd.map(lambda lp: lp.label).distinct().collect()

predictions = model.predict(validationOutputRdd.map(lambda x: x.features))

predictionAndLabels = predictions.zip(validationOutputRdd.map(lambda lp: lp.label))

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

output_dir =  "./output/pythonRandomForestModel"

# if path not exit，delete
shutil.rmtree(output_dir, ignore_errors=True) 

#Saving model
model.save(sc, output_dir)

print("Model Saved successfully")
