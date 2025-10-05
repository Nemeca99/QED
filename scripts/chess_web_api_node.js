/**
 * Chess Web API Integration for QEC
 * Node.js script using chess-web-api package
 */

const ChessWebAPI = require('chess-web-api');
const fs = require('fs').promises;
const path = require('path');

class QECChessWebAPIIntegrator {
    constructor() {
        this.chessAPI = new ChessWebAPI();
        this.dataDir = path.join(__dirname, '..', 'data', 'chess_web_api');
        this.rateLimitDelay = 1000; // 1 second between requests
    }

    async init() {
        // Create data directory
        try {
            await fs.mkdir(this.dataDir, { recursive: true });
            console.log(`Created data directory: ${this.dataDir}`);
        } catch (error) {
            console.log(`Data directory already exists: ${this.dataDir}`);
        }
    }

    async getPlayerGames(username, maxGames = 100) {
        console.log(`Fetching ${maxGames} games for ${username}...`);
        
        try {
            // Get player profile
            const player = await this.chessAPI.getPlayer(username);
            console.log(`Player: ${player.name} (${player.username})`);
            
            // Get recent games
            const games = await this.chessAPI.getPlayerGames(username, maxGames);
            console.log(`Fetched ${games.length} games`);
            
            // Process games for QEC analysis
            const processedGames = games.map(game => this.processGameForQEC(game));
            
            return {
                player: player,
                games: processedGames,
                totalGames: games.length
            };
            
        } catch (error) {
            console.error(`Error fetching games for ${username}:`, error.message);
            return { player: null, games: [], totalGames: 0 };
        }
    }

    processGameForQEC(game) {
        const qecAnalysis = {
            entanglementOpportunities: this.findEntanglementOpportunities(game),
            forcedMovePatterns: this.findForcedMovePatterns(game),
            reactiveEscapePatterns: this.findReactiveEscapePatterns(game),
            tacticalCombinations: this.findTacticalCombinations(game),
            positionalThemes: this.identifyPositionalThemes(game),
            timePressure: this.analyzeTimePressure(game),
            performanceMetrics: this.analyzePerformanceMetrics(game)
        };

        return {
            id: game.id,
            white: game.white,
            black: game.black,
            winner: game.winner,
            status: game.status,
            rated: game.rated,
            timeControl: game.time_control,
            timeClass: game.time_class,
            rules: game.rules,
            pgn: game.pgn,
            moves: game.moves,
            clock: game.clock,
            createdAt: game.createdAt,
            lastMoveAt: game.lastMoveAt,
            turns: game.turns,
            qecAnalysis: qecAnalysis
        };
    }

    findEntanglementOpportunities(game) {
        const opportunities = [];
        const moves = game.moves || [];
        
        for (let i = 0; i < moves.length; i++) {
            const move = moves[i];
            
            // Look for captures (potential entanglement)
            if (move.includes('x')) {
                opportunities.push({
                    moveNumber: i + 1,
                    move: move,
                    type: 'capture_entanglement',
                    description: 'Capture move that could create entanglement'
                });
            }
            
            // Look for checks (potential entanglement)
            if (move.includes('+') || move.includes('#')) {
                opportunities.push({
                    moveNumber: i + 1,
                    move: move,
                    type: 'check_entanglement',
                    description: 'Check move that could create entanglement'
                });
            }
            
            // Look for piece coordination
            if (i > 0 && this.piecesCoordinated(moves[i-1], move)) {
                opportunities.push({
                    moveNumber: i + 1,
                    move: move,
                    type: 'coordination_entanglement',
                    description: 'Piece coordination that could create entanglement'
                });
            }
        }
        
        return opportunities;
    }

    findForcedMovePatterns(game) {
        const patterns = [];
        const moves = game.moves || [];
        
        for (let i = 0; i < moves.length; i++) {
            const move = moves[i];
            
            // Check for checks (forced responses)
            if (move.includes('+') || move.includes('#')) {
                patterns.push({
                    moveNumber: i + 1,
                    move: move,
                    type: 'check_forced',
                    description: 'Check that forces response'
                });
            }
            
            // Check for tactical sequences
            if (i < moves.length - 1) {
                const nextMove = moves[i + 1];
                if (this.isTacticalSequence(move, nextMove)) {
                    patterns.push({
                        moveNumber: i + 1,
                        move: move,
                        type: 'tactical_forced',
                        description: 'Tactical sequence that forces response'
                    });
                }
            }
            
            // Check for mate threats
            if (move.includes('#')) {
                patterns.push({
                    moveNumber: i + 1,
                    move: move,
                    type: 'mate_threat',
                    description: 'Mate threat that forces response'
                });
            }
        }
        
        return patterns;
    }

