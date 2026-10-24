from __future__ import annotations

from typing import Any, Dict, List

import pandas as pd


# Features used by the anomaly detection model.
FEATURE_COLUMNS = [
    "source_port",
    "destination_port",
    "bytes",
    "packets",
    "duration",
    "protocol_encoded",
    "event_category_encoded",
]


def _to_number(value: Any, default: float = 0.0) -> float:
    """Safely convert a value to a number."""
    if value is None:
        return default

    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _encode_protocol(value: Any) -> float:
    """Convert common network protocols into numerical values."""
    if value is None:
        return 0.0

    protocol = str(value).strip().lower()

    protocol_map = {
        "tcp": 1.0,
        "udp": 2.0,
        "icmp": 3.0,
        "http": 4.0,
        "https": 5.0,
        "ssh": 6.0,
        "ftp": 7.0,
        "dns": 8.0,
    }

    return protocol_map.get(protocol, 0.0)


def _encode_category(value: Any) -> float:
    """Convert common security-event categories into numerical values."""
    if value is None:
        return 0.0

    category = str(value).strip().lower()

    category_map = {
        "network": 1.0,
        "authentication": 2.0,
        "malware": 3.0,
        "intrusion": 4.0,
        "endpoint": 5.0,
        "firewall": 6.0,
        "application": 7.0,
        "cloud": 8.0,
        "system": 9.0,
        "process_execution": 10.0,
        "credential_access": 11.0,
        "lateral_movement": 12.0,
        "data_exfiltration": 13.0,
    }

    return category_map.get(category, 0.0)


def event_to_features(event: Dict[str, Any]) -> Dict[str, float]:
    """
    Convert one normalized security event into ML features.
    """

    return {
        "source_port": _to_number(
            event.get("source_port", event.get("src_port"))
        ),
        "destination_port": _to_number(
            event.get("destination_port", event.get("dst_port"))
        ),
        "bytes": _to_number(
            event.get("bytes", event.get("byte_count"))
        ),
        "packets": _to_number(
            event.get("packets", event.get("packet_count"))
        ),
        "duration": _to_number(
            event.get("duration", event.get("duration_seconds"))
        ),
        "protocol_encoded": _encode_protocol(
            event.get("protocol")
        ),
        "event_category_encoded": _encode_category(
            event.get("event_category")
        ),
    }


def events_to_dataframe(events: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Convert multiple security events into a DataFrame
    suitable for the ML model.
    """

    if not events:
        return pd.DataFrame(columns=FEATURE_COLUMNS)

    feature_rows = [
        event_to_features(event)
        for event in events
    ]

    dataframe = pd.DataFrame(feature_rows)

    # Guarantee a consistent column order.
    dataframe = dataframe.reindex(
        columns=FEATURE_COLUMNS,
        fill_value=0.0,
    )

    # Replace invalid numerical values.
    dataframe = dataframe.replace(
        [float("inf"), float("-inf")],
        0.0,
    )

    dataframe = dataframe.fillna(0.0)

    return dataframe