from typing import Type, Dict, Optional
from autosoc_response.executors.base import BaseExecutor
from autosoc_response.executors.mock_firewall import MockFirewallExecutor
from autosoc_response.executors.quarantine import FileQuarantineExecutor
from autosoc_response.executors.keycloak import KeycloakDisableExecutor

_EXECUTOR_REGISTRY: Dict[str, Type[BaseExecutor]] = {
    "mock_firewall": MockFirewallExecutor,
    "file_quarantine": FileQuarantineExecutor,
    "keycloak_disable": KeycloakDisableExecutor,
    # increase monitoring might just be an internal API call or simulation
    "simulation_only": BaseExecutor # A simple pass-through if needed, but usually we just use simulation mode
}

def get_executor(name: str, target: str, arguments: dict = None) -> Optional[BaseExecutor]:
    executor_cls = _EXECUTOR_REGISTRY.get(name)
    if not executor_cls:
        return None
    return executor_cls(target, arguments)
