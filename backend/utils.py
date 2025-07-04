"""
Utility functions for Quranic Roots Analysis API
Phase 2: Backend API & Analytics Engine
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Union, Tuple
import re
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Buckwalter to Arabic conversion mappings
ARABIC_TO_BUCKWALTER = {
    "\u0627": 'A', "\u0628": 'b', "\u062A": 't', "\u062B": 'v', "\u062C": 'j',
    "\u062D": 'H', "\u062E": 'x', "\u062F": 'd', "\u0630": '*', "\u0631": 'r',
    "\u0632": 'z', "\u0633": 's', "\u0634": '$', "\u0635": 'S', "\u0636": 'D',
    "\u0637": 'T', "\u0638": 'Z', "\u0639": 'E', "\u063A": 'g', "\u0641": 'f',
    "\u0642": 'q', "\u0643": 'k', "\u0644": 'l', "\u0645": 'm', "\u0646": 'n',
    "\u0647": 'h', "\u0648": 'w', "\u0649": 'Y', "\u064A": 'y',
    ' ': ' ', "\u0621": "'", "\u0623": '>', "\u0625": '<', "\u0624": '&',
    "\u0626": '}', "\u0622": '|', "\u064E": 'a', "\u064F": 'u', "\u0650": 'i',
    "\u0651": '~', "\u0652": 'o', "\u064B": 'F', "\u064C": 'N', "\u064D": 'K',
    "\u0640": '_', "\u0670": '`', "\u0629": 'p'
}

BUCKWALTER_TO_ARABIC = {v: k for k, v in ARABIC_TO_BUCKWALTER.items()}

def buck_to_arabic(text: str) -> str:
    """
    Convert Buckwalter transliteration to Arabic script
    
    Args:
        text: Text in Buckwalter transliteration
        
    Returns:
        Text in Arabic script
    """
    try:
        if not text or pd.isna(text):
            return ""
        
        result = ""
        for char in str(text):
            result += BUCKWALTER_TO_ARABIC.get(char, char)
        
        return result
    except Exception as e:
        logger.error(f"Error converting Buckwalter to Arabic: {e}")
        return str(text)

def arabic_to_buck(text: str) -> str:
    """
    Convert Arabic script to Buckwalter transliteration
    
    Args:
        text: Text in Arabic script
        
    Returns:
        Text in Buckwalter transliteration
    """
    try:
        if not text or pd.isna(text):
            return ""
        
        result = ""
        for char in str(text):
            result += ARABIC_TO_BUCKWALTER.get(char, char)
        
        return result
    except Exception as e:
        logger.error(f"Error converting Arabic to Buckwalter: {e}")
        return str(text)

def clean_text(text: str) -> str:
    """
    Clean and normalize text input
    
    Args:
        text: Input text to clean
        
    Returns:
        Cleaned text
    """
    if not text or pd.isna(text):
        return ""
    
    # Remove extra whitespace
    text = str(text).strip()
    
    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    return text

def validate_sura_number(sura: Union[int, str]) -> int:
    """
    Validate and convert sura number
    
    Args:
        sura: Sura number as int or string
        
    Returns:
        Valid sura number as integer
        
    Raises:
        ValueError: If sura number is invalid
    """
    try:
        sura_int = int(sura)
        if not 1 <= sura_int <= 114:
            raise ValueError(f"Sura number must be between 1 and 114, got {sura_int}")
        return sura_int
    except (ValueError, TypeError):
        raise ValueError(f"Invalid sura number: {sura}")

def validate_aya_number(aya: Union[int, str], sura: int = None) -> int:
    """
    Validate and convert aya (verse) number
    
    Args:
        aya: Aya number as int or string
        sura: Optional sura number for range validation
        
    Returns:
        Valid aya number as integer
        
    Raises:
        ValueError: If aya number is invalid
    """
    try:
        aya_int = int(aya)
        if aya_int < 1:
            raise ValueError(f"Aya number must be positive, got {aya_int}")
        
        # If sura is provided, validate against known verse counts
        if sura:
            max_verses = get_max_verses_for_sura(sura)
            if max_verses and aya_int > max_verses:
                raise ValueError(f"Aya {aya_int} exceeds maximum verses ({max_verses}) for sura {sura}")
        
        return aya_int
    except (ValueError, TypeError):
        raise ValueError(f"Invalid aya number: {aya}")

def get_max_verses_for_sura(sura: int) -> Optional[int]:
    """
    Get maximum number of verses for a sura
    
    Args:
        sura: Sura number
        
    Returns:
        Maximum verse count or None if unknown
    """
    # Standard verse counts for each sura
    verse_counts = {
        1: 7, 2: 286, 3: 200, 4: 176, 5: 120, 6: 165, 7: 206, 8: 75, 9: 129, 10: 109,
        11: 123, 12: 111, 13: 43, 14: 52, 15: 99, 16: 128, 17: 111, 18: 110, 19: 98, 20: 135,
        21: 112, 22: 78, 23: 118, 24: 64, 25: 77, 26: 227, 27: 93, 28: 88, 29: 69, 30: 60,
        31: 34, 32: 30, 33: 73, 34: 54, 35: 45, 36: 83, 37: 182, 38: 88, 39: 75, 40: 85,
        41: 54, 42: 53, 43: 89, 44: 59, 45: 37, 46: 35, 47: 38, 48: 29, 49: 18, 50: 45,
        51: 60, 52: 49, 53: 62, 54: 55, 55: 78, 56: 96, 57: 29, 58: 22, 59: 24, 60: 13,
        61: 14, 62: 11, 63: 11, 64: 18, 65: 12, 66: 12, 67: 30, 68: 52, 69: 52, 70: 44,
        71: 28, 72: 28, 73: 20, 74: 56, 75: 40, 76: 31, 77: 50, 78: 40, 79: 46, 80: 42,
        81: 29, 82: 19, 83: 36, 84: 25, 85: 22, 86: 17, 87: 19, 88: 26, 89: 30, 90: 20,
        91: 15, 92: 21, 93: 11, 94: 8, 95: 8, 96: 19, 97: 5, 98: 8, 99: 8, 100: 11,
        101: 11, 102: 8, 103: 3, 104: 9, 105: 5, 106: 4, 107: 7, 108: 3, 109: 6, 110: 3,
        111: 5, 112: 4, 113: 5, 114: 6
    }
    return verse_counts.get(sura)

def format_location_reference(sura: int, aya: int, word: int = None) -> str:
    """
    Format a location reference in standard format
    
    Args:
        sura: Sura number
        aya: Aya number
        word: Optional word number
        
    Returns:
        Formatted location string (e.g., "2:255" or "2:255:3")
    """
    reference = f"{sura}:{aya}"
    if word is not None:
        reference += f":{word}"
    return reference

def parse_location_reference(location: str) -> Dict[str, int]:
    """
    Parse a location reference string
    
    Args:
        location: Location string (e.g., "2:255:3")
        
    Returns:
        Dictionary with sura, aya, and optionally word numbers
        
    Raises:
        ValueError: If location format is invalid
    """
    try:
        parts = location.split(':')
        if len(parts) < 2 or len(parts) > 4:
            raise ValueError("Location must have format 'sura:aya' or 'sura:aya:word' or 'sura:aya:word:segment'")
        
        result = {
            'sura': validate_sura_number(parts[0]),
            'aya': validate_aya_number(parts[1])
        }
        
        if len(parts) >= 3:
            result['word'] = int(parts[2])
        
        if len(parts) == 4:
            result['segment'] = int(parts[3])
        
        return result
    except (ValueError, IndexError) as e:
        raise ValueError(f"Invalid location format '{location}': {e}")

def safe_int(value: Any, default: int = 0) -> int:
    """
    Safely convert value to integer
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
        
    Returns:
        Integer value or default
    """
    try:
        if pd.isna(value):
            return default
        return int(value)
    except (ValueError, TypeError):
        return default

def safe_float(value: Any, default: float = 0.0) -> float:
    """
    Safely convert value to float
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
        
    Returns:
        Float value or default
    """
    try:
        if pd.isna(value):
            return default
        return float(value)
    except (ValueError, TypeError):
        return default

def safe_str(value: Any, default: str = "") -> str:
    """
    Safely convert value to string
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
        
    Returns:
        String value or default
    """
    try:
        if pd.isna(value):
            return default
        return str(value).strip()
    except (ValueError, TypeError):
        return default

def paginate_results(data: List[Any], offset: int = 0, limit: int = 50) -> Tuple[List[Any], Dict[str, int]]:
    """
    Paginate a list of results
    
    Args:
        data: List of data to paginate
        offset: Number of items to skip
        limit: Maximum number of items to return
        
    Returns:
        Tuple of (paginated_data, pagination_info)
    """
    total = len(data)
    
    # Validate offset and limit
    offset = max(0, offset)
    limit = max(1, min(limit, 1000))  # Cap at 1000 items
    
    # Calculate pagination
    start = offset
    end = min(offset + limit, total)
    paginated_data = data[start:end]
    
    pagination_info = {
        'total': total,
        'offset': offset,
        'limit': limit,
        'returned': len(paginated_data),
        'has_more': end < total
    }
    
    return paginated_data, pagination_info

def calculate_similarity(text1: str, text2: str) -> float:
    """
    Calculate similarity between two texts using simple character overlap
    
    Args:
        text1: First text
        text2: Second text
        
    Returns:
        Similarity score between 0 and 1
    """
    try:
        if not text1 or not text2:
            return 0.0
        
        # Convert to sets of characters
        set1 = set(text1.lower())
        set2 = set(text2.lower())
        
        # Calculate Jaccard similarity
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0
    except Exception:
        return 0.0

def create_response_metadata(total: int, returned: int, query_time: float = None) -> Dict[str, Any]:
    """
    Create standardized response metadata
    
    Args:
        total: Total number of results available
        returned: Number of results returned
        query_time: Optional query execution time
        
    Returns:
        Metadata dictionary
    """
    metadata = {
        'total_results': total,
        'returned_results': returned,
        'timestamp': datetime.now().isoformat()
    }
    
    if query_time is not None:
        metadata['query_time_ms'] = round(query_time * 1000, 2)
    
    return metadata

def validate_semantic_category(category: str) -> bool:
    """
    Validate if a semantic category is known
    
    Args:
        category: Category name to validate
        
    Returns:
        True if valid category
    """
    valid_categories = {
        'divine_attributes', 'worship_ritual', 'faith_belief',
        'family_relations', 'social_justice', 'commerce_economics',
        'knowledge_wisdom', 'communication', 'books_revelation',
        'creation_nature', 'time_temporal', 'natural_elements',
        'movement_direction', 'emotions_states', 'moral_conduct',
        'uncategorized'
    }
    return category in valid_categories

def normalize_search_query(query: str) -> str:
    """
    Normalize search query for consistent matching
    
    Args:
        query: Search query to normalize
        
    Returns:
        Normalized query string
    """
    if not query:
        return ""
    
    # Remove extra whitespace and convert to lowercase
    query = re.sub(r'\s+', ' ', query.strip().lower())
    
    # Remove special characters except Arabic and Buckwalter chars
    query = re.sub(r'[^\w\s\u0600-\u06FF><&}|`~*$#+_-]', '', query)
    
    return query

def export_to_csv(data: List[Dict[str, Any]], filename: str = None) -> str:
    """
    Export data to CSV format
    
    Args:
        data: List of dictionaries to export
        filename: Optional filename
        
    Returns:
        CSV content as string
    """
    try:
        if not data:
            return ""
        
        df = pd.DataFrame(data)
        return df.to_csv(index=False)
    except Exception as e:
        logger.error(f"Error exporting to CSV: {e}")
        return ""

def export_to_json(data: Any, pretty: bool = True) -> str:
    """
    Export data to JSON format
    
    Args:
        data: Data to export
        pretty: Whether to format JSON prettily
        
    Returns:
        JSON content as string
    """
    try:
        if pretty:
            return json.dumps(data, indent=2, ensure_ascii=False, default=str)
        else:
            return json.dumps(data, ensure_ascii=False, default=str)
    except Exception as e:
        logger.error(f"Error exporting to JSON: {e}")
        return "{}"

def get_revelation_type(sura: int) -> str:
    """
    Get revelation type for a sura
    
    Args:
        sura: Sura number
        
    Returns:
        'Meccan' or 'Medinan'
    """
    # Medinan suras (traditionally accepted classification)
    medinan_suras = {2, 3, 4, 5, 8, 9, 13, 22, 24, 33, 47, 48, 49, 55, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 76, 98, 99, 110}
    
    return "Medinan" if sura in medinan_suras else "Meccan"

def calculate_frequency_stats(frequencies: List[int]) -> Dict[str, float]:
    """
    Calculate statistical measures for frequency data
    
    Args:
        frequencies: List of frequency values
        
    Returns:
        Dictionary with statistical measures
    """
    try:
        if not frequencies:
            return {}
        
        frequencies = [f for f in frequencies if f is not None and f >= 0]
        
        if not frequencies:
            return {}
        
        frequencies_array = np.array(frequencies)
        
        return {
            'mean': float(np.mean(frequencies_array)),
            'median': float(np.median(frequencies_array)),
            'std': float(np.std(frequencies_array)),
            'min': float(np.min(frequencies_array)),
            'max': float(np.max(frequencies_array)),
            'q25': float(np.percentile(frequencies_array, 25)),
            'q75': float(np.percentile(frequencies_array, 75))
        }
    except Exception as e:
        logger.error(f"Error calculating frequency stats: {e}")
        return {}

def detect_language(text: str) -> str:
    """
    Simple language detection for Arabic vs Buckwalter
    
    Args:
        text: Text to analyze
        
    Returns:
        'arabic', 'buckwalter', or 'unknown'
    """
    if not text:
        return 'unknown'
    
    # Count Arabic vs Buckwalter characters
    arabic_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
    buckwalter_chars = sum(1 for c in text if c in BUCKWALTER_TO_ARABIC)
    
    if arabic_chars > len(text) * 0.3:
        return 'arabic'
    elif buckwalter_chars > len(text) * 0.3:
        return 'buckwalter'
    else:
        return 'unknown' 