
# Import necessary modules, classes, functions
import Battleship
from Battleship import Board
from Battleship import Player, AI  # Import AI class here
from Battleship import setup_ships
from Battleship import play_game
from Battleship import clear_screen
from Battleship import validate_numships
from Battleship import getGamemode
from Battleship import getDifficulty

# Import time module for delays
import time

# Main function
# Contains overall game flow
def main():
    # Initialize a board for each player
    board1 = Board()
    board2 = Board()

    gameMode = getGamemode() # Asks the user for the desired gamemode
    num_ships = validate_numships() # Validates the number of ships the players selected

    # Initialize board for AI and User player
    if gameMode == 1:
        aiDifficulty = getDifficulty()
        player1 = Player("User", board1)
        player2 = AI("AI", board2)  # AI instance properly used

        setup_ships(player1, num_ships)  # Allow player to place their ships
        player2.place_ships_randomly(range(1, num_ships + 1))  # AI places its ships randomly

        print("\nThe game is starting! You are playing against the AI.")
        play_game(player1, player2, is_ai=True)  # Start the game against AI

    # Initialize 2 players for a 2-player game
    elif gameMode == 2:
        player1 = Player("Player 1", board1)
        player2 = Player("Player 2", board2)

        setup_ships(player1, num_ships)
        print("All of Player 1's ships are placed!")
        time.sleep(2)
        clear_screen()

        print("Please switch players!")
        time.sleep(2)
        clear_screen()

        setup_ships(player2, num_ships)
        print("All of Player 2's ships are placed!")
        time.sleep(2)
        clear_screen()

        print("The game is starting!")
        play_game(player1, player2)

if __name__ == "__main__":
    main()
