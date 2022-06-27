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

    def predict_raw(self, request, feature_names = None) -> np.ndarray:
        """
        Return a prediction.

        Parameters
        ----------
        request: array-like
        feature_names : array of feature names (optional)
        """
        if isinstance(request, dict) and "data" in request:
            output = self.model.predict(request["data"]["ndarray"], predict_disable_shape_check=True)
            return {"data": array_to_rest_datadef("ndarray", output)}
        elif isinstance(request, prediction_pb2.SeldonMessage):
            data = get_data_from_proto(request)
            output = self.model.predict(data, predict_disable_shape_check=True)
            return prediction_pb2.SeldonMessage(data=array_to_grpc_datadef("ndarray", output))
        else:
            raise RuntimeError("Received unexpected request format.")

    def handle_request_grpc(
        self, request: prediction_pb2.SeldonMessage
    ) -> prediction_pb2.SeldonMessage:
        data = json_format.MessageToDict(request.jsonData)
        embedding = data["embedding"]
        num_neighbors = int(data["num_neighbors"])
        distances, indices = self.loaded_index.search(
            np.array([np.array(embedding).astype(np.float32)]), num_neighbors
        )
        return prediction_pb2.SeldonMessage(
            data=array_to_grpc_datadef("ndarray", indices[0])
        )

    def metadata(self) -> Dict:
        return {
            "name": "my-model-name",
            "versions": ["my-model-version-01"],
            "platform": "seldon",
            "inputs": [{"name": "input", "datatype": "INT64", "shape": [1, 2]}],
            "outputs": [{"name": "output", "datatype": "INT64", "shape": [1, 2]}],
            "custom": {"model": "MYMODEL"},
        }
