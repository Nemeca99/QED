"""
Chess Data Adapters
Interface for fetching chess data from various sources
"""

import hashlib
import json
import time
import asyncio
import aiohttp
from pathlib import Path
from typing import Iterator, Optional, Dict, Any, List
from dataclasses import dataclass
import logging

from .schemas import RawGame, DataIngestConfig

logger = logging.getLogger(__name__)

class ChessDataAdapter:
    """Base class for chess data adapters"""
    
    def __init__(self, config: DataIngestConfig):
        self.config = config
        self.cache_dir = Path(config.cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def fetch(self, source: str, user: str, max_games: int) -> Iterator[RawGame]:
        """Fetch chess games from source"""
        raise NotImplementedError
    
    def _get_cache_path(self, source: str, user: str) -> Path:
        """Get cache file path for source/user combination"""
        return self.cache_dir / f"{source}_{user}.json"
    
    def _load_cache(self, cache_path: Path) -> Optional[Dict[str, Any]]:
        """Load cached data if available"""
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load cache {cache_path}: {e}")
            return None
    
    def _save_cache(self, cache_path: Path, data: Dict[str, Any]) -> None:
        """Save data to cache"""
        try:
            with open(cache_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save cache {cache_path}: {e}")
    
    def _compute_content_hash(self, content: str) -> str:
        """Compute SHA256 hash of content"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

class LichessAdapter(ChessDataAdapter):
    """Lichess chess data adapter with caching and rate limiting"""
    
    def __init__(self, config: DataIngestConfig):
        super().__init__(config)
        self.base_url = "https://lichess.org/api"
        self.rate_limit_delay = config.rate_limit_delay
        self.allow_live = config.allow_live
    
    def fetch(self, source: str, user: str, max_games: int) -> Iterator[RawGame]:
        """Fetch games from Lichess with caching"""
        cache_path = self._get_cache_path(source, user)
        
        # Check cache first
        if not self.allow_live and cache_path.exists():
            logger.info(f"Using cached data for {user} from {source}")
            cached_data = self._load_cache(cache_path)
            if cached_data:
                for game_data in cached_data.get('games', []):
                    yield self._parse_lichess_game(game_data, source)
                return
        
        # Fetch live data
        logger.info(f"Fetching live data for {user} from {source}")
        games = self._fetch_lichess_games(user, max_games)
        
        # Cache the results
        cache_data = {
            'source': source,
            'user': user,
            'fetch_timestamp': time.time(),
            'games': games
        }
        self._save_cache(cache_path, cache_data)
        
        # Yield games
        for game_data in games:
            yield self._parse_lichess_game(game_data, source)
    
    def _fetch_lichess_games(self, user: str, max_games: int) -> List[Dict[str, Any]]:
        """Fetch games from Lichess API"""
        games = []
        url = f"{self.base_url}/games/user/{user}"
        
        params = {
            'max': max_games,
            'perfType': 'blitz,rapid,classical',
            'clocks': 'true',
            'evals': 'true'
        }
        
        try:
            # Use synchronous requests for now (can be made async later)
            import requests
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            # Lichess returns PGN format
            pgn_text = response.text
            games = self._parse_lichess_pgn(pgn_text, user)
            
            # Rate limiting
            time.sleep(self.rate_limit_delay)
            
        except Exception as e:
            logger.error(f"Failed to fetch Lichess games for {user}: {e}")
        
        return games
    
    def _parse_lichess_pgn(self, pgn_text: str, user: str) -> List[Dict[str, Any]]:
        """Parse Lichess PGN text into game data"""
        games = []
        
        # Split PGN into individual games
        pgn_games = pgn_text.split('\n\n\n')
        
        for pgn_game in pgn_games:
            if not pgn_game.strip():
                continue
            
            try:
                game_data = self._parse_single_pgn(pgn_game, user)
                if game_data:
                    games.append(game_data)
            except Exception as e:
                logger.warning(f"Failed to parse PGN game: {e}")
                continue
        
        return games
    
    def _parse_single_pgn(self, pgn_text: str, user: str) -> Optional[Dict[str, Any]]:
        """Parse single PGN game"""
        lines = pgn_text.strip().split('\n')
        headers = {}
        moves = []
        
        for line in lines:
            if line.startswith('[') and line.endswith(']'):
                # Parse header
                key_value = line[1:-1].split(' ', 1)
                if len(key_value) == 2:
                    key = key_value[0]
                    value = key_value[1].strip('"')
                    headers[key] = value
            else:
                # Parse moves
                if line.strip() and not line.startswith('['):
                    moves.extend(line.strip().split())
        
        if not headers:
            return None
        
        return {
            'headers': headers,
            'moves': moves,
            'pgn': pgn_text,
            'user': user
        }
    
    def _parse_lichess_game(self, game_data: Dict[str, Any], source: str) -> RawGame:
        """Parse Lichess game data into RawGame"""
        headers = game_data['headers']
        pgn = game_data['pgn']
        
        # Compute game UID
        game_uid = self._compute_game_uid(pgn)
        
        # Extract key headers
        canonical_headers = {
            'Event': headers.get('Event', ''),
            'Site': headers.get('Site', ''),
            'Date': headers.get('Date', ''),
            'Round': headers.get('Round', ''),
            'White': headers.get('White', ''),
            'Black': headers.get('Black', ''),
            'Result': headers.get('Result', ''),
            'ECO': headers.get('ECO', ''),
            'UTCDate': headers.get('UTCDate', ''),
            'UTCTime': headers.get('UTCTime', ''),
            'WhiteElo': headers.get('WhiteElo', ''),
            'BlackElo': headers.get('BlackElo', ''),
            'TimeControl': headers.get('TimeControl', '')
        }
        
        return RawGame(
            game_uid=game_uid,
            source=source,
            pgn=pgn,
            headers=canonical_headers,
            etag=None,  # Lichess doesn't provide ETags
            content_hash=self._compute_content_hash(pgn),
            fetch_timestamp=str(int(time.time()))
        )
    
    def _compute_game_uid(self, pgn: str) -> str:
        """Compute canonical game UID from PGN"""
        # Remove comments and normalize whitespace
        lines = pgn.split('\n')
        canonical_lines = []
        
        for line in lines:
            if line.startswith('[') and line.endswith(']'):
                canonical_lines.append(line)
            elif line.strip() and not line.startswith('['):
                # Remove comments from move text
                clean_line = line.split('{')[0].split('}')[0].strip()
                if clean_line:
                    canonical_lines.append(clean_line)
        
        canonical_pgn = '\n'.join(canonical_lines)
        return hashlib.sha256(canonical_pgn.encode('utf-8')).hexdigest()

class ChessComAdapter(ChessDataAdapter):
    """Chess.com data adapter (placeholder for future implementation)"""
    
    def fetch(self, source: str, user: str, max_games: int) -> Iterator[RawGame]:
        """Fetch games from Chess.com"""
        # TODO: Implement Chess.com adapter
        logger.warning("Chess.com adapter not yet implemented")
        return iter([])

class LumbraAdapter(ChessDataAdapter):
    """Lumbra's Gigabase adapter (placeholder for future implementation)"""
    
    def fetch(self, source: str, user: str, max_games: int) -> Iterator[RawGame]:
        """Fetch games from Lumbra's Gigabase"""
        # TODO: Implement Lumbra adapter
        logger.warning("Lumbra adapter not yet implemented")
        return iter([])

def get_adapter(source: str, config: DataIngestConfig) -> ChessDataAdapter:
    """Get appropriate adapter for source"""
    if source == "lichess":
        return LichessAdapter(config)
    elif source == "chesscom":
        return ChessComAdapter(config)
    elif source == "lumbra":
        return LumbraAdapter(config)
    else:
        raise ValueError(f"Unknown source: {source}")
