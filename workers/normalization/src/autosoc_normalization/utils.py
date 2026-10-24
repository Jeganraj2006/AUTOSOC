import ipaddress
import re
from datetime import datetime, timezone
from typing import Optional, Tuple, Any

def parse_utc_timestamp(ts: Any) -> Tuple[Optional[datetime], str]:
    """
    Parses a timestamp into UTC datetime.
    Returns (datetime_obj, quality).
    """
    if not ts:
        return None, "invalid"
    
    if isinstance(ts, datetime):
        if ts.tzinfo is None:
            return ts.replace(tzinfo=timezone.utc), "inferred_timezone"
        return ts.astimezone(timezone.utc), "exact"
        
    if isinstance(ts, (int, float)):
        # Assume epoch seconds if reasonable, milliseconds if large
        try:
            if ts > 253402300799: # After year 9999
                ts = ts / 1000.0
            return datetime.fromtimestamp(ts, tz=timezone.utc), "exact"
        except (ValueError, OverflowError):
            return None, "invalid"
            
    if isinstance(ts, str):
        # Try ISO 8601
        try:
            # Handle Z timezone indicator
            if ts.endswith("Z"):
                ts = ts[:-1] + "+00:00"
            dt = datetime.fromisoformat(ts)
            if dt.tzinfo is None:
                return dt.replace(tzinfo=timezone.utc), "inferred_timezone"
            return dt.astimezone(timezone.utc), "exact"
        except ValueError:
            # Add more parsing logic for syslog here if necessary, or let parsers handle specific formats
            pass
            
    return None, "invalid"

def validate_ip(ip: Any) -> Optional[str]:
    """Validates and normalizes an IP address."""
    if not ip or not isinstance(ip, str):
        return None
    try:
        return str(ipaddress.ip_address(ip))
    except ValueError:
        return None

def validate_port(port: Any) -> Optional[int]:
    """Validates a port number."""
    try:
        port_int = int(port)
        if 0 <= port_int <= 65535:
            return port_int
    except (ValueError, TypeError):
        pass
    return None

def mask_sensitive_data(val: str) -> str:
    """Masks potential secrets in strings."""
    if not val:
        return val
    # Very basic credential masking (JWT, AWS keys, etc)
    # AWS AKIA
    val = re.sub(r'(?<![A-Z0-9])AKIA[A-Z0-9]{16}(?![A-Z0-9])', 'AKIA****************', val)
    # Bearer tokens
    val = re.sub(r'Bearer\s+[A-Za-z0-9\-\._~\+\/]+=*', 'Bearer [REDACTED]', val, flags=re.IGNORECASE)
    return val
