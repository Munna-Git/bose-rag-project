#!/usr/bin/env python3
"""
Clear ChromaDB database and start fresh
"""
import sys
from pathlib import Path
import shutil

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import config
from src.error_handling.logger import logger


def main():
    """Clear the vector database"""
    
    print("=" * 70)
    print("ChromaDB Database Cleaner")
    print("=" * 70)
    
    db_path = config.VECTOR_DB_DIR
    
    print(f"\nDatabase path: {db_path}")
    
    if not db_path.exists():
        print("\nDatabase directory doesn't exist. Nothing to clear.")
        return 0
    
    # Confirm
    print("\nWARNING: This will delete all stored documents!")
    response = input("Are you sure you want to continue? (yes/no): ")
    
    if response.lower() != 'yes':
        print("\nCancelled.")
        return 0
    
    try:
        # Remove database directory
        shutil.rmtree(db_path)
        print(f"\nSUCCESS: Database cleared!")
        print(f"Removed: {db_path}")
        
        # Recreate directory
        db_path.mkdir(parents=True, exist_ok=True)
        print(f"Created empty directory: {db_path}")
        
        print("\nYou can now run demo.py to process documents again.")
        
        return 0
    
    except Exception as e:
        logger.error(f"Failed to clear database: {str(e)}")
        print(f"\nERROR: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
