#!/usr/bin/env python3
"""
Shared API Client for Spotify Data Platform APIs

Provides simple HTTP clients for:
- data-endpoints-service v3
- partition-status-service
- lineage-service

No authentication required for read operations from internal network.
"""

from typing import Any

import requests


class DataEndpointClient:
    """Client for data-endpoints-service v3 API."""

    BASE_URL = "https://data-endpoints-service.spotify.net/v3"

    def get_endpoint(self, endpoint_id: str) -> dict[str, Any]:
        """Get endpoint metadata including schema, retention, SLO config."""
        response = requests.get(
            f"{self.BASE_URL}/endpoints/{endpoint_id}",
            timeout=30
        )
        response.raise_for_status()
        return response.json()

    def search_endpoints(
        self,
        storage_uri_pattern: str | None = None,
        owner: str | None = None,
        limit: int = 100
    ) -> list[dict[str, Any]]:
        """Search for endpoints by storage URI pattern or owner."""
        params: dict[str, str | int] = {"limit": limit}
        if storage_uri_pattern:
            params["storageUriPatternGlob"] = storage_uri_pattern
        if owner:
            params["owner"] = owner

        response = requests.get(
            f"{self.BASE_URL}/endpoints",
            params=params,
            timeout=30
        )
        response.raise_for_status()
        return response.json().get("endpoints", [])


class PartitionStatusClient:
    """Client for partition-status-service API."""

    BASE_URL = "http://data-status-service.spotify.net:8080/v0"

    def get_statuses(
        self,
        endpoint_id: str,
        partition_min: str | None = None,
        partition_max: str | None = None,
        state: str | None = None,
        limit: int = 100
    ) -> list[dict[str, Any]]:
        """Get partition statuses for an endpoint.

        Args:
            endpoint_id: The data endpoint ID
            partition_min: Min partition date (ISO 8601)
            partition_max: Max partition date (ISO 8601)
            state: Filter by state (OK, WARNING, ERROR)
            limit: Maximum results to return
        """
        params: dict[str, str | int] = {"endpoint": endpoint_id, "limit": limit}
        if partition_min:
            params["partition_min"] = partition_min
        if partition_max:
            params["partition_max"] = partition_max
        if state:
            params["state"] = state

        response = requests.get(
            f"{self.BASE_URL}/statuses",
            params=params,
            timeout=30
        )
        response.raise_for_status()
        return response.json()

    def get_latest_status(self, endpoint_id: str) -> dict[str, Any] | None:
        """Get the most recent partition status."""
        statuses = self.get_statuses(endpoint_id, limit=1)
        return statuses[0] if statuses else None


class LineageClient:
    """Client for lineage-service API."""

    BASE_URL = "http://lineage-service.spotify.net:8080/v2"

    def get_upstream(
        self,
        endpoint_id: str,
        partition: str | None = None
    ) -> list[dict[str, Any]]:
        """Get upstream dependencies for an endpoint.

        Args:
            endpoint_id: The data endpoint ID
            partition: Optional partition date (e.g., "2025-01-22")
        """
        params: dict[str, str] = {}
        if partition:
            params["partition"] = partition

        response = requests.get(
            f"{self.BASE_URL}/dataEndpoints/{endpoint_id}/upstream",
            params=params,
            timeout=30
        )
        response.raise_for_status()
        return response.json()

    def get_downstream(
        self,
        endpoint_id: str,
        partition: str | None = None
    ) -> list[dict[str, Any]]:
        """Get downstream consumers for an endpoint.

        Args:
            endpoint_id: The data endpoint ID
            partition: Optional partition date
        """
        params: dict[str, str] = {}
        if partition:
            params["partition"] = partition

        response = requests.get(
            f"{self.BASE_URL}/dataEndpoints/{endpoint_id}/downstream",
            params=params,
            timeout=30
        )
        response.raise_for_status()
        return response.json()


def create_clients() -> dict[str, DataEndpointClient | PartitionStatusClient | LineageClient]:
    """Create all API clients."""
    return {
        "endpoints": DataEndpointClient(),
        "status": PartitionStatusClient(),
        "lineage": LineageClient()
    }
