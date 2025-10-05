"""
QEC Data Ingest Schemas
Define schemas for chess data processing and QEC feature extraction
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import pyarrow as pa
import pyarrow.parquet as pq

class Result(Enum):
    """Chess game result enum"""
    WHITE_WINS = "1-0"
    BLACK_WINS = "0-1" 
    DRAW = "1/2-1/2"
    UNKNOWN = "*"

@dataclass
class RawGame:
    """Raw chess game data from source"""
    game_uid: str
    source: str
    pgn: str
    headers: Dict[str, str]
    etag: Optional[str] = None
    content_hash: Optional[str] = None
    fetch_timestamp: Optional[str] = None

@dataclass
class QECFeatures:
    """QEC-specific features extracted from chess game"""
    game_uid: str
    plies: int
    checks: int
    captures: int
    promotions: int
    king_escape_ops: int
    forced_seq_spans: List[int]
    opening_phase_end_ply: int
    tactical_density: float
    reactive_escape_candidates: int
    white_rating: int
    black_rating: int
    time_control: str
    result: Result
    eco: str
    phase_splits: Dict[str, int]

class ChessDataSchema:
    """Schema definitions for chess data processing"""
    
    @staticmethod
    def raw_game_schema() -> pa.Schema:
        """Schema for raw game data"""
        return pa.schema([
            pa.field('game_uid', pa.string()),
            pa.field('source', pa.string()),
            pa.field('pgn', pa.string()),
            pa.field('headers', pa.map_(pa.string(), pa.string())),
            pa.field('etag', pa.string()),
            pa.field('content_hash', pa.string()),
            pa.field('fetch_timestamp', pa.string())
        ])
    
    @staticmethod
    def qec_features_schema() -> pa.Schema:
        """Schema for QEC features v1"""
        return pa.schema([
            pa.field('game_uid', pa.string()),
            pa.field('plies', pa.int16()),
            pa.field('checks', pa.int16()),
            pa.field('captures', pa.int16()),
            pa.field('promotions', pa.int8()),
            pa.field('king_escape_ops', pa.int16()),
            pa.field('forced_seq_spans', pa.list_(pa.int16())),
            pa.field('opening_phase_end_ply', pa.int16()),
            pa.field('tactical_density', pa.float32()),
            pa.field('reactive_escape_candidates', pa.int16()),
            pa.field('white_rating', pa.int16()),
            pa.field('black_rating', pa.int16()),
            pa.field('time_control', pa.string()),
            pa.field('result', pa.string()),
            pa.field('eco', pa.string()),
            pa.field('phase_splits', pa.map_(pa.string(), pa.int16()))
        ])
    
    @staticmethod
    def manifest_schema() -> pa.Schema:
        """Schema for processing manifest"""
        return pa.schema([
            pa.field('batch_id', pa.string()),
            pa.field('source', pa.string()),
            pa.field('files', pa.list_(pa.string())),
            pa.field('sha256_hashes', pa.list_(pa.string())),
            pa.field('row_counts', pa.int64()),
            pa.field('start_date', pa.string()),
            pa.field('end_date', pa.string()),
            pa.field('schema_version', pa.string()),
            pa.field('tool_versions', pa.map_(pa.string(), pa.string())),
            pa.field('cmdline', pa.string()),
            pa.field('git_sha', pa.string()),
            pa.field('license', pa.string()),
            pa.field('created_at', pa.string())
        ])

class DataIngestConfig:
    """Configuration for data ingest pipeline"""
    
    def __init__(self):
        # Rate limiting
        self.rate_limit_delay = 1.0  # seconds between requests
        self.max_concurrent_requests = 4
        
        # Caching
        self.cache_dir = "data/cache"
        self.allow_live = False  # Require cache unless --allow-live
        
        # Processing
        self.batch_size = 64 * 1024  # 64k rows
        self.row_group_size = 128 * 1024 * 1024  # 128MB
        self.compression_level = 7
        self.compression = "zstd"
        
        # Partitioning
        self.partition_by = ["year", "month", "source"]
        
        # Deduplication
        self.prefer_lichess = True
        self.keep_highest_rating = True
        
        # QEC features
        self.opening_phase_heuristic = "first_capture_or_zero_eval"
        self.tactical_density_threshold = 0.1
        
        # Reproducibility
        self.deterministic_sampling = True
        self.reservoir_k = 1000
        self.frozen_snapshots_only = True

# Global configuration instance
config = DataIngestConfig()
