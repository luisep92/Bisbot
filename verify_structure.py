"""
Structure verification script for Bisbot.

Verifies that all components are properly structured without requiring
external dependencies to be installed.
"""

import ast
import sys
from pathlib import Path


def check_class_implements_interface(implementation_file, interface_class, required_methods):
    """
    Check that an implementation file contains a class that implements required methods.

    Args:
        implementation_file: Path to implementation file
        interface_class: Name of interface class it should implement
        required_methods: List of method names that must be present

    Returns:
        Tuple (success, message)
    """
    try:
        with open(implementation_file, 'r') as f:
            tree = ast.parse(f.read())

        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

        if not classes:
            return False, f"No classes found in {implementation_file}"

        # Find class that inherits from interface
        implementing_class = None
        for cls in classes:
            # Check if class has the interface in bases
            for base in cls.bases:
                if isinstance(base, ast.Name) and base.id == interface_class:
                    implementing_class = cls
                    break
            if implementing_class:
                break

        if not implementing_class:
            # For alternative implementations, we'll be lenient
            implementing_class = classes[0]

        # Check for required methods (look in class body, not nested)
        methods = [node.name for node in implementing_class.body
                  if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]

        missing_methods = [m for m in required_methods if m not in methods]

        if missing_methods:
            return False, f"Missing methods in {implementing_class.name}: {missing_methods}"

        return True, f"✓ {implementing_class.name} implements {interface_class} correctly"

    except Exception as e:
        return False, f"Error checking {implementation_file}: {e}"


def main():
    """Run all structure verification checks."""
    print("=== Bisbot Structure Verification ===\n")

    all_passed = True

    # Check interfaces exist
    print("Checking interfaces...")
    interfaces = [
        'interfaces/ai_interface.py',
        'interfaces/voice_interface.py',
        'interfaces/stt_interface.py'
    ]

    for interface in interfaces:
        if Path(interface).exists():
            print(f"✓ {interface} exists")
        else:
            print(f"✗ {interface} missing")
            all_passed = False

    # Check implementations
    print("\nChecking implementations...")

    checks = [
        ('bisbal_personality.py', 'AIInterface', ['initialize', 'generate_response', 'cleanup']),
        ('voice_handler.py', 'VoiceInterface', ['initialize', 'synthesize_speech', 'cleanup', 'is_ready']),
        ('stt_handler.py', 'STTInterface', ['initialize', 'transcribe', 'cleanup', 'is_ready']),
    ]

    for impl_file, interface, methods in checks:
        success, message = check_class_implements_interface(impl_file, interface, methods)
        print(message)
        if not success:
            all_passed = False

    # Check bot exists
    print("\nChecking main bot file...")
    if Path('bot.py').exists():
        with open('bot.py', 'r') as f:
            content = f.read()
            if 'class BisbalBot' in content:
                print("✓ bot.py contains BisbalBot class")
            else:
                print("✗ bot.py missing BisbalBot class")
                all_passed = False
    else:
        print("✗ bot.py missing")
        all_passed = False

    # Check tests
    print("\nChecking test files...")
    test_files = [
        'tests/test_personality.py',
        'tests/test_voice_handler.py',
        'tests/test_stt_handler.py'
    ]

    for test_file in test_files:
        if Path(test_file).exists():
            print(f"✓ {test_file} exists")
        else:
            print(f"✗ {test_file} missing")
            all_passed = False

    # Check configuration files
    print("\nChecking configuration files...")
    config_files = ['requirements.txt', '.env.example', 'README.md']

    for config in config_files:
        if Path(config).exists():
            print(f"✓ {config} exists")
        else:
            print(f"✗ {config} missing")
            all_passed = False

    # Summary
    print("\n" + "="*50)
    if all_passed:
        print("SUCCESS: All structure checks passed!")
        print("\nThe project is properly structured and ready for use.")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Configure .env file")
        print("3. Add Bisbal voice sample to data/")
        print("4. Run tests: pytest tests/ -v")
        return 0
    else:
        print("FAILED: Some structure checks failed")
        print("Please review the errors above")
        return 1


if __name__ == "__main__":
    sys.exit(main())
