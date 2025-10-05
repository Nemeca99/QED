"""
Working Chess APIs Test
Test working chess APIs with proper error handling
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timedelta

async def test_lichess_working():
    """Test Lichess API with working parameters"""
    print("Testing Lichess API with working parameters...")
    
    # Try different usernames and parameters
    usernames = ["MagnusCarlsen", "Hikaru", "DingLiren", "FabianoCaruana"]
    
    for username in usernames:
        print(f"\nTrying {username}...")
        
        url = "https://lichess.org/api/games/user/" + username
        params = {
            'max': 5,
            'perfType': 'blitz,rapid,classical',
            'clocks': 'true'
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    print(f"  Status: {response.status}")
                    print(f"  Content-Type: {response.headers.get('Content-Type', 'N/A')}")
                    
                    if response.status == 200:
                        text = await response.text()
                        print(f"  Response length: {len(text)}")
                        
                        if len(text) > 0:
                            print(f"  ✅ Found games for {username}")
                            print(f"  First 200 chars: {text[:200]}")
                            return True, username, text
                        else:
                            print(f"  ⚠️  No games found for {username}")
                    else:
                        print(f"  ❌ Error {response.status} for {username}")
                        
        except Exception as e:
            print(f"  ❌ Exception for {username}: {e}")
    
    return False, None, None

async def test_chesscom_working():
    """Test Chess.com API with working parameters"""
    print("\nTesting Chess.com API...")
    
    username = "MagnusCarlsen"
    url = f"https://api.chess.com/pub/player/{username}/games/archives"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                print(f"Status: {response.status}")
                print(f"Content-Type: {response.headers.get('Content-Type', 'N/A')}")
                
                if response.status == 200:
                    data = await response.json()
                    archives = data.get('archives', [])
                    print(f"✅ Found {len(archives)} archives for {username}")
                    
                    if archives:
                        # Try to get games from the most recent archive
                        recent_archive = archives[-1]
                        print(f"Trying recent archive: {recent_archive}")
                        
                        async with session.get(recent_archive) as archive_response:
                            if archive_response.status == 200:
                                archive_data = await archive_response.json()
                                games = archive_data.get('games', [])
                                print(f"✅ Found {len(games)} games in recent archive")
                                
                                if games:
                                    # Show first game details
                                    first_game = games[0]
                                    print(f"First game:")
                                    print(f"  White: {first_game.get('white', {}).get('username', 'N/A')}")
                                    print(f"  Black: {first_game.get('black', {}).get('username', 'N/A')}")
                                    print(f"  Result: {first_game.get('result', 'N/A')}")
                                    print(f"  Time Control: {first_game.get('time_control', 'N/A')}")
                                    
                                    return True, games
                    
                    return False, []
                else:
                    print(f"❌ Error: {response.status}")
                    return False, []
                    
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False, []

async def test_lichess_puzzles():
    """Test Lichess puzzles API"""
    print("\nTesting Lichess puzzles API...")
    
    url = "https://lichess.org/api/puzzle/daily"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                print(f"Status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Daily puzzle found")
                    print(f"  Puzzle ID: {data.get('puzzle', {}).get('id', 'N/A')}")
                    print(f"  Rating: {data.get('puzzle', {}).get('rating', 'N/A')}")
                    print(f"  Themes: {data.get('puzzle', {}).get('themes', [])}")
                    return True, data
                else:
                    print(f"❌ Error: {response.status}")
                    return False, None
                    
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False, None

async def test_lichess_tournaments():
    """Test Lichess tournaments API"""
    print("\nTesting Lichess tournaments API...")
    
    url = "https://lichess.org/api/tournament"
    params = {'nb': 5}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                print(f"Status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    tournaments = data.get('featured', [])
                    print(f"✅ Found {len(tournaments)} featured tournaments")
                    
                    if tournaments:
                        first_tournament = tournaments[0]
                        print(f"First tournament:")
                        print(f"  Name: {first_tournament.get('fullName', 'N/A')}")
                        print(f"  Status: {first_tournament.get('status', 'N/A')}")
                        print(f"  Players: {first_tournament.get('nbPlayers', 'N/A')}")
                        
                    return True, tournaments
                else:
                    print(f"❌ Error: {response.status}")
                    return False, []
                    
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False, []

async def main():
    """Main test function"""
    print("🧪 Testing Working Chess APIs")
    print("=" * 50)
    
    # Test Lichess games
    lichess_games_result, lichess_username, lichess_data = await test_lichess_working()
    
    # Test Chess.com games
    chesscom_result, chesscom_games = await test_chesscom_working()
    
    # Test Lichess puzzles
    puzzles_result, puzzle_data = await test_lichess_puzzles()
    
    # Test Lichess tournaments
    tournaments_result, tournament_data = await test_lichess_tournaments()
    
    print("\n" + "=" * 50)
    print("📊 API Test Results:")
    print("=" * 50)
    print(f"  Lichess Games: {'✅ WORKING' if lichess_games_result else '❌ FAILED'}")
    print(f"  Chess.com Games: {'✅ WORKING' if chesscom_result else '❌ FAILED'}")
    print(f"  Lichess Puzzles: {'✅ WORKING' if puzzles_result else '❌ FAILED'}")
    print(f"  Lichess Tournaments: {'✅ WORKING' if tournaments_result else '❌ FAILED'}")
    
    working_apis = sum([lichess_games_result, chesscom_result, puzzles_result, tournaments_result])
    total_apis = 4
    
    print(f"\nOverall: {working_apis}/{total_apis} APIs working")
    
    if working_apis > 0:
        print("🎉 At least some chess APIs are working!")
        print("\n💡 Recommendations:")
        
        if chesscom_result:
            print("  - Use Chess.com API for game data collection")
        if puzzles_result:
            print("  - Use Lichess puzzles API for QEC puzzle generation")
        if tournaments_result:
            print("  - Use Lichess tournaments API for live tournament data")
        if lichess_games_result:
            print("  - Use Lichess games API for player game data")
    else:
        print("⚠️  No chess APIs are working. Check network connection and API status.")

if __name__ == "__main__":
    asyncio.run(main())