    findReactiveEscapePatterns(game) {
        const patterns = [];
        const moves = game.moves || [];
        
        for (let i = 0; i < moves.length; i++) {
            const move = moves[i];
            
            // Look for king moves (potential escapes)
            if (move.includes('K')) {
                patterns.push({
                    moveNumber: i + 1,
                    move: move,
                    type: 'king_escape',
                    description: 'King move that could be an escape'
                });
            }
            
            // Look for piece retreats
            if (i > 0 && this.isRetreatMove(moves[i-1], move)) {
                patterns.push({
                    moveNumber: i + 1,
                    move: move,
                    type: 'piece_retreat',
                    description: 'Piece retreat from attack'
                });
            }
            
            // Look for defensive moves
            if (this.isDefensiveMove(move)) {
                patterns.push({
                    moveNumber: i + 1,
                    move: move,
                    type: 'defensive_move',
                    description: 'Defensive move to avoid loss'
                });
            }
        }
        
        return patterns;
    }

    findTacticalCombinations(game) {
        const combinations = [];
        const moves = game.moves || [];
        
        for (let i = 0; i < moves.length; i++) {
            const move = moves[i];
            
            // Look for tactical sequences
            if (i < moves.length - 2) {
                const nextMove = moves[i + 1];
                const nextNextMove = moves[i + 2];
                
                if (this.isTacticalCombination(move, nextMove, nextNextMove)) {
                    combinations.push({
                        moveNumber: i + 1,
                        move: move,
                        type: 'tactical_combination',
                        description: 'Tactical combination sequence'
                    });
                }
            }
            
            // Look for sacrifices
            if (this.isSacrificeMove(move)) {
                combinations.push({
                    moveNumber: i + 1,
                    move: move,
                    type: 'sacrifice',
                    description: 'Sacrifice move'
                });
            }
            
            // Look for pins
            if (this.isPinMove(move)) {
                combinations.push({
                    moveNumber: i + 1,
                    move: move,
                    type: 'pin',
                    description: 'Pin move'
                });
            }
        }
        
        return combinations;
    }

    identifyPositionalThemes(game) {
        const themes = [];
        const moves = game.moves || [];
        
        // Look for opening themes
        if (moves.length <= 20) {
            if (moves.slice(0, 5).some(move => move.includes('e4'))) {
                themes.push('e4_opening');
            }
            if (moves.slice(0, 5).some(move => move.includes('d4'))) {
                themes.push('d4_opening');
            }
            if (moves.slice(0, 5).some(move => move.includes('Nf3'))) {
                themes.push('Nf3_opening');
            }
        }
        
        // Look for middlegame themes
        if (moves.length > 20 && moves.length <= 40) {
            if (moves.slice(20, 40).some(move => move.includes('x'))) {
                themes.push('middlegame_tactics');
            }
            if (moves.slice(20, 40).some(move => move.includes('+'))) {
                themes.push('middlegame_attacks');
            }
        }
        
        // Look for endgame themes
        if (moves.length > 40) {
            if (moves.slice(-20).some(move => move.includes('K'))) {
                themes.push('endgame_king_activity');
            }
            if (moves.slice(-20).some(move => move.includes('='))) {
                themes.push('endgame_promotion');
            }
        }
        
        return themes;
    }

    analyzeTimePressure(game) {
        const clock = game.clock || {};
        return {
            initialTime: clock.initial || 0,
            increment: clock.increment || 0,
            timeControl: `${clock.initial || 0}+${clock.increment || 0}`,
            timePressureLevel: (clock.initial || 0) < 300 ? 'high' : 
                             (clock.initial || 0) < 600 ? 'medium' : 'low'
        };
    }

    analyzePerformanceMetrics(game) {
        return {
            timeClass: game.time_class || '',
            rules: game.rules || '',
            rated: game.rated || false,
            status: game.status || ''
        };
    }

    // Helper methods
    piecesCoordinated(prevMove, currMove) {
        return prevMove !== currMove;
    }

