# -*- coding: utf-8 -*-
"""Machine Learning with PySpark someda.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1OORWZ1OlAqpt8d7XjMX52EBGFosiz0VV

# **Machine Learning with PySpark**

**Background Information**

Customer churn is a significant challenge in the telecom industry. Identifying customers who are
likely to churn is crucial for implementing proactive measures to retain them. By leveraging PySpark,
we can take advantage of its distributed computing capabilities to handle large volumes of data
efficiently and build an accurate machine learning model for churn prediction.

**Problem Statement**

The goal of this project is to develop a machine learning model using PySpark that accurately
predicts customer churn in a telecom company. The model should achieve a minimum accuracy of
0.8, enabling the company to proactively identify and retain customers at risk of leaving. By
effectively predicting churn, the company can implement targeted retention strategies, reduce
customer attrition, and improve overall business performance.
"""

!pip install pyspark

#Import the necesary libraries
from pyspark.sql import SparkSession
from pyspark.ml.feature import StringIndexer, VectorAssembler
from pyspark.ml import Pipeline
from pyspark.ml.classification import RandomForestClassifier, LogisticRegression
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.ml.tuning import CrossValidator, ParamGridBuilder
from pyspark import SparkContext

# Create a SparkSession
spark = SparkSession.builder.appName("Churn101").getOrCreate()

# Local file path to save the downloaded CSV file
local_file_path = os.getcwd() + "/telecom_dataset.csv"

#Dataset URL
csv_url = "https://archive.org/download/telecom_dataset/telecom_dataset.csv"

# Download the CSV file
urllib.request.urlretrieve(csv_url, local_file_path)

# Fetch and load dataset: https://archive.org/download/telecom_dataset/telecom_dataset.csv
df = spark.read.csv(local_file_path, header=True)

"""**Data Preprocessing:**"""

df.show(5)

df.shape

# Handling missing values
mydf = df.dropna()

"""**Feature Engineering:**"""

# Define the numerical columns
numerical_columns = ['Age', 'MonthlyCharges', 'TotalCharges', 'Month_Total_Ratio']

# Assemble the numerical columns into a vector column
assembler = VectorAssembler(inputCols=numerical_columns, outputCol="vFeatures")

# Create a MinMaxScaler object
scaler = MinMaxScaler(inputCol="vFeatures", outputCol="scaled_features")

# Encoding categorical variables
indexers = [StringIndexer(inputCol=col, outputCol=col + "_index").fit(df) for col in ['Gender', 'Contract', 'Churn']]
pipeline = Pipeline(stages=indexers)
df = pipeline.fit(df).transform(df)

"""**Model Selection and Training:**"""

# Split the Data into Training set and Testing set
train_data, test_data = df.randomSplit([0.8, 0.2], seed=42)

# Define the models to try
models = [
    RandomForestClassifier(labelCol="label", featuresCol="features", seed=42),
    LogisticRegression(labelCol="label", featuresCol="features")
]

# Create a list of parameter grids to search through
paramGrids = [
    ParamGridBuilder().addGrid(RandomForestClassifier.maxDepth, [5, 10]).build(),
    ParamGridBuilder().addGrid(LogisticRegression.regParam, [0.01, 0.1]).build()
]

# Create a list to store the accuracy for each model
accuracies = []

"""**Model Evaluation:**"""

# Train and evaluate each model
for i in range(len(models)):
    model = models[i]
    paramGrid = paramGrids[i]

    evaluator = BinaryClassificationEvaluator(labelCol="label")
    tvs = TrainValidationSplit(estimator=model, estimatorParamMaps=paramGrid, evaluator=evaluator)

    # Train the model
    tvs_model = tvs.fit(train_data)

    # Make predictions
    predictions = tvs_model.transform(test_data)

    # Evaluate model performance
    accuracy = evaluator.evaluate(predictions)
    accuracies.append(accuracy)

    print("Model", i+1, "Accuracy:", accuracy)