import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_squared_error

st.set_page_config(page_title="PM2.5 머신러닝", layout="wide")

st.title("🌫️ PM2.5 예측 머신러닝")

uploaded_file = st.file_uploader(
    "PRSA_data_2010.1.1-2014.12.31.csv를 업로드하세요",
    type=["csv"]
)

if uploaded_file is not None:

    df = pd.read_csv(uploaded_file)

    st.subheader("데이터 미리보기")
    st.dataframe(df.head())

    if "No" in df.columns:
        df = df.drop(columns=["No"])

    df = df.dropna(subset=["pm2.5"])

    X = df.drop(columns=["pm2.5"])
    y = df["pm2.5"]

    numeric_features = X.select_dtypes(include=["int64","float64"]).columns
    categorical_features = X.select_dtypes(include=["object"]).columns

    numeric_transformer = Pipeline([
        ("imputer", SimpleImputer(strategy="mean")),
        ("scaler", StandardScaler())
    ])

    categorical_transformer = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore"))
    ])

    preprocessor = ColumnTransformer([
        ("num", numeric_transformer, numeric_features),
        ("cat", categorical_transformer, categorical_features)
    ])

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42
    )

    models = {
        "Linear Regression": LinearRegression(),
        "Random Forest": RandomForestRegressor(
            n_estimators=200,
            random_state=42,
            n_jobs=-1
        )
    }

    st.subheader("모델 성능")

    result = []

    rf_pipe = None
    rf_pred = None

    for name, model in models.items():

        pipe = Pipeline([
            ("preprocessor", preprocessor),
            ("model", model)
        ])

        pipe.fit(X_train, y_train)

        pred = pipe.predict(X_test)

        r2 = r2_score(y_test, pred)
        rmse = np.sqrt(mean_squared_error(y_test, pred))

        result.append([name, round(r2,3), round(rmse,3)])

        if name == "Random Forest":
            rf_pipe = pipe
            rf_pred = pred

    result_df = pd.DataFrame(
        result,
        columns=["Model","R²","RMSE"]
    )

    st.dataframe(result_df)

    st.subheader("실제값 vs 예측값")

    fig, ax = plt.subplots(figsize=(6,6))

    ax.scatter(y_test, rf_pred, s=10)

    m = min(y_test.min(), rf_pred.min())
    M = max(y_test.max(), rf_pred.max())

    ax.plot([m,M],[m,M],"r--")

    ax.set_xlabel("Actual")
    ax.set_ylabel("Predicted")

    st.pyplot(fig)

    st.subheader("Feature Importance")

    ohe = rf_pipe.named_steps["preprocessor"]\
        .named_transformers_["cat"]\
        .named_steps["onehot"]

    cat_names = ohe.get_feature_names_out(categorical_features)

    feature_names = list(numeric_features) + list(cat_names)

    importance = rf_pipe.named_steps["model"].feature_importances_

    idx = np.argsort(importance)[-10:]

    fig2, ax2 = plt.subplots(figsize=(8,5))

    ax2.barh(
        np.array(feature_names)[idx],
        importance[idx]
    )

    st.pyplot(fig2)

else:
    st.info("CSV 파일을 업로드하면 분석이 시작됩니다.")
