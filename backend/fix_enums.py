#!/usr/bin/env python
"""
Fix all SQLEnum definitions to use values_callable for proper enum value handling.

This script adds values_callable=lambda x: [e.value for e in x] to all SQLEnum
definitions that don't already have it, ensuring PostgreSQL uses the enum values
rather than names.
"""

import re
import sys
from pathlib import Path

def fix_sql_enum(content: str) -> tuple[str, int]:
    """
    Fix SQLEnum definitions in a file content.

    Returns:
        tuple: (fixed_content, number_of_fixes)
    """
    fixes = 0

    # Pattern to match SQLEnum(...) that doesn't have values_callable
    # This matches multiline SQLEnum definitions
    pattern = r'SQLEnum\(([^)]+)\)'

    def replacer(match):
        nonlocal fixes
        sql_enum_content = match.group(1)

        # Check if values_callable is already present
        if 'values_callable' in sql_enum_content:
            return match.group(0)  # No change needed

        # Check if this has create_type parameter
        if 'create_type' in sql_enum_content:
            # Add values_callable before the closing parenthesis
            fixed = f'SQLEnum({sql_enum_content}, values_callable=lambda x: [e.value for e in x])'
            fixes += 1
            return fixed
        else:
            # Also add for ones without create_type
            fixed = f'SQLEnum({sql_enum_content}, values_callable=lambda x: [e.value for e in x])'
            fixes += 1
            return fixed

    fixed_content = re.sub(pattern, replacer, content, flags=re.DOTALL)
    return fixed_content, fixes

def main():
    models_dir = Path(__file__).parent / 'models'

    files_to_fix = [
        'estate_iht.py',
        'goal.py',
        'investment.py',
        'life_assurance.py',
        'personalization.py',
        'recommendation.py',
        'retirement.py',
        'savings_account.py'
    ]

    total_fixes = 0

    for filename in files_to_fix:
        file_path = models_dir / filename
        if not file_path.exists():
            print(f"⚠️  {filename} not found")
            continue

        # Read file
        with open(file_path, 'r') as f:
            content = f.read()

        # Fix enums
        fixed_content, fixes = fix_sql_enum(content)

        if fixes > 0:
            # Write back
            with open(file_path, 'w') as f:
                f.write(fixed_content)
            print(f"✓ {filename}: Fixed {fixes} enum(s)")
            total_fixes += fixes
        else:
            print(f"  {filename}: No fixes needed")

    print(f"\n✅ Total fixes: {total_fixes}")
    return 0 if total_fixes >= 0 else 1

if __name__ == '__main__':
    sys.exit(main())
