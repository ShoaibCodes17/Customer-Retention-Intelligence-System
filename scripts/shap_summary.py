import shap
import joblib
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
from src.config import Config
from src.models.train import FEATURES

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
model = joblib.load("src/models/churn_model.pkl")
df = pd.read_sql(f"SELECT {', '.join(FEATURES)} FROM rfm_features", engine)

explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(df)

shap.summary_plot(shap_values, df, show=False)
plt.tight_layout()
plt.savefig("docs/shap_summary.png", dpi=150)
print("Saved docs/shap_summary.png")