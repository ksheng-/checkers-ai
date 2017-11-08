# checkers-ai

## Setup
Clone the project:
```
git clone https://github.com/ksheng-/checkers-ai.git
cd checkers-ai
```
Make sure Python 3.x is installed, and install the dependencies:
```
pip install -r requirements.txt
```

## Running the program
```
python game.py
```

## Usage

The program will will begin by presenting a series of settings to customize the game. At each prompt, select one of the option numbers to continue. If you input an invalid selection, it will prompt again until a valid one is chosen.

The following settings are prompted:
#### Gameplay mode
Choose between player vs player, player vs AI, and AI vs AI.

#### Time limit
The time limit in seconds each AI will spend searching for a move.

#### Side
If player vs AI is chosen, select the player side.

#### Board preset
Allows the user to input a custom initial board state.

#### Draw detection
Enable automatic detection of draws.

Once these options are configured, the game will begin. At each turn, the current board state is printed
  * Square ID numbers in the top right hand corner of each black square.
  * Black pieces are represented by a red B
  * White pieces are represented by a white W
  * Kings are represented by the piece representation surrounded by braces i.e {B} and {W}
 
If it is a human user's turn, a list of valid moves is presented and the user is prompted to select one.

If it is an AI's turn, the AI will search for the best move within the time limit, printing the depth reached and the time spent searching

## Implementation
### Game
A checkers game class is implemented within checkers.py.

This implementation uses a 4-tuple of integers to represent state: (black, white, kings, turn).
Black, white, and kings are bitboards stored in numpy uint32s, while turn is an integer set to 0 if it is black's turn and 1 if it is white's turn.

This class implements all move and jump validity detection, using bitwise operations in order to test each case.
One Bitboard() is kept to represent the actual game, while copies are created from the state 4-tuple in the AI to search the game tree.

### AI
#### Searching
#### Evaluation

### AI
