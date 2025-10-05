"""
Simple Lichess API Test
Test Lichess API with minimal parameters
"""

import asyncio
import aiohttp

async def test_lichess_simple():
    """Test Lichess API with simple request"""
    print("Testing Lichess API with simple request...")
    
    url = "https://lichess.org/api/games/user/MagnusCarlsen"
    params = {
        'max': 3,
        'perfType': 'blitz'
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                print(f"Status: {response.status}")
                print(f"Content-Type: {response.headers.get('Content-Type', 'N/A')}")
                
                if response.status == 200:
                    # Try to get text first
                    text = await response.text()
                    print(f"Response length: {len(text)}")
                    print(f"First 200 chars: {text[:200]}")
                    
                    # Check if it's PGN format
                    if '[Event' in text:
                        print("✅ Lichess API is working - returns PGN format")
                        return True
                    else:
                        print("❌ Unexpected response format")
                        return False
                else:
                    print(f"❌ Error: {response.status}")
                    return False
                    
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

async def test_lichess_json():
    """Test Lichess API with JSON request"""
    print("\nTesting Lichess API with JSON request...")
    
    url = "https://lichess.org/api/games/user/MagnusCarlsen"
    params = {
        'max': 3,
        'perfType': 'blitz',
        'pgnInJson': 'true'
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                print(f"Status: {response.status}")
                print(f"Content-Type: {response.headers.get('Content-Type', 'N/A')}")
                
                if response.status == 200:
                    try:
                        data = await response.json()
                        print(f"✅ Lichess JSON API is working")
                        print(f"Games count: {len(data.get('games', []))}")
                        return True
                    except Exception as e:
                        print(f"❌ JSON parsing error: {e}")
                        return False
                else:
                    print(f"❌ Error: {response.status}")
                    return False
                    
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

async def main():
    """Main test function"""
    print("🧪 Testing Lichess API")
    print("=" * 40)
    
    # Test simple PGN request
    pgn_result = await test_lichess_simple()
    
    # Test JSON request
    json_result = await test_lichess_json()
    
    print("\n" + "=" * 40)
    print("📊 Results:")
    print(f"  PGN Format: {'✅ PASSED' if pgn_result else '❌ FAILED'}")
    print(f"  JSON Format: {'✅ PASSED' if json_result else '❌ FAILED'}")
    
    if pgn_result or json_result:
        print("🎉 Lichess API is working!")
    else:
        print("⚠️  Lichess API has issues")

if __name__ == "__main__":
    asyncio.run(main())
