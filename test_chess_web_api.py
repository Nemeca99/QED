"""
Test Chess Web API Integration
Test the chess web API integration for real-time data
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from data.chess_web_api_integration import ChessWebAPIIntegrator

async def test_lichess_api():
    """Test Lichess API integration"""
    print("Testing Lichess API integration...")
    
    integrator = ChessWebAPIIntegrator()
    
    try:
        # Test with a well-known player
        username = "MagnusCarlsen"
        print(f"Fetching recent games for {username}...")
        
        games = await integrator.get_lichess_games(username, max_games=5)
        
        if games:
            print(f"✅ Successfully fetched {len(games)} games from Lichess")
            
            # Show first game details
            first_game = games[0]
            print(f"\nFirst game details:")
            print(f"  Game ID: {first_game.get('id', 'N/A')}")
            print(f"  White: {first_game.get('white', {}).get('username', 'N/A')}")
            print(f"  Black: {first_game.get('black', {}).get('username', 'N/A')}")
            print(f"  Winner: {first_game.get('winner', 'N/A')}")
            print(f"  Status: {first_game.get('status', 'N/A')}")
            print(f"  Rated: {first_game.get('rated', False)}")
            print(f"  Time Control: {first_game.get('timeControl', 'N/A')}")
            print(f"  Turns: {first_game.get('turns', 0)}")
            
            # Show QEC analysis
            qec_analysis = first_game.get('qec_analysis', {})
            print(f"\nQEC Analysis:")
            print(f"  Entanglement Opportunities: {len(qec_analysis.get('entanglement_opportunities', []))}")
            print(f"  Forced Move Patterns: {len(qec_analysis.get('forced_move_patterns', []))}")
            print(f"  Reactive Escape Patterns: {len(qec_analysis.get('reactive_escape_patterns', []))}")
            print(f"  Tactical Combinations: {len(qec_analysis.get('tactical_combinations', []))}")
            print(f"  Positional Themes: {len(qec_analysis.get('positional_themes', []))}")
            
            return True
        else:
            print("❌ No games fetched from Lichess")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Lichess API: {e}")
        return False

async def test_chesscom_api():
    """Test Chess.com API integration"""
    print("\nTesting Chess.com API integration...")
    
    integrator = ChessWebAPIIntegrator()
    
    try:
        # Test with a well-known player
        username = "MagnusCarlsen"
        print(f"Fetching recent games for {username}...")
        
        games = await integrator.get_chesscom_games(username, max_games=5)
        
        if games:
            print(f"✅ Successfully fetched {len(games)} games from Chess.com")
            
            # Show first game details
            first_game = games[0]
            print(f"\nFirst game details:")
            print(f"  URL: {first_game.get('url', 'N/A')}")
            print(f"  White: {first_game.get('white', {}).get('username', 'N/A')}")
            print(f"  Black: {first_game.get('black', {}).get('username', 'N/A')}")
            print(f"  Winner: {first_game.get('winner', 'N/A')}")
            print(f"  Time Control: {first_game.get('timeControl', 'N/A')}")
            print(f"  Time Class: {first_game.get('timeClass', 'N/A')}")
            print(f"  Rated: {first_game.get('rated', False)}")
            
            return True
        else:
            print("❌ No games fetched from Chess.com")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Chess.com API: {e}")
        return False

async def test_position_analysis():
    """Test position analysis API"""
    print("\nTesting position analysis...")
    
    integrator = ChessWebAPIIntegrator()
    
    try:
        # Test with a common opening position
        fen = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"  # After 1.e4
        print(f"Analyzing position: {fen}")
        
        analysis = await integrator.get_position_analysis(fen)
        
        if analysis:
            print(f"✅ Successfully analyzed position")
            print(f"  FEN: {analysis.get('fen', 'N/A')}")
            print(f"  Moves: {len(analysis.get('moves', []))}")
            print(f"  Score: {analysis.get('score', 'N/A')}")
            print(f"  Depth: {analysis.get('depth', 'N/A')}")
            print(f"  Nodes: {analysis.get('nodes', 'N/A')}")
            
            return True
        else:
            print("❌ No analysis returned")
            return False
            
    except Exception as e:
        print(f"❌ Error testing position analysis: {e}")
        return False

async def test_data_collection():
    """Test data collection from multiple sources"""
    print("\nTesting data collection from multiple sources...")
    
    integrator = ChessWebAPIIntegrator()
    
    try:
        # Test with multiple players
        usernames = ["MagnusCarlsen", "FabianoCaruana"]
        print(f"Collecting data for {usernames}...")
        
        data = await integrator.collect_user_data(usernames, max_games_per_user=3)
        
        if data:
            print(f"✅ Successfully collected data")
            print(f"  Total Lichess games: {len(data.get('lichess_games', []))}")
            print(f"  Total Chess.com games: {len(data.get('chesscom_games', []))}")
            print(f"  Total position analyses: {len(data.get('position_analyses', []))}")
            
            # Create training dataset
            training_dataset = integrator.create_qec_training_dataset(data)
            print(f"\nTraining Dataset:")
            print(f"  Entanglement Examples: {len(training_dataset.get('entanglement_examples', []))}")
            print(f"  Forced Move Examples: {len(training_dataset.get('forced_move_examples', []))}")
            print(f"  Reactive Escape Examples: {len(training_dataset.get('reactive_escape_examples', []))}")
            print(f"  Tactical Examples: {len(training_dataset.get('tactical_examples', []))}")
            print(f"  Positional Examples: {len(training_dataset.get('positional_examples', []))}")
            
            # Save data
            output_path = integrator.save_data(data, "test_chess_web_api_data.json")
            print(f"  Data saved to: {output_path}")
            
            return True
        else:
            print("❌ No data collected")
            return False
            
    except Exception as e:
        print(f"❌ Error testing data collection: {e}")
        return False

async def main():
    """Main test function"""
    print("🧪 Testing Chess Web API Integration")
    print("=" * 50)
    
    tests = [
        ("Lichess API", test_lichess_api),
        ("Chess.com API", test_chesscom_api),
        ("Position Analysis", test_position_analysis),
        ("Data Collection", test_data_collection)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name} test...")
        try:
            result = await test_func()
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
        print("🎉 All tests passed! Chess Web API integration is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the error messages above.")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
