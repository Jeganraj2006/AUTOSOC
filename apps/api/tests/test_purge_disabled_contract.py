"""Contract guard: destructive bulk purge must remain unavailable."""
import ast
from pathlib import Path


def test_bulk_purge_has_no_database_deletion_logic():
    endpoint = Path(__file__).resolve().parents[1] / 'src/autosoc_api/api/v1/endpoints/system.py'
    tree = ast.parse(endpoint.read_text(encoding='utf-8'))
    funcs = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == 'purge_all_database_records']
    assert len(funcs) == 1
    source = ast.get_source_segment(endpoint.read_text(encoding='utf-8'), funcs[0])
    assert 'HTTP_410_GONE' in source
    assert 'delete(' not in source and 'TRUNCATE' not in source and 'commit(' not in source
