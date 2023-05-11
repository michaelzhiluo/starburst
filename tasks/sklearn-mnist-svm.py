from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn import svm

digits = datasets.load_digits()
X = digits.data
y = digits.target

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = svm.SVC(gamma=0.001)
model.fit(X_train, y_train)

score = model.score(X_test, y_test)
print('Accuracy:', score)
