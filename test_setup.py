#!/usr/bin/env python3
"""
Test script to verify the Quranic Root Words Analysis environment setup
"""

import sys
import os

def test_python_version():
    """Test if Python version is compatible"""
    print("🔍 Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 7:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.7+")
        return False

def test_required_packages():
    """Test if required packages are installed"""
    print("\n🔍 Checking required packages...")
    required_packages = {
        'pandas': 'Data manipulation and analysis',
        'jupyter': 'Interactive notebook environment'
    }
    
    success = True
    for package, description in required_packages.items():
        try:
            __import__(package)
            if package == 'pandas':
                import pandas as pd
                print(f"✅ {package} {pd.__version__} - {description}")
            else:
                print(f"✅ {package} - {description}")
        except ImportError:
            print(f"❌ {package} - {description} (NOT INSTALLED)")
            success = False
    
    return success

def test_data_files():
    """Test if required data files exist"""
    print("\n🔍 Checking data files...")
    required_files = {
        'quran.ipynb': 'Main analysis notebook',
        'toc.csv': 'Table of contents (114 entries)',
        'quran-morphology-final.csv': 'Processed morphology data (optional - will be created)'
    }
    
    success = True
    for filename, description in required_files.items():
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            if filename == 'toc.csv' and size > 0:
                # Quick check of toc.csv content
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        if len(lines) >= 114:  # Should have header + 114 suras
                            print(f"✅ {filename} - {description} ({size} bytes, {len(lines)} lines)")
                        else:
                            print(f"⚠️  {filename} - {description} ({size} bytes, {len(lines)} lines - may be incomplete)")
                except Exception as e:
                    print(f"⚠️  {filename} - {description} ({size} bytes, error reading: {e})")
            else:
                print(f"✅ {filename} - {description} ({size} bytes)")
        else:
            if filename == 'quran-morphology-final.csv':
                print(f"⚠️  {filename} - {description} (will be created by notebook)")
            else:
                print(f"❌ {filename} - {description} (MISSING)")
                success = False
    
    return success

def test_quick_functionality():
    """Test basic functionality"""
    print("\n🔍 Testing basic functionality...")
    try:
        import pandas as pd
        
        # Test if we can load the toc file
        if os.path.exists('toc.csv'):
            toc = pd.read_csv('toc.csv')
            print(f"✅ Successfully loaded toc.csv with {len(toc)} suras")
            
            # Check if we have the expected columns
            expected_cols = ['No.', 'Place']
            if all(col in toc.columns for col in expected_cols):
                meccan_count = len(toc[toc['Place'] == 'Meccan'])
                medinan_count = len(toc[toc['Place'] == 'Medinan'])
                print(f"✅ Classification data: {meccan_count} Meccan, {medinan_count} Medinan suras")
            else:
                print("⚠️  toc.csv missing expected columns")
        
        # Test if we can load the main data file
        if os.path.exists('quran-morphology-final.csv'):
            try:
                quran = pd.read_csv('quran-morphology-final.csv')
                print(f"✅ Successfully loaded morphology data with {len(quran)} entries")
                
                # Quick data validation
                if 'sura' in quran.columns and 'Root' in quran.columns:
                    unique_suras = quran['sura'].nunique()
                    root_entries = quran['Root'].notna().sum()
                    print(f"✅ Data validation: {unique_suras} suras, {root_entries} entries with roots")
                else:
                    print("⚠️  Morphology data missing expected columns")
                    
            except Exception as e:
                print(f"❌ Error loading morphology data: {e}")
        else:
            print("ℹ️  Morphology data file not found - will be downloaded by notebook")
            
        return True
        
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Quranic Root Words Analysis - Environment Test\n")
    
    tests = [
        test_python_version(),
        test_required_packages(),
        test_data_files(),
        test_quick_functionality()
    ]
    
    print("\n" + "="*50)
    if all(tests):
        print("🎉 ALL TESTS PASSED! You're ready to run the analysis.")
        print("\nNext steps:")
        print("1. Run: jupyter notebook")
        print("2. Open: quran.ipynb")
        print("3. Execute cells with Shift+Enter")
    else:
        print("⚠️  SOME ISSUES FOUND. Please address the failed tests above.")
        print("\nTo install missing packages:")
        print("pip install -r requirements.txt")
    print("="*50)

if __name__ == "__main__":
    main() 