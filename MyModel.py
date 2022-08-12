import os
from typing import Dict, Iterable

import joblib
import numpy as np
from google.protobuf import json_format
from seldon_core.proto import prediction_pb2
from seldon_core.utils import array_to_grpc_datadef, array_to_rest_datadef, get_data_from_proto


class MyModel:
    """
    Model template. You can load your model parameters in __init__ from a location accessible at runtime
    This is a Layer 2 file (ie. modelset-specific, but parametrizable by model (by setting MODEL_GCS_LOCATION, or something similar))
    """

    def __init__(self) -> None:
        """
        This is a method for any initialization that happens only once, for example downloading a model binary, etc
        """
        pass

    def load(self) -> None:
        """
        This is a method for any worker-level initialization, like loading the model
        """
        self.model = joblib.load(f"/app/lgb.pkl")

    def predict(self, X, feature_names = None) -> np.ndarray:
        """
        Return a prediction.

        Parameters
        ----------
        request: array-like
        feature_names : array of feature names (optional)
        """
        output = self.model.predict(X, predict_disable_shape_check=True)
        return output

    def metadata(self) -> Dict:
        return {
            "name": "my-model-name",
            "versions": ["my-model-version-01"],
            "platform": "seldon",
            "inputs": [{"name": "input", "datatype": "INT64", "shape": [1, 2]}],
            "outputs": [{"name": "output", "datatype": "INT64", "shape": [1, 2]}],
            "custom": {"model": "MYMODEL"},
        }
