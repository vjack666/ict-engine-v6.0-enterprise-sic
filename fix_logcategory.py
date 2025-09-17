#!/usr/bin/env python3
"""
Quick fix script to remove LogCategory usage from production modules
"""
import re
from pathlib import Path

def fix_logcategory_in_file(file_path):
    """Fix LogCategory usage in a single file"""
    print(f"Fixing LogCategory usage in {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to match logging calls with LogCategory
    patterns = [
        r'self\.logger\.(info|warning|error|debug|critical)\([^,]+,\s*LogCategory\.[^,]+,?\s*[^)]*\)',
        r'self\.logger\.(info|warning|error|debug|critical)\([^,]+,\s*LogCategory\.[^)]*\)',
        r'_safe_log\([^,]+,\s*[^,]+,\s*[^,]+,\s*LogCategory\.[^)]*\)'
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, content)
        for match in matches:
            full_match = match.group(0)
            # Extract just the message part
            if 'self.logger' in full_match:
                # Extract method name and message
                method_match = re.search(r'self\.logger\.(\w+)\(([^,]+)', full_match)
                if method_match:
                    method = method_match.group(1)
                    message = method_match.group(2)
                    replacement = f'self.logger.{method}({message})'
                    content = content.replace(full_match, replacement)
                    print(f"  Replaced: {full_match[:50]}... -> {replacement}")
    
    # Remove any orphaned lines from previous LogCategory calls
    lines = content.split('\n')
    fixed_lines = []
    skip_next = False
    
    for i, line in enumerate(lines):
        if skip_next:
            skip_next = False
            if '"' in line and ('components' in line or 'status' in line):
                continue  # Skip orphaned metadata lines
        
        # Check if this is an orphaned metadata line
        if (line.strip().startswith('"') and 
            ('components' in line or 'status' in line or 'symbols' in line) and 
            line.strip().endswith(',') and i > 0 and 
            'logger.' in lines[i-1]):
            continue  # Skip orphaned metadata
        
        if line.strip() == '})' and i > 0 and ('"' in lines[i-1] or 'logger.' in lines[i-1]):
            continue  # Skip orphaned closing
            
        fixed_lines.append(line)
    
    fixed_content = '\n'.join(fixed_lines)
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print(f"  ✅ Fixed {file_path}")

def main():
    """Fix LogCategory in all production modules"""
    files_to_fix = [
        "01-CORE/production/production_system_integrator.py"
    ]
    
    for file_path in files_to_fix:
        if Path(file_path).exists():
            fix_logcategory_in_file(file_path)
        else:
            print(f"⚠️ File not found: {file_path}")
    
    print("🎯 LogCategory fixes complete!")

if __name__ == "__main__":
    main()