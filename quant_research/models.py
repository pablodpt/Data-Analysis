"""Leakage-safe expanding walk-forward ML benchmarks."""
from __future__ import annotations

from dataclasses import dataclass
import importlib.util
import warnings
from typing import Any

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    recall_score,
    r2_score,
    roc_auc_score,
)
from sklearn.model_selection import TimeSeriesSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from .backtest import backtest_positions, buy_and_hold_metrics
from .features import MODEL_FEATURES


@dataclass
class ModelSpec:
    name: str
    family: str
    factory: Any
    available: bool = True
    status: str = "available"
    tasks: tuple[str, ...] = ("classification", "regression")



def model_specs() -> list[ModelSpec]:
    specs = [
        ModelSpec(
            "Logistic Regression", "linear",
            lambda task: LogisticRegression(C=0.1, max_iter=2000, solver="lbfgs", random_state=42),
            tasks=("classification",),
        ),
        ModelSpec(
            "Ridge Regression", "linear",
            lambda task: Ridge(alpha=10.0),
            tasks=("regression",),
        ),
        ModelSpec(
            "Random Forest", "tree",
            lambda task: (
                RandomForestClassifier(n_estimators=160, max_depth=4, min_samples_leaf=25,
                                       max_features=0.7, random_state=42, n_jobs=1)
                if task == "classification" else
                RandomForestRegressor(n_estimators=160, max_depth=4, min_samples_leaf=25,
                                      max_features=0.7, random_state=42, n_jobs=1)
            ),
        ),
        ModelSpec(
            "Gradient Boosting", "tree",
            lambda task: (
                GradientBoostingClassifier(n_estimators=100, learning_rate=0.03, max_depth=2,
                                           min_samples_leaf=25, subsample=0.8, random_state=42)
                if task == "classification" else
                GradientBoostingRegressor(n_estimators=100, learning_rate=0.03, max_depth=2,
                                          min_samples_leaf=25, loss="huber", random_state=42)
            ),
        ),
    ]
    if importlib.util.find_spec("xgboost"):
        from xgboost import XGBClassifier, XGBRegressor
        specs.append(ModelSpec(
            "XGBoost", "tree",
            lambda task: (
                XGBClassifier(n_estimators=140, max_depth=2, learning_rate=0.03,
                              min_child_weight=25, subsample=0.8, colsample_bytree=0.8,
                              reg_lambda=10.0, objective="binary:logistic", eval_metric="logloss",
                              n_jobs=1, random_state=42, verbosity=0)
                if task == "classification" else
                XGBRegressor(n_estimators=140, max_depth=2, learning_rate=0.03,
                             min_child_weight=25, subsample=0.8, colsample_bytree=0.8,
                             reg_lambda=10.0, objective="reg:squarederror", n_jobs=1,
                             random_state=42, verbosity=0)
            ),
        ))
    else:
        specs.append(ModelSpec("XGBoost", "tree", None, False, "paquete xgboost no instalado"))
    if importlib.util.find_spec("lightgbm"):
        from lightgbm import LGBMClassifier, LGBMRegressor
        specs.append(ModelSpec(
            "LightGBM", "tree",
            lambda task: (
                LGBMClassifier(n_estimators=140, learning_rate=0.03, max_depth=3, num_leaves=7,
                               min_child_samples=25, reg_lambda=10.0, verbosity=-1,
                               n_jobs=1, random_state=42)
                if task == "classification" else
                LGBMRegressor(n_estimators=140, learning_rate=0.03, max_depth=3, num_leaves=7,
                              min_child_samples=25, reg_lambda=10.0, verbosity=-1,
                              n_jobs=1, random_state=42)
            ),
        ))
    else:
        specs.append(ModelSpec("LightGBM", "tree", None, False, "paquete lightgbm no instalado"))
    if importlib.util.find_spec("catboost"):
        from catboost import CatBoostClassifier, CatBoostRegressor
        specs.append(ModelSpec(
            "CatBoost", "tree",
            lambda task: (
                CatBoostClassifier(iterations=140, depth=3, learning_rate=0.03, l2_leaf_reg=10,
                                   verbose=False, thread_count=1, random_seed=42, allow_writing_files=False)
                if task == "classification" else
                CatBoostRegressor(iterations=140, depth=3, learning_rate=0.03, l2_leaf_reg=10,
                                  loss_function="RMSE", verbose=False, thread_count=1,
                                  random_seed=42, allow_writing_files=False)
            ),
        ))
    else:
        specs.append(ModelSpec("CatBoost", "tree", None, False, "paquete catboost no instalado"))
    return specs


