from __future__ import annotations

import numpy as np


def regression_metrics(y_true, y_pred) -> dict:
    yt = np.asarray(y_true, dtype=float)
    yp = np.asarray(y_pred, dtype=float)
    mask = np.isfinite(yt) & np.isfinite(yp)
    if mask.sum() == 0:
        return {"mae": None, "rmse": None, "mape": None}
    yt = yt[mask]
    yp = yp[mask]
    err = yp - yt
    nonzero = np.abs(yt) > 1e-12
    return {
        "mae": float(np.mean(np.abs(err))),
        "rmse": float(np.sqrt(np.mean(err**2))),
        "mape": float(np.mean(np.abs(err[nonzero] / yt[nonzero]))) if nonzero.any() else None,
    }
