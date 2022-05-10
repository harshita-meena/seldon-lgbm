from typing import Dict, Iterable

import numpy as np


class Dummy:
    """
    Model template. You can load your model parameters in __init__ from a location accessible at runtime
    This is a Layer 2 file (ie. modelset-specific, but parametrizable by model (by setting MODEL_GCS_LOCATION, or something similar))
    """

    def __init__(self) -> None:
        """
        This is a method for any initialization that happens only once, for example downloading a model binary, etc
        """

    def load(self) -> None:
        """
        This is a method for any worker-level initialization, like loading the model
        """

    def predict(self, X: np.ndarray, features_names: Iterable[str]) -> np.ndarray:
        """
        Return a prediction.

        Parameters
        ----------
        X : array-like
        feature_names : array of feature names (optional)
        """

        return X

    def metadata(self) -> Dict:
        return {
            "name": "my-model-name",
            "versions": ["my-model-version-01"],
            "platform": "seldon",
            "inputs": [{"name": "input", "datatype": "INT64", "shape": [1, 2]}],
            "outputs": [{"name": "output", "datatype": "INT64", "shape": [1, 2]}],
            "custom": {"author": "seldon-dev"},
        }
