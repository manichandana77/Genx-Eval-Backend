"""
Evaluator Service Pydantic Models
"""
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom ObjectId for Pydantic v2"""
    
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        from pydantic_core import core_schema
        return core_schema.no_info_plain_validator_function(cls.validate)
    
    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str) and ObjectId.is_valid(v):
            return ObjectId(v)
        raise ValueError("Invalid ObjectId")
    
    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema, handler):
        field_schema.update(type="string", format="objectid")


# ===== Request Models =====
class EvaluationRequest(BaseModel):
    """Main evaluation request model"""
    file_path: str = Field(..., description="Path to dataset file (YAML/JSON)")
    metrics: List[str] = Field(
        default=["answer_relevancy", "faithfulness", "bias"],
        description="List of metrics to calculate"
    )
    user_id: str = Field(default="default_user", description="User identifier")
    session_id: str = Field(default="", description="Session identifier")
    process_name: str = Field(default="evaluation", description="Process name")
    config_id: List[Dict[str, str]] = Field(
        default=[{"default": "default_model"}],
        description="List of model configurations"
    )
    client_api_key: str = Field(default="", description="Client API key")


class EvaluationRequestPayload(BaseModel):
    """Request payload matching your original structure"""
    orgId: str
    payload: Dict[str, Any]


class StatusRequest(BaseModel):
    """Status check request"""
    process_id: str
    service: str = "evaluation"


class ResultsRequest(BaseModel):
    """Results retrieval request"""
    orgId: str
    user_id: str
    page: int = 1
    page_size: int = 10


class StopEvaluationRequest(BaseModel):
    """Stop evaluation request"""
    process_id: str
    orgId: str


# ===== Response Models =====
class APIResponse(BaseModel):
    """Standard API response"""
    success: bool = True
    message: str = ""
    data: Optional[Any] = None
    status_code: int = 200


class EvaluationResponse(BaseModel):
    """Evaluation start response"""
    status_code: int = 200
    process_id: str
    message: str = "Evaluation has been started in the background"


class StatusResponse(BaseModel):
    """Status response model"""
    models: List[Dict[str, Any]]
    overall_status: str
    error: Optional[str] = None


class ResultsResponse(BaseModel):
    """Results response with pagination"""
    results: List[Dict[str, Any]]
    pagination: Dict[str, Any]


# ===== Database Models =====
class ModelStatus(BaseModel):
    """Model status tracking"""
    config_id: str
    model_name: str
    status: str  # "Not Started", "In Progress", "Completed", "Failed"
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None


class StatusRecord(BaseModel):
    """Status record for MongoDB"""
    process_id: str
    user_id: str
    models: List[ModelStatus] = Field(default_factory=list)
    overall_status: str = "Pending"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class EvaluationResult(BaseModel):
    """Evaluation result model"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    process_id: str
    user_id: str
    model_name: str
    
    # Results data
    results: Dict[str, Any] = Field(default_factory=dict)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class MetricsResult(BaseModel):
    """Metrics calculation result"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    process_id: str
    user_id: str
    
    # Metrics data
    metrics_results: List[Dict[str, Any]] = Field(default_factory=list)
    metrics_calculated: List[str] = Field(default_factory=list)
    calculation_timestamp: float = Field(default_factory=lambda: datetime.utcnow().timestamp())
    execution_time_ms: float = 0.0
    summary_stats: Dict[str, Any] = Field(default_factory=dict)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


# ===== Health Models =====
class HealthStatus(BaseModel):
    """Service health status"""
    status: str = "healthy"
    version: str = "1.0.0"
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    services: Dict[str, bool] = Field(default_factory=dict)
    uptime_seconds: float = 0.0


class ServiceInfo(BaseModel):
    """Service information"""
    service: str = "evaluator"
    version: str = "1.0.0"
    status: str = "running"
    docs: str = "/docs"
    health: str = "/health"
