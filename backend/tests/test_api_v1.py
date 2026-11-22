"""OpenAPI contract tests for the versioned FastAPI surface."""

from main import app


def test_versioned_core_routes_are_registered():
    paths = app.openapi()["paths"]

    assert "/api/v1/health" in paths
    assert "/api/v1/documents/upload" in paths
    assert "/api/v1/chat" in paths
    assert "/api/v1/conversations/clear" in paths
    assert "/api/v1/workspaces/{workspace_id}/status" in paths
    assert "/api/v1/workspaces/{workspace_id}/documents/{document_id}" in paths


def test_legacy_routes_remain_available_during_migration():
    paths = app.openapi()["paths"]

    assert "/health" in paths
    assert "/upload" in paths
    assert "/chat" in paths
    assert "/status" in paths


def test_analysis_api_is_mounted_under_both_prefixes():
    paths = app.openapi()["paths"]

    assert "/api/analysis/document" in paths
    assert "/api/v1/analysis/document" in paths


def test_upload_response_contract_exposes_document_and_workspace_ids():
    schema = app.openapi()
    operation = schema["paths"]["/api/v1/documents/upload"]["post"]
    response_ref = operation["responses"]["200"]["content"]["application/json"]["schema"]["$ref"]

    response_name = response_ref.rsplit("/", 1)[-1]
    properties = schema["components"]["schemas"][response_name]["properties"]

    assert "document_id" in properties
    assert "workspace_id" in properties
