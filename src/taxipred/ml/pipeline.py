def scaling(X_train, X_test, scaler):
    scaled_X_train = scaler.fit_transform(X_train)
    scaled_X_test = scaler.transform(X_test)
    return scaled_X_train, scaled_X_test, scaler


def fit_predict(scaled_X_train, scaled_X_test, y_train, model):
    model.fit(scaled_X_train, y_train)
    y_pred = model.predict(scaled_X_test)
    return y_pred, model
