"""
BuildWise-AI — Performance Service Wrapper

Re-exports the PerformancePredictionService from experiments.performance_prediction.service
for convenient top-level access within src and app modules.
"""
from experiments.performance_prediction.service import (
    PerformancePredictionService,
    get_performance_service,
    parse_specs_safely,
)

__all__ = [
    "PerformancePredictionService",
    "get_performance_service",
    "parse_specs_safely",
]
