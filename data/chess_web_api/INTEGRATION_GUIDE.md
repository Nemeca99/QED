# Chess Web API Integration Guide for QEC

## Overview
This guide explains how to integrate various chess web APIs with the QEC (Quantum Entanglement Chess) system for comprehensive training data collection.

## Available APIs

### 1. Lichess API
- **Endpoint**: https://lichess.org/api
- **Features**: Games, players, tournaments, puzzles
- **Rate Limit**: 60 requests/minute
- **Authentication**: Optional (for private data)

### 2. Chess.com API
- **Endpoint**: https://api.chess.com
- **Features**: Games, players, clubs, tournaments
- **Rate Limit**: 30 requests/minute
- **Authentication**: Not required for public data

### 3. ChessDB API
- **Endpoint**: https://chessdb.cn
- **Features**: Position analysis, opening book
- **Rate Limit**: 20 requests/minute
- **Authentication**: Not required

## Integration Methods

### Python Integration
```bash
# Install dependencies
pip install aiohttp requests

# Run Python integration
python data/chess_web_api_integration.py --usernames MagnusCarlsen FabianoCaruana --max-games 50
```

### Node.js Integration
```bash
# Install dependencies
npm install chess-web-api axios node-fetch

# Run Node.js integration
node scripts/chess_web_api_node.js MagnusCarlsen FabianoCaruana Hikaru DingLiren
```

## Data Collection

### Player Data
- **Games**: Recent games with full PGN
- **Ratings**: Current and historical ratings
- **Performance**: Time control and performance metrics
- **Analysis**: QEC-specific pattern analysis

### Game Analysis
- **Entanglement Opportunities**: Captures, checks, coordination
- **Forced Move Patterns**: Checks, tactical sequences, mate threats
- **Reactive Escape Patterns**: King escapes, piece retreats, defensive moves
- **Tactical Combinations**: Sacrifices, pins, tactical sequences
- **Positional Themes**: Opening, middlegame, endgame themes

## QEC Training Applications

### 1. Real-time Data Collection
- **Live Games**: Collect games as they're played
- **Player Tracking**: Monitor specific players' games
- **Tournament Data**: Collect tournament games
- **Puzzle Generation**: Create QEC puzzles from real games

### 2. Pattern Analysis
- **Entanglement Patterns**: Identify entanglement opportunities
- **Forced Move Sequences**: Analyze forced move patterns
- **Reactive Escapes**: Study defensive patterns
- **Tactical Combinations**: Learn tactical sequences

### 3. Training Dataset Creation
- **Entanglement Examples**: Real game entanglement opportunities
- **Forced Move Examples**: Actual forced move sequences
- **Reactive Escape Examples**: Real defensive patterns
- **Tactical Examples**: Actual tactical combinations
- **Positional Examples**: Real positional themes

## Usage Examples

### Collect Player Data
```python
# Python
integrator = ChessWebAPIIntegrator()
data = await integrator.collect_user_data(['MagnusCarlsen'], 100)
```

```javascript
// Node.js
const integrator = new QECChessWebAPIIntegrator();
const data = await integrator.collectMultiplePlayers(['MagnusCarlsen'], 100);
```

### Analyze Games for QEC
```python
# Analyze game for QEC patterns
qec_analysis = integrator._analyze_game_for_qec(game_data)
```

### Create Training Dataset
```python
# Create QEC training dataset
training_dataset = integrator.create_qec_training_dataset(data)
```

## Rate Limiting

### Lichess API
- **Limit**: 60 requests/minute
- **Implementation**: 1 second delay between requests
- **Best Practice**: Use async requests with proper delays

### Chess.com API
- **Limit**: 30 requests/minute
- **Implementation**: 2 second delay between requests
- **Best Practice**: Batch requests when possible

### ChessDB API
- **Limit**: 20 requests/minute
- **Implementation**: 3 second delay between requests
- **Best Practice**: Cache results for repeated positions

## Error Handling

### Common Issues
1. **Rate Limiting**: Implement proper delays
2. **Network Errors**: Use retry logic with exponential backoff
3. **Data Parsing**: Handle malformed game data gracefully
4. **Authentication**: Handle API key expiration

### Best Practices
1. **Respect Rate Limits**: Always implement proper delays
2. **Error Recovery**: Use try-catch blocks and retry logic
3. **Data Validation**: Validate collected data before processing
4. **Logging**: Log errors and successful operations

## Performance Optimization

### Async Processing
- Use async/await for concurrent requests
- Implement proper rate limiting
- Use connection pooling for HTTP requests

### Caching
- Cache frequently accessed data
- Implement local storage for game data
- Use Redis for distributed caching

### Data Processing
- Process games in batches
- Use streaming for large datasets
- Implement progress tracking

## Security Considerations

### API Keys
- Store API keys securely
- Use environment variables
- Rotate keys regularly

### Data Privacy
- Respect user privacy
- Only collect public data
- Implement data retention policies

### Rate Limiting
- Monitor API usage
- Implement circuit breakers
- Use exponential backoff

## Monitoring and Logging

### Metrics to Track
- API request success rate
- Response times
- Rate limit hits
- Data collection progress

### Logging
- Log all API requests
- Track errors and exceptions
- Monitor performance metrics
- Generate usage reports

## Troubleshooting

### Common Problems
1. **Rate Limiting**: Implement proper delays
2. **Network Issues**: Use retry logic
3. **Data Parsing**: Validate input data
4. **Memory Usage**: Process data in batches

### Solutions
1. **Rate Limiting**: Use exponential backoff
2. **Network Issues**: Implement circuit breakers
3. **Data Parsing**: Use robust parsing libraries
4. **Memory Usage**: Use streaming and batching

## Future Enhancements

### Planned Features
1. **Real-time Streaming**: Live game data streaming
2. **Advanced Analytics**: Machine learning integration
3. **Custom APIs**: QEC-specific API endpoints
4. **Performance Monitoring**: Advanced metrics and alerting

### Integration Opportunities
1. **Chess Engines**: Integrate with Stockfish, Leela
2. **Databases**: Store data in PostgreSQL, MongoDB
3. **Cloud Services**: Use AWS, GCP, Azure for scalability
4. **Monitoring**: Integrate with Prometheus, Grafana
