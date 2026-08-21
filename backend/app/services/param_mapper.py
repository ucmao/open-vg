"""Parameter mapping parser for workflow execution."""
from typing import Any, Dict, Optional
import re
from ..utils.logger import logger


class ParamMapper:
    """Parse and resolve parameter mappings using JSONPath-like syntax."""
    
    @staticmethod
    def resolve(mapping: str, context: Dict[str, Any]) -> Any:
        """
        Resolve a parameter mapping string to a value from context.
        
        Supported syntax:
        - $.user_input.prompt: Get prompt from user input
        - $.user_input.negative_prompt: Get negative_prompt from user input
        - $.node_0.output.url: Get URL from node 0 output
        - $.node_0.output.width: Get width from node 0 output metadata
        
        Args:
            mapping: Mapping string (e.g., "$.user_input.prompt")
            context: Execution context containing user_input and node outputs
            
        Returns:
            Resolved value or None if not found
        """
        if not mapping or not mapping.startswith("$."):
            # If not a mapping, return as-is (could be a literal value)
            return mapping
        
        try:
            # Remove leading "$."
            path = mapping[2:]
            parts = path.split(".")
            
            if len(parts) < 2:
                logger.warning(f"Invalid mapping path: {mapping}")
                return None
            
            # Handle user_input
            if parts[0] == "user_input":
                user_input = context.get("user_input", {})
                if len(parts) == 2:
                    param_name = parts[1]
                    # Check if mapping contains fallback syntax (e.g., "param_name || fallback_name")
                    if " || " in param_name:
                        # Try each option in order until one is found
                        fallback_names = [name.strip() for name in param_name.split(" || ")]
                        for name in fallback_names:
                            value = user_input.get(name)
                            if value is not None:
                                return value
                        return None
                    return user_input.get(param_name)
                else:
                    # Nested access (e.g., $.user_input.params.width)
                    current = user_input
                    for part in parts[1:]:
                        if isinstance(current, dict):
                            current = current.get(part)
                        else:
                            return None
                    return current
            
            # Handle node outputs (e.g., $.node_0.output.url or $.node_1769452809290.output.url)
            # Also support actual node IDs like $.promptPreset_1769514191045.output.prompt
            # Check if this is a node reference (starts with "node_" or is an actual node ID in context)
            node_id = parts[0]
            node_output = None
            
            # First try exact match (for actual node IDs like promptPreset_1769514191045)
            if node_id in context:
                node_output = context.get(node_id, {})
            
            # If not found and starts with "node_", try that format
            if not node_output and node_id.startswith("node_"):
                node_output = context.get(node_id, {})
            
            if not node_output:
                logger.warning(f"Node output not found: {node_id}. Available context keys: {list(context.keys())}")
                return None
            
            # Check if it's an output object
            if len(parts) >= 2 and parts[1] == "output":
                output = node_output.get("output", {})
                if len(parts) == 3:
                    # $.node_0.output.url or $.promptPreset_1769514191045.output.prompt
                    result = output.get(parts[2])
                    if result is None:
                        # Log available keys for debugging
                        logger.warning(f"Parameter mapping '{mapping}' not found. Available keys in output: {list(output.keys())}")
                    return result
                elif len(parts) > 3:
                    # Nested access (e.g., $.node_0.output.metadata.width)
                    current = output
                    for part in parts[2:]:
                        if isinstance(current, dict):
                            current = current.get(part)
                        else:
                            logger.warning(f"Parameter mapping '{mapping}' failed at '{part}'. Current value is not a dict: {type(current)}")
                            return None
                    return current
            else:
                # Direct node access (e.g., $.node_0.status)
                current = node_output
                for part in parts[1:]:
                    if isinstance(current, dict):
                        current = current.get(part)
                    else:
                        return None
                return current
            
            logger.warning(f"Unknown mapping prefix: {parts[0]}")
            return None
            
        except Exception as e:
            logger.error(f"Error resolving mapping {mapping}: {str(e)}")
            return None
    
    @staticmethod
    def resolve_params(
        param_mappings: Dict[str, str],
        preset_params: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Resolve all parameter mappings and merge with preset parameters.
        
        Args:
            param_mappings: Dictionary of param_name -> mapping_string
            preset_params: Dictionary of preset (fixed) parameter values
            context: Execution context
            
        Returns:
            Merged parameters dictionary
        """
        resolved_params = {}
        
        # First, add preset parameters (these are fixed values)
        resolved_params.update(preset_params)
        
        # Then, resolve mapped parameters
        for param_name, mapping in param_mappings.items():
            logger.info(f"Resolving mapping for {param_name}: {mapping}")
            resolved_value = ParamMapper.resolve(mapping, context)
            logger.info(f"  Resolved value for {param_name}: {resolved_value[:100] if isinstance(resolved_value, str) else resolved_value}")
            # If mapping resolves to a value (including empty string), use it
            # If mapping resolves to None or empty string, fallback to preset/default value
            if resolved_value is not None:
                # Only override preset if resolved value is not empty string
                # Empty string means user explicitly cleared the field, so use it
                # None means mapping failed, so use preset/default
                if resolved_value != "" or param_name not in resolved_params:
                    resolved_params[param_name] = resolved_value
                    logger.info(f"  Mapped {param_name} = {str(resolved_value)[:100] if isinstance(resolved_value, str) else type(resolved_value)}")
            else:
                # Mapping failed - log warning with more details
                logger.warning(f"  Failed to resolve mapping for {param_name}: {mapping}")
                logger.warning(f"  Available context keys: {list(context.keys())}")
                # If resolved_value is None and we have a preset, keep the preset
                # (preset is already set above)
        
        return resolved_params
