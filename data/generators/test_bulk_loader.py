#!/usr/bin/env python3
"""
Test Script for Bulk Data Loader

This script tests the bulk loader functionality with a single user
to verify everything works before running the full dataset.

Usage:
    python test_bulk_loader.py
    python test_bulk_loader.py --dry-run
"""

import sys
import argparse
from pathlib import Path

# Import our bulk loader
from bulk_data_loader import BulkDataLoader

def test_single_user():
    """Test with just Alex to verify functionality"""
    print("🧪 TESTING BULK DATA LOADER")
    print("=" * 50)
    print("Testing with Alex user only...")
    print()
    
    # Create loader instance
    loader = BulkDataLoader(dry_run=False)
    
    # Test with just Alex
    try:
        loader.run(specific_users=["Alex"])
        print("\n✅ Test completed successfully!")
        print("You can now run the full bulk loader with confidence.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        return False
    
    return True

def test_dry_run():
    """Test dry run mode with all users"""
    print("🔍 TESTING DRY RUN MODE")
    print("=" * 50)
    print("Testing dry run with all users...")
    print()
    
    # Create loader instance in dry run mode
    loader = BulkDataLoader(dry_run=True)
    
    # Test dry run with all users
    try:
        loader.run()
        print("\n✅ Dry run completed successfully!")
        print("Structure and data look good for full execution.")
        
    except Exception as e:
        print(f"\n❌ Dry run failed: {str(e)}")
        return False
    
    return True

def main():
    """Main test function"""
    parser = argparse.ArgumentParser(description="Test the bulk data loader")
    parser.add_argument("--dry-run-only", action="store_true", 
                       help="Only test dry run mode, don't make real API calls")
    
    args = parser.parse_args()
    
    print("🧪 BULK DATA LOADER TESTING SUITE")
    print("=" * 60)
    print("This script tests the bulk loader before running the full dataset")
    print("=" * 60)
    print()
    
    # Always test dry run first
    print("STEP 1: Testing dry run mode...")
    if not test_dry_run():
        print("❌ Dry run test failed. Please check the setup.")
        sys.exit(1)
    
    print("\n" + "-" * 50)
    
    if not args.dry_run_only:
        print("STEP 2: Testing with real API calls (Alex only)...")
        if not test_single_user():
            print("❌ Real API test failed. Please check backend connectivity.")
            sys.exit(1)
        
        print("\n🎉 ALL TESTS PASSED!")
        print("You can now run the full bulk loader:")
        print("   python bulk_data_loader.py")
    else:
        print("\n🎉 DRY RUN TEST PASSED!")
        print("To test with real API calls:")
        print("   python test_bulk_loader.py")
        print("To run the full bulk loader:")
        print("   python bulk_data_loader.py")

if __name__ == "__main__":
    main() 