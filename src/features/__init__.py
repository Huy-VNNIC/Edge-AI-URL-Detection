"""Feature extraction modules for URL, domain, DNS, and graph features."""

import pandas as pd
import numpy as np
from typing import Dict, List, Any
import re
import math
from urllib.parse import urlparse
import tldextract
from collections import Counter
import logging

from src.utils import setup_logging

logger = setup_logging()

class URLLexicalFeatures:
    """Extract lexical features from URLs and domains."""
    
    def __init__(self):
        self.suspicious_tlds = {
            'tk', 'ml', 'ga', 'cf', 'pw', 'cc', 'top', 'work', 'click', 'download',
            'bid', 'win', 'party', 'gq', 'stream', 'accountant', 'science', 'racing'
        }
        
    def extract_features(self, url_or_domain: str) -> Dict[str, float]:
        """Extract comprehensive lexical features."""
        if pd.isna(url_or_domain) or not url_or_domain:
            return self._get_empty_features()
            
        url_str = str(url_or_domain).strip()
        
        # Parse URL components
        if url_str.startswith(('http://', 'https://')):
            parsed = urlparse(url_str)
            domain = parsed.netloc
            path = parsed.path
            query = parsed.query
            full_url = url_str
        else:
            # Treat as domain
            domain = url_str
            path = "/"
            query = ""
            full_url = f"http://{domain}/"
            
        # Extract TLD info
        tld_extract = tldextract.extract(domain)
        
        features = {}
        
        # URL-level features
        features.update(self._url_features(full_url))
        
        # Domain-level features  
        features.update(self._domain_features(domain, tld_extract))
        
        # Path-level features
        features.update(self._path_features(path))
        
        # Query-level features
        features.update(self._query_features(query))
        
        return features
        
    def _url_features(self, url: str) -> Dict[str, float]:
        """Extract URL-level features."""
        return {
            'url_length': len(url),
            'url_entropy': self._calculate_entropy(url),
            'url_digit_ratio': sum(c.isdigit() for c in url) / max(len(url), 1),
            'url_special_ratio': sum(not c.isalnum() for c in url) / max(len(url), 1),
            'has_https': 1.0 if url.startswith('https://') else 0.0,
            'has_ip': 1.0 if self._is_ip_address(url) else 0.0
        }
        
    def _domain_features(self, domain: str, tld_extract) -> Dict[str, float]:
        """Extract domain-level features."""
        domain_clean = domain.lower().replace('www.', '')
        
        return {
            'domain_length': len(domain_clean),
            'domain_entropy': self._calculate_entropy(domain_clean),
            'num_subdomains': len(tld_extract.subdomain.split('.')) if tld_extract.subdomain else 0,
            'domain_digit_ratio': sum(c.isdigit() for c in domain_clean) / max(len(domain_clean), 1),
            'num_hyphens': domain_clean.count('-'),
            'num_underscores': domain_clean.count('_'),
            'suspicious_tld': 1.0 if tld_extract.suffix in self.suspicious_tlds else 0.0,
            'domain_has_vowels': 1.0 if any(v in domain_clean for v in 'aeiou') else 0.0
        }
        
    def _path_features(self, path: str) -> Dict[str, float]:
        """Extract path-level features."""
        if not path or path == "/":
            return {
                'path_length': 0,
                'num_path_segments': 0,
                'path_entropy': 0.0,
                'has_exe': 0.0
            }
            
        return {
            'path_length': len(path),
            'num_path_segments': len(path.split('/')) - 1,
            'path_entropy': self._calculate_entropy(path),
            'has_exe': 1.0 if '.exe' in path.lower() else 0.0
        }
        
    def _query_features(self, query: str) -> Dict[str, float]:
        """Extract query string features."""
        if not query:
            return {
                'query_length': 0,
                'num_query_params': 0,
                'query_entropy': 0.0
            }
            
        return {
            'query_length': len(query),
            'num_query_params': len(query.split('&')),
            'query_entropy': self._calculate_entropy(query)
        }
        
    def _calculate_entropy(self, text: str) -> float:
        """Calculate Shannon entropy of text."""
        if not text:
            return 0.0
            
        counts = Counter(text)
        total = len(text)
        entropy = 0.0
        
        for count in counts.values():
            p = count / total
            if p > 0:
                entropy -= p * math.log2(p)
                
        return entropy
        
    def _is_ip_address(self, url: str) -> bool:
        """Check if URL contains IP address instead of domain."""
        try:
            parsed = urlparse(url)
            host = parsed.netloc.split(':')[0]  # Remove port if present
            
            # Simple IP regex check
            ip_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
            return bool(re.match(ip_pattern, host))
        except:
            return False
            
    def _get_empty_features(self) -> Dict[str, float]:
        """Return empty feature dict for invalid inputs."""
        return {
            'url_length': 0, 'url_entropy': 0, 'url_digit_ratio': 0, 'url_special_ratio': 0,
            'has_https': 0, 'has_ip': 0, 'domain_length': 0, 'domain_entropy': 0,
            'num_subdomains': 0, 'domain_digit_ratio': 0, 'num_hyphens': 0, 'num_underscores': 0,
            'suspicious_tld': 0, 'domain_has_vowels': 0, 'path_length': 0, 'num_path_segments': 0,
            'path_entropy': 0, 'has_exe': 0, 'query_length': 0, 'num_query_params': 0, 'query_entropy': 0
        }

