"""Serialization utilities for SubscriptionNode."""

from __future__ import annotations

from dataclasses import asdict, fields
from typing import Any

from models.node import SubscriptionNode


def node_to_dict(node: SubscriptionNode) -> dict[str, Any]:
    """Convert a SubscriptionNode to a dictionary for serialization.
    
    Args:
        node: The SubscriptionNode to convert.
        
    Returns:
        Dictionary representation of the node.
    """
    return asdict(node)


def dict_to_node(data: dict[str, Any]) -> SubscriptionNode:
    """Convert a dictionary back to a SubscriptionNode.
    
    Args:
        data: Dictionary representation of a node.
        
    Returns:
        A reconstructed SubscriptionNode.
        
    Raises:
        ValueError: If the dictionary is missing required fields or has invalid types.
    """
    required_fields = {"protocol", "host", "port"}
    missing = required_fields - set(data.keys())
    if missing:
        raise ValueError(f"Missing required fields for SubscriptionNode: {missing}")
    
    # Extract only valid fields from data
    valid_fields = {f.name for f in fields(SubscriptionNode)}
    filtered_data = {k: v for k, v in data.items() if k in valid_fields}
    
    try:
        return SubscriptionNode(**filtered_data)
    except TypeError as exc:
        raise ValueError(f"Invalid data for SubscriptionNode: {exc}") from exc


def nodes_to_dicts(nodes: list[SubscriptionNode]) -> list[dict[str, Any]]:
    """Convert a list of SubscriptionNodes to dictionaries.
    
    Args:
        nodes: List of SubscriptionNodes.
        
    Returns:
        List of dictionary representations.
    """
    return [node_to_dict(node) for node in nodes]


def dicts_to_nodes(dicts: list[dict[str, Any]]) -> list[SubscriptionNode]:
    """Convert a list of dictionaries to SubscriptionNodes.
    
    Args:
        dicts: List of dictionary representations.
        
    Returns:
        List of reconstructed SubscriptionNodes.
    """
    nodes = []
    for d in dicts:
        try:
            nodes.append(dict_to_node(d))
        except ValueError:
            # Skip invalid entries
            pass
    return nodes
