"""
Quranic Roots Analysis - Backend API
Main FastAPI application entry point

Phase 2: Backend API & Analytics Engine
"""

from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import pandas as pd
import numpy as np
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

# Import our custom modules
from models import *
from analytics import QuranicAnalytics
from utils import buck_to_arabic, arabic_to_buck

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Quranic Roots Analysis API",
    description="Advanced API for analyzing Quranic root words, morphology, and semantic patterns",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize analytics engine
analytics = QuranicAnalytics()

# Load enhanced dataset on startup
@app.on_event("startup")
async def startup_event():
    """Initialize the application with data loading"""
    logger.info("🚀 Starting Quranic Roots Analysis API...")
    
    try:
        # Load the enhanced dataset
        global enhanced_df
        enhanced_df = pd.read_csv('quran-enhanced-phase1.csv')
        logger.info(f"✅ Loaded enhanced dataset: {len(enhanced_df):,} entries")
        
        # Load frequency analysis
        global frequency_df
        frequency_df = pd.read_csv('root-frequency-analysis.csv')
        logger.info(f"✅ Loaded frequency analysis: {len(frequency_df):,} roots")
        
        # Load co-occurrence data
        global cooccurrence_df
        cooccurrence_df = pd.read_csv('root-cooccurrence-matrix.csv')
        logger.info(f"✅ Loaded co-occurrence matrix: {len(cooccurrence_df):,} pairs")
        
        logger.info("🎯 API Ready for requests!")
        
    except Exception as e:
        logger.error(f"❌ Failed to load data: {e}")
        raise

@app.get("/")
async def root():
    """API Root endpoint with basic information"""
    return {
        "message": "Quranic Roots Analysis API",
        "version": "2.0.0",
        "status": "active",
        "phase": "Phase 2: Backend API & Analytics Engine",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "roots": "/api/v1/roots/",
            "suras": "/api/v1/suras/",
            "analytics": "/api/v1/analytics/"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "data_loaded": {
            "enhanced_dataset": len(enhanced_df) if 'enhanced_df' in globals() else 0,
            "frequency_analysis": len(frequency_df) if 'frequency_df' in globals() else 0,
            "cooccurrence_matrix": len(cooccurrence_df) if 'cooccurrence_df' in globals() else 0
        }
    }

# Root API endpoints
@app.get("/api/v1/roots/", response_model=List[RootResponse])
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
                df['root_arabic'].str.contains(search, case=False, na=False)
            )
            df = df[search_mask]
        
        # Apply pagination
        total = len(df)
        df = df.iloc[offset:offset + limit]
        
        # Convert to response format
        roots = []
        for _, row in df.iterrows():
            roots.append(RootResponse(
                root_buckwalter=row['root'],
                root_arabic=row['root_arabic'],
                semantic_category=row['semantic_category'],
                total_frequency=int(row['total_frequency']),
                meccan_frequency=int(row['meccan_frequency']),
                medinan_frequency=int(row['medinan_frequency']),
                meccan_ratio=float(row['meccan_ratio']),
                frequency_rank=int(df.index.get_loc(row.name) + 1)
            ))
        
        return roots
        
    except Exception as e:
        logger.error(f"Error in get_roots: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/roots/{root_id}", response_model=RootDetailResponse)
async def get_root_detail(root_id: str):
    """Get detailed information about a specific root"""
    try:
        # Find root in frequency data
        root_data = frequency_df[frequency_df['root'] == root_id]
        if root_data.empty:
            # Try Arabic search
            root_data = frequency_df[frequency_df['root_arabic'] == root_id]
            if root_data.empty:
                raise HTTPException(status_code=404, detail=f"Root '{root_id}' not found")
        
        root_info = root_data.iloc[0]
        
        # Get related co-occurrences
        related_roots = cooccurrence_df[
            (cooccurrence_df['root1'] == root_info['root']) | 
            (cooccurrence_df['root2'] == root_info['root'])
        ].head(10)
        
        # Get usage examples from enhanced dataset
        usage_examples = enhanced_df[
            enhanced_df['Root'] == root_info['root']
        ].head(5)[['sura', 'aya', 'FORM', 'TAG']].to_dict('records')
        
        return RootDetailResponse(
            root_buckwalter=root_info['root'],
            root_arabic=root_info['root_arabic'],
            semantic_category=root_info['semantic_category'],
            total_frequency=int(root_info['total_frequency']),
            meccan_frequency=int(root_info['meccan_frequency']),
            medinan_frequency=int(root_info['medinan_frequency']),
            meccan_ratio=float(root_info['meccan_ratio']),
            frequency_rank=int(root_data.index[0] + 1),
            related_roots=[
                {
                    "root": r['root2'] if r['root1'] == root_info['root'] else r['root1'],
                    "cooccurrence_count": int(r['cooccurrence_count'])
                }
                for _, r in related_roots.iterrows()
            ],
            usage_examples=usage_examples
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_root_detail: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 