"""Workflow execution engine for multi-step API calls."""
from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict, deque
from ..models.workflow import Workflow
from ..models.generation_model import APILibrary
from ..models.base import SessionLocal
from ..services.providers.factory import ProviderFactory
from ..services.param_mapper import ParamMapper
from ..utils.logger import logger


class WorkflowExecutor:
    """Execute workflows by chaining multiple API calls."""
    
    def __init__(self, db_session=None):
        self.db = db_session or SessionLocal()
        self.context: Dict[str, Any] = {}
        self.workflow: Optional[Workflow] = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if not hasattr(self, '_db_provided') or not self._db_provided:
            self.db.close()
    
    async def execute(
        self,
        workflow: Workflow,
        user_input: Dict[str, Any],
        work_id: int,
        webhook_url: str
    ) -> Dict[str, Any]:
        """
        Execute a workflow with user input.
        
        Args:
            workflow: Workflow to execute
            user_input: User-provided parameters
            work_id: Work ID for tracking
            webhook_url: Webhook URL for final result
            
        Returns:
            Dictionary with execution results
        """
        try:
            from .mock_generation_service import is_mock_generation_enabled, process_mock_generation
            if is_mock_generation_enabled():
                logger.info(f"[WorkflowExecutor] MOCK_AI_GENERATION enabled for work_id={work_id}")
                res = process_mock_generation(self.db, work_id)
                return {
                    "status": "submitted",
                    "prediction_id": f"mock_prediction_{work_id}",
                    "node_id": "mock_node",
                    "output": res.get("file_url")
                }

            # Store workflow for access in node execution
            self.workflow = workflow
            # Initialize context
            self.context = {
                "user_input": user_input,
                "work_id": work_id
            }
            
            # Add input node outputs to context. Default-value nodes (prompt_default_hidden, image_default, video_default)
            # are NOT executed here: their values are only used as param defaults (resolved from edges in
            # get_user_visible_params). At runtime we only need user_input + param_defaults; mappings to
            # those nodes resolve to None and we use preset (param_defaults).
            if workflow.nodes:
                _default_value_node_types = {"prompt_default_hidden", "image_default", "video_default", "media_list_default"}
                for node in workflow.nodes:
                    node_type = node.get("type")
                    node_id = node.get("id")
                    node_data = node.get("data", {})
                    if node_type in _default_value_node_types:
                        continue
                    if node_type == "prompt_input":
                        # Add promptInput node output to context (user input overrides workflow default)
                        ui = self.context.get("user_input") or {}
                        prompt_value = ui.get("prompt") or node_data.get("value", "")
                        self.context[node_id] = {
                            "output": {
                                "prompt": prompt_value
                            }
                        }
                    elif node_type == "param_input":
                        # Add paramInput node output to context
                        param_name = node_data.get("param_name", "param")
                        param_value = node_data.get("value", "")
                        self.context[node_id] = {
                            "output": {
                                param_name: param_value
                            }
                        }
            
            # Validate workflow
            if not workflow.nodes or len(workflow.nodes) == 0:
                raise ValueError("Workflow has no nodes")
            
            # Filter out invalid nodes (edges that might be in nodes array)
            valid_node_types = {'api_call', 'prompt_input', 'image_default', 'video_default', 'param_input', 'prompt_default_hidden', 'media_list_default'}
            valid_nodes = [
                node for node in workflow.nodes 
                if node.get("type") in valid_node_types
            ]
            
            if not valid_nodes:
                raise ValueError("Workflow has no valid nodes (only api_call, prompt_input, image_default, video_default, param_input, prompt_default_hidden, media_list_default are supported)")
            
            # For single node, execute directly
            if len(valid_nodes) == 1:
                # Create a temporary workflow with only valid nodes
                temp_workflow = type('TempWorkflow', (), {
                    'nodes': valid_nodes,
                    'edges': workflow.edges,
                    'work_type': workflow.work_type
                })()
                return await self._execute_single_node(temp_workflow, work_id, webhook_url)
            
            # For multiple nodes, use topological sort and chain execution
            return await self._execute_multi_node(workflow, work_id, webhook_url)
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {str(e)}")
            raise
    
    async def _execute_single_node(
        self,
        workflow: Workflow,
        work_id: int,
        webhook_url: str
    ) -> Dict[str, Any]:
        """Execute a single-node workflow."""
        # Filter out invalid nodes (edges that might be in nodes array)
        valid_node_types = {'api_call', 'prompt_input', 'image_default', 'video_default', 'param_input', 'prompt_default_hidden', 'media_list_default'}
        valid_nodes = [
            node for node in workflow.nodes 
            if node.get("type") in valid_node_types
        ]
        
        if not valid_nodes:
            raise ValueError("Workflow has no valid nodes")
        
        # Get the first valid node (should be api_call for execution)
        node = valid_nodes[0]
        
        if node.get("type") != "api_call":
            raise ValueError(f"Unsupported node type: {node.get('type')}. Only 'api_call' nodes can be executed.")
        
        api_id = node.get("api_id")
        if not api_id:
            raise ValueError("Node missing api_id")
        
        # Get API configuration
        api = self.db.query(APILibrary).filter(APILibrary.id == api_id).first()
        if not api:
            raise ValueError(f"API Library not found: {api_id}")
        
        # Resolve parameters
        node_data = node.get("data", {})
        # Use param_defaults (from frontend) as preset_params, fallback to preset_params for backward compatibility
        param_defaults = node_data.get("param_defaults", {})
        preset_params = node_data.get("preset_params", {})
        # Merge: param_defaults takes precedence, then preset_params
        merged_preset_params = {**preset_params, **param_defaults}
        param_mappings = node_data.get("param_mappings", {}).copy()  # Make a copy to avoid modifying original
        
        # Auto-map visible parameters to user_input if not manually mapped and not connected
        if api.params_schema and self.workflow:
            params_visibility = node_data.get("params_visibility", {})
            node_id = node.get("id")
            
            # Get edges that connect to this node's parameters
            connected_params = set()
            if self.workflow.edges:
                for edge in self.workflow.edges:
                    if edge.get("target") == node_id:
                        target_handle = edge.get("targetHandle", "")
                        # Extract parameter name from targetHandle (e.g., "input-prompt" -> "prompt")
                        if target_handle.startswith("input-"):
                            param_name = target_handle.replace("input-", "", 1)
                        else:
                            param_name = target_handle
                        if param_name:
                            connected_params.add(param_name)
            
            # Auto-map visible parameters that are not manually mapped and not connected
            for param_name, param_def in api.params_schema.items():
                # Skip if already has manual mapping
                if param_name in param_mappings:
                    continue
                
                # Skip if connected to another node
                if param_name in connected_params:
                    continue
                
                # Check if parameter is visible (default to True if not specified)
                is_visible = params_visibility.get(param_name, True)
                
                # Auto-map visible parameters to user_input
                if is_visible:
                    # Check if this parameter might have a prefixed version in user_input
                    # (e.g., if workflow has multiple nodes with same param name but different definitions)
                    node_label = node_data.get("label", "") or api.name or f"Node_{node_id}"
                    # Use node label as prefix, but fallback to original name if prefixed version doesn't exist
                    prefixed_name = f"{node_label}_{param_name}" if node_label else f"{node_id}_{param_name}"
                    
                    # Try prefixed name first, then fallback to original name
                    # This allows users to input either "seed" (if same definition) or "Node1_seed" (if different)
                    param_mappings[param_name] = f"$.user_input.{prefixed_name} || {param_name}"
                    logger.info(f"Auto-mapped visible parameter '{param_name}' to $.user_input.{prefixed_name} || {param_name} for node {node_id}")
        
        resolved_params = ParamMapper.resolve_params(
            param_mappings,
            merged_preset_params,
            self.context
        )
        
        # Extract prompt and negative_prompt
        prompt = resolved_params.pop("prompt", "")
        negative_prompt = resolved_params.pop("negative_prompt", None)
        
        # Determine work_type from API or use workflow work_type
        work_type = workflow.work_type
        
        # Get provider
        provider = ProviderFactory.get_provider(api.provider)
        
        # Use provider_model_id as model_id
        model_id = api.provider_model_id
        
        # Execute API call
        logger.info(f"Executing workflow node {node.get('id')} for work {work_id}")
        prediction_id = await provider.create_generation(
            work_id=work_id,
            work_type=work_type,
            model_id=model_id,
            prompt=prompt,
            negative_prompt=negative_prompt,
            params=resolved_params,
            webhook_url=webhook_url
        )
        
        return {
            "status": "started",
            "prediction_id": prediction_id,
            "node_id": node.get("id")
        }
    
    async def _execute_multi_node(
        self,
        workflow: Workflow,
        work_id: int,
        webhook_url: str
    ) -> Dict[str, Any]:
        """
        Execute a multi-node workflow by starting only the first node(s).
        Subsequent nodes will be triggered via webhook callbacks.
        """
        # Filter out invalid nodes (edges that might be in nodes array)
        valid_node_types = {'api_call', 'prompt_input', 'image_default', 'video_default', 'param_input', 'prompt_default_hidden', 'media_list_default'}
        valid_nodes = [
            node for node in workflow.nodes 
            if node.get("type") in valid_node_types
        ]
        
        if not valid_nodes:
            raise ValueError("Workflow has no valid nodes (only api_call, prompt_input, image_default, video_default, param_input, prompt_default_hidden are supported)")
        
        # Build execution graph
        execution_order = self._topological_sort(valid_nodes, workflow.edges)
        
        if not execution_order:
            raise ValueError("Workflow has circular dependencies or invalid structure")
        
        # For multi-node workflows, we only start the first node(s) (nodes with no dependencies)
        # Only api_call nodes can be executed. Input nodes are data sources, not executable.
        # An api_call node is an entry node if:
        # 1. It has no incoming edges from other api_call nodes, OR
        # 2. All its incoming edges are from input nodes (which don't count as dependencies)
        input_node_types = {'prompt_input', 'image_default', 'video_default', 'prompt_default_hidden', 'media_list_default', 'param_input'}
        
        # Build a map of source node types for each edge
        source_node_map = {}
        for edge in workflow.edges:
            source_id = edge.get("source")
            target_id = edge.get("target")
            source_node = self._get_node_by_id(valid_nodes, source_id)
            if source_node and target_id:
                if target_id not in source_node_map:
                    source_node_map[target_id] = []
                source_node_map[target_id].append(source_node.get("type"))
        
        # Find entry nodes (api_call nodes with no dependencies from other api_call nodes)
        first_nodes = []
        for node_id in execution_order:
            node = self._get_node_by_id(valid_nodes, node_id)
            if node and node.get("type") == 'api_call':
                # Check if this node has dependencies from other api_call nodes
                source_types = source_node_map.get(node_id, [])
                has_api_dependencies = any(st == 'api_call' for st in source_types)
                
                # If no api_call dependencies, this is an entry node
                if not has_api_dependencies:
                    first_nodes.append(node_id)
        
        if not first_nodes:
            raise ValueError("Workflow has no entry nodes (all api_call nodes have dependencies from other api_call nodes)")
        
        # Start all first nodes (they can run in parallel)
        results = []
        for node_id in first_nodes:
            node = self._get_node_by_id(valid_nodes, node_id)
            if not node:
                raise ValueError(f"Node not found: {node_id}")
            
            # Double-check node type before execution
            if node.get("type") not in valid_node_types:
                logger.warning(f"Skipping invalid node {node_id} with type {node.get('type')}")
                continue
            
            # Check if this is the final node (last in execution order)
            is_final = node_id == execution_order[-1]
            result = await self._execute_node(node, work_id, webhook_url, is_final=is_final)
            results.append(result)
        
        # Return the first result (or all if needed)
        return results[0] if len(results) == 1 else {"status": "started", "nodes_started": len(results)}
    
    async def _execute_node(
        self,
        node: Dict[str, Any],
        work_id: int,
        webhook_url: str,
        is_final: bool = False
    ) -> Dict[str, Any]:
        """Execute a single workflow node."""
        if node.get("type") != "api_call":
            raise ValueError(f"Unsupported node type: {node.get('type')}")
        
        api_id = node.get("api_id")
        if not api_id:
            raise ValueError("Node missing api_id")
        
        # Get API configuration
        api = self.db.query(APILibrary).filter(APILibrary.id == api_id).first()
        if not api:
            raise ValueError(f"API Library not found: {api_id}")
        
        # Resolve parameters
        node_data = node.get("data", {})
        # Use param_defaults (from frontend) as preset_params, fallback to preset_params for backward compatibility
        param_defaults = node_data.get("param_defaults", {})
        preset_params = node_data.get("preset_params", {})
        # Merge: param_defaults takes precedence, then preset_params
        merged_preset_params = {**preset_params, **param_defaults}
        param_mappings = node_data.get("param_mappings", {}).copy()  # Make a copy to avoid modifying original
        
        # Auto-map visible parameters to user_input if not manually mapped and not connected
        if api.params_schema and self.workflow:
            params_visibility = node_data.get("params_visibility", {})
            node_id = node.get("id")
            
            # Get edges that connect to this node's parameters
            connected_params = set()
            if self.workflow.edges:
                for edge in self.workflow.edges:
                    if edge.get("target") == node_id:
                        target_handle = edge.get("targetHandle", "")
                        # Extract parameter name from targetHandle (e.g., "input-prompt" -> "prompt")
                        if target_handle.startswith("input-"):
                            param_name = target_handle.replace("input-", "", 1)
                        else:
                            param_name = target_handle
                        if param_name:
                            connected_params.add(param_name)
            
            # Auto-map visible parameters that are not manually mapped and not connected
            for param_name, param_def in api.params_schema.items():
                # Skip if already has manual mapping
                if param_name in param_mappings:
                    continue
                
                # Skip if connected to another node
                if param_name in connected_params:
                    continue
                
                # Check if parameter is visible (default to True if not specified)
                is_visible = params_visibility.get(param_name, True)
                
                # Auto-map visible parameters to user_input
                if is_visible:
                    # Check if this parameter might have a prefixed version in user_input
                    # (e.g., if workflow has multiple nodes with same param name but different definitions)
                    node_label = node_data.get("label", "") or api.name or f"Node_{node_id}"
                    # Use node label as prefix, but fallback to original name if prefixed version doesn't exist
                    prefixed_name = f"{node_label}_{param_name}" if node_label else f"{node_id}_{param_name}"
                    
                    # Try prefixed name first, then fallback to original name
                    # This allows users to input either "seed" (if same definition) or "Node1_seed" (if different)
                    param_mappings[param_name] = f"$.user_input.{prefixed_name} || {param_name}"
                    logger.info(f"Auto-mapped visible parameter '{param_name}' to $.user_input.{prefixed_name} || {param_name} for node {node_id}")
        
        # Debug: log context and mappings for all nodes (not just intermediate)
        logger.info(f"Resolving params for node {node.get('id')} (is_final={is_final})")
        logger.info(f"Context keys: {list(self.context.keys()) if self.context else 'None'}")
        logger.info(f"Param mappings: {param_mappings}")
        if self.context:
            for key in self.context.keys():
                node_data_in_context = self.context[key]
                if isinstance(node_data_in_context, dict):
                    logger.info(f"  Context[{key}]: type={type(node_data_in_context)}, keys={list(node_data_in_context.keys())}")
                    # Log the output structure if it's a dict
                    if "output" in node_data_in_context:
                        output = node_data_in_context.get("output") or {}
                        logger.info(f"    Output keys: {list(output.keys()) if isinstance(output, dict) else 'not a dict'}")
                        # Log prompt value if present
                        if isinstance(output, dict) and "prompt" in output:
                            prompt_val = output.get("prompt", "")
                            logger.info(f"    Output prompt: {prompt_val[:100] if prompt_val else 'EMPTY'}")
                        # Log URL if present (value may be None for text-type nodes)
                        if isinstance(output, dict) and "url" in output:
                            url_val = output.get("url") or "N/A"
                            logger.info(f"    Output URL: {(str(url_val))[:100]}")
                else:
                    logger.info(f"  Context[{key}]: type={type(node_data_in_context)} (not a dict)")
        
        resolved_params = ParamMapper.resolve_params(
            param_mappings,
            merged_preset_params,
            self.context
        )
        
        # Overlay user_input so user-provided prompt/image/params override preset defaults
        user_input = self.context.get("user_input") or {}
        for key, value in user_input.items():
            if value is None:
                continue
            if isinstance(value, str) and value.strip() == "" and key in ("prompt", "negative_prompt"):
                continue  # Empty prompt/negative_prompt: keep preset, do not override
            if isinstance(value, (list, dict)) and len(value) == 0:
                continue  # Empty list/dict: keep preset
            resolved_params[key] = value
        
        # Debug: log resolved params for all nodes
        logger.info(f"Resolved params for node {node.get('id')}: {list(resolved_params.keys())}")
        # Check if prompt parameter was resolved
        if "prompt" in resolved_params:
            prompt_val = resolved_params['prompt']
            logger.info(f"  Resolved prompt param: {prompt_val[:100] if isinstance(prompt_val, str) else type(prompt_val)}")
        else:
            logger.warning(f"  Prompt parameter NOT found in resolved params!")
            logger.warning(f"  Param mappings: {param_mappings}")
            logger.warning(f"  Context keys: {list(self.context.keys())}")
        # Check if image parameter was resolved
        if "image" in resolved_params:
            image_val = resolved_params['image']
            logger.info(f"  Resolved image param: {image_val[:100] if isinstance(image_val, str) else type(image_val)}")
        # Log all resolved params for debugging
        for param_name, param_value in resolved_params.items():
            if param_name not in ["prompt", "negative_prompt"]:
                logger.info(f"  {param_name}: {str(param_value)[:100] if isinstance(param_value, str) else type(param_value)}")
        
        # Extract prompt and negative_prompt
        prompt = resolved_params.pop("prompt", "")
        negative_prompt = resolved_params.pop("negative_prompt", None)
        
        # Log final prompt value before API call
        logger.info(f"Final prompt value for node {node.get('id')}: '{prompt[:100] if prompt else 'EMPTY'}'")
        
        # Determine work_type from API
        # For intermediate nodes, we might need to infer from API
        work_type = self._infer_work_type(api)
        
        # Get provider
        provider = ProviderFactory.get_provider(api.provider)
        
        # Use provider_model_id as model_id
        model_id = api.provider_model_id
        
        # For intermediate nodes, we need a different webhook URL
        # For now, we'll use the same webhook and handle it there
        node_webhook_url = webhook_url if is_final else f"{webhook_url}?node_id={node.get('id')}"
        
        # Execute API call
        logger.info(f"Executing workflow node {node.get('id')} for work {work_id}")
        prediction_id = await provider.create_generation(
            work_id=work_id,
            work_type=work_type,
            model_id=model_id,
            prompt=prompt,
            negative_prompt=negative_prompt,
            params=resolved_params,
            webhook_url=node_webhook_url
        )
        
        return {
            "status": "started",
            "prediction_id": prediction_id,
            "node_id": node.get("id"),
            "api_id": api_id
        }
    
    def _topological_sort(
        self,
        nodes: List[Dict[str, Any]],
        edges: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Perform topological sort on workflow nodes.
        Returns list of node IDs in execution order.
        """
        # Build graph
        graph = defaultdict(list)
        in_degree = defaultdict(int)
        # Filter out invalid nodes (edges that might be in nodes array)
        valid_node_types = {'api_call', 'prompt_input', 'image_default', 'video_default', 'param_input', 'prompt_default_hidden', 'media_list_default'}
        valid_nodes = [node for node in nodes if node.get("type") in valid_node_types]
        node_ids = {node.get("id") for node in valid_nodes if node.get("id")}
        
        # Initialize in_degree for all nodes
        for node_id in node_ids:
            in_degree[node_id] = 0
        
        # Build graph from edges
        for edge in edges:
            source = edge.get("source")
            target = edge.get("target")
            
            if source in node_ids and target in node_ids:
                graph[source].append(target)
                in_degree[target] += 1
        
        # Kahn's algorithm
        queue = deque([node_id for node_id in node_ids if in_degree[node_id] == 0])
        result = []
        
        while queue:
            node_id = queue.popleft()
            result.append(node_id)
            
            for neighbor in graph[node_id]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        # Check for cycles
        if len(result) != len(node_ids):
            logger.error("Workflow has circular dependencies")
            return []
        
        return result
    
    def _get_node_by_id(self, nodes: List[Dict[str, Any]], node_id: str) -> Optional[Dict[str, Any]]:
        """Get a node by its ID."""
        valid_node_types = {'api_call', 'prompt_input', 'image_default', 'video_default', 'param_input', 'prompt_default_hidden', 'media_list_default'}
        for node in nodes:
            if node.get("id") == node_id:
                # Ensure it's a valid node type, not an edge
                node_type = node.get("type")
                if node_type in valid_node_types:
                    return node
                else:
                    logger.warning(f"Found object with ID {node_id} but invalid type: {node_type}")
        return None
    
    def _has_no_dependencies(self, node_id: str, edges: List[Dict[str, Any]]) -> bool:
        """Check if a node has no incoming edges (no dependencies)."""
        for edge in edges:
            if edge.get("target") == node_id:
                return False
        return True
    
    def _get_next_nodes(self, completed_node_id: str, edges: List[Dict[str, Any]]) -> List[str]:
        """Get all nodes that depend on the completed node."""
        next_nodes = []
        for edge in edges:
            if edge.get("source") == completed_node_id:
                next_nodes.append(edge.get("target"))
        return next_nodes
    
    def _are_dependencies_ready(
        self,
        node_id: str,
        edges: List[Dict[str, Any]],
        completed_nodes: set,
        nodes: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """Check if all dependencies of a node have been completed."""
        dependencies = []
        for edge in edges:
            if edge.get("target") == node_id:
                dependencies.append(edge.get("source"))
        
        # If no dependencies, node is ready
        if not dependencies:
            return True
        
        # Filter out input nodes (promptPreset, promptInput, imageInput, etc.)
        # These nodes are data sources, not executable nodes, so they don't need to be "completed"
        input_node_types = {'prompt_default_hidden', 'prompt_input', 'image_default', 'video_default', 'media_list_default', 'param_input'}
        executable_dependencies = []
        
        if nodes:
            # Check node types to filter out input nodes
            for dep_id in dependencies:
                dep_node = self._get_node_by_id(nodes, dep_id)
                if dep_node:
                    dep_type = dep_node.get("type")
                    # Only count api_call nodes as dependencies that need to be completed
                    # Input nodes are always "ready" (they provide data, not execution)
                    if dep_type == "api_call":
                        executable_dependencies.append(dep_id)
                    elif dep_type not in input_node_types:
                        # Unknown node type, treat as dependency
                        executable_dependencies.append(dep_id)
                else:
                    # Node not found, assume it's an input node (already available)
                    logger.warning(f"Dependency node {dep_id} not found in workflow nodes, assuming it's an input node")
        else:
            # Fallback: if nodes list not provided, check all dependencies
            executable_dependencies = dependencies
        
        # If no executable dependencies, node is ready
        if not executable_dependencies:
            return True
        
        # Check if all executable dependencies are completed
        all_ready = all(dep in completed_nodes for dep in executable_dependencies)
        if not all_ready:
            missing = [dep for dep in executable_dependencies if dep not in completed_nodes]
            logger.info(f"Node {node_id} dependencies not ready. Missing: {missing}, Completed: {list(completed_nodes)}")
        return all_ready
    
    def _infer_work_type(self, api: APILibrary) -> str:
        """Infer work_type from API configuration."""
        # Check task_type first
        if api.task_type:
            task_type_lower = api.task_type.lower()
            if "video" in task_type_lower:
                return "text-to-video"
            elif "image" in task_type_lower:
                return "text-to-image"
        
        # Check provider_model_id
        model_id_lower = api.provider_model_id.lower()
        if "video" in model_id_lower or "wan" in model_id_lower:
            return "text-to-video"
        elif "image" in model_id_lower or "flux" in model_id_lower or "qwen" in model_id_lower:
            return "text-to-image"
        
        # Default
        return "text-to-image"


def get_workflow_output_work_type(db, workflow: Workflow) -> Optional[str]:
    """
    Infer work_type from the workflow's last (api_call) node's output_type.
    Used when creating a Work so that work.type matches what the pipeline actually produces.
    Returns a work_type string (e.g. "text2video", "text2img") or None to keep request type.
    """
    if not workflow or not workflow.nodes or not workflow.edges:
        return None
    valid_node_types = {'api_call', 'prompt_input', 'image_default', 'video_default', 'param_input', 'prompt_default_hidden', 'media_list_default'}
    valid_nodes = [n for n in workflow.nodes if n.get("type") in valid_node_types]
    if not valid_nodes:
        return None
    executor = WorkflowExecutor(db_session=db)
    try:
        execution_order = executor._topological_sort(valid_nodes, workflow.edges or [])
        if not execution_order:
            return None
        last_api_node = None
        for node_id in reversed(execution_order):
            node = executor._get_node_by_id(valid_nodes, node_id)
            if node and node.get("type") == "api_call":
                last_api_node = node
                break
        if not last_api_node:
            return None
        api_id = last_api_node.get("api_id")
        if not api_id:
            return None
        api = db.query(APILibrary).filter(APILibrary.id == api_id).first()
        if not api:
            return None
        output_type = (last_api_node.get("data") or {}).get("output_type") or api.output_type or ""
        output_type = (output_type or "").strip().lower()
        workflow_type = (workflow.work_type or "").strip().lower()
        if output_type == "video":
            if workflow_type in ("text2video", "img2video", "text-to-video", "image-to-video"):
                return workflow_type
            return "text-to-video"
        if output_type in ("image", "string"):
            if workflow_type in ("text2img", "img2img", "img_effects", "text-to-image", "image-to-image", "image-effects"):
                return workflow_type
            return "text-to-image"
        return None
    except Exception:
        return None
