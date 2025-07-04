"""
Additional API endpoints for Quranic Roots Analysis
Phase 2: Backend API & Analytics Engine
"""

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from typing import List, Optional, Dict, Any
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import logging

from models import *
from analytics import QuranicAnalytics
from utils import *
from config import current_settings

logger = logging.getLogger(__name__)

# Initialize routers
analytics_router = APIRouter(prefix="/analytics", tags=["analytics"])
suras_router = APIRouter(prefix="/suras", tags=["suras"])
export_router = APIRouter(prefix="/export", tags=["export"])
utilities_router = APIRouter(prefix="/utils", tags=["utilities"])

# Add a roots router
roots_router = APIRouter(prefix="/roots", tags=["roots"])

# Global data references (will be loaded at startup)
enhanced_df = None
frequency_df = None
cooccurrence_df = None
analytics_engine = None

def initialize_data(enhanced_data, frequency_data, cooccurrence_data, analytics):
    """Initialize global data references"""
    global enhanced_df, frequency_df, cooccurrence_df, analytics_engine
    enhanced_df = enhanced_data
    frequency_df = frequency_data
    cooccurrence_df = cooccurrence_data
    analytics_engine = analytics

# Roots Endpoints
@roots_router.get("/", response_model=List[Dict[str, Any]])
async def get_roots(
    limit: int = Query(50, ge=1, le=1000, description="Number of roots to return"),
    offset: int = Query(0, ge=0, description="Number of roots to skip"),
    category: Optional[str] = Query(None, description="Filter by semantic category"),
    revelation: Optional[str] = Query(None, description="Filter by revelation type (Meccan/Medinan)"),
    min_frequency: Optional[int] = Query(None, description="Minimum frequency threshold"),
    search: Optional[str] = Query(None, description="Search in root text (Arabic or Buckwalter)")
):
    """Get list of roots with optional filtering"""
    try:
        if frequency_df is None or frequency_df.empty:
            raise HTTPException(status_code=503, detail="Data not available")
            
        df = frequency_df.copy()
        
        # Apply filters
        if category:
            df = df[df['semantic_category'] == category]
        
        if revelation:
            # This would need revelation data - we'll implement based on our enhanced dataset
            pass
            
        if min_frequency:
            df = df[df['total_frequency'] >= min_frequency]
            
        if search:
            # Search in both Buckwalter and Arabic
            search_mask = (
                df['root'].str.contains(search, case=False, na=False) |
                df.get('root_arabic', pd.Series()).str.contains(search, case=False, na=False)
            )
            df = df[search_mask]
        
        # Apply pagination
        total = len(df)
        df = df.iloc[offset:offset + limit]
        
        # Convert to response format
        roots = []
        for _, row in df.iterrows():
            roots.append({
                "root_buckwalter": row['root'],
                "root_arabic": row.get('root_arabic', ''),
                "semantic_category": row['semantic_category'],
                "total_frequency": int(row['total_frequency']),
                "meccan_frequency": int(row['meccan_frequency']),
                "medinan_frequency": int(row['medinan_frequency']),
                "meccan_ratio": float(row['meccan_ratio']),
                "frequency_rank": int(row.name + 1)
            })
        
        return roots
        
    except Exception as e:
        logger.error(f"Error in get_roots: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@roots_router.get("/{root_id}", response_model=Dict[str, Any])
async def get_root_detail(root_id: str):
    """Get detailed information about a specific root"""
    try:
        if frequency_df is None or frequency_df.empty:
            raise HTTPException(status_code=503, detail="Data not available")
            
        # Find root in frequency data
        root_data = frequency_df[frequency_df['root'] == root_id]
        if root_data.empty:
            # Try Arabic search
            if 'root_arabic' in frequency_df.columns:
                root_data = frequency_df[frequency_df['root_arabic'] == root_id]
            if root_data.empty:
                raise HTTPException(status_code=404, detail=f"Root '{root_id}' not found")
        
        root_info = root_data.iloc[0]
        
        # Get related co-occurrences
        related_roots = []
        if cooccurrence_df is not None and not cooccurrence_df.empty:
            related_df = cooccurrence_df[
                (cooccurrence_df['root1'] == root_info['root']) | 
                (cooccurrence_df['root2'] == root_info['root'])
            ].head(10)
            
            for _, r in related_df.iterrows():
                related_roots.append({
                    "root": r['root2'] if r['root1'] == root_info['root'] else r['root1'],
                    "cooccurrence_count": int(r['cooccurrence_count'])
                })
        
        # Get usage examples from enhanced dataset
        usage_examples = []
        if enhanced_df is not None and not enhanced_df.empty:
            examples = enhanced_df[
                enhanced_df['Root'] == root_info['root']
            ].head(5)
            if not examples.empty:
                usage_examples = examples[['sura', 'aya', 'FORM', 'TAG']].to_dict('records')
        
        return {
            "root_buckwalter": root_info['root'],
            "root_arabic": root_info.get('root_arabic', ''),
            "semantic_category": root_info['semantic_category'],
            "total_frequency": int(root_info['total_frequency']),
            "meccan_frequency": int(root_info['meccan_frequency']),
            "medinan_frequency": int(root_info['medinan_frequency']),
            "meccan_ratio": float(root_info['meccan_ratio']),
            "frequency_rank": int(root_data.index[0] + 1),
            "related_roots": related_roots,
            "usage_examples": usage_examples
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_root_detail: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Analytics Endpoints
@analytics_router.get("/", response_model=Dict[str, Any])
async def get_analytics_info():
    """Get analytics endpoints information"""
    return {
        "message": "Quranic Roots Analytics API",
        "available_endpoints": {
            "frequency": "/frequency - Comprehensive frequency analysis",
            "cooccurrence": "/cooccurrence - Co-occurrence patterns and network metrics", 
            "thematic": "/thematic - Semantic category analysis",
            "clustering": "/clustering - Machine learning clustering results",
            "statistics": "/statistics - Dataset summary statistics"
        },
        "status": "active"
    }

@analytics_router.get("/frequency", response_model=Dict[str, Any])
async def get_frequency_analysis(
    min_frequency: Optional[int] = Query(None, description="Minimum frequency threshold"),
    category: Optional[str] = Query(None, description="Filter by semantic category"),
    revelation: Optional[str] = Query(None, description="Filter by revelation type")
):
    """Get comprehensive frequency analysis"""
    try:
        filters = {}
        if min_frequency:
            filters['min_frequency'] = min_frequency
        if category:
            filters['semantic_category'] = category
        if revelation:
            filters['revelation_type'] = revelation
        
        result = analytics_engine.frequency_analysis(filters)
        
        return {
            "success": True,
            "data": result,
            "metadata": create_response_metadata(
                total=result.get('total_unique_roots', 0),
                returned=len(result.get('top_frequent_roots', []))
            )
        }
        
    except Exception as e:
        logger.error(f"Error in frequency analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@analytics_router.get("/cooccurrence", response_model=Dict[str, Any])
async def get_cooccurrence_analysis(
    min_cooccurrence: int = Query(2, ge=1, description="Minimum co-occurrence threshold"),
    category: Optional[str] = Query(None, description="Filter by semantic category")
):
    """Get co-occurrence analysis and network metrics"""
    try:
        result = analytics_engine.cooccurrence_analysis(min_cooccurrence)
        
        return {
            "success": True,
            "data": result,
            "metadata": create_response_metadata(
                total=result.get('total_pairs_analyzed', 0),
                returned=len(result.get('top_cooccurring_pairs', []))
            )
        }
        
    except Exception as e:
        logger.error(f"Error in co-occurrence analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@analytics_router.get("/thematic", response_model=Dict[str, Any])
async def get_thematic_analysis():
    """Get thematic analysis of semantic categories"""
    try:
        result = analytics_engine.thematic_analysis()
        
        return {
            "success": True,
            "data": result,
            "metadata": create_response_metadata(
                total=len(result.get('category_distribution', {})),
                returned=len(result.get('category_distribution', {}))
            )
        }
        
    except Exception as e:
        logger.error(f"Error in thematic analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@analytics_router.get("/clustering", response_model=Dict[str, Any])
async def get_semantic_clustering(
    n_clusters: int = Query(8, ge=2, le=20, description="Number of clusters to create")
):
    """Get semantic clustering analysis"""
    try:
        result = analytics_engine.semantic_clustering(n_clusters)
        
        return {
            "success": True,
            "data": result,
            "metadata": create_response_metadata(
                total=result.get('clustering_metrics', {}).get('total_roots_clustered', 0),
                returned=len(result.get('clusters', {}))
            )
        }
        
    except Exception as e:
        logger.error(f"Error in semantic clustering: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@analytics_router.get("/statistics", response_model=Dict[str, Any])
async def get_dataset_statistics():
    """Get comprehensive dataset statistics"""
    try:
        # Basic dataset info
        dataset_info = {
            "total_entries": len(enhanced_df) if enhanced_df is not None else 0,
            "total_unique_roots": len(frequency_df) if frequency_df is not None else 0,
            "total_cooccurrence_pairs": len(cooccurrence_df) if cooccurrence_df is not None else 0,
            "creation_date": datetime.now().isoformat()
        }
        
        # Root statistics
        if frequency_df is not None and not frequency_df.empty:
            root_stats = {
                "frequency_stats": calculate_frequency_stats(frequency_df['total_frequency'].tolist()),
                "meccan_roots": len(frequency_df[frequency_df['meccan_frequency'] > 0]),
                "medinan_roots": len(frequency_df[frequency_df['medinan_frequency'] > 0]),
                "hapax_legomena": len(frequency_df[frequency_df['total_frequency'] == 1])
            }
        else:
            root_stats = {}
        
        # Category distribution
        if frequency_df is not None and not frequency_df.empty:
            category_dist = frequency_df['semantic_category'].value_counts().to_dict()
        else:
            category_dist = {}
        
        return {
            "success": True,
            "data": {
                "dataset_info": dataset_info,
                "root_statistics": root_stats,
                "categorical_distribution": category_dist
            },
            "metadata": create_response_metadata(
                total=dataset_info["total_entries"],
                returned=1
            )
        }
        
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Sura Endpoints
@suras_router.get("/", response_model=List[Dict[str, Any]])
async def get_suras(
    limit: int = Query(50, ge=1, le=114, description="Number of suras to return"),
    offset: int = Query(0, ge=0, description="Number of suras to skip"),
    revelation_type: Optional[str] = Query(None, description="Filter by revelation type")
):
    """Get list of suras with basic information"""
    try:
        if enhanced_df is None or enhanced_df.empty:
            raise HTTPException(status_code=503, detail="Data not available")
        
        # Get unique suras from dataset
        suras = enhanced_df.groupby('sura').agg({
            'aya': 'max',  # Max verse number = total verses
            'Root': 'nunique'  # Unique roots count
        }).reset_index()
        
        suras.columns = ['sura_number', 'verse_count', 'unique_roots_count']
        
        # Add revelation type and names
        sura_list = []
        for _, row in suras.iterrows():
            sura_info = {
                "sura_number": int(row['sura_number']),
                "verse_count": int(row['verse_count']),
                "unique_roots_count": int(row['unique_roots_count']),
                "revelation_type": get_revelation_type(int(row['sura_number'])),
                "name_arabic": f"سورة {row['sura_number']}",  # Placeholder
                "name_english": f"Sura {row['sura_number']}"  # Placeholder
            }
            
            if revelation_type and sura_info['revelation_type'].lower() != revelation_type.lower():
                continue
                
            sura_list.append(sura_info)
        
        # Apply pagination
        total = len(sura_list)
        paginated_suras = sura_list[offset:offset + limit]
        
        return paginated_suras
        
    except Exception as e:
        logger.error(f"Error getting suras: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@suras_router.get("/{sura_number}", response_model=Dict[str, Any])
async def get_sura_detail(sura_number: int):
    """Get detailed information about a specific sura"""
    try:
        # Validate sura number
        sura_number = validate_sura_number(sura_number)
        
        if enhanced_df is None or enhanced_df.empty:
            raise HTTPException(status_code=503, detail="Data not available")
        
        # Get sura data
        sura_data = enhanced_df[enhanced_df['sura'] == sura_number]
        if sura_data.empty:
            raise HTTPException(status_code=404, detail=f"Sura {sura_number} not found")
        
        # Basic info
        verse_count = sura_data['aya'].max()
        unique_roots = sura_data['Root'].unique()
        
        # Most frequent roots in this sura
        root_freq = sura_data['Root'].value_counts().head(10)
        most_frequent_roots = []
        for root, freq in root_freq.items():
            arabic_form = ""
            if frequency_df is not None:
                arabic_row = frequency_df[frequency_df['root'] == root]
                if not arabic_row.empty and 'root_arabic' in arabic_row.columns:
                    arabic_form = arabic_row['root_arabic'].iloc[0]
            
            most_frequent_roots.append({
                "root": root,
                "root_arabic": arabic_form,
                "frequency_in_sura": int(freq)
            })
        
        # Thematic breakdown
        if frequency_df is not None:
            # Get categories for roots in this sura
            sura_roots_with_categories = frequency_df[
                frequency_df['root'].isin(unique_roots)
            ]['semantic_category'].value_counts()
            thematic_breakdown = sura_roots_with_categories.to_dict()
        else:
            thematic_breakdown = {}
        
        return {
            "sura_number": sura_number,
            "verse_count": int(verse_count),
            "unique_roots_count": len(unique_roots),
            "revelation_type": get_revelation_type(sura_number),
            "name_arabic": f"سورة {sura_number}",
            "name_english": f"Sura {sura_number}",
            "most_frequent_roots": most_frequent_roots,
            "thematic_breakdown": thematic_breakdown,
            "metadata": create_response_metadata(
                total=len(unique_roots),
                returned=len(most_frequent_roots)
            )
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting sura detail: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@suras_router.post("/compare", response_model=Dict[str, Any])
async def compare_suras(request: SuraComparisonRequest):
    """Compare multiple suras"""
    try:
        if enhanced_df is None or enhanced_df.empty:
            raise HTTPException(status_code=503, detail="Data not available")
        
        # Validate sura numbers
        validated_suras = [validate_sura_number(s) for s in request.sura_numbers]
        
        comparison_data = {}
        
        for sura_num in validated_suras:
            sura_data = enhanced_df[enhanced_df['sura'] == sura_num]
            if not sura_data.empty:
                comparison_data[str(sura_num)] = {
                    "unique_roots": set(sura_data['Root'].unique()),
                    "total_words": len(sura_data),
                    "verse_count": sura_data['aya'].max()
                }
        
        # Calculate comparison metrics
        if request.comparison_metric == "vocabulary_overlap":
            result = _calculate_vocabulary_overlap(comparison_data)
        elif request.comparison_metric == "thematic_similarity":
            result = _calculate_thematic_similarity(comparison_data)
        else:
            result = {"note": f"Comparison metric '{request.comparison_metric}' not implemented"}
        
        return {
            "success": True,
            "comparison_metric": request.comparison_metric,
            "suras_compared": validated_suras,
            "data": result,
            "metadata": create_response_metadata(
                total=len(validated_suras),
                returned=len(validated_suras)
            )
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing suras: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Export Endpoints
@export_router.get("/", response_model=Dict[str, Any])
async def get_export_info():
    """Get export endpoints information"""
    return {
        "message": "Quranic Roots Export API",
        "available_endpoints": {
            "export_data": "POST / - Export data in specified format (JSON/CSV/XML)",
            "download": "GET /download/{filename} - Download exported files"
        },
        "supported_formats": ["json", "csv", "xml"],
        "supported_data_types": ["roots", "suras", "cooccurrence", "thematic"],
        "status": "active",
        "example_request": {
            "data_type": "roots",
            "format": "json",
            "filters": {
                "min_frequency": 10,
                "semantic_category": "divine_attributes"
            }
        }
    }

@export_router.post("/", response_model=Dict[str, Any])
async def export_data(request: ExportRequest, background_tasks: BackgroundTasks):
    """Export data in specified format"""
    try:
        # Validate data type
        if request.data_type not in ['roots', 'suras', 'cooccurrence', 'thematic']:
            raise HTTPException(status_code=400, detail="Invalid data type")
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{request.data_type}_export_{timestamp}.{request.format}"
        
        # Prepare data based on type
        if request.data_type == 'roots':
            data = _prepare_roots_export(request.filters)
        elif request.data_type == 'cooccurrence':
            data = _prepare_cooccurrence_export(request.filters)
        else:
            data = {"note": f"Export for {request.data_type} not implemented yet"}
        
        # Generate export file in background
        file_path = current_settings.get_export_file_path(filename)
        background_tasks.add_task(_generate_export_file, data, file_path, request.format)
        
        # Return download info
        expiry_time = datetime.now() + timedelta(hours=current_settings.export_url_expiry_hours)
        
        return {
            "success": True,
            "download_url": f"/api/v1/export/download/{filename}",
            "filename": filename,
            "estimated_size": len(str(data)),  # Rough estimate
            "record_count": len(data) if isinstance(data, list) else 1,
            "expiry_time": expiry_time.isoformat(),
            "status": "processing"
        }
        
    except Exception as e:
        logger.error(f"Error exporting data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@export_router.get("/download/{filename}")
async def download_export(filename: str):
    """Download exported file"""
    try:
        file_path = current_settings.get_export_file_path(filename)
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Export file not found")
        
        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type='application/octet-stream'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading export: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Utility Endpoints
@utilities_router.get("/", response_model=Dict[str, Any])
async def get_utilities_info():
    """Get utilities endpoints information"""
    return {
        "message": "Quranic Roots Utilities API",
        "available_endpoints": {
            "convert": "POST /convert - Convert between Arabic and Buckwalter transliteration",
            "search": "GET /search - Advanced search across the dataset"
        },
        "status": "active"
    }

@utilities_router.post("/convert", response_model=TextConversionResponse)
async def convert_text(request: TextConversionRequest):
    """Convert between Arabic and Buckwalter transliteration"""
    try:
        if request.from_format == request.to_format:
            converted_text = request.text
        elif request.from_format == "buckwalter" and request.to_format == "arabic":
            converted_text = buck_to_arabic(request.text)
        elif request.from_format == "arabic" and request.to_format == "buckwalter":
            converted_text = arabic_to_buck(request.text)
        else:
            raise HTTPException(status_code=400, detail="Invalid conversion format")
        
        return TextConversionResponse(
            original_text=request.text,
            converted_text=converted_text,
            from_format=request.from_format,
            to_format=request.to_format
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error converting text: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@utilities_router.get("/search", response_model=Dict[str, Any])
async def advanced_search(
    query: str = Query(..., description="Search query"),
    search_in: str = Query("roots", description="What to search in: roots, suras, or both"),
    limit: int = Query(50, ge=1, le=1000, description="Result limit")
):
    """Advanced search across the dataset"""
    try:
        normalized_query = normalize_search_query(query)
        results = []
        
        if search_in in ["roots", "both"] and frequency_df is not None:
            # Search in roots
            root_matches = frequency_df[
                frequency_df['root'].str.contains(normalized_query, case=False, na=False) |
                frequency_df.get('root_arabic', pd.Series()).str.contains(query, case=False, na=False)
            ].head(limit)
            
            for _, row in root_matches.iterrows():
                results.append({
                    "type": "root",
                    "root": row['root'],
                    "root_arabic": row.get('root_arabic', ''),
                    "frequency": int(row['total_frequency']),
                    "category": row['semantic_category']
                })
        
        return {
            "success": True,
            "query": query,
            "results": results,
            "metadata": create_response_metadata(
                total=len(results),
                returned=len(results)
            )
        }
        
    except Exception as e:
        logger.error(f"Error in advanced search: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Helper functions
def _calculate_vocabulary_overlap(comparison_data: Dict) -> Dict[str, Any]:
    """Calculate vocabulary overlap between suras"""
    sura_roots = {sura: data["unique_roots"] for sura, data in comparison_data.items()}
    
    # Calculate pairwise overlaps
    overlaps = {}
    sura_list = list(sura_roots.keys())
    
    for i in range(len(sura_list)):
        for j in range(i + 1, len(sura_list)):
            sura1, sura2 = sura_list[i], sura_list[j]
            intersection = len(sura_roots[sura1] & sura_roots[sura2])
            union = len(sura_roots[sura1] | sura_roots[sura2])
            
            overlaps[f"{sura1}-{sura2}"] = {
                "intersection": intersection,
                "union": union,
                "jaccard_similarity": intersection / union if union > 0 else 0
            }
    
    return overlaps

def _calculate_thematic_similarity(comparison_data: Dict) -> Dict[str, Any]:
    """Calculate thematic similarity between suras"""
    # This would require more complex analysis
    return {"note": "Thematic similarity calculation not implemented yet"}

def _prepare_roots_export(filters: Optional[Dict]) -> List[Dict]:
    """Prepare roots data for export"""
    if frequency_df is None:
        return []
    
    df = frequency_df.copy()
    
    # Apply filters if provided
    if filters:
        if 'min_frequency' in filters:
            df = df[df['total_frequency'] >= filters['min_frequency']]
        if 'semantic_category' in filters:
            df = df[df['semantic_category'] == filters['semantic_category']]
    
    return df.to_dict('records')

def _prepare_cooccurrence_export(filters: Optional[Dict]) -> List[Dict]:
    """Prepare co-occurrence data for export"""
    if cooccurrence_df is None:
        return []
    
    df = cooccurrence_df.copy()
    
    # Apply filters if provided
    if filters:
        if 'min_cooccurrence' in filters:
            df = df[df['cooccurrence_count'] >= filters['min_cooccurrence']]
    
    return df.to_dict('records')

async def _generate_export_file(data: Any, file_path: Path, format: str):
    """Generate export file in background"""
    try:
        if format == "json":
            content = export_to_json(data, pretty=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        elif format == "csv":
            content = export_to_csv(data)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        logger.info(f"Export file generated: {file_path}")
    except Exception as e:
        logger.error(f"Error generating export file: {e}")

# Include all routers
all_routers = [roots_router, analytics_router, suras_router, export_router, utilities_router] 