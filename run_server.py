"""
Server startup script with environment check.
"""
import os
import sys

# Check if .env file exists
if not os.path.exists('.env'):
    print("=" * 60)
    print("WARNING: .env file not found!")
    print("=" * 60)
    print("\nPlease create a .env file with the following variables:")
    print("\n  DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT].supabase.co:5432/postgres")
    print("  SUPABASE_URL=https://[PROJECT].supabase.co")
    print("  SUPABASE_KEY=your-anon-key")
    print("  SUPABASE_JWT_SECRET=your-jwt-secret")
    print("  APP_NAME=Smart Student Expense & Budget System")
    print("  DEBUG=True")
    print("\nSee QUICKSTART.md for detailed setup instructions.")
    print("=" * 60)
    sys.exit(1)

# Import and run server
if __name__ == "__main__":
    try:
        import uvicorn
        print("Starting FastAPI server...")
        print("API Documentation: http://localhost:8000/docs")
        print("Press CTRL+C to stop\n")
        
        # This guard is required for Windows to avoid infinite reload loops
        uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
        
    except KeyboardInterrupt:
        print("\n\nServer stopped.")
    except Exception as e:
        print(f"\nERROR: Failed to start server: {e}")
        sys.exit(1)