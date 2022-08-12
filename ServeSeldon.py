import importlib
import os
import time
from typing import Dict, Iterable, List, Union

import numpy as np
import logging
from seldon_core.user_model import SeldonComponent
from seldon_core.proto import prediction_pb2
from seldon_core.utils import construct_response_json, get_meta_from_proto
from opentracing_instrumentation.request_context import get_current_span, span_in_context
from google.protobuf import json_format

# Dynamically import class name
class_name = os.environ.get("MODEL_NAME", "Dummy")
ApplicationLogic = getattr(importlib.import_module(class_name), class_name)
logger = logging.getLogger(__name__)


class ServeSeldon(ApplicationLogic, SeldonComponent):
    """
    This logic contains Seldon-specific details.
    This class inherits from the ApplicationLogic class and appropriately calls the init_once, init, predict, and metadata methods.
    It keeps the `MODEL_NAME`.py file server-agnostic and separates application and implementation logic
    This is a Layer 1 file (ie. corresponds to base serving image)
    """

    def __init__(self) -> None:

        super().__init__()

        self.model_name = self.metadata().get("name", "Model name unspecified")
        self.request_duration_ms = 0
        self.route = "NA"

    def predict(
        self, X: np.ndarray, feature_names: Iterable[str], meta: Dict = None
    ) -> Union[np.ndarray, List, str, bytes]:
        t0 = time.time()

        # Call predict from super class (ie. Application Logic layer )
        with self.tracing.tracer.start_span('Calling-mymodel-predict', child_of=get_current_span()) as span:
           with span_in_context(span):
              output = super().predict(X, feature_names)

        self.request_duration_ms = (time.time() - t0) * 1000
        return output

    def predict_raw(self, msg) -> Union[prediction_pb2.SeldonMessage, dict]:
        is_proto = isinstance(msg, prediction_pb2.SeldonMessage)

        t0 = time.time()
        # Call predict from super class (ie. Application Logic layer )
        with self.tracing.tracer.start_span('Calling-mymodel-predictraw', child_of=get_current_span()) as span:
           with span_in_context(span):
              output = super().predict_raw(msg)
        self.request_duration_ms = (time.time() - t0) * 1000

        if is_proto:
            self.route = "GRPC"
            # extend metrics meta in seldon msg
            meta_json = get_meta_from_proto(output)
            metrics = meta_json.get("metrics", [])
            metrics.extend(self.metrics())
            meta_json["metrics"] = metrics

            # extend tags, request path in output
            # TODO add any custom tags if needed

            metrics_meta = prediction_pb2.Meta()
            json_format.ParseDict(meta_json, metrics_meta)
            return prediction_pb2.SeldonMessage(data=output.data, meta=metrics_meta, status=output.status)
        else:
            self.route = "REST"
            return construct_response_json(self, False, msg, output, output.get("meta", None), self.metrics()) 


    def metrics(self) -> List[Dict]:
        return [
            {
                "type": "TIMER",
                "key": "seldon_run_time_histogram",
                # a timer which will add sum and count metrics - the "value" is expected to be in ms 
                # but the final recorded value on prometheus is in secs
                # https://github.com/SeldonIO/seldon-core/blob/master/python/seldon_core/metrics.py#L133
                "value": self.request_duration_ms,
                # TODO uncomment it once the bug fix is released by seldon-core
                "tags": {"service": self.model_name, 'route': self.route},
            },  
        ]

    def init_metadata(self) -> Dict:
        return self.metadata()

    def set_tracer(self, tracing) -> Dict:
        self.tracing = tracing
        logger.info("Tracing object init inside ServeSeldon.")
