"""
Advanced Analytics Engine for Quranic Roots Analysis
Phase 2: Backend API & Analytics Engine
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from collections import defaultdict, Counter
import logging

logger = logging.getLogger(__name__)

try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    logger.warning("NetworkX not available - network analysis disabled")

try:
    from sklearn.cluster import KMeans
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("Scikit-learn not available - clustering disabled")

try:
    from scipy import stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    logger.warning("SciPy not available - advanced statistics disabled")

class QuranicAnalytics:
    """
    Advanced analytics engine for Quranic root word analysis
    
    Provides statistical analysis, machine learning insights,
    and network analysis capabilities for the Quranic dataset.
    """
    
    def __init__(self):
        """Initialize the analytics engine"""
        self.enhanced_df = None
        self.frequency_df = None
        self.cooccurrence_df = None
        self.network_graph = None
        self._load_data()
    
    def _load_data(self):
        """Load all required datasets"""
        try:
            self.enhanced_df = pd.read_csv('quran-enhanced-phase1.csv')
            self.frequency_df = pd.read_csv('root-frequency-analysis.csv')
            self.cooccurrence_df = pd.read_csv('root-cooccurrence-matrix.csv')
            
            if NETWORKX_AVAILABLE:
                self._build_network_graph()
            
            logger.info("✅ Analytics engine initialized with data")
        except Exception as e:
            logger.error(f"❌ Failed to load data for analytics: {e}")
            # Create empty dataframes as fallback
            self.enhanced_df = pd.DataFrame()
            self.frequency_df = pd.DataFrame()
            self.cooccurrence_df = pd.DataFrame()
    
    def _build_network_graph(self):
        """Build NetworkX graph from co-occurrence data"""
        if not NETWORKX_AVAILABLE:
            return
            
        try:
            self.network_graph = nx.Graph()
            
            # Add nodes (roots)
            for _, row in self.frequency_df.iterrows():
                self.network_graph.add_node(
                    row['root'],
                    frequency=row['total_frequency'],
                    category=row['semantic_category'],
                    arabic=row.get('root_arabic', '')
                )
            
            # Add edges (co-occurrences)
            for _, row in self.cooccurrence_df.iterrows():
                self.network_graph.add_edge(
                    row['root1'],
                    row['root2'],
                    weight=row['cooccurrence_count']
                )
            
            logger.info(f"✅ Network graph built: {len(self.network_graph.nodes)} nodes, {len(self.network_graph.edges)} edges")
            
        except Exception as e:
            logger.error(f"❌ Failed to build network graph: {e}")
            self.network_graph = nx.Graph()
    
    def frequency_analysis(self, filters: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Comprehensive frequency analysis of roots
        
        Args:
            filters: Optional filters to apply to the analysis
            
        Returns:
            Dictionary with frequency analysis results
        """
        try:
            if self.frequency_df.empty:
                return {"error": "No frequency data available"}
                
            df = self.frequency_df.copy()
            
            # Apply filters if provided
            if filters:
                if 'min_frequency' in filters:
                    df = df[df['total_frequency'] >= filters['min_frequency']]
                if 'semantic_category' in filters:
                    df = df[df['semantic_category'] == filters['semantic_category']]
                if 'revelation_preference' in filters:
                    if filters['revelation_preference'] == 'meccan':
                        df = df[df['meccan_ratio'] > 0.6]
                    elif filters['revelation_preference'] == 'medinan':
                        df = df[df['meccan_ratio'] < 0.4]
            
            # Calculate statistics
            total_roots = len(df)
            hapax_legomena = len(df[df['total_frequency'] == 1])
            very_frequent = len(df[df['total_frequency'] >= 100])
            
            # Frequency distribution
            freq_ranges = {
                '1': len(df[df['total_frequency'] == 1]),
                '2-5': len(df[(df['total_frequency'] >= 2) & (df['total_frequency'] <= 5)]),
                '6-20': len(df[(df['total_frequency'] >= 6) & (df['total_frequency'] <= 20)]),
                '21-100': len(df[(df['total_frequency'] >= 21) & (df['total_frequency'] <= 100)]),
                '100+': len(df[df['total_frequency'] > 100])
            }
            
            # Top frequent roots
            top_roots = df.nlargest(20, 'total_frequency')[
                ['root', 'root_arabic', 'total_frequency', 'semantic_category']
            ].to_dict('records')
            
            # Category distribution
            category_dist = df.groupby('semantic_category').agg({
                'total_frequency': ['count', 'sum', 'mean']
            }).round(2).to_dict()
            
            # Revelation analysis
            meccan_total = df['meccan_frequency'].sum()
            medinan_total = df['medinan_frequency'].sum()
            
            revelation_stats = {
                'meccan_total_occurrences': int(meccan_total),
                'medinan_total_occurrences': int(medinan_total),
                'meccan_percentage': round(meccan_total / (meccan_total + medinan_total) * 100, 2),
                'strongly_meccan_roots': len(df[df['meccan_ratio'] > 0.8]),
                'strongly_medinan_roots': len(df[df['meccan_ratio'] < 0.2]),
                'balanced_roots': len(df[(df['meccan_ratio'] >= 0.4) & (df['meccan_ratio'] <= 0.6)])
            }
            
            # Statistical summary
            stats_summary = {
                'mean_frequency': float(df['total_frequency'].mean()),
                'median_frequency': float(df['total_frequency'].median()),
                'std_frequency': float(df['total_frequency'].std()),
            }
            
            if SCIPY_AVAILABLE:
                stats_summary['skewness'] = float(stats.skew(df['total_frequency']))
            
            return {
                'total_unique_roots': total_roots,
                'hapax_legomena_count': hapax_legomena,
                'very_frequent_count': very_frequent,
                'frequency_distribution': freq_ranges,
                'top_frequent_roots': top_roots,
                'category_distribution': category_dist,
                'revelation_analysis': revelation_stats,
                'statistical_summary': stats_summary
            }
            
        except Exception as e:
            logger.error(f"Error in frequency analysis: {e}")
            return {"error": str(e)}
    
    def cooccurrence_analysis(self, min_cooccurrence: int = 2) -> Dict[str, Any]:
        """
        Analyze co-occurrence patterns and build network metrics
        
        Args:
            min_cooccurrence: Minimum co-occurrence threshold
            
        Returns:
            Dictionary with co-occurrence analysis results
        """
        try:
            if self.cooccurrence_df.empty:
                return {"error": "No co-occurrence data available"}
                
            # Filter co-occurrences
            df = self.cooccurrence_df[self.cooccurrence_df['cooccurrence_count'] >= min_cooccurrence]
            
            # Top co-occurring pairs
            top_pairs = df.nlargest(20, 'cooccurrence_count')[
                ['root1', 'root2', 'cooccurrence_count']
            ].to_dict('records')
            
            # Add Arabic forms
            for pair in top_pairs:
                pair['root1_arabic'] = self._get_arabic_form(pair['root1'])
                pair['root2_arabic'] = self._get_arabic_form(pair['root2'])
            
            # Network analysis
            network_metrics = self._calculate_network_metrics()
            
            # Semantic clustering
            semantic_clusters = self._analyze_semantic_clustering()
            
            # Strong associations (high co-occurrence relative to individual frequencies)
            strong_associations = self._find_strong_associations(df)
            
            return {
                'total_pairs_analyzed': len(self.cooccurrence_df),
                'significant_pairs': len(df),
                'top_cooccurring_pairs': top_pairs,
                'network_metrics': network_metrics,
                'semantic_clustering': semantic_clusters,
                'strong_associations': strong_associations,
                'statistics': {
                    'mean_cooccurrence': float(df['cooccurrence_count'].mean()),
                    'max_cooccurrence': int(df['cooccurrence_count'].max()),
                    'network_density': float(nx.density(self.network_graph)) if self.network_graph else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error in co-occurrence analysis: {e}")
            return {"error": str(e)}
    
    def thematic_analysis(self) -> Dict[str, Any]:
        """
        Analyze thematic patterns and semantic categories
        
        Returns:
            Dictionary with thematic analysis results
        """
        try:
            if self.frequency_df.empty:
                return {"error": "No frequency data available"}
                
            # Category distribution
            category_stats = self.frequency_df.groupby('semantic_category').agg({
                'total_frequency': ['count', 'sum', 'mean'],
                'meccan_frequency': 'sum',
                'medinan_frequency': 'sum'
            }).round(2)
            
            category_stats.columns = ['root_count', 'total_occurrences', 'avg_frequency', 'meccan_total', 'medinan_total']
            category_stats['meccan_ratio'] = category_stats['meccan_total'] / (category_stats['meccan_total'] + category_stats['medinan_total'])
            
            # Revelation preferences by category
            revelation_preferences = {}
            for category, row in category_stats.iterrows():
                if row['meccan_ratio'] > 0.7:
                    revelation_preferences[category] = 'strongly_meccan'
                elif row['meccan_ratio'] < 0.3:
                    revelation_preferences[category] = 'strongly_medinan'
                else:
                    revelation_preferences[category] = 'balanced'
            
            # Category relationships (co-occurrence between categories)
            category_relationships = self._analyze_category_relationships()
            
            # Temporal evolution (if chronological data available)
            temporal_evolution = self._analyze_temporal_evolution()
            
            return {
                'category_distribution': category_stats.to_dict('index'),
                'revelation_preferences': revelation_preferences,
                'category_relationships': category_relationships,
                'temporal_evolution': temporal_evolution,
                'diversity_metrics': {
                    'categories_with_data': len(category_stats[category_stats['root_count'] > 0]),
                    'most_diverse_category': category_stats['root_count'].idxmax(),
                    'most_frequent_category': category_stats['total_occurrences'].idxmax()
                }
            }
            
        except Exception as e:
            logger.error(f"Error in thematic analysis: {e}")
            return {"error": str(e)}
    
    def semantic_clustering(self, n_clusters: int = 8) -> Dict[str, Any]:
        """
        Perform semantic clustering of roots based on co-occurrence patterns
        
        Args:
            n_clusters: Number of clusters to create
            
        Returns:
            Dictionary with clustering results
        """
        if not SKLEARN_AVAILABLE:
            return {"error": "Scikit-learn not available for clustering"}
            
        try:
            if self.frequency_df.empty:
                return {"error": "No frequency data available"}
                
            # Create feature matrix based on co-occurrence
            roots = self.frequency_df['root'].tolist()
            cooccurrence_matrix = self._create_cooccurrence_matrix(roots)
            
            # Apply K-means clustering
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(cooccurrence_matrix)
            
            # Organize results
            clusters = defaultdict(list)
            for i, root in enumerate(roots):
                cluster_id = cluster_labels[i]
                clusters[f"cluster_{cluster_id}"].append({
                    'root': root,
                    'root_arabic': self._get_arabic_form(root),
                    'category': self._get_semantic_category(root),
                    'frequency': self._get_frequency(root)
                })
            
            # Analyze cluster characteristics
            cluster_analysis = {}
            for cluster_id, members in clusters.items():
                categories = [member['category'] for member in members]
                category_dist = Counter(categories)
                
                cluster_analysis[cluster_id] = {
                    'size': len(members),
                    'dominant_category': category_dist.most_common(1)[0][0] if category_dist else 'unknown',
                    'category_diversity': len(set(categories)),
                    'avg_frequency': np.mean([member['frequency'] for member in members]),
                    'top_roots': sorted(members, key=lambda x: x['frequency'], reverse=True)[:5]
                }
            
            return {
                'clusters': dict(clusters),
                'cluster_analysis': cluster_analysis,
                'clustering_metrics': {
                    'n_clusters': n_clusters,
                    'silhouette_score': self._calculate_silhouette_score(cooccurrence_matrix, cluster_labels),
                    'inertia': float(kmeans.inertia_)
                }
            }
            
        except Exception as e:
            logger.error(f"Error in semantic clustering: {e}")
            return {"error": str(e)}
    
    def revelation_evolution_analysis(self) -> Dict[str, Any]:
        """
        Analyze vocabulary evolution between Meccan and Medinan periods
        
        Returns:
            Dictionary with evolution analysis results
        """
        try:
            meccan_roots = set(self.frequency_df[self.frequency_df['meccan_frequency'] > 0]['root'])
            medinan_roots = set(self.frequency_df[self.frequency_df['medinan_frequency'] > 0]['root'])
            
            # Calculate overlaps and unique sets
            shared_roots = meccan_roots & medinan_roots
            meccan_only = meccan_roots - medinan_roots
            medinan_only = medinan_roots - meccan_roots
            
            # Analyze category evolution
            category_evolution = {}
            for category in self.frequency_df['semantic_category'].unique():
                cat_data = self.frequency_df[self.frequency_df['semantic_category'] == category]
                
                meccan_freq = cat_data['meccan_frequency'].sum()
                medinan_freq = cat_data['medinan_frequency'].sum()
                total_freq = meccan_freq + medinan_freq
                
                if total_freq > 0:
                    category_evolution[category] = {
                        'meccan_prominence': meccan_freq / total_freq,
                        'medinan_prominence': medinan_freq / total_freq,
                        'evolution_trend': 'increased' if medinan_freq > meccan_freq else 'decreased'
                    }
            
            # New vocabulary introduction
            new_roots_medinan = self._analyze_new_vocabulary('medinan')
            
            return {
                'vocabulary_overlap': {
                    'total_roots': len(meccan_roots | medinan_roots),
                    'shared_roots': len(shared_roots),
                    'meccan_only': len(meccan_only),
                    'medinan_only': len(medinan_only),
                    'overlap_percentage': len(shared_roots) / len(meccan_roots | medinan_roots) * 100
                },
                'category_evolution': category_evolution,
                'new_vocabulary': new_roots_medinan,
                'frequency_shifts': self._analyze_frequency_shifts(),
                'linguistic_diversity': {
                    'meccan_diversity': len(meccan_roots),
                    'medinan_diversity': len(medinan_roots),
                    'diversity_ratio': len(medinan_roots) / len(meccan_roots) if meccan_roots else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error in revelation evolution analysis: {e}")
            raise
    
    # Helper methods
    def _get_arabic_form(self, root: str) -> str:
        """Get Arabic form of a root"""
        try:
            if not self.frequency_df.empty and 'root_arabic' in self.frequency_df.columns:
                result = self.frequency_df[self.frequency_df['root'] == root]['root_arabic']
                if not result.empty:
                    arabic = result.iloc[0]
                    return arabic if pd.notna(arabic) else root
            return root
        except:
            return root
    
    def _get_semantic_category(self, root: str) -> str:
        """Get semantic category of a root"""
        try:
            if not self.frequency_df.empty:
                result = self.frequency_df[self.frequency_df['root'] == root]['semantic_category']
                if not result.empty:
                    return result.iloc[0]
            return 'uncategorized'
        except:
            return 'uncategorized'
    
    def _get_frequency(self, root: str) -> int:
        """Get total frequency of a root"""
        try:
            if not self.frequency_df.empty:
                result = self.frequency_df[self.frequency_df['root'] == root]['total_frequency']
                if not result.empty:
                    return int(result.iloc[0])
            return 0
        except:
            return 0
    
    def _calculate_network_metrics(self) -> Dict[str, Any]:
        """Calculate network analysis metrics"""
        if not NETWORKX_AVAILABLE or not self.network_graph or len(self.network_graph.nodes) == 0:
            return {'note': 'Network analysis not available'}
        
        try:
            metrics = {
                'nodes': len(self.network_graph.nodes),
                'edges': len(self.network_graph.edges),
                'density': float(nx.density(self.network_graph)),
                'number_of_components': int(nx.number_connected_components(self.network_graph))
            }
            
            if nx.is_connected(self.network_graph):
                metrics['average_path_length'] = float(nx.average_shortest_path_length(self.network_graph))
                metrics['diameter'] = int(nx.diameter(self.network_graph))
            
            return metrics
        except Exception as e:
            logger.error(f"Error calculating network metrics: {e}")
            return {'error': str(e)}
    
    def _analyze_semantic_clustering(self) -> Dict[str, List[str]]:
        """Analyze clustering by semantic categories"""
        try:
            if self.cooccurrence_df.empty:
                return {}
                
            clusters = defaultdict(list)
            
            for _, row in self.cooccurrence_df.head(50).iterrows():
                cat1 = self._get_semantic_category(row['root1'])
                cat2 = self._get_semantic_category(row['root2'])
                
                if cat1 == cat2 and cat1 != 'uncategorized':
                    clusters[cat1].append(f"{row['root1']}-{row['root2']}")
            
            return dict(clusters)
        except Exception as e:
            logger.error(f"Error in semantic clustering analysis: {e}")
            return {}
    
    def _find_strong_associations(self, cooccurrence_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Find statistically strong associations"""
        try:
            associations = []
            
            for _, row in cooccurrence_df.head(20).iterrows():
                freq1 = self._get_frequency(row['root1'])
                freq2 = self._get_frequency(row['root2'])
                cooccur = row['cooccurrence_count']
                
                # Simple association strength calculation
                expected = (freq1 * freq2) / self.enhanced_df['Root'].notna().sum()
                strength = cooccur / expected if expected > 0 else 0
                
                if strength > 2:  # Significantly higher than expected
                    associations.append({
                        'root1': row['root1'],
                        'root2': row['root2'],
                        'cooccurrence': int(cooccur),
                        'association_strength': float(strength)
                    })
            
            return sorted(associations, key=lambda x: x['association_strength'], reverse=True)
        except Exception as e:
            logger.error(f"Error finding strong associations: {e}")
            return []
    
    def _create_cooccurrence_matrix(self, roots: List[str]) -> np.ndarray:
        """Create cooccurrence matrix for clustering"""
        try:
            n_roots = len(roots)
            matrix = np.zeros((n_roots, n_roots))
            
            root_to_idx = {root: i for i, root in enumerate(roots)}
            
            for _, row in self.cooccurrence_df.iterrows():
                if row['root1'] in root_to_idx and row['root2'] in root_to_idx:
                    i = root_to_idx[row['root1']]
                    j = root_to_idx[row['root2']]
                    matrix[i][j] = row['cooccurrence_count']
                    matrix[j][i] = row['cooccurrence_count']  # Symmetric
            
            return matrix
        except Exception as e:
            logger.error(f"Error creating cooccurrence matrix: {e}")
            return np.zeros((len(roots), len(roots)))
    
    def _calculate_silhouette_score(self, matrix: np.ndarray, labels: np.ndarray) -> float:
        """Calculate silhouette score for clustering quality"""
        try:
            from sklearn.metrics import silhouette_score
            if len(set(labels)) > 1:
                return float(silhouette_score(matrix, labels))
            return 0.0
        except Exception as e:
            logger.error(f"Error calculating silhouette score: {e}")
            return 0.0
    
    def _analyze_category_relationships(self) -> Dict[str, Any]:
        """Analyze relationships between semantic categories"""
        try:
            # This would analyze co-occurrence patterns between categories
            # Implementation depends on having category co-occurrence data
            return {'note': 'Category relationship analysis requires category co-occurrence matrix'}
        except Exception as e:
            logger.error(f"Error in category relationships: {e}")
            return {}
    
    def _analyze_temporal_evolution(self) -> Dict[str, Any]:
        """Analyze temporal evolution of themes"""
        try:
            # This would require chronological ordering data
            return {'note': 'Temporal evolution analysis requires chronological data'}
        except Exception as e:
            logger.error(f"Error in temporal evolution: {e}")
            return {}
    
    def _analyze_new_vocabulary(self, period: str) -> Dict[str, Any]:
        """Analyze new vocabulary introduced in a period"""
        try:
            if period == 'medinan':
                medinan_only = self.frequency_df[
                    (self.frequency_df['medinan_frequency'] > 0) & 
                    (self.frequency_df['meccan_frequency'] == 0)
                ]
                
                return {
                    'count': len(medinan_only),
                    'examples': medinan_only.head(10)[['root', 'root_arabic', 'semantic_category']].to_dict('records')
                }
            
            return {'note': f'Analysis for period {period} not implemented'}
        except Exception as e:
            logger.error(f"Error analyzing new vocabulary: {e}")
            return {}
    
    def _analyze_frequency_shifts(self) -> Dict[str, Any]:
        """Analyze frequency shifts between periods"""
        try:
            # Calculate roots with significant frequency changes
            df = self.frequency_df.copy()
            df['frequency_shift'] = df['medinan_frequency'] - df['meccan_frequency']
            df['relative_shift'] = df['frequency_shift'] / df['total_frequency']
            
            increasing = df.nlargest(10, 'relative_shift')[['root', 'root_arabic', 'relative_shift']].to_dict('records')
            decreasing = df.nsmallest(10, 'relative_shift')[['root', 'root_arabic', 'relative_shift']].to_dict('records')
            
            return {
                'increasing_usage': increasing,
                'decreasing_usage': decreasing
            }
        except Exception as e:
            logger.error(f"Error analyzing frequency shifts: {e}")
            return {} 