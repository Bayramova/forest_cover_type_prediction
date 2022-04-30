from joblib import dump

import click
import mlflow

import pandas as pd
from sklearn.model_selection import cross_validate

from forest_cover_type.data.load_dataset import load_dataset
from forest_cover_type.models.make_pipeline import make_pipeline


@click.command()
@click.option("-d", "--dataset-path", default="data/train.csv", show_default=True, help="Path to csv with data.")
@click.option("-s", "--save-model-path", default="models/model.joblib", show_default=True, help="Path to save trained model.")
@click.option("--test-split-ratio", default=0.2, show_default=True, help="Proportion of the dataset to include in the test split, should be between 0.0 and 1.0.")
@click.option("--random-state", default=42, show_default=True, help="Random state.")
@click.option("--use-scaler", default=True, show_default=True, help="Specifies whether to scale the data.")
@click.option("--logreg-c", default=1.0, show_default=True, help="Inverse of regularization strength.")
@click.option("--max-iter", default=100, show_default=True, help="Maximum number of iterations taken for the solvers to converge.")
@click.option("--k-folds", default=5, show_default=True, help="Number of folds in cross-validation.")
@click.option("--model", default="LogisticRegression", show_default=True, help="Name of model for training.")
@click.option("--n-estimators", default=100, show_default=True, help="The number of trees in the forest.")
def train(dataset_path, save_model_path, test_split_ratio, random_state, use_scaler, logreg_c, max_iter, k_folds, model, n_estimators):
    """Script that trains a model and saves it to a file."""
    with mlflow.start_run():
        X_train, X_val, y_train, y_val = load_dataset(
            dataset_path=dataset_path, test_split_ratio=test_split_ratio, random_state=random_state)

        pipeline = make_pipeline(model=model, use_scaler=use_scaler,
                                 logreg_c=logreg_c, max_iter=max_iter, random_state=random_state, n_estimators=n_estimators)

        scores = cross_validate(pipeline, pd.concat([X_train, X_val]), pd.concat(
            [y_train, y_val]), cv=k_folds, scoring=('accuracy', 'neg_log_loss', 'roc_auc_ovr'))
        accuracy = scores['test_accuracy'].mean()
        log_loss = - scores['test_neg_log_loss'].mean()
        roc_auc = scores['test_roc_auc_ovr'].mean()
        click.echo(
            f"Mean accuracy across all CV splits: {accuracy}")
        click.echo(
            f"Mean log_loss across all CV splits: {log_loss}")
        click.echo(
            f"Mean roc_auc_ovr across all CV splits: {roc_auc}")

        pipeline.fit(pd.concat([X_train, X_val]), pd.concat([y_train, y_val]))
        dump(pipeline, save_model_path)
        click.echo(f"Model is saved to {save_model_path}.")

        if model == "LogisticRegression":
            mlflow.log_param("use_scaler", use_scaler)
            mlflow.log_param("logreg_c", logreg_c)
            mlflow.log_param("max_iter", max_iter)
        elif model == "RandomForestClassifier":
            mlflow.log_param("n_estimators", n_estimators)

        mlflow.log_metrics(
            {"accuracy": accuracy, "log_loss": log_loss, "roc_auc": roc_auc})
        mlflow.sklearn.log_model(pipeline, "model")
