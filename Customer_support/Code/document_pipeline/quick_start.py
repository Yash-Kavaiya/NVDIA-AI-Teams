"""
Quick start script for the document pipeline.
This script runs the complete pipeline: setup → ingest → test
"""
import subprocess
import sys
import time
from pathlib import Path

def print_header(text):
    """Print formatted header."""
    print(f"\n{'='*80}")
    print(f"  {text}")
    print(f"{'='*80}\n")

def print_step(step, total, description):
    """Print step information."""
    print(f"\n[Step {step}/{total}] {description}")
    print("-" * 80)

def run_command(cmd, description):
    """Run a command and return success status."""
    print(f"Running: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} - Success")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} - Failed")
        print(f"Error: {e.stderr}")
        return False

def check_qdrant():
    """Check if Qdrant is running."""
    try:
        import requests
        response = requests.get("http://localhost:6333/", timeout=2)
        return response.status_code == 200
    except:
        return False

def main():
    """Run the complete pipeline setup and test."""
    print_header("Customer Support Document Pipeline - Quick Start")
    
    current_dir = Path(__file__).parent
    data_dir = current_dir.parent.parent / "Data"
    
    # Step 1: Check Qdrant
    print_step(1, 5, "Checking Qdrant Vector Database")
    if check_qdrant():
        print("✓ Qdrant is already running at http://localhost:6333")
    else:
        print("✗ Qdrant is not running")
        print("\nPlease start Qdrant:")
        print("  docker run -d -p 6333:6333 -p 6334:6334 -v qdrant_storage:/qdrant/storage --name qdrant qdrant/qdrant")
        print("\nOr if already installed, start it:")
        print("  docker start qdrant")
        
        response = input("\nPress Enter after starting Qdrant (or 'q' to quit): ")
        if response.lower() == 'q':
            return
        
        # Wait a bit for Qdrant to start
        print("Waiting for Qdrant to start...")
        time.sleep(3)
        
        if not check_qdrant():
            print("✗ Still cannot connect to Qdrant. Please check Docker logs.")
            return
        
        print("✓ Qdrant is now running")
    
    # Step 2: Check for PDFs
    print_step(2, 5, "Checking for PDF files")
    data_dir.mkdir(parents=True, exist_ok=True)
    pdf_files = list(data_dir.glob("*.pdf"))
    
    if pdf_files:
        print(f"✓ Found {len(pdf_files)} PDF file(s) in {data_dir}")
        for pdf in pdf_files:
            print(f"  - {pdf.name}")
    else:
        print(f"✗ No PDF files found in {data_dir}")
        print("\nOptions:")
        print("1. Create a test PDF with CPSC content")
        print("2. Add your own PDFs to the Data folder and run again")
        
        choice = input("\nEnter choice (1 or 2): ").strip()
        
        if choice == "1":
            print("\nCreating test PDF...")
            success = run_command(
                f"python {current_dir / 'create_test_pdf.py'}",
                "Test PDF creation"
            )
            if not success:
                print("Failed to create test PDF. Install reportlab:")
                print("  pip install reportlab")
                return
        else:
            print("\nPlease add PDF files to:")
            print(f"  {data_dir}")
            print("Then run this script again.")
            return
    
    # Step 3: Run ingestion
    print_step(3, 5, "Running Document Ingestion")
    print("This will:")
    print("  1. Extract text from PDFs using Docling OCR")
    print("  2. Chunk documents (512 tokens, 50 overlap)")
    print("  3. Generate embeddings using NVIDIA API")
    print("  4. Store in Qdrant vector database")
    
    response = input("\nProceed with ingestion? (y/n): ")
    if response.lower() != 'y':
        print("Skipping ingestion...")
    else:
        success = run_command(
            f"python {current_dir / 'main.py'}",
            "Document ingestion"
        )
        if not success:
            print("\n✗ Ingestion failed. Check logs/pipeline.log for details.")
            return
    
    # Step 4: Run tests
    print_step(4, 5, "Running Search Tests")
    print("\nTest modes available:")
    print("1. Single query test")
    print("2. Batch test (8 CPSC queries)")
    print("3. Custom query")
    
    print("\nTo run tests manually:")
    print(f"  cd {current_dir / 'tests'}")
    print("  python test_search.py")
    
    # Step 5: Summary
    print_step(5, 5, "Setup Complete!")
    print("\n✓ Pipeline is ready to use!")
    print("\nNext steps:")
    print("1. Run tests:")
    print(f"   cd {current_dir / 'tests'}")
    print("   python test_search.py")
    print("\n2. View Qdrant dashboard:")
    print("   http://localhost:6333/dashboard")
    print("\n3. Check logs:")
    print(f"   {current_dir / 'logs' / 'pipeline.log'}")
    print("\n4. Add more PDFs:")
    print(f"   {data_dir}")
    print("   Then run: python main.py")
    
    print_header("All Done!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
    except Exception as e:
        print(f"\n\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