class DomainMetadataFeatures:
    """Extract features from domain metadata (WHOIS, DNS, etc)."""
    
    def extract_features(self, row: pd.Series) -> Dict[str, float]:
        """Extract domain metadata features from CSV row."""
        features = {}
        
        # DNS features
        features['ttl_normalized'] = self._normalize_ttl(row.get('TTL', 0))
        features['name_server_count'] = self._safe_float(row.get('Name_Server_Count', 0))
        
        # Domain age features
        domain_age = row.get('Domain_Age', 0)
        if pd.notna(domain_age) and isinstance(domain_age, (int, float)):
            features['domain_age_days'] = float(domain_age)
        else:
            features['domain_age_days'] = 0.0
            
        # Page rank and Alexa rank - handle string values
        page_rank = self._safe_float(row.get('Page_Rank', -1))
        alexa_rank = self._safe_float(row.get('Alexa_Rank', -1))
        features['has_page_rank'] = 1.0 if page_rank > 0 else 0.0
        features['has_alexa_rank'] = 1.0 if alexa_rank > 0 else 0.0
        
        # Organization features
        features['has_organization'] = 1.0 if pd.notna(row.get('Organization')) else 0.0
        features['has_registrant'] = 1.0 if pd.notna(row.get('Registrant_Name')) else 0.0
        
        # Security features
        features['is_shortened'] = self._safe_float(row.get('shortened', 0))
        features['has_punycode'] = self._safe_float(row.get('puny_coded', 0))
        features['obfuscated'] = self._safe_float(row.get('obfuscate_at_sign', 0))
        
        return features
        
    def _normalize_ttl(self, ttl_value) -> float:
        """Normalize TTL value to [0,1] range."""
        if pd.isna(ttl_value):
            return 0.0
            
        try:
            ttl = float(ttl_value)
            # Common TTL ranges: 300 (5min) to 86400 (24h)
            return min(ttl / 86400.0, 1.0)
        except (ValueError, TypeError):
            return 0.0
            
    def _safe_float(self, value, default: float = 0.0) -> float:
        """Safely convert value to float."""
        if pd.isna(value):
            return default
        try:
            return float(value)
        except (ValueError, TypeError):
            return default

class FeatureExtractor:
    """Main feature extraction class that combines all feature types."""
    
    def __init__(self):
        self.url_extractor = URLLexicalFeatures()
        self.domain_extractor = DomainMetadataFeatures()
        
    def extract_all_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract all features from dataset."""
        logger.info(f"Extracting features from {len(df)} records")
        
        all_features = []
        
        for idx, row in df.iterrows():
            if idx % 1000 == 0:
                logger.info(f"Processing {idx}/{len(df)} records")
                
            features = {}
            
            # Get URL/domain string
            url_or_domain = self._get_url_or_domain(row)
            
            # Extract lexical features
            lexical_features = self.url_extractor.extract_features(url_or_domain)
            features.update(lexical_features)
            
            # Extract domain metadata features if available
            metadata_features = self.domain_extractor.extract_features(row)
            features.update(metadata_features)
            
            # Add target and metadata
            features['label'] = row.get('label', 0)
            features['source'] = row.get('source', 'unknown')
            
            all_features.append(features)
            
        features_df = pd.DataFrame(all_features)
        logger.info(f"Extracted {len(features_df.columns)} features")
        
        return features_df
        
    def _get_url_or_domain(self, row: pd.Series) -> str:
        """Extract URL or domain string from row."""
        # Try different column names
        for col_name in ['url', 'Domain', 'domain', 'domain_clean']:
            if col_name in row and pd.notna(row[col_name]):
                return str(row[col_name])
                
        return ""