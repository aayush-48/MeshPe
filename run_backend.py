import uvicorn
import os
import sys

if __name__ == "__main__":
    # Ensure we are running from the project root
    sys.path.append(os.getcwd())
    
    print("Starting MeshPe Backend on http://localhost:8000")
    print("Note: First startup may take time to load ML models...")
    
    uvicorn.run("backend.app:app", host="0.0.0.0", port=8000, reload=True)
