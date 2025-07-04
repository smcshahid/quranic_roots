"""
Simple test server to debug startup issues
"""

import uvicorn
import sys
from pathlib import Path

# Ensure we can import from the backend directory
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from startup import create_application

if __name__ == "__main__":
    print("🔍 Creating application...")
    print(f"📁 Running from: {Path.cwd()}")
    print(f"📁 Backend directory: {backend_dir}")
    print(f"📁 Project root: {backend_dir.parent}")
    
    try:
        app = create_application()
        print("✅ Application created successfully!")
        
        print("🚀 Starting simple server on localhost:8000...")
        print("📚 API Documentation: http://127.0.0.1:8000/docs")
        print("🔍 Health Check: http://127.0.0.1:8000/health")
        print("📊 Root endpoints: http://127.0.0.1:8000/api/v1/roots/")
        print("📈 Analytics: http://127.0.0.1:8000/api/v1/analytics/")
        print("📤 Export: http://127.0.0.1:8000/api/v1/export/")
        print("🛠️ Utils: http://127.0.0.1:8000/api/v1/utils/")
        print("\nPress Ctrl+C to stop the server")
        
        uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc() 