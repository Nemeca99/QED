"""
Data Storage Pipeline
Parquet-based storage with partitioning and compression
"""

import pyarrow as pa
import pyarrow.parquet as pq
import pyarrow.compute as pc
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
import json
import hashlib
from datetime import datetime

from .schemas import RawGame, QECFeatures, ChessDataSchema, DataIngestConfig

logger = logging.getLogger(__name__)

class ChessDataStorage:
    """Parquet-based storage for chess data"""
    
    def __init__(self, config: DataIngestConfig):
        self.config = config
        self.schema = ChessDataSchema()
    
    def store_raw_games(self, games: List[RawGame], output_dir: Path) -> Path:
        """Store raw games as Parquet with partitioning"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Convert to PyArrow table
        table = self._raw_games_to_table(games)
        
        # Add partitioning columns
        table = self._add_partitioning_columns(table)
        
        # Partition by year/month/source
        partitioned_path = output_dir / "raw"
        
        # Write with partitioning
        pq.write_to_dataset(
            table,
            root_path=str(partitioned_path),
            partition_cols=self.config.partition_by,
            compression=self.config.compression,
            compression_level=self.config.compression_level,
            row_group_size=self.config.row_group_size
        )
        
        logger.info(f"Stored {len(games)} raw games to {partitioned_path}")
        return partitioned_path
    
    def _add_partitioning_columns(self, table: pa.Table) -> pa.Table:
        """Add partitioning columns to table"""
        # Add year, month, source columns for partitioning
        year_col = pa.array(['2025'] * len(table))
        month_col = pa.array(['01'] * len(table))
        source_col = pa.array([table['source'][i].as_py() for i in range(len(table))])
        
        # Create new table with partitioning columns
        new_data = {
            'game_uid': table['game_uid'],
            'source': table['source'],
            'pgn': table['pgn'],
            'headers': table['headers'],
            'etag': table['etag'],
            'content_hash': table['content_hash'],
            'fetch_timestamp': table['fetch_timestamp'],
            'year': year_col,
            'month': month_col
        }
        
        return pa.table(new_data)
    
    def store_qec_features(self, features: List[QECFeatures], output_dir: Path) -> Path:
        """Store QEC features as Parquet"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Convert to PyArrow table
        table = self._qec_features_to_table(features)
        
        # Write features
        features_path = output_dir / "features_v1.parquet"
        pq.write_table(
            table,
            str(features_path),
            compression=self.config.compression,
            compression_level=self.config.compression_level,
            row_group_size=self.config.row_group_size
        )
        
        logger.info(f"Stored {len(features)} QEC features to {features_path}")
        return features_path
    
    def create_manifest(self, batch_id: str, source: str, files: List[str], 
                       row_counts: int, start_date: str, end_date: str,
                       cmdline: str, git_sha: str, license: str) -> Dict[str, Any]:
        """Create processing manifest"""
        manifest = {
            'batch_id': batch_id,
            'source': source,
            'files': files,
            'sha256_hashes': [self._compute_file_hash(f) for f in files],
            'row_counts': row_counts,
            'start_date': start_date,
            'end_date': end_date,
            'schema_version': 'v1',
            'tool_versions': {
                'pyarrow': pa.__version__,
                'python': '3.8+'
            },
            'cmdline': cmdline,
            'git_sha': git_sha,
            'license': license,
            'created_at': datetime.now().isoformat()
        }
        
        return manifest
    
    def save_manifest(self, manifest: Dict[str, Any], output_dir: Path) -> Path:
        """Save manifest to file"""
        manifest_path = output_dir / "manifest.json"
        
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        logger.info(f"Saved manifest to {manifest_path}")
        return manifest_path
    
    def _raw_games_to_table(self, games: List[RawGame]) -> pa.Table:
        """Convert raw games to PyArrow table"""
        data = {
            'game_uid': [g.game_uid for g in games],
            'source': [g.source for g in games],
            'pgn': [g.pgn for g in games],
            'headers': [g.headers for g in games],
            'etag': [g.etag for g in games],
            'content_hash': [g.content_hash for g in games],
            'fetch_timestamp': [g.fetch_timestamp for g in games]
        }
        
        return pa.table(data, schema=self.schema.raw_game_schema())
    
    def _qec_features_to_table(self, features: List[QECFeatures]) -> pa.Table:
        """Convert QEC features to PyArrow table"""
        data = {
            'game_uid': [f.game_uid for f in features],
            'plies': [f.plies for f in features],
            'checks': [f.checks for f in features],
            'captures': [f.captures for f in features],
            'promotions': [f.promotions for f in features],
            'king_escape_ops': [f.king_escape_ops for f in features],
            'forced_seq_spans': [f.forced_seq_spans for f in features],
            'opening_phase_end_ply': [f.opening_phase_end_ply for f in features],
            'tactical_density': [f.tactical_density for f in features],
            'reactive_escape_candidates': [f.reactive_escape_candidates for f in features],
            'white_rating': [f.white_rating for f in features],
            'black_rating': [f.black_rating for f in features],
            'time_control': [f.time_control for f in features],
            'result': [f.result.value for f in features],
            'eco': [f.eco for f in features],
            'phase_splits': [f.phase_splits for f in features]
        }
        
        return pa.table(data, schema=self.schema.qec_features_schema())
    
    def _compute_file_hash(self, file_path: str) -> str:
        """Compute SHA256 hash of file"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                return hashlib.sha256(content).hexdigest()
        except Exception as e:
            logger.warning(f"Failed to compute hash for {file_path}: {e}")
            return ""
    
    def load_features(self, features_path: Path) -> pa.Table:
        """Load QEC features from Parquet"""
        return pq.read_table(str(features_path))
    
    def query_features(self, features_path: Path, filters: Dict[str, Any] = None) -> pa.Table:
        """Query QEC features with filters"""
        table = self.load_features(features_path)
        
        if filters:
            # Apply filters
            for column, value in filters.items():
                if column in table.column_names:
                    mask = pc.equal(table[column], value)
                    table = table.filter(mask)
        
        return table
