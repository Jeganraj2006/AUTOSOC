"""Stable prediction request identities shared by API and worker paths."""

from __future__ import annotations

import hashlib
import json
from typing import Iterable


def prediction_input_fingerprint(
    *,
    incident_id: object,
    model_name: str,
    model_version: str,
    attack_version: str,
    observed_techniques: Iterable[object],
) -> str:
    """Return a durable identity for one logical model input.

    The ordered observed-technique sequence is intentional: sequence order is an
    input to the Markov model.  JSON canonicalisation makes retries and concurrent
    deliveries produce the same key without relying on process-local state.
    """
    payload = {
        "attack_version": attack_version,
        "incident_id": str(incident_id),
        "model_name": model_name,
        "model_version": model_version,
        "observed_techniques": [str(technique) for technique in observed_techniques],
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
