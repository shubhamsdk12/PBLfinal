"""
Quick start script for the backend server.
"""
import subprocess
import sys

def main():
    print("\n[Starting] Smart Student Expense & Budget System API...")
    print("[Docs] API Docs: http://localhost:8000/docs")
    print("[Docs] ReDoc:    http://localhost:8000/redoc\n")

    try:
        subprocess.run(
            [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
            check=True,
        )
    except KeyboardInterrupt:
        print("\n\nServer stopped.")
    except FileNotFoundError:
        print("\n[ERROR] uvicorn not found. Install dependencies first:")
        print("  pip install -r requirements.txt")

if __name__ == "__main__":
    main()