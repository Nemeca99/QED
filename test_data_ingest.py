"""
Test Data Ingest Pipeline
Test the QEC data ingest pipeline components
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from data_ingest.schemas import DataIngestConfig, RawGame, Result
from data_ingest.adapters import LichessAdapter
from data_ingest.qec_features import QECFeatureExtractor
from data_ingest.storage import ChessDataStorage

def test_schemas():
    """Test schema definitions"""
    print("Testing schemas...")
    
    config = DataIngestConfig()
    assert config.rate_limit_delay == 1.0
    assert config.max_concurrent_requests == 4
    assert config.allow_live == False
    
    # Test schema creation
    from data_ingest.schemas import ChessDataSchema
    schema = ChessDataSchema()
    raw_schema = schema.raw_game_schema()
    features_schema = schema.qec_features_schema()
    
    assert raw_schema is not None
    assert features_schema is not None
    
    print("✅ Schemas test passed")

def test_lichess_adapter():
    """Test Lichess adapter"""
    print("Testing Lichess adapter...")
    
    config = DataIngestConfig()
    adapter = LichessAdapter(config)
    
    # Test with a known user (using cache if available)
    try:
        games = list(adapter.fetch("lichess", "MagnusCarlsen", 3))
        print(f"✅ Lichess adapter fetched {len(games)} games")
        
        if games:
            game = games[0]
            print(f"  Game UID: {game.game_uid[:16]}...")
            print(f"  Source: {game.source}")
            print(f"  Headers: {len(game.headers)} headers")
            print(f"  PGN length: {len(game.pgn)} characters")
        
        return True
        
    except Exception as e:
        print(f"⚠️  Lichess adapter test failed: {e}")
        return False

def test_qec_features():
    """Test QEC feature extraction"""
    print("Testing QEC feature extraction...")
    
    # Create a sample raw game
    sample_pgn = """[Event "Live Chess"]
[Site "Chess.com"]
[Date "2025.01.05"]
[Round "-"]
[White "MagnusCarlsen"]
[Black "TestPlayer"]
[Result "1-0"]
[WhiteElo "2850"]
[BlackElo "2700"]
[TimeControl "600"]

1. e4 e5 2. Nf3 Nc6 3. Bb5 Nf6 4. O-O Be7 5. Re1 O-O 6. d4 exd4 7. Nxd4 Nxd4 8. Qxd4 d6 9. Bxc6 bxc6 10. Qd3 Be6 11. Bg5 h6 12. Bh4 g5 13. Bg3 Nh5 14. Bxe5 dxe5 15. Qd8+ Bf8 16. Qxf8# 1-0"""
    
    raw_game = RawGame(
        game_uid="test_game_001",
        source="lichess",
        pgn=sample_pgn,
        headers={
            'Event': 'Live Chess',
            'Site': 'Chess.com',
            'Date': '2025.01.05',
            'White': 'MagnusCarlsen',
            'Black': 'TestPlayer',
            'Result': '1-0',
            'WhiteElo': '2850',
            'BlackElo': '2700',
            'TimeControl': '600',
            'ECO': 'C65'
        },
        etag=None,
        content_hash="test_hash",
        fetch_timestamp="1640995200"
    )
    
    # Extract features
    extractor = QECFeatureExtractor()
    features = extractor.extract_features(raw_game)
    
    print(f"✅ QEC features extracted:")
    print(f"  Game UID: {features.game_uid}")
    print(f"  Plies: {features.plies}")
    print(f"  Checks: {features.checks}")
    print(f"  Captures: {features.captures}")
    print(f"  Promotions: {features.promotions}")
    print(f"  King escape ops: {features.king_escape_ops}")
    print(f"  Forced seq spans: {features.forced_seq_spans}")
    print(f"  Opening phase end: {features.opening_phase_end_ply}")
    print(f"  Tactical density: {features.tactical_density:.3f}")
    print(f"  Reactive escape candidates: {features.reactive_escape_candidates}")
    print(f"  White rating: {features.white_rating}")
    print(f"  Black rating: {features.black_rating}")
    print(f"  Result: {features.result}")
    print(f"  ECO: {features.eco}")
    print(f"  Phase splits: {features.phase_splits}")
    
    return True

def test_storage():
    """Test storage functionality"""
    print("Testing storage...")
    
    config = DataIngestConfig()
    storage = ChessDataStorage(config)
    
    # Test manifest creation
    manifest = storage.create_manifest(
        batch_id="test_batch_001",
        source="lichess",
        files=["test_file_1.parquet", "test_file_2.parquet"],
        row_counts=100,
        start_date="2025-01-01",
        end_date="2025-01-05",
        cmdline="test command",
        git_sha="abc123",
        license="CC0"
    )
    
    print(f"✅ Manifest created:")
    print(f"  Batch ID: {manifest['batch_id']}")
    print(f"  Source: {manifest['source']}")
    print(f"  Row counts: {manifest['row_counts']}")
    print(f"  Schema version: {manifest['schema_version']}")
    print(f"  Created at: {manifest['created_at']}")
    
    return True

def main():
    """Main test function"""
    print("🧪 Testing QEC Data Ingest Pipeline")
    print("=" * 50)
    
    tests = [
        ("Schemas", test_schemas),
        ("Lichess Adapter", test_lichess_adapter),
        ("QEC Features", test_qec_features),
        ("Storage", test_storage)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name} test...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! QEC data ingest pipeline is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the error messages above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
