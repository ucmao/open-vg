"""Generation Model and API Library configuration database models."""
from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, DateTime, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base


class APILibrary(Base):
    """Base API configuration provided by external services."""
    
    __tablename__ = "api_library"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # API identification
    api_key = Column(String(100), nullable=False, unique=True, index=True)  # Internal unique key
    name = Column(String(200), nullable=False)  # Display name for admin
    task_type = Column(String(100), nullable=True)  # Short functional name, e.g., "Flux", "Luma V2"
    output_type = Column(String(50), nullable=True)  # Output type: "image", "video", "string", etc.
    
    # Provider configuration
    provider = Column(String(50), nullable=False)  # replicate, gemini, a2e
    provider_model_id = Column(String(200), nullable=False)  # Unified external ID
    
    # Parameters configuration (stored as JSON)
    # Complete parameter definitions: type, default, min, max, options, etc.
    params_schema = Column(JSON, nullable=False, default={})
    
    # Metadata & Cost Analysis (Official)
    api_docs_url = Column(String(500), nullable=True)
    official_price = Column(Float, nullable=True)
    official_currency = Column(String(10), nullable=True, default="USD")
    official_unit = Column(String(50), nullable=True)  # per_request, per_second, etc.
    
    is_active = Column(Boolean, default=True, nullable=False)
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "api_key": self.api_key,
            "name": self.name,
            "task_type": self.task_type,
            "output_type": self.output_type,
            "provider": self.provider,
            "provider_model_id": self.provider_model_id,
            "params_schema": self.params_schema or {},
            "api_docs_url": self.api_docs_url,
            "official_price": self.official_price,
            "official_currency": self.official_currency,
            "official_unit": self.official_unit,
            "is_active": self.is_active,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class GenerationModel(Base):
    """AI generation model configuration (Product instance) stored in database."""
    
    __tablename__ = "generation_models"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Association with Workflow (workflow-based; API is determined by workflow nodes)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=True, index=True)
    # workflow relationship is defined via backref in Workflow model
    
    # Model identification (Specific to this product instance)
    model_key = Column(String(100), nullable=False, unique=True, index=True)
    name = Column(String(200), nullable=False)  # Display name
    work_type = Column(String(50), nullable=False, index=True)  # text-to-image, text-to-video, etc.
    description = Column(Text, nullable=True)
    
    # Pricing and status (Business logic)
    cost = Column(Integer, nullable=False, default=0)  # Credit cost (charged to users)
    is_active = Column(Boolean, default=True, nullable=False, index=True)  # Whether enabled
    is_featured = Column(Boolean, default=False, nullable=False, index=True)  # Whether featured/
    sort_order = Column(Integer, default=0, nullable=False)  # Display order
    
    # Classification
    model_level = Column(String(50), nullable=True)  # : basic, pro, advanced, etc.
    category = Column(String(100), nullable=True)  # : quality, speed, portrait, etc.
    
    # Parameters configuration overlay (stored as JSON)
    # Only stores overrides: {"num_inference_steps": {"default": 30, "visible": false}}
    params_config = Column(JSON, nullable=False, default={})
    
    # Business-side metadata
    notes = Column(Text, nullable=True)  # Internal notes for this specific model
    
    # Example galleries (before/after effects)
    example_galleries = Column(JSON, nullable=True, default=[])

    # Display: icon URL (shown before model name), badge (free/new/hot, shown after name)
    icon_url = Column(String(500), nullable=True)
    badge = Column(String(20), nullable=True)  # free, new, hot, beta, 50off, pro, limited, verified, top, best or null

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(Integer, ForeignKey("admins.id"), nullable=True)
    
    # Keys in params_config that are only used for cost/credit (); not for visibility or defaults
    _PARAMS_CONFIG_COST_KEYS = ("cost_additions", "cost_addition")

    def get_effective_params(self):
        """
        Get effective parameters from workflow only. params_config is used only to attach
        cost/credit additions () to visible parameters.
        """
        try:
            if not self.workflow_id or not self.workflow:
                return {}
            params = self.workflow.get_user_visible_params()
            if not params:
                return {}
            cost_overrides = self.params_config or {}
            base_params = {}
            for k, v in params.items():
                base_params[k] = dict(v) if isinstance(v, dict) else v
            for key, patch in cost_overrides.items():
                if key in base_params and isinstance(base_params[key], dict) and isinstance(patch, dict):
                    for cost_key in self._PARAMS_CONFIG_COST_KEYS:
                        if cost_key in patch:
                            base_params[key][cost_key] = patch[cost_key]
            return base_params
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to get params from workflow {self.workflow_id}: {str(e)}")
            return {}

    def to_dict(self):
        """Convert model to dictionary format compatible with front-end expectations."""
        try:
            effective_params = self.get_effective_params()
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to get effective params for model {self.id}: {str(e)}")
            effective_params = {}
        
        # Primary API (from first api_call node of workflow, if any) is resolved by callers when needed
        return {
            "id": self.id,
            "api_id": None,
            "api_name": None,
            "provider": None,
            "provider_model_id": None,
            "work_type": self.work_type,
            "cost": self.cost,
            "name": self.name,
            "description": self.description,
            "params": effective_params,
            "api_docs_url": None,
            "official_price": None,
            "official_currency": None,
            "official_unit": None,
            "notes": self.notes,
            "model_level": self.model_level,
            "category": self.category,
            "example_galleries": self.example_galleries or [],
            "model_key": self.model_key,
            "is_featured": self.is_featured,
            "workflow_id": self.workflow_id,
            "sort_order": self.sort_order,
            "icon_url": self.icon_url,
            "badge": self.badge,
            "model_id": None,
        }
    
    def to_full_dict(self):
        """Convert to full dictionary with all fields including internal ones."""
        data = self.to_dict()
        data.update({
            "is_active": self.is_active,
            "is_featured": self.is_featured,
            "workflow_id": self.workflow_id,
            "sort_order": self.sort_order,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by": self.created_by,
            "params_override": self.params_config,  # Raw override data
        })
        return data
