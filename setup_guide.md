# Setup Guide for Quranic Root Words Analysis

## Step-by-Step Installation and Setup

### 1. Verify Python Installation
```powershell
python --version
```
**Expected**: Python 3.7 or higher (tested with 3.12.9)

### 2. Install Required Packages
```powershell
pip install -r requirements.txt
```

**Alternative individual installation:**
```powershell
pip install pandas jupyter notebook matplotlib seaborn
```

### 3. Verify Installation
```powershell
python -c "import pandas; import jupyter; print('All packages installed successfully!')"
```

### 4. Check Data Files
Ensure these files exist in your project directory:
- `quran-morphology-final.csv` (the main dataset)
- `toc.csv` (table of contents)
- `quran.ipynb` (the main notebook)

### 5. Start Jupyter Notebook
```powershell
jupyter notebook
```
This will open your web browser with the Jupyter interface.

### 6. Open and Run the Notebook
1. Click on `quran.ipynb` in the Jupyter file browser
2. The notebook will open in a new tab
3. Run cells one by one using `Shift + Enter`
4. Or run all cells using `Cell > Run All`

## Troubleshooting Common Issues

### Issue 1: Missing Data Files
If `quran-morphology-final.csv` is missing, the notebook will create it by downloading data from the online source.

### Issue 2: Large File Size
The morphology file is quite large (>2MB). If you encounter memory issues:
- Close other applications
- Try running cells individually instead of all at once

### Issue 3: Encoding Issues
If you see strange characters, ensure your system supports UTF-8 encoding:
```powershell
chcp 65001
```

### Issue 4: Internet Connection Required
The notebook downloads data from online sources. Ensure you have an active internet connection for the first run.

## Quick Test
After setup, you can quickly test if everything works:

```python
import pandas as pd
import sys

print(f"Python version: {sys.version}")
print(f"Pandas version: {pd.__version__}")

# Try loading the data
try:
    quran = pd.read_csv('quran-morphology-final.csv')
    print(f"✅ Data loaded successfully! {len(quran)} entries found.")
except FileNotFoundError:
    print("⚠️  Data file not found - will be created when you run the notebook")
``` 