"""
Transformer-based model for URL sequence analysis.
Processes URLs as text sequences for malicious pattern detection.
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Tuple, List
import pickle
import logging
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score, classification_report
import re
from collections import Counter

logger = logging.getLogger(__name__)

class URLTokenizer:
    """Tokenizer for URL text sequences"""
    
    def __init__(self, max_length: int = 256, min_freq: int = 2):
        self.max_length = max_length
        self.min_freq = min_freq
        self.char_to_idx = {}
        self.idx_to_char = {}
        self.vocab_size = 0
        
        # Special tokens
        self.pad_token = '<PAD>'
        self.unk_token = '<UNK>'
        self.cls_token = '<CLS>'
        
    def build_vocab(self, urls: List[str]):
        """Build character-level vocabulary from URLs"""
        logger.info("Building URL vocabulary...")
        
        # Count character frequencies
        char_counts = Counter()
        for url in urls:
            # Normalize URL
            normalized = self._normalize_url(url)
            char_counts.update(normalized)
        
        # Create vocabulary with special tokens
        vocab = [self.pad_token, self.unk_token, self.cls_token]
        
        # Add frequent characters
        for char, count in char_counts.items():
            if count >= self.min_freq:
                vocab.append(char)
        
        # Create mappings
        self.char_to_idx = {char: idx for idx, char in enumerate(vocab)}
        self.idx_to_char = {idx: char for char, idx in self.char_to_idx.items()}
        self.vocab_size = len(vocab)
        
        logger.info(f"Built vocabulary with {self.vocab_size} characters")
        
    def _normalize_url(self, url: str) -> str:
        """Normalize URL for tokenization"""
        # Convert to lowercase
        url = url.lower()
        
        # Remove protocol
        url = re.sub(r'^https?://', '', url)
        
        # Replace special patterns with tokens
        url = re.sub(r'\d+', '<NUM>', url)  # Numbers
        url = re.sub(r'[0-9a-f]{8,}', '<HEX>', url)  # Hex strings
        
        return url
    
    def encode(self, url: str) -> List[int]:
        """Encode URL to sequence of character indices"""
        normalized = self._normalize_url(url)
        
        # Start with CLS token
        tokens = [self.char_to_idx[self.cls_token]]
        
        # Add character tokens
        for char in normalized:
            if char in self.char_to_idx:
                tokens.append(self.char_to_idx[char])
            else:
                tokens.append(self.char_to_idx[self.unk_token])
        
        # Truncate or pad to max_length
        if len(tokens) > self.max_length:
            tokens = tokens[:self.max_length]
        else:
            tokens.extend([self.char_to_idx[self.pad_token]] * (self.max_length - len(tokens)))
            
        return tokens
    
    def encode_batch(self, urls: List[str]) -> torch.Tensor:
        """Encode batch of URLs"""
        encoded = [self.encode(url) for url in urls]
        return torch.tensor(encoded, dtype=torch.long)

class URLDataset(Dataset):
    """Dataset for URL classification"""
    
    def __init__(self, urls: List[str], labels: List[int], tokenizer: URLTokenizer):
        self.urls = urls
        self.labels = labels
        self.tokenizer = tokenizer
        
    def __len__(self):
        return len(self.urls)
    
    def __getitem__(self, idx):
        url = self.urls[idx]
        label = self.labels[idx]
        
        # Tokenize URL
        tokens = torch.tensor(self.tokenizer.encode(url), dtype=torch.long)
        label = torch.tensor(label, dtype=torch.long)
        
        return tokens, label

class TransformerURLClassifier(nn.Module):
    """Transformer model for URL classification"""
    
    def __init__(self, vocab_size: int, embed_dim: int = 128, num_heads: int = 8, 
                 num_layers: int = 4, max_length: int = 256, dropout: float = 0.1):
        super().__init__()
        
        self.embed_dim = embed_dim
        self.max_length = max_length
        
        # Embedding layers
        self.char_embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.pos_embedding = nn.Embedding(max_length, embed_dim)
        
        # Transformer encoder
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=embed_dim,
            nhead=num_heads,
            dim_feedforward=embed_dim * 4,
            dropout=dropout,
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        
        # Classification head
        self.classifier = nn.Sequential(
            nn.LayerNorm(embed_dim),
            nn.Linear(embed_dim, embed_dim // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(embed_dim // 2, 2)
        )
        
        self.dropout = nn.Dropout(dropout)
        
    def forward(self, tokens, attention_mask=None):
        batch_size, seq_len = tokens.shape
        
        # Create position indices
        positions = torch.arange(seq_len, device=tokens.device).unsqueeze(0).repeat(batch_size, 1)
        
        # Embeddings
        char_emb = self.char_embedding(tokens)
        pos_emb = self.pos_embedding(positions)
        
        # Combined embeddings
        embeddings = self.dropout(char_emb + pos_emb)
        
        # Create attention mask (ignore padding tokens)
        if attention_mask is None:
            attention_mask = (tokens != 0)  # 0 is padding token
        
        # Transformer encoding
        # Convert attention mask to transformer format (inverted)
        transformer_mask = ~attention_mask
        
        encoded = self.transformer(embeddings, src_key_padding_mask=transformer_mask)
        
        # Use CLS token representation (first token)
        cls_representation = encoded[:, 0]  # [batch_size, embed_dim]
        
        # Classification
        logits = self.classifier(cls_representation)
        
        return logits

class TransformerModel:
    """Transformer model wrapper for URL classification"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config.get('transformer', {})
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Model parameters
        self.max_length = self.config.get('max_length', 256)
        self.embed_dim = self.config.get('embed_dim', 128)
        self.num_heads = self.config.get('num_heads', 8)
        self.num_layers = self.config.get('num_layers', 4)
        self.dropout = self.config.get('dropout', 0.1)
        self.batch_size = self.config.get('batch_size', 32)
        self.epochs = self.config.get('epochs', 10)
        self.learning_rate = self.config.get('learning_rate', 0.001)
        
        # Components
        self.tokenizer = None
        self.model = None
        
    def prepare_data(self, df: pd.DataFrame) -> Tuple[List[str], List[int]]:
        """Prepare URLs and labels for training"""
        urls = df['url'].tolist()
        labels = df['label'].tolist()
        
        return urls, labels
    
    def train(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Train Transformer model"""
        logger.info("Training Transformer URL classifier...")
        
        # Prepare data
        urls, labels = self.prepare_data(df)
        
        # Split data
        urls_train, urls_test, labels_train, labels_test = train_test_split(
            urls, labels, test_size=0.2, random_state=42, stratify=labels
        )
        
        # Build tokenizer
        self.tokenizer = URLTokenizer(max_length=self.max_length)
        self.tokenizer.build_vocab(urls_train)
        
        # Create datasets
        train_dataset = URLDataset(urls_train, labels_train, self.tokenizer)
        test_dataset = URLDataset(urls_test, labels_test, self.tokenizer)
        
        # Create data loaders
        train_loader = DataLoader(train_dataset, batch_size=self.batch_size, shuffle=True)
        test_loader = DataLoader(test_dataset, batch_size=self.batch_size, shuffle=False)
        
        # Initialize model
        self.model = TransformerURLClassifier(
            vocab_size=self.tokenizer.vocab_size,
            embed_dim=self.embed_dim,
            num_heads=self.num_heads,
            num_layers=self.num_layers,
            max_length=self.max_length,
            dropout=self.dropout
        ).to(self.device)
        
        # Training setup
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate)
        scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=3, gamma=0.7)
        
        # Training loop
        self.model.train()
        for epoch in range(self.epochs):
            total_loss = 0
            correct = 0
            total = 0
            
            for tokens, labels_batch in train_loader:
                tokens = tokens.to(self.device)
                labels_batch = labels_batch.to(self.device)
                
                optimizer.zero_grad()
                
                # Forward pass
                logits = self.model(tokens)
                loss = criterion(logits, labels_batch)
                
                # Backward pass
                loss.backward()
                optimizer.step()
                
                # Statistics
                total_loss += loss.item()
                _, predicted = torch.max(logits.data, 1)
                total += labels_batch.size(0)
                correct += (predicted == labels_batch).sum().item()
            
            scheduler.step()
            
            train_acc = 100 * correct / total
            avg_loss = total_loss / len(train_loader)
            
            logger.info(f"Epoch {epoch+1}/{self.epochs} - Loss: {avg_loss:.4f}, Accuracy: {train_acc:.2f}%")
        
        # Evaluate on test set
        self.model.eval()
        test_predictions = []
        test_probabilities = []
        test_labels = []
        
        with torch.no_grad():
            for tokens, labels_batch in test_loader:
                tokens = tokens.to(self.device)
                labels_batch = labels_batch.to(self.device)
                
                logits = self.model(tokens)
                probabilities = torch.softmax(logits, dim=1)
                
                _, predicted = torch.max(logits, 1)
                
                test_predictions.extend(predicted.cpu().numpy())
                test_probabilities.extend(probabilities[:, 1].cpu().numpy())  # Malicious class prob
                test_labels.extend(labels_batch.cpu().numpy())
        
        # Calculate metrics
        accuracy = accuracy_score(test_labels, test_predictions)
        roc_auc = roc_auc_score(test_labels, test_probabilities)
        
        metrics = {
            'accuracy': accuracy,
            'roc_auc': roc_auc,
            'classification_report': classification_report(test_labels, test_predictions, output_dict=True)
        }
        
        logger.info(f"Transformer Test Accuracy: {accuracy:.4f}")
        logger.info(f"Transformer Test ROC-AUC: {roc_auc:.4f}")
        
        return metrics
    
    def predict(self, urls: List[str]) -> Tuple[np.ndarray, np.ndarray]:
        """Make predictions on URLs"""
        if self.model is None or self.tokenizer is None:
            raise ValueError("Model not trained yet")
        
        self.model.eval()
        
        # Create dataset
        dummy_labels = [0] * len(urls)  # Dummy labels for prediction
        dataset = URLDataset(urls, dummy_labels, self.tokenizer)
        loader = DataLoader(dataset, batch_size=self.batch_size, shuffle=False)
        
        predictions = []
        probabilities = []
        
        with torch.no_grad():
            for tokens, _ in loader:
                tokens = tokens.to(self.device)
                
                logits = self.model(tokens)
                probs = torch.softmax(logits, dim=1)
                
                _, preds = torch.max(logits, 1)
                
                predictions.extend(preds.cpu().numpy())
                probabilities.extend(probs[:, 1].cpu().numpy())  # Malicious class prob
        
        return np.array(predictions), np.array(probabilities)
    
    def save(self, model_dir: Path):
        """Save model and tokenizer"""
        model_dir.mkdir(parents=True, exist_ok=True)
        
        # Save model state dict
        torch.save(self.model.state_dict(), model_dir / 'transformer_model.pth')
        
        # Save tokenizer
        with open(model_dir / 'transformer_tokenizer.pkl', 'wb') as f:
            pickle.dump(self.tokenizer, f)
        
        # Save model config
        model_config = {
            'vocab_size': self.tokenizer.vocab_size,
            'embed_dim': self.embed_dim,
            'num_heads': self.num_heads,
            'num_layers': self.num_layers,
            'max_length': self.max_length,
            'dropout': self.dropout
        }
        
        with open(model_dir / 'transformer_config.pkl', 'wb') as f:
            pickle.dump(model_config, f)
        
        logger.info(f"Transformer model saved to {model_dir}")
    
    def load(self, model_dir: Path):
        """Load model and tokenizer"""
        # Load tokenizer
        with open(model_dir / 'transformer_tokenizer.pkl', 'rb') as f:
            self.tokenizer = pickle.load(f)
        
        # Load model config
        with open(model_dir / 'transformer_config.pkl', 'rb') as f:
            model_config = pickle.load(f)
        
        # Initialize model
        self.model = TransformerURLClassifier(**model_config).to(self.device)
        
        # Load model weights
        self.model.load_state_dict(torch.load(model_dir / 'transformer_model.pth', map_location=self.device))
        
        logger.info(f"Transformer model loaded from {model_dir}")