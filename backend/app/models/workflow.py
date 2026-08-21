"""Workflow model for multi-step API execution."""
from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base


class Workflow(Base):
    """Workflow configuration for chaining multiple API calls."""
    
    __tablename__ = "workflows"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic information
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    work_type = Column(String(50), nullable=False, index=True)  # text-to-image, text-to-video, etc.
    
    # Workflow structure (stored as JSON)
    nodes = Column(JSON, nullable=False, default=[])  # List of workflow nodes
    edges = Column(JSON, nullable=False, default=[])  # List of connections between nodes
    viewport = Column(JSON, nullable=True)  # Canvas viewport position for editor
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(Integer, ForeignKey("admins.id"), nullable=True)
    
    # Relationships
    models = relationship("GenerationModel", backref="workflow")
    
    def to_dict(self):
        """Convert workflow to dictionary format."""
        import json
        
        # Safely handle JSON fields
        nodes = []
        edges = []
        viewport = None
        
        try:
            if self.nodes is not None:
                # If nodes is already a list/dict, use it directly
                if isinstance(self.nodes, (list, dict)):
                    nodes = self.nodes
                # If it's a string, try to parse it
                elif isinstance(self.nodes, str):
                    nodes = json.loads(self.nodes) if self.nodes else []
        except (json.JSONDecodeError, TypeError, ValueError) as e:
            # Log error but continue with empty list
            import logging
            logging.warning(f"Error parsing workflow nodes for workflow {self.id}: {e}")
            nodes = []
        
        try:
            if self.edges is not None:
                if isinstance(self.edges, (list, dict)):
                    edges = self.edges
                elif isinstance(self.edges, str):
                    edges = json.loads(self.edges) if self.edges else []
        except (json.JSONDecodeError, TypeError, ValueError) as e:
            import logging
            logging.warning(f"Error parsing workflow edges for workflow {self.id}: {e}")
            edges = []
        
        try:
            if self.viewport is not None:
                if isinstance(self.viewport, dict):
                    viewport = self.viewport
                elif isinstance(self.viewport, str):
                    viewport = json.loads(self.viewport) if self.viewport else None
        except (json.JSONDecodeError, TypeError, ValueError) as e:
            import logging
            logging.warning(f"Error parsing workflow viewport for workflow {self.id}: {e}")
            viewport = None
        
        return {
            "id": self.id,
            "name": self.name or "",
            "description": self.description or "",
            "work_type": self.work_type or "",
            "nodes": nodes,
            "edges": edges,
            "viewport": viewport,
            "is_active": self.is_active if self.is_active is not None else True,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by": self.created_by,
        }
    
    def to_full_dict(self):
        """Convert to full dictionary with all fields."""
        return self.to_dict()
    
    def extract_default_values_for_params_config(self):
        """
        Extract default values from workflow nodes (promptPreset, imageInput, etc.)
        and return them in params_config format.
        
        Only extracts values from input nodes (image_default, video_default) that are mapped
        to user-visible parameters. Does NOT extract values from API call outputs.
        
        Returns a dict like: {"prompt": {"default": "..."}, "image_default": {"default": "..."}}
        """
        params_config = {}
        
        if not self.nodes:
            return params_config
        
        # Build a map of node_id -> node for quick lookup
        node_map = {node.get("id"): node for node in self.nodes}
        
        # First, find all input/preset nodes and their values
        input_nodes = {}
        for node in self.nodes:
            node_type = node.get("type")
            node_data = node.get("data", {})
            node_value = node_data.get("value")
            
            if node_type == "prompt_default_hidden" and node_value:
                input_nodes[node.get("id")] = {"type": "prompt", "value": node_value}
            elif node_type == "image_default" and node_value:
                input_nodes[node.get("id")] = {"type": "image", "value": node_value}
            elif node_type == "video_default" and node_value:
                input_nodes[node.get("id")] = {"type": "video", "value": node_value}
        
        # Find all API call nodes and their mappings
        for node in self.nodes:
            if node.get("type") != "api_call":
                continue
            
            node_data = node.get("data", {})
            param_mappings = node_data.get("param_mappings", {})
            params_visibility = node_data.get("params_visibility", {})
            
            # For each parameter mapping, check if it points to an input node (not API call output)
            for param_name, mapping in param_mappings.items():
                # Check visibility: only extract defaults for visible parameters (user input)
                # System preset parameters (params_visibility[param_name] == False) should not be extracted
                is_visible = params_visibility.get(param_name, True)
                if not is_visible:
                    # Skip system preset parameters
                    continue
                
                # Only extract if mapping points to an input node (image_default, video_default)
                # Do NOT extract if mapping points to another API call output (e.g., $.apiCall_xxx.output.image)
                if mapping.startswith("$."):
                    parts = mapping.split(".")
                    if len(parts) >= 2:
                        source_node_id = parts[1]
                        source_node = node_map.get(source_node_id)
                        
                        if source_node:
                            source_type = source_node.get("type")
                            source_data = source_node.get("data", {})
                            source_value = source_data.get("value")
                            
                            # Only extract from input nodes (image_default, video_default)
                            # Skip API call nodes (api_call) - these are intermediate outputs, not user inputs
                            if source_type == "image_default" and source_value:
                                # Image input URL - only if visible
                                if param_name not in params_config:
                                    params_config[param_name] = {}
                                params_config[param_name]["default"] = source_value
                            
                            elif source_type == "video_default" and source_value:
                                # Video input URL - only if visible
                                if param_name not in params_config:
                                    params_config[param_name] = {}
                                params_config[param_name]["default"] = source_value
                            
                            # Skip if source is an API call node (intermediate output, not user input)
                            elif source_type == "api_call":
                                continue
                        
                        # Also check if mapping is to user_input but there's a corresponding input node
                        elif mapping.startswith("$.user_input."):
                            # Extract parameter name from user_input mapping (e.g., "$.user_input.image" -> "image")
                            user_param_name = mapping.replace("$.user_input.", "")
                            
                            # Find corresponding input node
                            # For image: look for image_default node
                            # For prompt: look for promptPreset node (but it's usually mapped directly)
                            if user_param_name == "image":
                                # Find imageInput node
                                for input_node_id, input_info in input_nodes.items():
                                    if input_info["type"] == "image":
                                        if param_name not in params_config:
                                            params_config[param_name] = {}
                                        params_config[param_name]["default"] = input_info["value"]
                                        break
            
            # Also check param_defaults directly (for imageInput/videoInput connections)
            # Only extract defaults for visible parameters that come from input nodes
            param_defaults = node_data.get("param_defaults", {})
            for param_name, default_value in param_defaults.items():
                if default_value:  # Only include non-empty defaults
                    # Check visibility: only extract defaults for visible parameters
                    is_visible = params_visibility.get(param_name, True)
                    if not is_visible:
                        continue
                    
                    # Check if this parameter is mapped to an input node (not API call output)
                    mapping = param_mappings.get(param_name, "")
                    should_extract = False
                    
                    if mapping.startswith("$."):
                        parts = mapping.split(".")
                        if len(parts) >= 2:
                            source_node_id = parts[1]
                            source_node = node_map.get(source_node_id)
                            if source_node:
                                source_type = source_node.get("type")
                                # Only extract if source is an input node, not an API call output
                                if source_type in ["image_default", "video_default"]:
                                    should_extract = True
                            elif mapping.startswith("$.user_input."):
                                # Check if there's a corresponding input node
                                user_param_name = mapping.replace("$.user_input.", "")
                                if user_param_name == "image" and any(info["type"] == "image" for info in input_nodes.values()):
                                    should_extract = True
                    
                    if should_extract:
                        if param_name not in params_config:
                            params_config[param_name] = {}
                        params_config[param_name]["default"] = default_value
        
        return params_config
    
    # Node types that only provide default values; not executed at runtime
    _DEFAULT_VALUE_NODE_TYPES = ("prompt_default_hidden", "image_default", "video_default", "media_list_default")

    def _get_default_from_edge(self, node_id: str, param_name: str, node_map: dict, edges: list):
        """
        Resolve default value for param_name from edges: if an edge connects a default-value node
        (prompt_default_hidden, image_default, video_default) to this api_call param, return that node's value.
        So default-value nodes are only used here to fill param default; no runtime resolution.
        """
        if not edges:
            return None
        for edge in edges:
            if edge.get("target") != node_id:
                continue
            th = edge.get("targetHandle") or ""
            param_handle = th.replace("input-", "", 1) if th.startswith("input-") else th
            if param_handle != param_name:
                continue
            source_id = edge.get("source")
            source_node = node_map.get(source_id) if source_id else None
            if not source_node or source_node.get("type") not in self._DEFAULT_VALUE_NODE_TYPES:
                continue
            val = source_node.get("data", {}).get("value")
            if val is not None:
                return val
        return None

    def get_user_visible_params(self):
        """
        Get all parameters that should be visible to users.
        Visibility and defaults come from workflow only (API params_visibility + edges to default-value nodes).
        Default-value nodes (prompt_default_hidden, image_default, video_default) are only used here to set param default;
        they are not executed at runtime.
        """
        visible_params = {}
        param_sources = {}  # Track which nodes each param comes from
        
        if not self.nodes:
            return visible_params
        
        node_map = {node.get("id"): node for node in self.nodes}
        edges = self.edges if self.edges is not None else []
        if isinstance(edges, str):
            try:
                import json
                edges = json.loads(edges) if edges else []
            except (TypeError, ValueError):
                edges = []
        if not isinstance(edges, list):
            edges = []
        
        # Import here to avoid circular dependency
        from .generation_model import APILibrary
        from .base import SessionLocal
        import json
        
        db = SessionLocal()
        try:
            for node in self.nodes:
                if node.get("type") != "api_call":
                    continue
                    
                api_id = node.get("api_id")
                if not api_id:
                    continue
                
                api = db.query(APILibrary).filter(APILibrary.id == api_id).first()
                if not api or not api.params_schema:
                    continue
                
                node_id = node.get("id", "")
                node_label = node.get("data", {}).get("label", "") or api.name or f"Node_{node_id}"
                params_visibility = node.get("data", {}).get("params_visibility", {})
                param_defaults = node.get("data", {}).get("param_defaults", {})
                
                # Add visible parameters from this node
                for param_name, param_def in api.params_schema.items():
                    # Check visibility (default to True if not specified)
                    is_visible = params_visibility.get(param_name, True)
                    if not is_visible:
                        continue
                    
                    # Default from edge (default-value node -> this param), else from param_defaults
                    param_def_with_default = param_def.copy() if isinstance(param_def, dict) else param_def
                    if isinstance(param_def_with_default, dict):
                        default_val = self._get_default_from_edge(node_id, param_name, node_map, edges)
                        if default_val is not None:
                            param_def_with_default["default"] = default_val
                        elif param_name in param_defaults:
                            param_def_with_default["default"] = param_defaults[param_name]
                    
                    # Check if this parameter already exists
                    if param_name in visible_params:
                        # Compare definitions (convert to JSON string for comparison)
                        existing_def = visible_params[param_name]
                        existing_def_str = json.dumps(existing_def, sort_keys=True)
                        new_def_str = json.dumps(param_def_with_default, sort_keys=True)
                        
                        if existing_def_str == new_def_str:
                            # Same definition: merge (keep existing, just track source)
                            if param_name not in param_sources:
                                param_sources[param_name] = []
                            param_sources[param_name].append(node_label)
                        else:
                            # Different definition: add prefix to distinguish
                            # Use node label or node ID as prefix
                            prefixed_name = f"{node_label}_{param_name}" if node_label else f"{node_id}_{param_name}"
                            # If prefix already exists, use node_id
                            if prefixed_name in visible_params:
                                prefixed_name = f"{node_id}_{param_name}"
                            
                            visible_params[prefixed_name] = param_def_with_default
                            # Store original name for reference
                            if prefixed_name not in param_sources:
                                param_sources[prefixed_name] = []
                            param_sources[prefixed_name].append(node_label)
                    else:
                        # New parameter: add it
                        visible_params[param_name] = param_def_with_default
                        param_sources[param_name] = [node_label]
        finally:
            db.close()
        
        return visible_params
