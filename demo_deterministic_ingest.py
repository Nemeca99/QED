"""
Demo Deterministic Chess Data Ingest
Demonstrate the deterministic chess data ingest pipeline using Chess.com data
"""

import sys
import os
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from data_ingest.schemas import RawGame, DataIngestConfig, Result
from data_ingest.qec_features import QECFeatureExtractor
from data_ingest.storage import ChessDataStorage

def load_chesscom_data():
    """Load Chess.com data from our previous collection"""
    data_file = Path("data/realtime_chess/realtime_chess_data.json")
    
    if not data_file.exists():
        print("❌ No Chess.com data found. Run realtime_chess_data.py first.")
        return []
    
    with open(data_file, 'r') as f:
        data = json.load(f)
    
    games = []
    for user_data in data.get('chesscom_games', []):
        for game in user_data.get('games', []):
            games.append(game)
    
    print(f"✅ Loaded {len(games)} Chess.com games")
    return games

def convert_chesscom_to_raw_games(chesscom_games):
    """Convert Chess.com games to RawGame format"""
    raw_games = []
    
    for game in chesscom_games:
        # Extract PGN
        pgn = game.get('pgn', '')
        if not pgn:
            continue
        
        # Create headers from game data
        headers = {
            'Event': 'Live Chess',
            'Site': 'Chess.com',
            'Date': '2025.01.05',  # Would extract from actual data
            'Round': '-',
            'White': game.get('white', {}).get('username', ''),
            'Black': game.get('black', {}).get('username', ''),
            'Result': game.get('result', ''),
            'WhiteElo': str(game.get('white', {}).get('rating', 0)),
            'BlackElo': str(game.get('black', {}).get('rating', 0)),
            'TimeControl': game.get('time_control', ''),
            'ECO': 'A00'  # Would extract from PGN
        }
        
        # Compute game UID from PGN
        import hashlib
        game_uid = hashlib.sha256(pgn.encode('utf-8')).hexdigest()
        
        raw_game = RawGame(
            game_uid=game_uid,
            source='chesscom',
            pgn=pgn,
            headers=headers,
            etag=None,
            content_hash=hashlib.sha256(pgn.encode('utf-8')).hexdigest(),
            fetch_timestamp=str(int(1640995200))  # Would use actual timestamp
        )
        
        raw_games.append(raw_game)
    
    return raw_games

def demo_qec_feature_extraction():
    """Demo QEC feature extraction"""
    print("🧪 Demo: QEC Feature Extraction")
    print("=" * 50)
    
    # Load Chess.com data
    chesscom_games = load_chesscom_data()
    if not chesscom_games:
        return
    
    # Convert to RawGame format
    raw_games = convert_chesscom_to_raw_games(chesscom_games)
    print(f"✅ Converted {len(raw_games)} games to RawGame format")
    
    # Extract QEC features
    extractor = QECFeatureExtractor()
    features_list = []
    
    print("\n🔍 Extracting QEC features...")
    for i, raw_game in enumerate(raw_games[:3]):  # Process first 3 games
        print(f"\nProcessing game {i+1}/{min(3, len(raw_games))}:")
        print(f"  Game UID: {raw_game.game_uid[:16]}...")
        print(f"  White: {raw_game.headers.get('White', 'N/A')}")
        print(f"  Black: {raw_game.headers.get('Black', 'N/A')}")
        print(f"  PGN length: {len(raw_game.pgn)} characters")
        
        # Extract features
        features = extractor.extract_features(raw_game)
        features_list.append(features)
        
        print(f"  ✅ Features extracted:")
        print(f"    Plies: {features.plies}")
        print(f"    Checks: {features.checks}")
        print(f"    Captures: {features.captures}")
        print(f"    King escape ops: {features.king_escape_ops}")
        print(f"    Tactical density: {features.tactical_density:.3f}")
        print(f"    Result: {features.result}")
    
    return features_list