def _pipeline(spec: ModelSpec, task: str) -> Pipeline:
    estimator = spec.factory(task)
    steps: list[tuple[str, Any]] = [("imputer", SimpleImputer(strategy="median"))]
    if spec.name in {"Logistic Regression", "Ridge Regression"}:
        steps.append(("scaler", StandardScaler()))
    steps.append(("model", estimator))
    return Pipeline(steps)


def _positive_probability(estimator: Any, x: pd.DataFrame) -> np.ndarray:
    if hasattr(estimator, "predict_proba"):
        probabilities = estimator.predict_proba(x)
        classes = list(estimator.classes_)
        if 1 in classes:
            return np.asarray(probabilities[:, classes.index(1)], dtype=float)
        return np.asarray(probabilities[:, -1], dtype=float)
    if hasattr(estimator, "decision_function"):
        score = np.asarray(estimator.decision_function(x), dtype=float)
        return 1.0 / (1.0 + np.exp(-np.clip(score, -30, 30)))
    return np.asarray(estimator.predict(x), dtype=float)


def _safe_auc(actual: np.ndarray, score: np.ndarray) -> float:
    if len(np.unique(actual)) < 2:
        return np.nan
    try:
        return float(roc_auc_score(actual, score))
    except Exception:
        return np.nan


def _classification_metrics(actual: np.ndarray, probability: np.ndarray) -> dict[str, float | int]:
    predicted = (probability >= 0.5).astype(int)
    positive_rate = float(np.mean(actual))
    return {
        "oos_observations": int(len(actual)),
        "positive_rate": positive_rate,
        "baseline_accuracy": float(max(positive_rate, 1.0 - positive_rate)),
        "accuracy": float(accuracy_score(actual, predicted)),
        "precision": float(precision_score(actual, predicted, zero_division=0)),
        "recall": float(recall_score(actual, predicted, zero_division=0)),
        "f1": float(f1_score(actual, predicted, zero_division=0)),
        "roc_auc": _safe_auc(actual, probability),
    }


def _regression_metrics(actual: np.ndarray, prediction: np.ndarray) -> dict[str, float | int]:
    predicted_direction = prediction > 0
    actual_direction = actual > 0
    positive_rate = float(actual_direction.mean())
    metrics: dict[str, float | int] = {
        "oos_observations": int(len(actual)),
        "positive_rate": positive_rate,
        "baseline_accuracy": float(max(positive_rate, 1.0 - positive_rate)),
        "accuracy": float(accuracy_score(actual_direction.astype(int), predicted_direction.astype(int))),
        "precision": float(precision_score(actual_direction.astype(int), predicted_direction.astype(int), zero_division=0)),
        "recall": float(recall_score(actual_direction.astype(int), predicted_direction.astype(int), zero_division=0)),
        "f1": float(f1_score(actual_direction.astype(int), predicted_direction.astype(int), zero_division=0)),
        "roc_auc": _safe_auc(actual_direction.astype(int), prediction),
        "mae": float(mean_absolute_error(actual, prediction)),
        "rmse": float(np.sqrt(mean_squared_error(actual, prediction))),
        "r2": float(r2_score(actual, prediction)) if len(actual) > 1 else np.nan,
        "directional_accuracy": float(np.mean(actual_direction == predicted_direction)),
    }
    try:
        from scipy.stats import spearmanr
        metrics["spearman_ic"] = float(spearmanr(actual, prediction).statistic)
    except Exception:
        metrics["spearman_ic"] = np.nan
    return metrics


def _classification_position(probability: np.ndarray) -> np.ndarray:
    return np.where(probability >= 0.55, 1.0, np.where(probability <= 0.45, -1.0, 0.0))


