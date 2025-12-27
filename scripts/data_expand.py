#!/usr/bin/env python3
"""
Data Expander for Edge-AI URL Detection
Expands dataset by downloading from:
- URLhaus: Malicious URLs (CSV online + text format)
- Majestic Million: Top benign domains
- Auto-deduplication and balanced sampling
"""

import os
import re
import io
import json
import time
import hashlib
import pandas as pd
import requests
from urllib.parse import urlsplit, urlunsplit
import logging
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --------- SOURCES (official pages cited in paper) ----------
URLHAUS_CSV_ONLINE = "https://urlhaus.abuse.ch/downloads/csv_online/"
URLHAUS_TEXT = "https://urlhaus.abuse.ch/downloads/text/"
MAJESTIC_MILLION_PAGE = "https://majestic.com/reports/majestic-million"

# Backup direct CSV URL (if scraping fails)
MAJESTIC_DIRECT_CSV = "http://downloads.majestic.com/majestic_million.csv"

WS = re.compile(r"\s+")

def normalize_url(url: str) -> str:
    """Normalize URL for consistent processing"""
    if not isinstance(url, str):
        return ""
    url = WS.sub("", url.strip())
    if not url:
        return ""
    if "://" not in url:
        url = "http://" + url
    try:
        p = urlsplit(url)
        scheme = (p.scheme or "http").lower()
        netloc = (p.netloc or "").lower().rstrip(".")
        path = p.path or "/"
        query = p.query or ""
        # ignore fragment
        return urlunsplit((scheme, netloc, path, query, ""))
    except Exception:
        return ""

def extract_host(url: str) -> str:
    """Extract hostname from URL"""
    try:
        p = urlsplit(url if "://" in url else "http://" + url)
        return (p.hostname or "").lower()
    except Exception:
        return ""