def demo_storage_pipeline():
    """Demo storage pipeline"""
    print("\n💾 Demo: Storage Pipeline")
    print("=" * 50)
    
    # Load and convert data
    chesscom_games = load_chesscom_data()
    if not chesscom_games:
        return
    
    raw_games = convert_chesscom_to_raw_games(chesscom_games)
    
    # Extract features
    extractor = QECFeatureExtractor()
    features_list = []
    
    for raw_game in raw_games:
        features = extractor.extract_features(raw_game)
        features_list.append(features)
    
    print(f"✅ Extracted features for {len(features_list)} games")
    
    # Store data
    config = DataIngestConfig()
    storage = ChessDataStorage(config)
    
    output_dir = Path("data/demo_ingest")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Store raw games
    print("\n📁 Storing raw games...")
    raw_path = storage.store_raw_games(raw_games, output_dir)
    print(f"✅ Raw games stored to {raw_path}")
    
    # Store QEC features
    print("\n📁 Storing QEC features...")
    features_path = storage.store_qec_features(features_list, output_dir)
    print(f"✅ QEC features stored to {features_path}")
    
    # Create manifest
    print("\n📋 Creating manifest...")
    manifest = storage.create_manifest(
        batch_id="demo_batch_001",
        source="chesscom",
        files=[str(raw_path), str(features_path)],
        row_counts=len(raw_games),
        start_date="2025-01-05",
        end_date="2025-01-05",
        cmdline="demo_deterministic_ingest.py",
        git_sha="demo_sha",
        license="CC0"
    )
    
    manifest_path = storage.save_manifest(manifest, output_dir)
    print(f"✅ Manifest saved to {manifest_path}")
    
    return output_dir

def demo_data_analysis():
    """Demo data analysis capabilities"""
    print("\n📊 Demo: Data Analysis")
    print("=" * 50)
    
    # Load stored features
    features_path = Path("data/demo_ingest/features_v1.parquet")
    
    if not features_path.exists():
        print("❌ No features file found. Run storage demo first.")
        return
    
    try:
        import pyarrow.parquet as pq
        table = pq.read_table(str(features_path))
        
        print(f"✅ Loaded {len(table)} QEC features")
        
        # Basic statistics
        plies = table['plies'].to_pylist()
        checks = table['checks'].to_pylist()
        captures = table['captures'].to_pylist()
        tactical_density = table['tactical_density'].to_pylist()
        
        print(f"\n📈 Statistics:")
        print(f"  Average plies: {sum(plies) / len(plies):.1f}")
        print(f"  Average checks: {sum(checks) / len(checks):.1f}")
        print(f"  Average captures: {sum(captures) / len(captures):.1f}")
        print(f"  Average tactical density: {sum(tactical_density) / len(tactical_density):.3f}")
        
        # QEC-specific analysis
        high_tactical = [d for d in tactical_density if d > 0.3]
        print(f"  High tactical games (>0.3): {len(high_tactical)}/{len(tactical_density)} ({len(high_tactical)/len(tactical_density)*100:.1f}%)")
        
        # Results analysis
        results = table['result'].to_pylist()
        white_wins = results.count('1-0')
        black_wins = results.count('0-1')
        draws = results.count('1/2-1/2')
        
        print(f"\n🏆 Results:")
        print(f"  White wins: {white_wins} ({white_wins/len(results)*100:.1f}%)")
        print(f"  Black wins: {black_wins} ({black_wins/len(results)*100:.1f}%)")
        print(f"  Draws: {draws} ({draws/len(results)*100:.1f}%)")
        
    except Exception as e:
        print(f"❌ Error analyzing data: {e}")

def main():
    """Main demo function"""
    print("🚀 QEC Deterministic Data Ingest Demo")
    print("=" * 60)
    
    try:
        # Demo QEC feature extraction
        features = demo_qec_feature_extraction()
        
        if features:
            # Demo storage pipeline
            output_dir = demo_storage_pipeline()
            
            if output_dir:
                # Demo data analysis
                demo_data_analysis()
                
                print(f"\n🎉 Demo completed successfully!")
                print(f"📁 Output directory: {output_dir}")
                print(f"🔍 Check the generated Parquet files and manifest")
            else:
                print("❌ Storage demo failed")
        else:
            print("❌ Feature extraction demo failed")
    
    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
