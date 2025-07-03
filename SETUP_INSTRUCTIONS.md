# Setup Instructions - Phase 1 Enhancement

## 🚨 **Quick Fix for ModuleNotFoundError**

If you're getting `ModuleNotFoundError: No module named 'networkx'`, follow these steps:

### **Option 1: Install Individual Package (Quick Fix)**
```bash
pip install networkx
```

### **Option 2: Install All Enhanced Requirements (Recommended)**
```bash
pip install -r requirements.txt
```

### **Option 3: Install Specific Enhanced Packages**
```bash
pip install pandas jupyter matplotlib seaborn numpy networkx scipy plotly scikit-learn
```

---

## 📦 **Complete Installation Guide**

### **1. Check Your Python Version**
```bash
python --version
# Should be Python 3.8 or higher
```

### **2. Update pip (Recommended)**
```bash
python -m pip install --upgrade pip
```

### **3. Install All Dependencies**
```bash
# Navigate to your project directory
cd /path/to/quranic_roots

# Install enhanced requirements
pip install -r requirements.txt
```

### **4. Verify Installation**
```bash
python -c "import pandas, matplotlib, seaborn, networkx, numpy; print('✅ All packages installed successfully!')"
```

---

## 🔧 **Troubleshooting Common Issues**

### **Issue 1: networkx Not Found**
```bash
# Direct installation
pip install networkx>=2.6.0
```

### **Issue 2: seaborn Style Warning**
If you get warnings about `plt.style.use('seaborn-v0_8')`, update the notebook cell:
```python
# Replace this line in the notebook:
plt.style.use('seaborn-v0_8')

# With this:
try:
    plt.style.use('seaborn-v0_8')
except OSError:
    plt.style.use('seaborn')  # Fallback for older versions
```

### **Issue 3: Import Errors on Windows**
```bash
# Use conda instead of pip if you have Anaconda/Miniconda
conda install pandas matplotlib seaborn networkx numpy scipy scikit-learn
```

### **Issue 4: Virtual Environment Issues**
```bash
# Create new virtual environment
python -m venv quranic_env
quranic_env\Scripts\activate  # Windows
# source quranic_env/bin/activate  # macOS/Linux

# Then install requirements
pip install -r requirements.txt
```

---

## 🧪 **Testing Phase 1 Enhancements**

### **1. Start Jupyter**
```bash
cd /path/to/quranic_roots
jupyter notebook
```

### **2. Run Enhanced Analysis**
1. Open `enhanced_quran_analysis.ipynb`
2. Run all cells in order
3. Check for any remaining import errors

### **3. Expected Output Files**
After successful execution, you should see these new files:
- `quran-enhanced-phase1.csv`
- `root-frequency-analysis.csv`
- `semantic-category-analysis.csv`
- `root-cooccurrence-matrix.csv`
- `category-cooccurrence-matrix.csv`
- `sura-thematic-distribution.csv`
- `sura-thematic-relative.csv`
- `enhancement-metadata.json`

---

## 🐛 **Alternative Import Fix for Notebook**

If you want to run the notebook without installing networkx immediately, edit the import cell:

```python
# Enhanced imports for advanced analysis
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter, defaultdict

# Optional imports with fallbacks
try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    print("⚠️ NetworkX not installed. Network analysis features will be skipped.")
    HAS_NETWORKX = False

from itertools import combinations
import json
from functools import lru_cache
import warnings
warnings.filterwarnings('ignore')

# Set plotting style with fallback
try:
    plt.style.use('seaborn-v0_8')
except OSError:
    plt.style.use('seaborn')

sns.set_palette("husl")
print("📚 Enhanced libraries imported successfully!")
```

---

## ✅ **Verification Checklist**

- [ ] Python 3.8+ installed
- [ ] All packages from requirements.txt installed
- [ ] Jupyter notebook running without import errors
- [ ] Base data files present (`quran-morphology-final.csv`, `toc.csv`)
- [ ] Enhanced analysis notebook executes successfully
- [ ] Output files generated correctly

---

## 🆘 **Getting Help**

If you continue to have issues:

1. **Check Python Environment:** Ensure you're using the correct Python/pip version
2. **Virtual Environment:** Consider using a fresh virtual environment
3. **Package Versions:** Verify package versions match requirements.txt
4. **System Dependencies:** Some packages may require system-level dependencies

**Common Commands for Debugging:**
```bash
pip list                    # Show installed packages
pip show networkx          # Check specific package info
python -m pip check        # Check for dependency conflicts
```

---

## 🚀 **Next Steps After Setup**

1. **Run Phase 1 Analysis:** Execute the enhanced notebook completely
2. **Explore Generated Data:** Review the CSV outputs and JSON metadata
3. **Verify Enhancements:** Check that all new columns are present in the enhanced dataset
4. **Prepare for Phase 2:** Database setup and API development

**Ready to proceed with Phase 2 once Phase 1 testing is complete!** 