def _feature_importance(
    context: dict[str, Any] | None,
    feature_names: list[str],
    random_state: int = 42,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    if context is None:
        return pd.DataFrame(), {"status": "not_run", "reason": "No hay modelo de clasificación con fold final válido."}
    estimator = context["estimator"]
    x_test = context["x_test"]
    y_test = context["y_test"]
    rows: list[dict[str, Any]] = []
    metadata: dict[str, Any] = {
        "model": context["model"],
        "task": "classification_direction_1d",
        "fold": int(context["fold"]),
        "test_start": context["test_start"],
        "test_end": context["test_end"],
        "status": "permutation importance run on final chronological test fold",
    }
    try:
        from sklearn.inspection import permutation_importance
        perm = permutation_importance(
            estimator, x_test, y_test, scoring="roc_auc", n_repeats=5,
            random_state=random_state, n_jobs=1,
        )
        for name, mean, std in zip(feature_names, perm.importances_mean, perm.importances_std):
            rows.append({
                "feature": name,
                "importance_type": "permutation_roc_auc",
                "importance_mean": float(mean),
                "importance_std": float(std),
                "model": context["model"],
            })
    except Exception as exc:
        metadata["permutation_error"] = f"{type(exc).__name__}: {exc}"

    final_estimator = estimator.named_steps["model"]
    native = getattr(final_estimator, "feature_importances_", None)
    if native is not None and len(native) == len(feature_names):
        for name, value in zip(feature_names, native):
            rows.append({
                "feature": name,
                "importance_type": "native_model_importance",
                "importance_mean": float(value),
                "importance_std": np.nan,
                "model": context["model"],
            })

    # SHAP is optional at import time but listed in requirements. We explain a
    # capped sample using only the final, chronological validation fold.
    try:
        import shap  # type: ignore
        transformer = estimator[:-1]
        x_test_array = np.asarray(transformer.transform(x_test), dtype=float)
        x_train_array = np.asarray(transformer.transform(context["x_train"]), dtype=float)
        background = x_train_array[: min(80, len(x_train_array))]
        explain = x_test_array[: min(150, len(x_test_array))]
        try:
            explainer = shap.TreeExplainer(final_estimator, data=background)
            shap_values = explainer.shap_values(explain)
        except Exception:
            explainer = shap.Explainer(final_estimator, background)
            shap_values = explainer(explain).values
        if isinstance(shap_values, list):
            shap_values = shap_values[-1]
        shap_array = np.asarray(shap_values)
        if shap_array.ndim == 3:
            shap_array = shap_array[:, :, -1]
        mean_abs = np.nanmean(np.abs(shap_array), axis=0)
        if len(mean_abs) == len(feature_names):
            for name, value in zip(feature_names, mean_abs):
                rows.append({
                    "feature": name,
                    "importance_type": "shap_mean_abs",
                    "importance_mean": float(value),
                    "importance_std": np.nan,
                    "model": context["model"],
                })
            metadata["shap_status"] = "completed on up to 150 validation rows"
        else:
            metadata["shap_status"] = f"shape inesperada: {shap_array.shape}"
    except Exception as exc:
        metadata["shap_status"] = f"not_available_or_failed: {type(exc).__name__}: {exc}"
    return pd.DataFrame(rows), metadata


def run_walk_forward(
    features: pd.DataFrame,
    targets: pd.DataFrame,
    prices: pd.DataFrame,
    cost_bps: float = 5.0,
    n_splits: int = 5,
) -> dict[str, Any]:
    """Compare classifiers/regressors using only expanding chronological folds."""
    feature_names = [name for name in MODEL_FEATURES if name in features.columns and features[name].notna().any()]
    if not feature_names:
        raise ValueError("No hay features utilizables para machine learning.")
    x_all = features[feature_names].replace([np.inf, -np.inf], np.nan)
    specs = model_specs()
    metric_records: list[dict[str, Any]] = []
    fold_records: list[dict[str, Any]] = []
    prediction_records: list[dict[str, Any]] = []
    backtest_records: list[dict[str, Any]] = []
    backtest_curves: dict[str, pd.DataFrame] = {}
    importance_contexts: dict[str, dict[str, Any]] = {}
    model_status: list[dict[str, Any]] = []

    for spec in specs:
        for task in ("classification", "regression"):
            supported = task in spec.tasks
            model_status.append({
                "model": spec.name,
                "task": task,
                "available": bool(spec.available and supported),
                "status": (
                    spec.status if not spec.available else
                    "available" if supported else
                    f"not applicable: supports {', '.join(spec.tasks)}"
                ),
            })

    for horizon in (1, 5):
        target = targets[f"forward_return_{horizon}d"]
        valid = target.notna() & x_all.notna().all(axis=1)
        x = x_all.loc[valid].copy()
        y_return = target.loc[valid].astype(float)
        dates = x.index
        if len(x) < max(200, n_splits * 20):
            raise ValueError(f"Muestra insuficiente para CV del horizonte {horizon}d: {len(x)} filas.")
        splitter = TimeSeriesSplit(n_splits=n_splits, gap=horizon)
        splits = list(splitter.split(x))
        if not splits:
            raise ValueError("TimeSeriesSplit no generó pliegues.")
        y_class = (y_return.to_numpy() > 0).astype(int)

        for task in ("classification", "regression"):
            y = y_class if task == "classification" else y_return.to_numpy()
            for spec in specs:
                if task not in spec.tasks or not spec.available:
                    status = (
                        spec.status if not spec.available else
                        f"not applicable: supports {', '.join(spec.tasks)}"
                    )
                    metric_records.append({
                        "task": task,
                        "horizon": horizon,
                        "model": spec.name,
                        "status": status,
                        "oos_observations": 0,
                        "accuracy": np.nan,
                        "precision": np.nan,
                        "recall": np.nan,
                        "f1": np.nan,
                        "roc_auc": np.nan,
                        "sharpe": np.nan,
                        "cagr": np.nan,
                        "max_drawdown": np.nan,
                    })
                    continue
                prediction = np.full(len(x), np.nan, dtype=float)
                probability = np.full(len(x), np.nan, dtype=float) if task == "classification" else None
                last_fold_context = None
                fit_failed: str | None = None
                for fold_number, (train_indices, test_indices) in enumerate(splits, start=1):
                    fold_model = _pipeline(spec, task)
                    x_train = x.iloc[train_indices]
                    x_test = x.iloc[test_indices]
                    y_train = y[train_indices]
                    y_test = y[test_indices]
                    try:
                        with warnings.catch_warnings():
                            warnings.simplefilter("ignore")
                            fold_model.fit(x_train, y_train)
                        if task == "classification":
                            fold_probability = _positive_probability(fold_model, x_test)
                            probability[test_indices] = fold_probability
                            prediction[test_indices] = (fold_probability >= 0.5).astype(int)
                            fold_metrics = _classification_metrics(y_test, fold_probability)
                        else:
                            fold_prediction = np.asarray(fold_model.predict(x_test), dtype=float)
                            prediction[test_indices] = fold_prediction
                            fold_metrics = _regression_metrics(y_test, fold_prediction)
                        fold_records.append({
                            "task": task,
                            "horizon": horizon,
                            "model": spec.name,
                            "fold": fold_number,
                            "train_n": int(len(train_indices)),
                            "test_n": int(len(test_indices)),
                            "train_end": dates[train_indices[-1]].date().isoformat(),
                            "test_start": dates[test_indices[0]].date().isoformat(),
                            "test_end": dates[test_indices[-1]].date().isoformat(),
                            **fold_metrics,
                        })
                        if task == "classification" and horizon == 1 and fold_number == len(splits):
                            last_fold_context = {
                                "estimator": fold_model,
                                "x_train": x_train,
                                "x_test": x_test,
                                "y_test": y_test,
                                "model": spec.name,
                                "fold": fold_number,
                                "test_start": dates[test_indices[0]].date().isoformat(),
                                "test_end": dates[test_indices[-1]].date().isoformat(),
                            }
                    except Exception as exc:
                        fit_failed = f"{type(exc).__name__}: {exc}"
                        fold_records.append({
                            "task": task,
                            "horizon": horizon,
                            "model": spec.name,
                            "fold": fold_number,
                            "train_n": int(len(train_indices)),
                            "test_n": int(len(test_indices)),
                            "train_end": dates[train_indices[-1]].date().isoformat(),
                            "test_start": dates[test_indices[0]].date().isoformat(),
                            "test_end": dates[test_indices[-1]].date().isoformat(),
                            "status": f"fit failed: {fit_failed}",
                        })
                        break
                valid_oof = np.isfinite(prediction)
                if not valid_oof.any():
                    metric_records.append({
                        "task": task,
                        "horizon": horizon,
                        "model": spec.name,
                        "status": f"fit failed: {fit_failed or 'no OOF predictions'}",
                        "oos_observations": 0,
                        "accuracy": np.nan,
                        "precision": np.nan,
                        "recall": np.nan,
                        "f1": np.nan,
                        "roc_auc": np.nan,
                        "sharpe": np.nan,
                        "cagr": np.nan,
                        "max_drawdown": np.nan,
                    })
                    continue
                actual = y[valid_oof]
                if task == "classification":
                    p = probability[valid_oof]
                    model_metrics = _classification_metrics(actual, p)
                    signals = _classification_position(p)
                    export_pred = p
                    direction_prediction = np.where(p >= 0.5, 1.0, -1.0)
                    full_signal = pd.Series(np.nan, index=features.index, dtype=float)
                    full_signal.loc[dates[valid_oof]] = signals
                    if horizon == 1:
                        full_direction_prediction = pd.Series(np.nan, index=features.index, dtype=float)
                        full_direction_prediction.loc[dates[valid_oof]] = direction_prediction
                    for date, truth, value, prob in zip(dates[valid_oof], actual, direction_prediction, p):
                        prediction_records.append({
                            "date": date.date().isoformat(),
                            "task": task,
                            "horizon": horizon,
                            "model": spec.name,
                            "actual": int(truth),
                            "prediction": int(value),
                            "probability_up": float(prob),
                        })
                else:
                    pred = prediction[valid_oof]
                    model_metrics = _regression_metrics(actual, pred)
                    signals = np.sign(pred)
                    export_pred = pred
                    full_signal = pd.Series(np.nan, index=features.index, dtype=float)
                    full_signal.loc[dates[valid_oof]] = signals
                    for date, truth, value in zip(dates[valid_oof], actual, pred):
                        prediction_records.append({
                            "date": date.date().isoformat(),
                            "task": task,
                            "horizon": horizon,
                            "model": spec.name,
                            "actual": float(truth),
                            "prediction": float(value),
                            "probability_up": np.nan,
                        })

                if task == "classification":
                    evaluation_start = dates[np.flatnonzero(valid_oof)[0]]
                else:
                    evaluation_start = dates[np.flatnonzero(valid_oof)[0]]
                strategy_name = f"{spec.name}_{task}_{horizon}d"
                bt, curve = backtest_positions(
                    prices, full_signal.fillna(0.0), evaluation_start=evaluation_start,
                    cost_bps=cost_bps, name=strategy_name, holding_horizon=horizon,
                )
                backtest_curves[strategy_name] = curve
                metric_records.append({
                    "task": task,
                    "horizon": horizon,
                    "model": spec.name,
                    "status": "ok" if fit_failed is None else f"partial fit failed: {fit_failed}",
                    **model_metrics,
                    "sharpe": bt.get("sharpe", np.nan),
                    "cagr": bt.get("cagr", np.nan),
                    "max_drawdown": bt.get("max_drawdown", np.nan),
                    "strategy_total_return": bt.get("total_return", np.nan),
                    "strategy_exposure": bt.get("exposure", np.nan),
                    "strategy_trades": bt.get("trades", np.nan),
                    "cost_bps_one_way": cost_bps,
                    "cv_method": f"TimeSeriesSplit expanding, n_splits={n_splits}, gap={horizon}",
                })
                backtest_records.append({
                    "strategy": f"{spec.name}_{task}_{horizon}d",
                    "task": task,
                    "horizon": horizon,
                    "model": spec.name,
                    **bt,
                })
                if task == "classification" and horizon == 1 and last_fold_context is not None:
                    importance_contexts[spec.name] = last_fold_context

        # Add a same-window passive benchmark for each horizon. The first
        # test-fold start is identical across models/tasks for this horizon.
        first_start = dates[splits[0][1][0]]
        benchmark_name = f"buy_and_hold_{horizon}d_window"
        benchmark_values = buy_and_hold_metrics(prices, evaluation_start=first_start)
        backtest_records.append({
            **benchmark_values,
            "strategy": benchmark_name,
            "task": "benchmark",
            "horizon": horizon,
            "model": "Buy & Hold",
        })
        benchmark_price = prices["open"].where(prices["open"].notna(), prices["close"]).astype(float)
        benchmark_return = benchmark_price.pct_change()
        benchmark_return = benchmark_return.loc[benchmark_return.index >= first_start].dropna()
        benchmark_equity = (1.0 + benchmark_return).cumprod()
        backtest_curves[benchmark_name] = pd.DataFrame({
            "market_return": benchmark_return,
            "gross_return": benchmark_return,
            "transaction_cost": 0.0,
            "net_return": benchmark_return,
            "equity": benchmark_equity,
            "drawdown": benchmark_equity / benchmark_equity.cummax().clip(lower=1.0) - 1.0,
        })

    # Explain the best horizon-1 classifier on its last chronological fold.
    one_day_rows = [
        row for row in metric_records
        if row.get("task") == "classification"
        and row.get("horizon") == 1
        and (row.get("status") == "ok" or str(row.get("status", "")).startswith("partial fit failed"))
        and np.isfinite(row.get("roc_auc", np.nan))
    ]
    best_model = max(one_day_rows, key=lambda row: row["roc_auc"])["model"] if one_day_rows else None
    importance, shap_status = _feature_importance(importance_contexts.get(best_model), feature_names) if best_model else (pd.DataFrame(), {"status": "not_run", "reason": "No classifier ROC AUC calculable."})

    return {
        "metrics": pd.DataFrame(metric_records),
        "fold_metrics": pd.DataFrame(fold_records),
        "predictions": pd.DataFrame(prediction_records),
        "backtests": pd.DataFrame(backtest_records),
        "backtest_curves": backtest_curves,
        "feature_importance": importance,
        "shap_status": pd.DataFrame([shap_status]),
        "model_status": pd.DataFrame(model_status),
        "feature_names": feature_names,
        "best_classifier_1d": best_model,
    }
