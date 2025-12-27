"""
Graph Neural Network model for domain relationship analysis.
Uses domain DNS and SSL relationships to build graph structures.
"""

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch_geometric.nn import GCNConv, GATConv, global_mean_pool
from torch_geometric.data import Data, DataLoader
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Tuple, List, Optional
import pickle
import logging
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score, classification_report
from sklearn.preprocessing import StandardScaler
import networkx as nx
from collections import defaultdict
import re

logger = logging.getLogger(__name__)

class GraphBuilder:
    """Build graph structures from domain and URL data"""
    
    def __init__(self):
        self.domain_to_idx = {}
        self.idx_to_domain = {}
        self.scaler = StandardScaler()
        
    def extract_domain_features(self, df: pd.DataFrame) -> Dict[str, np.ndarray]:
        """Extract node features for each domain"""
        logger.info("Extracting domain node features...")
        
        domain_features = {}
        
        for _, row in df.iterrows():
            url = row['url']
            domain = self._extract_domain(url)
            
            if domain not in domain_features:
                domain_features[domain] = []
            
            # Extract numerical features (exclude non-numerical columns)
            features = []
            for col in df.columns:
                if col not in ['url', 'domain', 'label', 'source'] and pd.api.types.is_numeric_dtype(df[col]):
                    features.append(row[col] if not pd.isna(row[col]) else 0.0)
            
            domain_features[domain].append(features)
        
        # Average features per domain
        averaged_features = {}
        for domain, feat_list in domain_features.items():
            if feat_list:
                averaged_features[domain] = np.mean(feat_list, axis=0)
            else:
                averaged_features[domain] = np.zeros(len(feat_list[0]) if feat_list else 10)
        
        return averaged_features
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        # Remove protocol
        url = re.sub(r'^https?://', '', url)
        
        # Extract domain part
        domain = url.split('/')[0]
        
        # Remove port if present
        domain = domain.split(':')[0]
        
        # Remove www prefix
        if domain.startswith('www.'):
            domain = domain[4:]
            
        return domain.lower()
    
    def build_domain_relationships(self, df: pd.DataFrame) -> List[Tuple[str, str]]:
        """Build edges based on domain relationships"""
        logger.info("Building domain relationship edges...")
        
        edges = []
        domain_ips = defaultdict(set)
        domain_nameservers = defaultdict(set)
        
        # Group domains by IP and nameservers (if available in features)
        for _, row in df.iterrows():
            domain = self._extract_domain(row['url'])
            
            # Simulate IP and nameserver relationships (in real implementation, use actual data)
            # For now, create edges based on domain similarity and features
            
            # Add edges based on similar top-level domains
            tld = domain.split('.')[-1] if '.' in domain else domain
            
            # Store for relationship building
            domain_ips[domain].add(f"ip_{hash(domain) % 1000}")  # Simulated IP
            domain_nameservers[domain].add(f"ns_{tld}")  # Simulated NS
        
        # Create edges between domains sharing IPs or nameservers
        domains = list(domain_ips.keys())
        
        for i, domain1 in enumerate(domains):
            for j, domain2 in enumerate(domains[i+1:], i+1):
                # Connect if domains share infrastructure
                if (domain_ips[domain1] & domain_ips[domain2] or 
                    domain_nameservers[domain1] & domain_nameservers[domain2]):
                    edges.append((domain1, domain2))
                
                # Connect similar domains (same TLD and similar structure)
                if self._domains_similar(domain1, domain2):
                    edges.append((domain1, domain2))
        
        logger.info(f"Created {len(edges)} domain relationship edges")
        return edges
    
    def _domains_similar(self, domain1: str, domain2: str) -> bool:
        """Check if two domains are structurally similar"""
        # Same TLD
        if domain1.split('.')[-1] != domain2.split('.')[-1]:
            return False
        
        # Similar length
        if abs(len(domain1) - len(domain2)) > 5:
            return False
        
        # Similar character patterns
        chars1 = set(domain1.replace('.', ''))
        chars2 = set(domain2.replace('.', ''))
        
        # Jaccard similarity
        jaccard = len(chars1 & chars2) / len(chars1 | chars2) if chars1 | chars2 else 0
        
        return jaccard > 0.7
    
    def build_graph_data(self, df: pd.DataFrame) -> List[Data]:
        """Build graph data objects for GNN training"""
        logger.info("Building graph data for GNN...")
        
        # Extract domain features
        domain_features = self.extract_domain_features(df)
        domains = list(domain_features.keys())
        
        # Create domain mappings
        self.domain_to_idx = {domain: idx for idx, domain in enumerate(domains)}
        self.idx_to_domain = {idx: domain for domain, idx in self.domain_to_idx.items()}
        
        # Build edges
        edge_list = self.build_domain_relationships(df)
        
        # Convert to node indices
        edge_index = []
        for domain1, domain2 in edge_list:
            if domain1 in self.domain_to_idx and domain2 in self.domain_to_idx:
                idx1 = self.domain_to_idx[domain1]
                idx2 = self.domain_to_idx[domain2]
                # Add both directions (undirected graph)
                edge_index.append([idx1, idx2])
                edge_index.append([idx2, idx1])
        
        # Create node feature matrix
        node_features = []
        node_labels = []
        
        for domain in domains:
            features = domain_features[domain]
            node_features.append(features)
            
            # Get label (majority vote from URLs of this domain)
            domain_urls = df[df['url'].str.contains(domain, regex=False, na=False)]
            if len(domain_urls) > 0:
                label = domain_urls['label'].mode().iloc[0] if len(domain_urls['label'].mode()) > 0 else 0
            else:
                label = 0
            node_labels.append(label)
        
        # Normalize features
        node_features = np.array(node_features)
        if len(node_features) > 0:
            node_features = self.scaler.fit_transform(node_features)
        
        # Convert to tensors
        x = torch.tensor(node_features, dtype=torch.float)
        edge_index = torch.tensor(edge_index, dtype=torch.long).t().contiguous() if edge_index else torch.empty((2, 0), dtype=torch.long)
        y = torch.tensor(node_labels, dtype=torch.long)
        
        # Create graph data object
        graph_data = Data(x=x, edge_index=edge_index, y=y)
        
        return [graph_data]  # Single graph for now