    isTacticalSequence(move1, move2) {
        return move1.includes('x') && move2.includes('x');
    }

    isRetreatMove(prevMove, currMove) {
        return prevMove !== currMove;
    }

    isDefensiveMove(move) {
        return move.includes('+') || move.includes('#');
    }

    isTacticalCombination(move1, move2, move3) {
        return [move1, move2, move3].every(move => move.includes('x'));
    }

    isSacrificeMove(move) {
        return move.includes('x') && move === move.toUpperCase();
    }

    isPinMove(move) {
        return move.includes('x') && move.length > 3;
    }

    async collectMultiplePlayers(usernames, maxGamesPerPlayer = 50) {
        console.log(`Collecting data for ${usernames.length} players...`);
        
        const allData = {
            players: [],
            totalGames: 0,
            metadata: {
                collectionTime: new Date().toISOString(),
                totalPlayers: usernames.length,
                maxGamesPerPlayer: maxGamesPerPlayer
            }
        };

        for (const username of usernames) {
            console.log(`\nCollecting data for ${username}...`);
            
            try {
                const playerData = await this.getPlayerGames(username, maxGamesPerPlayer);
                allData.players.push(playerData);
                allData.totalGames += playerData.totalGames;
                
                // Rate limiting
                await new Promise(resolve => setTimeout(resolve, this.rateLimitDelay));
                
            } catch (error) {
                console.error(`Error collecting data for ${username}:`, error.message);
            }
        }

        console.log(`\nCollected data for ${allData.players.length} players with ${allData.totalGames} total games`);
        return allData;
    }

    createQECTrainingDataset(data) {
        console.log('Creating QEC training dataset...');
        
        const trainingDataset = {
            entanglementExamples: [],
            forcedMoveExamples: [],
            reactiveEscapeExamples: [],
            tacticalExamples: [],
            positionalExamples: []
        };

        for (const player of data.players) {
            for (const game of player.games) {
                const qecAnalysis = game.qecAnalysis;
                
                if (qecAnalysis.entanglementOpportunities) {
                    trainingDataset.entanglementExamples.push(...qecAnalysis.entanglementOpportunities);
                }
                
                if (qecAnalysis.forcedMovePatterns) {
                    trainingDataset.forcedMoveExamples.push(...qecAnalysis.forcedMovePatterns);
                }
                
                if (qecAnalysis.reactiveEscapePatterns) {
                    trainingDataset.reactiveEscapeExamples.push(...qecAnalysis.reactiveEscapePatterns);
                }
                
                if (qecAnalysis.tacticalCombinations) {
                    trainingDataset.tacticalExamples.push(...qecAnalysis.tacticalCombinations);
                }
                
                if (qecAnalysis.positionalThemes) {
                    trainingDataset.positionalExamples.push(...qecAnalysis.positionalThemes);
                }
            }
        }

        const totalExamples = Object.values(trainingDataset).reduce((sum, examples) => sum + examples.length, 0);
        console.log(`Created training dataset with ${totalExamples} examples`);
        
        return trainingDataset;
    }

    async saveData(data, filename) {
        const filepath = path.join(this.dataDir, filename);
        await fs.writeFile(filepath, JSON.stringify(data, null, 2));
        console.log(`Data saved to: ${filepath}`);
        return filepath;
    }
}

// Main execution
async function main() {
    const integrator = new QECChessWebAPIIntegrator();
    await integrator.init();

    // Default usernames to collect data for
    const usernames = process.argv.slice(2).length > 0 ? 
        process.argv.slice(2) : 
        ['MagnusCarlsen', 'FabianoCaruana', 'Hikaru', 'DingLiren'];

    try {
        // Collect data from multiple players
        const collectedData = await integrator.collectMultiplePlayers(usernames, 50);
        
        // Save raw data
        await integrator.saveData(collectedData, 'chess_web_api_data.json');
        
        // Create QEC training dataset
        const trainingDataset = integrator.createQECTrainingDataset(collectedData);
        await integrator.saveData(trainingDataset, 'qec_training_dataset.json');
        
        console.log('\nChess Web API integration completed successfully!');
        
    } catch (error) {
        console.error('Error during chess web API integration:', error);
        process.exit(1);
    }
}

// Run if called directly
if (require.main === module) {
    main().catch(console.error);
}

module.exports = QECChessWebAPIIntegrator;
