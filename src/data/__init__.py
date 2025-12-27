"""Data loading and preprocessing utilities."""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Tuple, Dict, Optional
from urllib.parse import urlparse
import tldextract
import re
import logging

from src.utils import load_config, setup_logging

logger = setup_logging()

class DataLoader:
    """Unified data loader for all datasets in the project."""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config = load_config(config_path)
        self.root_path = Path(".")
        
    def load_csv_datasets(self) -> pd.DataFrame:
        """Load and combine CSV datasets (phishing, benign, malware, spam)."""
        datasets = []
        
        # Load phishing data
        phishing_path = self.root_path / self.config['data']['raw_dirs']['csvs'] / "CSV_phishing.csv"
        if phishing_path.exists():
            try:
                df_phishing = pd.read_csv(phishing_path, on_bad_lines='skip', low_memory=False)
                df_phishing['label'] = 1  # malicious
                df_phishing['source'] = 'csv_phishing'
                datasets.append(df_phishing)
                logger.info(f"Loaded phishing CSV: {len(df_phishing)} records")
            except Exception as e:
                logger.warning(f"Failed to load phishing CSV: {e}")
                # Try with different encoding
                try:
                    df_phishing = pd.read_csv(phishing_path, on_bad_lines='skip', encoding='latin-1', low_memory=False)
                    df_phishing['label'] = 1
                    df_phishing['source'] = 'csv_phishing'
                    datasets.append(df_phishing)
                    logger.info(f"Loaded phishing CSV with latin-1 encoding: {len(df_phishing)} records")
                except Exception as e2:
                    logger.error(f"Could not load phishing CSV: {e2}")
            
        # Load benign data  
        benign_path = self.root_path / self.config['data']['raw_dirs']['csvs'] / "CSV_benign.csv"
        if benign_path.exists():
            try:
                df_benign = pd.read_csv(benign_path, on_bad_lines='skip', low_memory=False)
                df_benign['label'] = 0  # benign
                df_benign['source'] = 'csv_benign'
                datasets.append(df_benign)
                logger.info(f"Loaded benign CSV: {len(df_benign)} records")
            except Exception as e:
                logger.warning(f"Failed to load benign CSV: {e}")
                try:
                    df_benign = pd.read_csv(benign_path, on_bad_lines='skip', encoding='latin-1', low_memory=False)
                    df_benign['label'] = 0
                    df_benign['source'] = 'csv_benign'
                    datasets.append(df_benign)
                    logger.info(f"Loaded benign CSV with latin-1 encoding: {len(df_benign)} records")
                except Exception as e2:
                    logger.error(f"Could not load benign CSV: {e2}")
            
        # Load malware data
        malware_path = self.root_path / self.config['data']['raw_dirs']['csvs'] / "CSV_malware.csv"
        if malware_path.exists():
            try:
                df_malware = pd.read_csv(malware_path, on_bad_lines='skip', low_memory=False)
                df_malware['label'] = 1  # malicious
                df_malware['source'] = 'csv_malware'
                datasets.append(df_malware)
                logger.info(f"Loaded malware CSV: {len(df_malware)} records")
            except Exception as e:
                logger.warning(f"Failed to load malware CSV: {e}")
            
        # Load spam data
        spam_path = self.root_path / self.config['data']['raw_dirs']['csvs'] / "CSV_spam.csv"  
        if spam_path.exists():
            try:
                df_spam = pd.read_csv(spam_path, on_bad_lines='skip', low_memory=False)
                df_spam['label'] = 1  # malicious
                df_spam['source'] = 'csv_spam'
                datasets.append(df_spam)
                logger.info(f"Loaded spam CSV: {len(df_spam)} records")
            except Exception as e:
                logger.warning(f"Failed to load spam CSV: {e}")
            
        if datasets:
            combined_df = pd.concat(datasets, ignore_index=True)
            logger.info(f"Loaded CSV datasets: {len(combined_df)} records")
            return combined_df
        else:
            logger.warning("No CSV datasets found")
            return pd.DataFrame()
    
    def load_malicious_urls_dataset(self) -> pd.DataFrame:
        """Load the large malicious URLs dataset."""
        urls_path = self.root_path / self.config['data']['raw_dirs']['malicious_urls'] / "malicious_phish.csv"
        
        if urls_path.exists():
            try:
                df = pd.read_csv(urls_path, on_bad_lines='skip', low_memory=False)
                # Map type to binary label
                df['label'] = df['type'].apply(lambda x: 0 if x == 'benign' else 1)
                df['source'] = 'malicious_phish_dataset'
                logger.info(f"Loaded malicious URLs dataset: {len(df)} records")
                return df
            except Exception as e:
                logger.error(f"Failed to load malicious URLs dataset: {e}")
                return pd.DataFrame()
        else:
            logger.warning("Malicious URLs dataset not found")
            return pd.DataFrame()
            
    def load_dns_domains(self) -> pd.DataFrame:
        """Load DNS domains data."""
        domains_path = self.root_path / self.config['data']['raw_dirs']['dns_data'] / "domains.csv"
        
        if domains_path.exists():
            df = pd.read_csv(domains_path)
            df['source'] = 'dns_2m'
            logger.info(f"Loaded DNS domains: {len(df)} records")
            return df
        else:
            logger.warning("DNS domains dataset not found") 
            return pd.DataFrame()
            
    def load_all_datasets(self) -> pd.DataFrame:
        """Load and combine all available datasets."""
        datasets = []
        
        # Load CSV datasets with rich features
        csv_data = self.load_csv_datasets()
        if not csv_data.empty:
            datasets.append(csv_data)
            
        # Load malicious URLs dataset
        urls_data = self.load_malicious_urls_dataset()
        if not urls_data.empty:
            datasets.append(urls_data)
            
        if datasets:
            # Combine all datasets
            combined_df = pd.concat(datasets, ignore_index=True, sort=False)
            
            # Clean and normalize
            combined_df = self._clean_dataset(combined_df)
            
            logger.info(f"Combined dataset: {len(combined_df)} total records")
            logger.info(f"Label distribution: {combined_df['label'].value_counts().to_dict()}")
            
            return combined_df
        else:
            logger.error("No datasets could be loaded")
            return pd.DataFrame()
            
    def _clean_dataset(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and normalize the combined dataset."""
        # Extract domain from various sources
        if 'Domain' in df.columns:
            df['domain_clean'] = df['Domain'].apply(self._clean_domain)
        elif 'url' in df.columns:
            df['domain_clean'] = df['url'].apply(self._extract_domain_from_url)
        elif 'domain' in df.columns:
            df['domain_clean'] = df['domain'].apply(self._clean_domain)
            
        # Remove duplicates based on domain
        if 'domain_clean' in df.columns:
            df = df.drop_duplicates(subset=['domain_clean'], keep='first')
            
        # Ensure we have required columns
        required_cols = ['label', 'source']
        for col in required_cols:
            if col not in df.columns:
                df[col] = None
                
        return df
        
    def _clean_domain(self, domain_str) -> str:
        """Clean domain string."""
        if pd.isna(domain_str):
            return ""
            
        domain_str = str(domain_str)
        
        # Remove b'' wrapper if present
        if domain_str.startswith("b'") and domain_str.endswith("'"):
            domain_str = domain_str[2:-1]
            
        # Remove trailing dot
        domain_str = domain_str.rstrip('.')
        
        # Remove www prefix
        if domain_str.startswith('www.'):
            domain_str = domain_str[4:]
            
        return domain_str.lower()
        
    def _extract_domain_from_url(self, url_str) -> str:
        """Extract domain from URL."""
        if pd.isna(url_str):
            return ""
            
        url_str = str(url_str)
        
        try:
            # Add scheme if missing
            if not url_str.startswith(('http://', 'https://')):
                url_str = 'http://' + url_str
                
            parsed = urlparse(url_str)
            domain = parsed.netloc.lower()
            
            # Remove www prefix
            if domain.startswith('www.'):
                domain = domain[4:]
                
            return domain
        except Exception:
            return ""