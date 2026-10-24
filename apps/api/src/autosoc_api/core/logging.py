import logging
import sys

def setup_logging(log_level: str = "INFO") -> None:
    """Configures structured logging foundation."""
    
    logger = logging.getLogger("autosoc_api")
    
    # Do not reconfigure if already configured
    if logger.handlers:
        return
        
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    # Prevent propagation to root logger
    logger.propagate = False

def get_logger(module_name: str) -> logging.Logger:
    return logging.getLogger(f"autosoc_api.{module_name}")
