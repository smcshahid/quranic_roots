"""
Startup script for Quranic Roots Analysis API
Phase 2: Backend API & Analytics Engine
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add the backend directory to the path
sys.path.insert(0, str(Path(__file__).parent))

import uvicorn
import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import current_settings
from analytics import QuranicAnalytics
from api_endpoints import all_routers, initialize_data
from models import *
from utils import *

# Configure logging
logging.basicConfig(
    level=getattr(logging, current_settings.log_level),
    format=current_settings.log_format
)
logger = logging.getLogger(__name__)

def create_application() -> FastAPI:
    """Create and configure the FastAPI application"""
    
    app = FastAPI(
        title=current_settings.app_name,
        description="Advanced API for analyzing Quranic root words, morphology, and semantic patterns",
        version=current_settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        **current_settings.cors_config
    )
    
    # Global variables for data
    app.state.enhanced_df = None
    app.state.frequency_df = None
    app.state.cooccurrence_df = None
    app.state.analytics_engine = None
    
    @app.on_event("startup")
    async def startup_event():
        """Initialize the application with data loading"""
        logger.info("🚀 Starting Quranic Roots Analysis API...")
        logger.info(f"Environment: {current_settings.environment}")
        logger.info(f"Debug mode: {current_settings.debug}")
        
        try:
            # Load the enhanced dataset
            enhanced_file = current_settings.get_data_file_path(current_settings.enhanced_dataset_file)
            if enhanced_file.exists():
                app.state.enhanced_df = pd.read_csv(enhanced_file)
                logger.info(f"✅ Loaded enhanced dataset: {len(app.state.enhanced_df):,} entries")
            else:
                logger.warning(f"⚠️ Enhanced dataset not found: {enhanced_file}")
                app.state.enhanced_df = pd.DataFrame()
            
            # Load frequency analysis
            frequency_file = current_settings.get_data_file_path(current_settings.frequency_analysis_file)
            if frequency_file.exists():
                app.state.frequency_df = pd.read_csv(frequency_file)
                logger.info(f"✅ Loaded frequency analysis: {len(app.state.frequency_df):,} roots")
            else:
                logger.warning(f"⚠️ Frequency analysis not found: {frequency_file}")
                app.state.frequency_df = pd.DataFrame()
            
            # Load co-occurrence data
            cooccurrence_file = current_settings.get_data_file_path(current_settings.cooccurrence_matrix_file)
            if cooccurrence_file.exists():
                app.state.cooccurrence_df = pd.read_csv(cooccurrence_file)
                logger.info(f"✅ Loaded co-occurrence matrix: {len(app.state.cooccurrence_df):,} pairs")
            else:
                logger.warning(f"⚠️ Co-occurrence matrix not found: {cooccurrence_file}")
                app.state.cooccurrence_df = pd.DataFrame()
            
            # Initialize analytics engine
            app.state.analytics_engine = QuranicAnalytics()
            logger.info("✅ Analytics engine initialized")
            
            # Initialize API endpoints with data
            initialize_data(
                app.state.enhanced_df,
                app.state.frequency_df,
                app.state.cooccurrence_df,
                app.state.analytics_engine
            )
            
            logger.info("🎯 API Ready for requests!")
            logger.info(f"📊 Dataset Summary:")
            logger.info(f"   - Enhanced entries: {len(app.state.enhanced_df):,}")
            logger.info(f"   - Unique roots: {len(app.state.frequency_df):,}")
            logger.info(f"   - Co-occurrence pairs: {len(app.state.cooccurrence_df):,}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize application: {e}")
            raise
    
    @app.on_event("shutdown")
    async def shutdown_event():
        """Cleanup on application shutdown"""
        logger.info("🛑 Shutting down Quranic Roots Analysis API...")
    
    @app.get("/")
    async def root():
        """API Root endpoint with basic information"""
        return {
            "message": "Quranic Roots Analysis API",
            "version": current_settings.app_version,
            "status": "active",
            "phase": "Phase 2: Backend API & Analytics Engine",
            "environment": current_settings.environment,
            "endpoints": {
                "docs": "/docs",
                "redoc": "/redoc",
                "health": "/health",
                "roots": f"{current_settings.api_v1_prefix}/roots/",
                "suras": f"{current_settings.api_v1_prefix}/suras/",
                "analytics": f"{current_settings.api_v1_prefix}/analytics/",
                "export": f"{current_settings.api_v1_prefix}/export/",
                "utils": f"{current_settings.api_v1_prefix}/utils/"
            }
        }
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "environment": current_settings.environment,
            "version": current_settings.app_version,
            "data_status": {
                "enhanced_dataset": len(app.state.enhanced_df) if app.state.enhanced_df is not None else 0,
                "frequency_analysis": len(app.state.frequency_df) if app.state.frequency_df is not None else 0,
                "cooccurrence_matrix": len(app.state.cooccurrence_df) if app.state.cooccurrence_df is not None else 0,
                "analytics_engine": "available" if app.state.analytics_engine else "unavailable"
            }
        }
    
    # Include API routers
    for router in all_routers:
        app.include_router(router, prefix=current_settings.api_v1_prefix)
    
    return app

def run_server():
    """Run the development server"""
    logger.info(f"🌐 Starting server on {current_settings.host}:{current_settings.port}")
    logger.info(f"📚 API Documentation: http://{current_settings.host}:{current_settings.port}/docs")
    logger.info(f"🔄 Reload enabled: {current_settings.reload}")
    
    if current_settings.reload:
        # Use import string for reload mode
        uvicorn.run(
            "startup:create_application",
            host=current_settings.host,
            port=current_settings.port,
            reload=True,
            log_level=current_settings.log_level.lower(),
            factory=True
        )
    else:
        # Use app instance for production
        app = create_application()
        uvicorn.run(
            app,
            host=current_settings.host,
            port=current_settings.port,
            reload=False,
            log_level=current_settings.log_level.lower(),
            workers=current_settings.workers
        )

def run_production():
    """Run the production server"""
    import os
    os.environ["ENVIRONMENT"] = "production"
    
    from config import get_settings
    settings = get_settings()
    
    app = create_application()
    
    logger.info(f"🚀 Starting production server on {settings.host}:{settings.port}")
    logger.info(f"👥 Workers: {settings.workers}")
    
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        workers=settings.workers,
        log_level=settings.log_level.lower(),
        reload=False
    )

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Quranic Roots Analysis API Server")
    parser.add_argument("--mode", choices=["dev", "prod"], default="dev", help="Server mode")
    parser.add_argument("--host", default=current_settings.host, help="Host to bind to")
    parser.add_argument("--port", type=int, default=current_settings.port, help="Port to bind to")
    
    args = parser.parse_args()
    
    # Override settings with command line arguments
    current_settings.host = args.host
    current_settings.port = args.port
    
    try:
        if args.mode == "prod":
            run_production()
        else:
            run_server()
    except KeyboardInterrupt:
        logger.info("👋 Server stopped by user")
    except Exception as e:
        logger.error(f"💥 Server failed to start: {e}")
        sys.exit(1) 