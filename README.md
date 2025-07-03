# Quranic Root Words Analysis

A comprehensive Python data analysis project for extracting and analyzing unique root words, lemmas, and word forms from the Holy Quran. This project processes morphological data to identify vocabulary patterns between Meccan and Medinan revelations.

## 📖 Project Overview

This project analyzes over 128,000 morphological entries from the Quranic Corpus to:
- Extract unique Arabic root words from specific suras (chapters)
- Compare vocabulary between Meccan and Medinan revelations  
- Convert between Buckwalter transliteration and Arabic script
- Provide functions for targeted vocabulary analysis and study

### Key Findings
- **547** unique root words appear only in Meccan suras
- **198** unique root words appear only in Medinan suras  
- **898** root words appear in both Meccan and Medinan suras

## 🗂️ Project Structure

```
quranic_roots/
├── quran.ipynb                    # Main analysis notebook
├── quran-morphology-final.csv     # Processed morphological data (128K+ entries)
├── toc.csv                        # Table of contents with sura metadata
└── README.md                      # This documentation
```

## 📊 Data Sources

1. **Morphological Data**: [Quranic Arabic Corpus](http://textminingthequran.com/data/quranic-corpus-morphology-0.4.txt)
   - Contains morphological analysis of every word in the Quran
   - Includes roots, lemmas, grammatical tags, and word forms
   - Originally in tab-separated format with 128,219 entries

2. **Sura Metadata**: Table of contents with:
   - Sura names (Arabic and English)
   - Revelation location (Meccan/Medinan)
   - Chronological order
   - Verse counts

## 🔧 Technical Implementation

### Data Processing Pipeline

1. **Data Acquisition**: Downloads morphological data from online corpus
2. **Column Parsing**: Extracts location data (sura:verse:word:segment) using regex
3. **Feature Extraction**: Parses ROOT and LEMMA information from features column
4. **Data Enrichment**: Merges with Meccan/Medinan classification
5. **Text Conversion**: Implements Buckwalter ↔ Arabic script conversion

### Key Data Columns

| Column | Description | Example |
|--------|-------------|---------|
| `sura` | Chapter number (1-114) | 1 |
| `aya` | Verse number | 1 |
| `word` | Word position in verse | 1 |
| `w_seg` | Word segment number | 1 |
| `FORM` | Arabic word in Buckwalter | `bi` |
| `TAG` | Grammatical tag | `P` (Preposition) |
| `Root` | Arabic root in Buckwalter | `smw` |
| `Lemma` | Lemma form | `{som` |
| `Place` | Revelation location | `Meccan`/`Medinan` |

## 🚀 Getting Started

### Prerequisites

```bash
# Python 3.x required (tested with 3.12.9)
pip install pandas
pip install jupyter
```

### Installation

1. Clone or download the repository
2. Ensure you have the required CSV files in the project directory
3. Open `quran.ipynb` in Jupyter Notebook/Lab

### Basic Usage

```python
import pandas as pd

# Load the processed data
quran = pd.read_csv('quran-morphology-final.csv')

# Get unique roots for a specific sura (e.g., Al-Fatiha)
sura_1_roots = sura_words([1], 'R')  # Returns Arabic roots

# Find roots unique to last two suras
unique_roots = unique_sura_words([113, 114], 'R')

# Compare Meccan vs Medinan vocabulary
meccan_roots = set(quran[quran.Place == 'Meccan'].Root.unique())
medinan_roots = set(quran[quran.Place == 'Medinan'].Root.unique())
```

## 🔍 Core Functions

### `sura_words(sura_list, kind='W')`
Returns unique words from specified suras.

**Parameters:**
- `sura_list`: List of sura numbers, e.g., `[1, 2, 3]`
- `kind`: Type of analysis
  - `'W'`: Word forms (default)
  - `'R'`: Root words  
  - `'L'`: Lemmas

**Returns:** List of words in Arabic script

### `unique_sura_words(sura_list, kind='W')`
Returns words that appear ONLY in the specified suras (not elsewhere in Quran).

**Parameters:** Same as `sura_words()`

**Returns:** List of unique words in Arabic script

### Text Conversion Functions

```python
# Convert Buckwalter to Arabic
arabic_text = buck_to_arabic('EalaY`')  # Returns: على

# Convert Arabic to Buckwalter  
buckwalter_text = arabic_to_buc('الحمد لله')  # Returns: AlHmd llh
```

## ✅ Verification Methods

### 1. Data Integrity Checks

```python
# Verify data completeness
print(f"Total entries: {len(quran)}")
print(f"Entries with roots: {quran.Root.notna().sum()}")
print(f"Entries with lemmas: {quran.Lemma.notna().sum()}")

# Check sura coverage (should be 1-114)
print(f"Sura range: {quran.sura.min()} - {quran.sura.max()}")
print(f"Missing suras: {set(range(1,115)) - set(quran.sura.unique())}")
```

### 2. Cross-Reference Validation

```python
# Verify against known Quranic facts
sura_verse_counts = quran.groupby('sura')['aya'].max()
# Compare with known verse counts from toc.csv

# Check Meccan/Medinan classification accuracy
toc = pd.read_csv('toc.csv')
classification_check = quran.groupby('sura')['Place'].first()
```

### 3. Linguistic Validation

```python
# Test text conversion functions
test_words = ['smw', 'Alh', 'ktb']
for word in test_words:
    arabic = buck_to_arabic(word)
    back_to_buck = arabic_to_buc(arabic)
    assert word == back_to_buck, f"Conversion failed for {word}"
```

### 4. Statistical Validation

```python
# Verify statistical claims
meccan_unique = len(k - d)  # Should be 547
medinan_unique = len(d - k)  # Should be 198
common_roots = len(k & d)   # Should be 898

print(f"Meccan-only roots: {meccan_unique}")
print(f"Medinan-only roots: {medinan_unique}")  
print(f"Common roots: {common_roots}")
```

## 🔬 Enhancement Possibilities

### 1. **Advanced Linguistic Analysis**
- **Semantic clustering**: Group roots by meaning/theme
- **Frequency analysis**: Most/least common roots across different periods
- **Morphological patterns**: Analyze verb forms, noun patterns, particle usage
- **Hapax legomena**: Words appearing only once in the Quran

### 2. **Temporal Analysis**
- **Chronological progression**: Vocabulary evolution over revelation period
- **Seasonal patterns**: Words associated with different times/events
- **Context analysis**: Roots in specific contexts (prayer, legal, narrative)

### 3. **Comparative Studies**
- **Sura-level analysis**: Vocabulary uniqueness by individual suras
- **Cross-sura relationships**: Shared vocabulary between specific suras
- **Thematic analysis**: Roots by topic (worship, law, stories, etc.)

### 4. **Technical Improvements**

#### Performance Optimization
```python
# Add caching for expensive operations
from functools import lru_cache

@lru_cache(maxsize=128)
def cached_sura_words(sura_tuple, kind='W'):
    return sura_words(list(sura_tuple), kind)
```

#### Enhanced Search Capabilities
```python
# Fuzzy matching for root searches
def find_similar_roots(target_root, threshold=0.8):
    # Implement Levenshtein distance or similar
    pass

# Pattern matching
def roots_matching_pattern(pattern):
    # Find roots matching specific morphological patterns
    pass
```

#### Data Visualization
```python
import matplotlib.pyplot as plt
import seaborn as sns

# Visualize vocabulary distribution
def plot_vocabulary_distribution():
    # Create charts showing Meccan vs Medinan vocabulary
    pass

# Network analysis of shared vocabulary
def create_sura_similarity_network():
    # Build network based on shared vocabulary
    pass
```

### 5. **Extended Functionality**

#### Multi-language Support
- Add English translations for roots
- Support for other transliteration systems
- Unicode normalization improvements

#### Interactive Tools
```python
# Web interface using Streamlit/Flask
def create_web_interface():
    # Interactive vocabulary explorer
    pass

# Command-line interface
def create_cli_tool():
    # CLI for batch processing and automation
    pass
```

#### Export Capabilities
```python
# Export to different formats
def export_to_json():
    # Structured JSON for API consumption
    pass

def export_to_xml():
    # XML format for linguistic tools
    pass

def create_anki_deck():
    # Generate flashcards for vocabulary study
    pass
```

### 6. **Research Applications**
- **Stylometric analysis**: Authorship and style consistency studies
- **Historical linguistics**: Language evolution patterns
- **Computational theology**: Systematic thematic analysis
- **Educational tools**: Vocabulary building applications

### 7. **Integration Opportunities**
- **Tafsir integration**: Link roots to commentary explanations
- **Recitation analysis**: Connect with audio data
- **Translation comparison**: Multi-language translation analysis
- **Academic databases**: Integration with Islamic studies resources

## 📚 Educational Use Cases

1. **Arabic Language Learning**
   - Progressive vocabulary building by sura
   - Root-based word family exploration
   - Morphological pattern recognition

2. **Islamic Studies Research**
   - Thematic vocabulary analysis
   - Historical development tracking
   - Comparative revelation studies

3. **Computational Linguistics**
   - Arabic NLP model training
   - Morphological analysis benchmarking
   - Text classification experiments

## 🤝 Contributing

Contributions are welcome! Areas for contribution:
- Enhanced text processing algorithms
- Additional linguistic analysis features
- Performance optimizations
- Documentation improvements
- Test coverage expansion

## 📄 License

This project uses data from the Quranic Arabic Corpus. Please refer to their licensing terms for data usage guidelines.

## 📖 References

- [Quranic Arabic Corpus](http://corpus.quran.com/)
- [Buckwalter Transliteration](http://corpus.quran.com/java/buckwalter.jsp)
- [Text Mining the Quran](http://textminingthequran.com/)

---

*This project demonstrates the power of computational analysis in understanding linguistic patterns within sacred texts while maintaining respect for the source material.*