class GNNClassifier(nn.Module):
    """Graph Neural Network for domain classification"""
    
    def __init__(self, num_features: int, hidden_dim: int = 64, num_classes: int = 2, 
                 dropout: float = 0.1, num_layers: int = 2):
        super().__init__()
        
        self.num_layers = num_layers
        self.dropout = dropout
        
        # GNN layers (using Graph Attention Networks)
        self.convs = nn.ModuleList()
        
        # First layer
        self.convs.append(GATConv(num_features, hidden_dim, heads=4, dropout=dropout))
        
        # Hidden layers
        for _ in range(num_layers - 2):
            self.convs.append(GATConv(hidden_dim * 4, hidden_dim, heads=4, dropout=dropout))
        
        # Last layer (single head)
        if num_layers > 1:
            self.convs.append(GATConv(hidden_dim * 4, hidden_dim, heads=1, dropout=dropout))
        
        # Classification head
        final_dim = hidden_dim if num_layers > 1 else hidden_dim * 4
        self.classifier = nn.Sequential(
            nn.LayerNorm(final_dim),
            nn.Linear(final_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim // 2, num_classes)
        )
    
    def forward(self, x, edge_index, batch=None):
        # Apply GNN layers
        for i, conv in enumerate(self.convs):
            x = conv(x, edge_index)
            if i < len(self.convs) - 1:  # Don't apply activation after last layer
                x = F.relu(x)
                x = F.dropout(x, p=self.dropout, training=self.training)
        
        # Global pooling (if batch is provided)
        if batch is not None:
            x = global_mean_pool(x, batch)
        else:
            # Node-level prediction (average across all nodes)
            x = torch.mean(x, dim=0, keepdim=True)
        
        # Classification
        logits = self.classifier(x)
        
        return logits

class GNNModel:
    """GNN model wrapper for domain relationship analysis"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config.get('gnn', {})
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Model parameters
        self.hidden_dim = self.config.get('hidden_dim', 64)
        self.num_layers = self.config.get('num_layers', 2)
        self.dropout = self.config.get('dropout', 0.1)
        self.batch_size = self.config.get('batch_size', 1)  # Typically 1 for graph-level tasks
        self.epochs = self.config.get('epochs', 50)
        self.learning_rate = self.config.get('learning_rate', 0.001)
        
        # Components
        self.graph_builder = None
        self.model = None
        self.graph_data = None
        
    def train(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Train GNN model"""
        logger.info("Training GNN model...")
        
        # Build graph data
        self.graph_builder = GraphBuilder()
        graph_list = self.graph_builder.build_graph_data(df)
        
        if not graph_list or len(graph_list) == 0:
            logger.error("No graph data generated")
            return {'accuracy': 0.0, 'roc_auc': 0.5}
        
        self.graph_data = graph_list[0]  # Single graph
        
        if self.graph_data.x.size(0) == 0:
            logger.error("Empty graph data")
            return {'accuracy': 0.0, 'roc_auc': 0.5}
        
        # Initialize model
        num_features = self.graph_data.x.size(1)
        self.model = GNNClassifier(
            num_features=num_features,
            hidden_dim=self.hidden_dim,
            num_layers=self.num_layers,
            dropout=self.dropout
        ).to(self.device)
        
        # Move data to device
        self.graph_data = self.graph_data.to(self.device)
        
        # Split nodes for training/testing
        num_nodes = self.graph_data.x.size(0)
        indices = torch.randperm(num_nodes)
        
        train_size = int(0.8 * num_nodes)
        train_mask = torch.zeros(num_nodes, dtype=torch.bool)
        test_mask = torch.zeros(num_nodes, dtype=torch.bool)
        
        train_mask[indices[:train_size]] = True
        test_mask[indices[train_size:]] = True
        
        # Training setup
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate)
        scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.7)
        
        # Training loop
        self.model.train()
        for epoch in range(self.epochs):
            optimizer.zero_grad()
            
            # Forward pass
            logits = self.model(self.graph_data.x, self.graph_data.edge_index)
            
            # Calculate loss only on training nodes
            if logits.size(0) == 1:  # Graph-level prediction
                # Use majority class from training nodes
                train_labels = self.graph_data.y[train_mask]
                if len(train_labels) > 0:
                    majority_label = train_labels.mode().values.item() if len(train_labels) > 1 else train_labels[0].item()
                    target = torch.tensor([majority_label], device=self.device)
                    loss = criterion(logits, target)
                else:
                    continue
            else:  # Node-level prediction
                loss = criterion(logits[train_mask], self.graph_data.y[train_mask])
            
            # Backward pass
            loss.backward()
            optimizer.step()
            scheduler.step()
            
            if (epoch + 1) % 10 == 0:
                logger.info(f"Epoch {epoch+1}/{self.epochs} - Loss: {loss.item():.4f}")
        
        # Evaluation
        self.model.eval()
        with torch.no_grad():
            logits = self.model(self.graph_data.x, self.graph_data.edge_index)
            
            if logits.size(0) == 1:  # Graph-level prediction
                # Use test nodes for evaluation
                test_labels = self.graph_data.y[test_mask].cpu().numpy()
                if len(test_labels) > 0:
                    # Predict majority class
                    probs = torch.softmax(logits, dim=1)
                    predicted_class = torch.argmax(logits, dim=1).cpu().numpy()[0]
                    
                    # Simple evaluation - predict same class for all test nodes
                    predictions = np.full(len(test_labels), predicted_class)
                    probabilities = np.full(len(test_labels), probs[0, 1].cpu().numpy())
                else:
                    predictions = np.array([])
                    probabilities = np.array([])
                    test_labels = np.array([])
            else:  # Node-level prediction
                predictions = torch.argmax(logits[test_mask], dim=1).cpu().numpy()
                probabilities = torch.softmax(logits[test_mask], dim=1)[:, 1].cpu().numpy()
                test_labels = self.graph_data.y[test_mask].cpu().numpy()
        
        # Calculate metrics
        if len(test_labels) > 0 and len(predictions) > 0:
            accuracy = accuracy_score(test_labels, predictions)
            if len(np.unique(test_labels)) > 1:
                roc_auc = roc_auc_score(test_labels, probabilities)
            else:
                roc_auc = 0.5
        else:
            accuracy = 0.0
            roc_auc = 0.5
        
        metrics = {
            'accuracy': accuracy,
            'roc_auc': roc_auc,
            'num_nodes': num_nodes,
            'num_edges': self.graph_data.edge_index.size(1)
        }
        
        logger.info(f"GNN Test Accuracy: {accuracy:.4f}")
        logger.info(f"GNN Test ROC-AUC: {roc_auc:.4f}")
        logger.info(f"Graph Stats - Nodes: {num_nodes}, Edges: {self.graph_data.edge_index.size(1)}")
        
        return metrics
    
    def predict(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Make predictions on new domains"""
        if self.model is None or self.graph_builder is None:
            raise ValueError("Model not trained yet")
        
        # For simplicity, use trained graph structure
        # In practice, you'd build a new graph with new domains
        self.model.eval()
        
        with torch.no_grad():
            logits = self.model(self.graph_data.x, self.graph_data.edge_index)
            
            if logits.size(0) == 1:  # Graph-level
                # Return prediction for all domains in input
                num_samples = len(df)
                predicted_class = torch.argmax(logits, dim=1).cpu().numpy()[0]
                probs = torch.softmax(logits, dim=1)[0, 1].cpu().numpy()
                
                predictions = np.full(num_samples, predicted_class)
                probabilities = np.full(num_samples, probs)
            else:  # Node-level
                predictions = torch.argmax(logits, dim=1).cpu().numpy()
                probabilities = torch.softmax(logits, dim=1)[:, 1].cpu().numpy()
                
                # Match to input samples (simple mapping)
                if len(predictions) != len(df):
                    # Repeat predictions to match input size
                    predictions = np.tile(predictions, (len(df) // len(predictions) + 1))[:len(df)]
                    probabilities = np.tile(probabilities, (len(df) // len(probabilities) + 1))[:len(df)]
        
        return predictions, probabilities
    
    def save(self, model_dir: Path):
        """Save model and graph builder"""
        model_dir.mkdir(parents=True, exist_ok=True)
        
        # Save model state dict
        torch.save(self.model.state_dict(), model_dir / 'gnn_model.pth')
        
        # Save graph builder
        with open(model_dir / 'gnn_graph_builder.pkl', 'wb') as f:
            pickle.dump(self.graph_builder, f)
        
        # Save graph data
        torch.save(self.graph_data, model_dir / 'gnn_graph_data.pt')
        
        # Save model config
        model_config = {
            'num_features': self.graph_data.x.size(1) if self.graph_data is not None else 0,
            'hidden_dim': self.hidden_dim,
            'num_layers': self.num_layers,
            'dropout': self.dropout
        }
        
        with open(model_dir / 'gnn_config.pkl', 'wb') as f:
            pickle.dump(model_config, f)
        
        logger.info(f"GNN model saved to {model_dir}")
    
    def load(self, model_dir: Path):
        """Load model and graph builder"""
        # Load graph builder
        with open(model_dir / 'gnn_graph_builder.pkl', 'rb') as f:
            self.graph_builder = pickle.load(f)
        
        # Load graph data
        self.graph_data = torch.load(model_dir / 'gnn_graph_data.pt', map_location=self.device)
        
        # Load model config
        with open(model_dir / 'gnn_config.pkl', 'rb') as f:
            model_config = pickle.load(f)
        
        # Initialize model
        self.model = GNNClassifier(**model_config).to(self.device)
        
        # Load model weights
        self.model.load_state_dict(torch.load(model_dir / 'gnn_model.pth', map_location=self.device))
        
        logger.info(f"GNN model loaded from {model_dir}")