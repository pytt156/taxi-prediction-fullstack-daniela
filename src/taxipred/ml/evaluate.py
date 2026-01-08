from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay,
)
import numpy as np


def regression_eval(y_test, y_pred):
    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    return {"mae": mae, "mse": mse, "rmse": rmse}


def classification_eval(y_test, y_pred):
    report = classification_report(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)
    display = ConfusionMatrixDisplay(cm)
    return report, display
