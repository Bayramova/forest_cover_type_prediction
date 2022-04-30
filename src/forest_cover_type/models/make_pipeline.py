from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline


def make_pipeline(model, use_scaler, logreg_c, max_iter, random_state, n_estimators, max_depth):
    steps = []
    if use_scaler:
        steps.append(("scaler", StandardScaler()))

    if model == "LogisticRegression":
        classifier = LogisticRegression(C=logreg_c, max_iter=max_iter)
    elif model == "RandomForestClassifier":
        classifier = RandomForestClassifier(
            n_estimators=n_estimators, max_depth=None if max_depth == -1 else max_depth, random_state=random_state)

    steps.append(("clf", classifier))
    return Pipeline(steps=steps)
