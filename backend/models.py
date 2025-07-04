"""
Pydantic models for API request/response validation
Phase 2: Backend API & Analytics Engine
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from enum import Enum
from datetime import datetime
import re

class RevelationType(str, Enum):
    """Enumeration for revelation types"""
    MECCAN = "Meccan"
    MEDINAN = "Medinan"

class SemanticCategory(str, Enum):
    """Enumeration for semantic categories"""
    DIVINE_ATTRIBUTES = "divine_attributes"
    WORSHIP_RITUAL = "worship_ritual" 
    FAITH_BELIEF = "faith_belief"
    FAMILY_RELATIONS = "family_relations"
    SOCIAL_JUSTICE = "social_justice"
    COMMERCE_ECONOMICS = "commerce_economics"
    KNOWLEDGE_WISDOM = "knowledge_wisdom"
    COMMUNICATION = "communication"
    BOOKS_REVELATION = "books_revelation"
    CREATION_NATURE = "creation_nature"
    TIME_TEMPORAL = "time_temporal"
    NATURAL_ELEMENTS = "natural_elements"
    MOVEMENT_DIRECTION = "movement_direction"
    EMOTIONS_STATES = "emotions_states"
    MORAL_CONDUCT = "moral_conduct"
    UNCATEGORIZED = "uncategorized"

class RarityLevel(str, Enum):
    """Enumeration for root rarity levels"""
    HAPAX_LEGOMENA = "hapax_legomena"  # Appears only once
    VERY_RARE = "very_rare"            # 2-5 occurrences
    RARE = "rare"                      # 6-20 occurrences
    COMMON = "common"                  # 21-100 occurrences
    VERY_COMMON = "very_common"        # 100+ occurrences

# Base Response Models
class BaseResponse(BaseModel):
    """Base response model with common fields"""
    success: bool = True
    message: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: str(datetime.now().isoformat()))

# Root Models
class RootResponse(BaseModel):
    """Response model for root information"""
    root_buckwalter: str = Field(..., description="Root in Buckwalter transliteration")
    root_arabic: str = Field(..., description="Root in Arabic script")
    semantic_category: str = Field(..., description="Semantic category of the root")
    total_frequency: int = Field(..., description="Total occurrences in Quran")
    meccan_frequency: int = Field(..., description="Occurrences in Meccan suras")
    medinan_frequency: int = Field(..., description="Occurrences in Medinan suras")
    meccan_ratio: float = Field(..., description="Proportion of Meccan occurrences")
    frequency_rank: int = Field(..., description="Rank by frequency (1 = most frequent)")

class RootDetailResponse(RootResponse):
    """Detailed response model for specific root"""
    related_roots: List[Dict[str, Union[str, int]]] = Field(..., description="Co-occurring roots")
    usage_examples: List[Dict[str, Any]] = Field(..., description="Usage examples from Quran")
    etymological_info: Optional[Dict[str, Any]] = Field(None, description="Etymological information")

class RootSearchRequest(BaseModel):
    """Request model for root search"""
    query: str = Field(..., min_length=1, max_length=100, description="Search query")
    search_type: str = Field("both", pattern="^(buckwalter|arabic|both)$", description="Search in Buckwalter, Arabic, or both")
    exact_match: bool = Field(False, description="Whether to use exact matching")

# Sura Models
class SuraResponse(BaseModel):
    """Response model for sura information"""
    sura_number: int = Field(..., ge=1, le=114, description="Sura number (1-114)")
    name_arabic: str = Field(..., description="Sura name in Arabic")
    name_english: str = Field(..., description="Sura name in English")
    revelation_type: RevelationType = Field(..., description="Meccan or Medinan")
    verse_count: int = Field(..., description="Number of verses")
    chronological_order: Optional[int] = Field(None, description="Chronological order of revelation")
    unique_roots_count: int = Field(..., description="Number of unique roots in this sura")

class SuraDetailResponse(SuraResponse):
    """Detailed response model for specific sura"""
    thematic_breakdown: Dict[str, float] = Field(..., description="Semantic categories distribution")
    most_frequent_roots: List[Dict[str, Any]] = Field(..., description="Top roots in this sura")
    rare_roots: List[str] = Field(..., description="Rare roots unique to this sura")

class SuraComparisonRequest(BaseModel):
    """Request model for comparing suras"""
    sura_numbers: List[int] = Field(..., min_items=2, max_items=10, description="List of sura numbers to compare")
    comparison_metric: str = Field("vocabulary_overlap", pattern="^(vocabulary_overlap|thematic_similarity|frequency_correlation)$")

# Analytics Models
class FrequencyAnalysisResponse(BaseModel):
    """Response model for frequency analysis"""
    total_unique_roots: int = Field(..., description="Total number of unique roots")
    hapax_legomena_count: int = Field(..., description="Number of roots appearing only once")
    most_frequent_roots: List[RootResponse] = Field(..., description="Most frequent roots")
    frequency_distribution: Dict[str, int] = Field(..., description="Distribution by frequency ranges")
    revelation_comparison: Dict[str, Dict[str, int]] = Field(..., description="Meccan vs Medinan statistics")

class CooccurrenceAnalysisResponse(BaseModel):
    """Response model for co-occurrence analysis"""
    total_pairs: int = Field(..., description="Total number of root pairs analyzed")
    top_cooccurring_pairs: List[Dict[str, Any]] = Field(..., description="Most co-occurring root pairs")
    semantic_clustering: Dict[str, List[str]] = Field(..., description="Semantic category clusters")
    network_metrics: Dict[str, float] = Field(..., description="Network analysis metrics")

class ThematicAnalysisResponse(BaseModel):
    """Response model for thematic analysis"""
    category_distribution: Dict[str, int] = Field(..., description="Roots per semantic category")
    revelation_preferences: Dict[str, str] = Field(..., description="Category preferences by revelation type")
    temporal_evolution: Dict[str, List[float]] = Field(..., description="Thematic evolution over revelation period")

# Query Models
class AdvancedQueryRequest(BaseModel):
    """Request model for advanced queries"""
    filters: Dict[str, Any] = Field(..., description="Query filters")
    sort_by: Optional[str] = Field("frequency", description="Sort field")
    sort_order: str = Field("desc", pattern="^(asc|desc)$", description="Sort order")
    limit: int = Field(50, ge=1, le=1000, description="Result limit")
    offset: int = Field(0, ge=0, description="Result offset")

# Export Models
class ExportRequest(BaseModel):
    """Request model for data export"""
    data_type: str = Field(..., pattern="^(roots|suras|cooccurrence|thematic)$", description="Type of data to export")
    format: str = Field("json", pattern="^(json|csv|xml)$", description="Export format")
    filters: Optional[Dict[str, Any]] = Field(None, description="Data filters")
    include_metadata: bool = Field(True, description="Include metadata in export")

class ExportResponse(BaseModel):
    """Response model for data export"""
    download_url: str = Field(..., description="URL to download the exported data")
    file_size: int = Field(..., description="File size in bytes")
    record_count: int = Field(..., description="Number of records exported")
    expiry_time: str = Field(..., description="When the download link expires")

# Utility Models
class TextConversionRequest(BaseModel):
    """Request model for text conversion"""
    text: str = Field(..., min_length=1, max_length=1000, description="Text to convert")
    from_format: str = Field(..., pattern="^(buckwalter|arabic)$", description="Source format")
    to_format: str = Field(..., pattern="^(buckwalter|arabic)$", description="Target format")

class TextConversionResponse(BaseModel):
    """Response model for text conversion"""
    original_text: str = Field(..., description="Original input text")
    converted_text: str = Field(..., description="Converted text")
    from_format: str = Field(..., description="Source format")
    to_format: str = Field(..., description="Target format")

# Statistics Models
class StatisticsResponse(BaseModel):
    """Response model for dataset statistics"""
    dataset_info: Dict[str, Any] = Field(..., description="Basic dataset information")
    root_statistics: Dict[str, Any] = Field(..., description="Root-related statistics")
    sura_statistics: Dict[str, Any] = Field(..., description="Sura-related statistics")
    categorical_distribution: Dict[str, Any] = Field(..., description="Semantic category distribution")
    frequency_patterns: Dict[str, Any] = Field(..., description="Frequency patterns analysis")

# Error Models
class ErrorResponse(BaseModel):
    """Standard error response model"""
    success: bool = False
    error_code: str = Field(..., description="Error code")
    error_message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: str = Field(default_factory=lambda: str(datetime.now().isoformat()))

# Validators
@validator('root_buckwalter', 'root_arabic', pre=True, always=True)
def validate_root_format(cls, v):
    """Validate root format"""
    if not v or len(v.strip()) == 0:
        raise ValueError("Root cannot be empty")
    return v.strip()

# Model configurations
class Config:
    """Pydantic model configuration"""
    use_enum_values = True
    validate_assignment = True
    arbitrary_types_allowed = True 