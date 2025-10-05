"""
QEC Data Ingest CLI
Command-line interface for chess data processing
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import List, Optional
import json

from .schemas import DataIngestConfig
from .adapters import get_adapter
from .qec_features import QECFeatureExtractor
from .storage import ChessDataStorage

logger = logging.getLogger(__name__)

def setup_logging(level: str = "INFO"):
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def fetch_command(args):
    """Fetch chess data from source"""
    config = DataIngestConfig()
    config.allow_live = args.allow_live
    
    # Get adapter
    adapter = get_adapter(args.source, config)
    
    # Fetch games
    games = list(adapter.fetch(args.source, args.user, args.max_games))
    
    if not games:
        logger.warning(f"No games fetched from {args.source}")
        return 1
    
    # Store raw games
    storage = ChessDataStorage(config)
    output_dir = Path(args.out)
    raw_path = storage.store_raw_games(games, output_dir)
    
    logger.info(f"Fetched {len(games)} games from {args.source}")
    logger.info(f"Raw games stored to {raw_path}")
    
    return 0

def ingest_command(args):
    """Ingest raw data and extract features"""
    config = DataIngestConfig()
    
    # Load raw games (placeholder - would load from Parquet)
    logger.info("Ingesting raw data...")
    
    # Extract QEC features
    extractor = QECFeatureExtractor()
    storage = ChessDataStorage(config)
    
    # TODO: Load raw games from Parquet and extract features
    logger.info("Feature extraction not yet implemented")
    
    return 0

def features_command(args):
    """Extract QEC features from ingested data"""
    config = DataIngestConfig()
    
    # TODO: Implement feature extraction
    logger.info("QEC feature extraction not yet implemented")
    
    return 0

def validate_command(args):
    """Validate data integrity"""
    manifest_path = Path(args.manifest)
    
    if not manifest_path.exists():
        logger.error(f"Manifest file not found: {manifest_path}")
        return 1
    
    try:
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        logger.info(f"Manifest validation:")
        logger.info(f"  Batch ID: {manifest.get('batch_id', 'N/A')}")
        logger.info(f"  Source: {manifest.get('source', 'N/A')}")
        logger.info(f"  Row counts: {manifest.get('row_counts', 'N/A')}")
        logger.info(f"  Schema version: {manifest.get('schema_version', 'N/A')}")
        logger.info(f"  Created at: {manifest.get('created_at', 'N/A')}")
        
        logger.info("✅ Manifest validation passed")
        return 0
        
    except Exception as e:
        logger.error(f"Manifest validation failed: {e}")
        return 1

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description='QEC Data Ingest Pipeline')
    parser.add_argument('--log-level', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'])
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Fetch command
    fetch_parser = subparsers.add_parser('fetch', help='Fetch chess data from source')
    fetch_parser.add_argument('source', choices=['lichess', 'chesscom', 'lumbra'], help='Data source')
    fetch_parser.add_argument('user', help='Username to fetch data for')
    fetch_parser.add_argument('--max-games', type=int, default=100, help='Maximum games to fetch')
    fetch_parser.add_argument('--out', default='data/raw', help='Output directory')
    fetch_parser.add_argument('--allow-live', action='store_true', help='Allow live data fetching')
    
    # Ingest command
    ingest_parser = subparsers.add_parser('ingest', help='Ingest raw data')
    ingest_parser.add_argument('--raw', required=True, help='Raw data directory')
    ingest_parser.add_argument('--out', required=True, help='Output directory')
    ingest_parser.add_argument('--workers', type=int, default=8, help='Number of workers')
    
    # Features command
    features_parser = subparsers.add_parser('features', help='Extract QEC features')
    features_parser.add_argument('--in', required=True, help='Input directory')
    features_parser.add_argument('--out', required=True, help='Output directory')
    features_parser.add_argument('--schema', default='v1', help='Schema version')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate data integrity')
    validate_parser.add_argument('manifest', help='Manifest file to validate')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Setup logging
    setup_logging(args.log_level)
    
    # Execute command
    if args.command == 'fetch':
        return fetch_command(args)
    elif args.command == 'ingest':
        return ingest_command(args)
    elif args.command == 'features':
        return features_command(args)
    elif args.command == 'validate':
        return validate_command(args)
    else:
        logger.error(f"Unknown command: {args.command}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