def download_text(url: str, timeout: int = 60) -> str:
    """Download text content from URL with retries"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    for attempt in range(3):
        try:
            logger.info(f"Downloading {url} (attempt {attempt + 1})")
            r = requests.get(url, timeout=timeout, headers=headers)
            r.raise_for_status()
            return r.text
        except Exception as e:
            logger.warning(f"Download attempt {attempt + 1} failed: {e}")
            if attempt < 2:
                time.sleep(5)
            else:
                raise

def load_urlhaus_csv_online(max_rows: int = 200000) -> pd.DataFrame:
    """Load malicious URLs from URLhaus CSV format"""
    logger.info("Loading URLhaus CSV online data...")
    try:
        txt = download_text(URLHAUS_CSV_ONLINE)
        # Remove comment lines starting with '#'
        lines = [ln for ln in txt.splitlines() if ln.strip() and not ln.startswith("#")]
        
        if not lines:
            logger.error("No valid data lines found in URLhaus CSV")
            return pd.DataFrame(columns=["url", "domain", "label", "source"])
        
        # Parse CSV - URLhaus format: id,dateadded,url,url_status,threat,tags,reporter
        df = pd.read_csv(io.StringIO("\n".join(lines)), header=None, on_bad_lines='skip')
        
        if df.empty or df.shape[1] < 3:
            logger.error("URLhaus CSV format unexpected")
            return pd.DataFrame(columns=["url", "domain", "label", "source"])
            
        # Column 2 is usually URL
        url_col = 2 if df.shape[1] > 2 else 0
        urls = df[url_col].astype(str).dropna()
        
        out = pd.DataFrame({
            "url_raw": urls
        })
        out["url"] = out["url_raw"].map(normalize_url)
        out["domain"] = out["url"].map(extract_host)
        out["label"] = 1
        out["source"] = "urlhaus_csv_online"
        
        # Filter valid URLs
        out = out.dropna(subset=["url"]).query("url != '' and domain != ''")
        result = out.head(max_rows)[["url", "domain", "label", "source"]]
        
        logger.info(f"Loaded {len(result)} URLs from URLhaus CSV")
        return result
        
    except Exception as e:
        logger.error(f"Failed to load URLhaus CSV: {e}")
        return pd.DataFrame(columns=["url", "domain", "label", "source"])

def load_urlhaus_text(max_rows: int = 200000) -> pd.DataFrame:
    """Load malicious URLs from URLhaus text format"""
    logger.info("Loading URLhaus text data...")
    try:
        txt = download_text(URLHAUS_TEXT)
        # Remove comment lines and empty lines
        lines = [ln.strip() for ln in txt.splitlines() 
                if ln.strip() and not ln.startswith("#")]
        
        if not lines:
            logger.error("No valid URLs found in URLhaus text")
            return pd.DataFrame(columns=["url", "domain", "label", "source"])
        
        out = pd.DataFrame({"url_raw": lines[:max_rows]})
        out["url"] = out["url_raw"].map(normalize_url)
        out["domain"] = out["url"].map(extract_host)
        out["label"] = 1
        out["source"] = "urlhaus_text"
        
        # Filter valid URLs
        out = out.dropna(subset=["url"]).query("url != '' and domain != ''")
        result = out[["url", "domain", "label", "source"]]
        
        logger.info(f"Loaded {len(result)} URLs from URLhaus text")
        return result
        
    except Exception as e:
        logger.error(f"Failed to load URLhaus text: {e}")
        return pd.DataFrame(columns=["url", "domain", "label", "source"])

def scrape_majestic_csv_url(html: str) -> Optional[str]:
    """Extract Majestic CSV download URL from page HTML"""
    # Look for CSV download links
    patterns = [
        r'https?://downloads\.majestic\.com/[^"\']*\.csv',
        r'https?://[^"\']*majestic[^"\']*\.csv',
        r'href=["\']([^"\']*\.csv)["\']'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, html, re.IGNORECASE)
        if match:
            return match.group(1) if len(match.groups()) > 0 else match.group(0)
    
    return None

def load_majestic_million(max_rows: int = 200000) -> pd.DataFrame:
    """Load benign domains from Majestic Million"""
    logger.info("Loading Majestic Million data...")
    
    csv_url = None
    
    # Try to scrape CSV URL from main page
    try:
        html = download_text(MAJESTIC_MILLION_PAGE)
        csv_url = scrape_majestic_csv_url(html)
        if csv_url and not csv_url.startswith('http'):
            csv_url = "https://majestic.com" + csv_url
    except Exception as e:
        logger.warning(f"Failed to scrape Majestic page: {e}")
    
    # Fallback to direct CSV URL
    if not csv_url:
        logger.info("Using direct CSV URL fallback")
        csv_url = MAJESTIC_DIRECT_CSV
    
    try:
        logger.info(f"Downloading Majestic CSV from: {csv_url}")
        csv_text = download_text(csv_url)
        df = pd.read_csv(io.StringIO(csv_text))
        
        # Find domain column (case insensitive)
        domain_col = None
        for col in df.columns:
            if col.lower() in ['domain', 'domain_name', 'host', 'hostname']:
                domain_col = col
                break
        
        if not domain_col:
            logger.error(f"Domain column not found. Available columns: {list(df.columns)}")
            return pd.DataFrame(columns=["url", "domain", "label", "source"])
        
        domains = df[domain_col].astype(str).str.lower().dropna()
        domains = domains[domains != 'nan'].head(max_rows)
        
        out = pd.DataFrame({"domain": domains})
        out["url"] = "http://" + out["domain"] + "/"
        out["url"] = out["url"].map(normalize_url)
        out["label"] = 0
        out["source"] = "majestic_million"
        
        # Filter valid domains
        out = out.dropna(subset=["url", "domain"]).query("domain != ''")
        result = out[["url", "domain", "label", "source"]]
        
        logger.info(f"Loaded {len(result)} domains from Majestic Million")
        return result
        
    except Exception as e:
        logger.error(f"Failed to load Majestic Million: {e}")
        return pd.DataFrame(columns=["url", "domain", "label", "source"])

def dedup_and_validate(df: pd.DataFrame) -> pd.DataFrame:
    """Deduplicate and validate URLs"""
    logger.info(f"Deduplicating {len(df)} URLs...")
    
    # Remove null/empty URLs
    df = df.dropna(subset=["url", "domain"]).copy()
    df = df[(df["url"] != "") & (df["domain"] != "")]
    
    # Remove duplicates by URL
    original_len = len(df)
    df = df.drop_duplicates(subset=["url"]).reset_index(drop=True)
    
    logger.info(f"Removed {original_len - len(df)} duplicate URLs")
    return df

def balance_dataset(df: pd.DataFrame, max_per_class: Optional[int] = None) -> pd.DataFrame:
    """Balance malicious vs benign samples"""
    malicious = df[df["label"] == 1].copy()
    benign = df[df["label"] == 0].copy()
    
    logger.info(f"Before balancing - Malicious: {len(malicious)}, Benign: {len(benign)}")
    
    if max_per_class:
        target_size = min(max_per_class, len(malicious), len(benign))
    else:
        target_size = min(len(malicious), len(benign))
    
    # Sample balanced subsets
    if len(malicious) > target_size:
        malicious = malicious.sample(n=target_size, random_state=42)
    if len(benign) > target_size:
        benign = benign.sample(n=target_size, random_state=42)
    
    # Combine and shuffle
    balanced_df = pd.concat([malicious, benign], axis=0, ignore_index=True)
    balanced_df = balanced_df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    logger.info(f"After balancing - Total: {len(balanced_df)} ({len(malicious)} malicious, {len(benign)} benign)")
    return balanced_df

def main():
    """Main data expansion pipeline"""
    logger.info("Starting data expansion pipeline...")
    
    # Create output directory
    os.makedirs("data/processed", exist_ok=True)
    
    # Load data from multiple sources
    datasets = []
    
    # Load malicious URLs
    urlhaus_csv = load_urlhaus_csv_online(max_rows=100000)
    if not urlhaus_csv.empty:
        datasets.append(urlhaus_csv)
    
    urlhaus_text = load_urlhaus_text(max_rows=100000)
    if not urlhaus_text.empty:
        datasets.append(urlhaus_text)
    
    # Load benign domains
    majestic = load_majestic_million(max_rows=200000)
    if not majestic.empty:
        datasets.append(majestic)
    
    if not datasets:
        logger.error("No datasets loaded successfully!")
        return
    
    # Combine all datasets
    logger.info("Combining datasets...")
    combined_df = pd.concat(datasets, axis=0, ignore_index=True)
    
    # Deduplicate and validate
    clean_df = dedup_and_validate(combined_df)
    
    if clean_df.empty:
        logger.error("No valid data after cleaning!")
        return
    
    # Save full dataset
    clean_df.to_csv("data/processed/urls_full_expanded.csv", index=False)
    logger.info(f"Saved full dataset: {len(clean_df)} URLs")
    
    # Create balanced dataset
    balanced_df = balance_dataset(clean_df, max_per_class=50000)
    balanced_df.to_csv("data/processed/urls_balanced_expanded.csv", index=False)
    logger.info(f"Saved balanced dataset: {len(balanced_df)} URLs")
    
    # Print statistics
    print("\n=== DATASET EXPANSION RESULTS ===")
    print(f"Full Dataset: {len(clean_df)} URLs")
    print("Label distribution (full):")
    print(clean_df["label"].value_counts().to_dict())
    print("\nSource distribution (full):")
    print(clean_df["source"].value_counts().to_dict())
    
    print(f"\nBalanced Dataset: {len(balanced_df)} URLs")
    print("Label distribution (balanced):")
    print(balanced_df["label"].value_counts().to_dict())
    print("Source distribution (balanced):")
    print(balanced_df["source"].value_counts().to_dict())
    
    # Sample preview
    print(f"\nSample URLs (first 5 from each class):")
    for label in [0, 1]:
        label_name = "Benign" if label == 0 else "Malicious"
        print(f"\n{label_name} URLs:")
        sample_urls = balanced_df[balanced_df["label"] == label]["url"].head(5).tolist()
        for i, url in enumerate(sample_urls, 1):
            print(f"  {i}. {url}")

if __name__ == "__main__":
    main()