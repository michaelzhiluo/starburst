from sklearn.datasets import fetch_openml
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

# Fetch the dataset using the name or dataset_id
mnist = fetch_openml('mnist_784', version=1)

# Split the data into features (X) and target (y)
X, y = mnist["data"], mnist["target"]

# It can be beneficial to scale the features in many ML algorithms
scaler = StandardScaler()
X = scaler.fit_transform(X)

# Split the dataset into a training and a testing set
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Define the parameter values that should be searched
n_estimators_range = list(range(1, 31))

# Create a parameter grid: map the parameter names to the values that should be searched
param_grid = dict(n_estimators=n_estimators_range)

# Instantiate the grid
grid = GridSearchCV(RandomForestClassifier(), param_grid, cv=10, scoring='accuracy', n_jobs=-1)

# Fit the grid with data
grid.fit(X_train, y_train)

print("Best parameters: ", grid.best_params_)
print("Best cross-validation score: ", grid.best_score_)
