import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_squared_error
import numpy as np

df = pd.read_csv("PRSA_data_2010.1.1-2014.12.31.csv")

# 불필요한 번호 컬럼 제거
if "No" in df.columns:
    df = df.drop(columns=["No"])

# Target 결측 제거
df = df.dropna(subset=["pm2.5"])

X = df.drop(columns=["pm2.5"])
y = df["pm2.5"]

num_cols = X.select_dtypes(include=["int64","float64"]).columns
cat_cols = X.select_dtypes(include=["object"]).columns

numeric = Pipeline([
    ("imputer", SimpleImputer(strategy="mean")),
    ("scaler", StandardScaler())
])

categorical = Pipeline([
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("onehot", OneHotEncoder(handle_unknown="ignore"))
])

pre = ColumnTransformer([
    ("num", numeric, num_cols),
    ("cat", categorical, cat_cols)
])

X_train,X_test,y_train,y_test=train_test_split(
    X,y,test_size=0.2,random_state=42)

models={
    "Linear Regression":LinearRegression(),
    "Random Forest":RandomForestRegressor(
        n_estimators=200,random_state=42,n_jobs=-1)
}

rf_pipe=None
for name,model in models.items():
    pipe=Pipeline([("pre",pre),("model",model)])
    pipe.fit(X_train,y_train)
    pred=pipe.predict(X_test)
    r2=r2_score(y_test,pred)
    rmse=np.sqrt(mean_squared_error(y_test,pred))
    print(f"{name}")
    print(f"R2   : {r2:.3f}")
    print(f"RMSE : {rmse:.3f}\n")
    if name=="Random Forest":
        rf_pipe=pipe
        rf_pred=pred

plt.figure(figsize=(6,6))
plt.scatter(y_test,rf_pred,s=8)
m=min(y_test.min(),rf_pred.min())
M=max(y_test.max(),rf_pred.max())
plt.plot([m,M],[m,M])
plt.xlabel("Actual PM2.5")
plt.ylabel("Predicted PM2.5")
plt.title("Random Forest: Actual vs Predicted")
plt.tight_layout()
plt.savefig("actual_vs_predicted.png")

ohe=rf_pipe.named_steps["pre"].named_transformers_["cat"]["onehot"]
cat_names=ohe.get_feature_names_out(cat_cols)
feature_names=list(num_cols)+list(cat_names)
imp=rf_pipe.named_steps["model"].feature_importances_
idx=np.argsort(imp)[-10:]

plt.figure(figsize=(8,5))
plt.barh(np.array(feature_names)[idx],imp[idx])
plt.title("Top 10 Feature Importances")
plt.tight_layout()
plt.savefig("feature_importance.png")

print("Graphs saved.")
