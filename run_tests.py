#!/usr/bin/env python3
"""
Minimal Test Runner for Insight Journey Backend
Simplified version for essential testing only.
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path


def check_environment():
    """Check if essential environment variables are set."""
    print("🔍 Checking test environment...")
    
    checks = [
        ("OpenAI API Key", os.getenv("OPENAI_API_KEY")),
        ("Neo4j URI", os.getenv("NEO4J_URI")),
        ("Neo4j User", os.getenv("NEO4J_USER") or os.getenv("NEO4J_USERNAME")),
        ("Neo4j Password", os.getenv("NEO4J_PASSWORD")),
        ("JWT Secret", os.getenv("JWT_SECRET")),
    ]
    
    all_good = True
    for name, value in checks:
        if value:
            print(f"  ✅ {name}")
        else:
            print(f"  ❌ {name}")
            all_good = False
    
    return all_good


def run_tests(test_type="essential", verbose=False):
    """Run the specified tests."""
    cmd = ["python", "-m", "pytest"]
    
    if verbose:
        cmd.append("-v")
    
    if test_type == "essential":
        cmd.extend(["-m", "essential", "tests/test_essential.py"])
    elif test_type == "unit":
        cmd.extend(["-m", "unit", "tests/unit/"])
    elif test_type == "integration":
        cmd.extend(["-m", "integration", "tests/integration/"])
    elif test_type == "auth-api":
        cmd.extend(["-m", "auth and api", "tests/test_auth_api.py"])
    elif test_type == "api":
        cmd.extend(["-m", "api", "tests/"])
    elif test_type == "all":
        cmd.append("tests/")
    else:
        cmd.append(f"tests/{test_type}")
    
    print(f"🧪 Running {test_type} tests...")
    result = subprocess.run(cmd, capture_output=False)
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(description="Minimal Test Runner")
    parser.add_argument("--check-env", action="store_true", help="Check environment only")
    parser.add_argument("--essential", action="store_true", help="Run essential tests only")
    parser.add_argument("--unit", action="store_true", help="Run unit tests")
    parser.add_argument("--integration", action="store_true", help="Run integration tests")
    parser.add_argument("--auth-api", action="store_true", help="Run authentication API tests")
    parser.add_argument("--api", action="store_true", help="Run all API tests")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    print("🧪 MINIMAL TEST RUNNER")
    print("=" * 50)
    
    # Check environment
    env_ok = check_environment()
    
    if args.check_env:
        if env_ok:
            print("\n✅ All environment checks passed!")
        else:
            print("\n❌ Some environment checks failed!")
            sys.exit(1)
        return
    
    if not env_ok:
        print("\n⚠️  Some environment variables missing, but continuing...")
    
    # Determine what tests to run
    if args.all:
        test_type = "all"
    elif args.unit:
        test_type = "unit"
    elif args.integration:
        test_type = "integration"
    elif args.auth_api:
        test_type = "auth-api"
    elif args.api:
        test_type = "api"
    elif args.essential:
        test_type = "essential"
    else:
        # Interactive mode
        print("\nAvailable tests:")
        print("1. Essential tests (recommended)")
        print("2. Unit tests") 
        print("3. Integration tests")
        print("4. Authentication API tests")
        print("5. All API tests")
        print("6. All tests")
        print("0. Exit")
        
        choice = input("\nSelect tests to run (1-6): ").strip()
        
        if choice == "1":
            test_type = "essential"
        elif choice == "2":
            test_type = "unit"
        elif choice == "3":
            test_type = "integration"
        elif choice == "4":
            test_type = "auth-api"
        elif choice == "5":
            test_type = "api"
        elif choice == "6":
            test_type = "all"
        elif choice == "0":
            print("Exiting...")
            return
        else:
            print("Invalid choice")
            return
    
    # Run tests
    success = run_tests(test_type, args.verbose)
    
    if success:
        print(f"\n✅ {test_type.title()} tests completed successfully!")
    else:
        print(f"\n❌ {test_type.title()} tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main() 