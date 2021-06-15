import pandas as pd
from matplotlib import pyplot as plt
from sklearn.datasets import load_boston
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

iris = load_iris()

boston = load_boston()
X = pd.DataFrame(boston.data, columns=boston.feature_names)
y = boston.target
X_train, X_test, y_train, y_test = train_test_split(X, y,
    test_size=0.25, random_state=42)
#feature_names = boston.feature_name
#print("Feature names:", feature_names)
print("\nFirst 10 rows of X:\n", X[:10])

rf = RandomForestRegressor(n_estimators=150)
rf.fit(X_train, y_train)

sort = rf.feature_importances_.argsort()
plt.barh(boston.feature_names[sort], rf.feature_importances_[sort])
plt.xlabel("Feature Importance")

plt.show()