"""
Authors: Kaitlyn Clements
         Taylor Slade
         Sam Muehlebach
         Aaditi Chinawalker
         Lizzie Soltis

Collaborators: Saje Cowell
               Spencer Sliffe
               Jeff Burns
               Charlie Gillund

Assignment: EECS 581 Project 1; Battleship
Program: Battleship.pyBattleship file to identify different classes/objects of the game
Inputs: Players.py, Board.py, Ship.py, User Input
Outputs: Battleship Game, interactive and dependent on User Input
Other Sources: ChatGPT
Date: 09/04/2024
last modified: 09/09/2024
"""

# Import libraries for later use
import random
import os
import time

# AI Object
class AI:
    def __init__(self, name, board):
        self.name = name
        self.board = board
        self.hunt_mode = True  # Start in "hunt" mode to randomly shoot
        self.target_mode = False  # Switch to "target" mode when a ship is hit
        self.target_list = []  # List of cells to target around a hit ship
        self.last_hit = None  # Track the last hit cell
        self.direction_queue = []  # Queue to handle directions

    def place_ships_randomly(self, ship_sizes):
        for size in ship_sizes:
            while True:
                start_x = random.randint(0, self.board.size - 1)
                start_y = random.randint(0, self.board.size - 1)
                orientation = 'H' if random.randint(0, 1) == 0 else 'V'
                ship = Ship(size, orientation, start_x, start_y)

                if self.board.is_valid_position(ship):
                    self.board.place_ship(ship)
                    break

    # Function for the medium mode AI
    def medModeAI(self, player_board):
        if self.hunt_mode:
            print("AI is in hunt mode...")
            while True:
                randRow = random.randint(0, player_board.size - 1)
                randCol = random.randint(0, player_board.size - 1)

            # Ensure the AI hasn't guessed this spot before on the player's board
            if player_board.grid[randRow][randCol] not in ("\033[31mX\033[0m", "O"):
                break

            print(f"AI randomly shoots at ({randRow + 1}, {chr(randCol + 65)})")
            hit_result, ship_sunk = self.process_shot(player_board, randRow, randCol)

            if hit_result == "Hit!":
                print(f"AI hit at ({randRow + 1}, {chr(randCol + 65)})! Switching to target mode.")
                self.hunt_mode = False
                self.target_mode = True
                self.last_hit = (randRow, randCol)
                self.direction_queue = self.populate_target_list(randRow, randCol)

            return hit_result, ship_sunk

        elif self.target_mode:
            print("AI is in target mode...")
            while self.direction_queue:
                # Get the next direction from the queue
                direction = self.direction_queue[0]
                targetRow, targetCol = self.get_next_target(self.last_hit[0], self.last_hit[1], direction)

                print(f"AI targets direction {direction} resulting in cell ({targetRow + 1}, {chr(targetCol + 65)})")

                # Check if this cell is valid
                if (0 <= targetRow < player_board.size and 0 <= targetCol < player_board.size
                    and player_board.grid[targetRow][targetCol] not in ("X", "O")):

                    hit_result, ship_sunk = self.process_shot(player_board, targetRow, targetCol)

                    if hit_result == "Hit!":
                        print(f"AI hit again at ({targetRow + 1}, {chr(targetCol + 65)})! Continuing in this direction.")
                        self.last_hit = (targetRow, targetCol)
                        if not ship_sunk:
                            return hit_result, ship_sunk
                        else:
                            print("AI has sunk a ship!")
                            self.hunt_mode = True
                            self.target_mode = False
                            self.direction_queue.clear()
                            return hit_result, ship_sunk

                    # If it misses, remove the current direction and try the next one
                    print(f"AI missed at ({targetRow + 1}, {chr(targetCol + 65)}). Trying next direction.")
                    self.direction_queue.pop(0)  # Remove current direction and try next

                else:
                    # Invalid cell or already hit/missed; remove the direction and try next
                    print(f"Invalid target or already hit at ({targetRow + 1}, {chr(targetCol + 65)}). Trying next direction.")
                    self.direction_queue.pop(0)

            # If all directions are exhausted, go back to hunt mode
            print("AI has exhausted all target directions. Returning to hunt mode.")
            self.hunt_mode = True
            self.target_mode = False
            return "Miss!", False

#Handles the logic of processing a shot at the given row and col
    def process_shot(self, player_board, row, col):
        ship_sunk = False
        if player_board.grid[row][col] == "S" or player_board.grid[row][col].isdigit():
            if (row, col) in player_board.hit_count:
                player_board.hit_count[(row, col)] += 1
            else:
                player_board.hit_count[(randRow, randCol)] = 1
            player_board.grid[randRow][randCol] = "\033[31mX\033[0m"
            player_board.hits.append((randRow, randCol))

            # Check if a ship was hit and whether it is sunk
            for ship in player_board.ships:
                if (row, col) in ship.coordinates:
                    if ship.is_sunk(player_board.hits):
                        ship_sunk = True
                        print(f"Ship sunk at ({row + 1}, {chr(col + 65)})!")

            return "Hit!", ship_sunk
        else:
            player_board.grid[row][col] = "O"
            player_board.misses.append((row, col))
            return "Miss!", ship_sunk


    def populate_target_list(self, row, col):
        #Populate list of directions to target around the initial hit in the order of Up, Down, Left, Right
        return [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def get_next_target(self, row, col, direction):
        dr, dc = direction
        return row + dr, col + dc


# Initializes a Player class/object. Each play has their own name and board.
class Player:
    def __init__(self, name, board):
        self.name = name
        self.board = board
        self.consecutive_hits = 0  # New variable to track consecutive hits
        self.ac130_available = False  # New flag for AC130 score streak

    # Function of a Player
    # Allow player to take a turn by firing at opponent's board
    def take_turn(self, opponent):
        print(f"{self.name}'s turn!")
        print("Your board: ")
        self.board.display()
        # Display current player's board^

        # Display how many times current player's ships have been hit
        print("\nHits on your ships:")
        self.display_hits()

        # Display opponent's board but hide the ships from the view
        print("\nOpponent's board: ")
        opponent.board.display(show_ships=False)

        # Get coordinates for firing, make sure valid cooardinates
        # If AC130 is available, allow the player to choose whether to use it or not
        if self.ac130_available:
            use_ac130 = input("AC130 score streak available! Do you want to use it? (yes/no): ").lower()
            if use_ac130 == 'yes':
                self.activate_ac130(opponent.board)
                self.ac130_available = False  # Reset after use
                return  # Skip normal turn if AC130 is used

        # Normal turn logic
        while True:
            target = input("Enter target coordinates (e.g., A5): ").upper()
            if len(target) >= 2 and target[0] in "ABCDEFGHIJ" and target[1:].isdigit():
                x = int(target[1:]) - 1
                y = ord(target[0]) - ord("A")
                if (
                    0 <= x < 10
                    and 0 <= y < 10
                    and (x, y) not in opponent.board.hits + opponent.board.misses
                ):
                    break
            print("Invalid coordinates, try again.")
            # Ensure target hasn't been fired at before

        # Fire at opponent's board. Print whether the shot was a hit or miss. If a ship is sunk, notify the player.
        result, ship_sunk = opponent.board.receive_fire(x, y)
        print(f"\n{self.name} fired at {target}: {result}")
        if ship_sunk:
            print(f"{self.name} has sunk a ship!")

        # Update consecutive hits and check for AC130 score streak activation
        if result == "Hit!":
            self.consecutive_hits += 1
            if self.consecutive_hits == 3:
                self.ac130_available = True  # AC130 is available but doesn't need to be used immediately
                print(f"AC130 score streak activated for {self.name}!")
        else:
            self.consecutive_hits = 0  # Reset on miss

    # Function of Player
    # Display how many times each ship has been hit; Calculated by comparing coordinates with hits on the board
    def display_hits(self):
        hit_count_by_ship = {}
        for ship in self.board.ships:
            hit_count = 0
            for coord in ship.coordinates:
                if coord in self.board.hits:
                    hit_count += 1
            hit_count_by_ship[tuple(ship.coordinates)] = hit_count

        # Print hit details for each ship
        for ship_coords, hit_count in hit_count_by_ship.items():
            print(f"{ship_coords}: {hit_count} hit(s)")

    def activate_ac130(self, opponent_board):
        # Ask the player if they want to hit a row or column
        choice = input("AC130 activated! Do you want to target a row or a column? (R/C): ").upper()

        if choice == 'R':  # Target row
            row = int(input("Enter the row number (1-10): ")) - 1
            # Show AC-130 inbound message after the player makes a choice
            print("Hostile AC-130 inbound!")
            time.sleep(3)
            plane_animation_with_payload()  # Play the animation

            for col in range(opponent_board.size):
                if opponent_board.grid[row][col] == "S":
                    opponent_board.grid[row][col] = "\033[31mX\033[0m"
                    opponent_board.hits.append((row, col))
                    print(f"Hit at {chr(col + ord('A'))}{row + 1}!")
                else:
                    opponent_board.grid[row][col] = "O"

        elif choice == 'C':  # Target column
            col = ord(input("Enter the column letter (A-J): ").upper()) - ord('A')
            # Show AC-130 inbound message after the player makes a choice
            print("Hostile AC-130 inbound!")
            time.sleep(3)
            plane_animation_with_payload()  # Play the animation

            for row in range(opponent_board.size):
                if opponent_board.grid[row][col] == "S":
                    opponent_board.grid[row][col] = "\033[31mX\033[0m"
                    opponent_board.hits.append((row, col))
                    print(f"Hit at {chr(col + ord('A'))}{row + 1}!")
                else:
                    opponent_board.grid[row][col] = "O"

        print("AC130 Strike Completed!")

# Initializes a Board class/object
# Each Board has a grid, ships, hits, misses, and hit count
class Board:
    def __init__(self, size=10):
        self.size = size
        self.grid = [["\033[34m~\033[0m"] * size for _ in range(size)]
        self.ships = []
        self.hits = []
        self.misses = []
        self.hit_count = {} #tracking how many times each cell is hit as dictionary

    # Function of a Board
    # Display the board. If show_ships is False, hide ships and only show hits and misses.
    def display(self, show_ships=True):
        print("   " + " ".join([chr(ord("A") + i) for i in range(self.size)]))
        # Display columns A-J ^
        for i in range(self.size):
            row = []
            for j in range(self.size):
                if not show_ships and self.grid[i][j] == "S":
                    row.append("\033[34m~\033[0m") # Hide ships if show_ships is False
                elif self.grid[i][j] == "\033[31mX\033[0m" and (i,j) in self.hit_count:
                    row.append("\033[31mX\033[0m") # Always display X when a ship has been hit
                else:
                    row.append(self.grid[i][j]) # Show the current state of the cell
            print(f"{i + 1:2} " + " ".join(row))
            # Display board row by row, either hiding ships or showing them based on 'show_ships' boolean

    # Function of a Board
    # Place a ship on the board
    def place_ship(self, ship):
        for x, y in ship.coordinates:
            self.grid[x][y] = "S"
        self.ships.append(ship)

    # Function of a Board
    # Check if the ship's position is valid on the board
    def is_valid_position(self, ship):
        for x, y in ship.coordinates:
            if (
                x < 0
                or x >= self.size
                or y < 0
                or y >= self.size
                or self.grid[x][y] == "S"
            ):
                return False
        return True
        # Verifies ship's position is within bounds and isn't overlapping with other ships

    # Function of a Board
    # Handle an incoming shot at (x, y)
    def receive_fire(self, x, y):
        ship_sunk = False
        if self.grid[x][y] == "S" or self.grid[x][y].isdigit():
            if (x,y) in self.hit_count: #if hit, increment hit counter for spot
                self.hit_count[(x,y)] += 1
            else:
                self.hit_count[(x,y)] = 1
            self.grid[x][y] = "\033[31mX\033[0m"
            self.hits.append((x, y))
            for ship in self.ships:
                if (x, y) in ship.coordinates:
                    if ship.is_sunk(self.hits):
                        ship_sunk = True
            return "Hit!", ship_sunk
        else:
            self.grid[x][y] = "O"
            self.misses.append((x, y))
            return "Miss!", ship_sunk
        # Process shot at board
        # If ship is hit, record it and check if the ship is sunk
        # Else, record it as a miss

    # Function of a Board
    # Check if all ships have been sunk
    def all_ships_sunk(self):
        for ship in self.ships:
            if not ship.is_sunk(self.hits):
                return False
        return True

# Initializes a Ship class/object
# Each Ship has a size, orientation, starting coordinates (x and y), and remaining coordinates
class Ship:
    def __init__(self, size, orientation, start_x, start_y):
        self.size = size
        self.orientation = orientation
        self.start_x = start_x
        self.start_y = start_y
        self.coordinates = self.generate_coordinates()

    # Function of a Ship
    # Generate the coordinates of the ship based on its size and orientation (horizontal or vertical)
    def generate_coordinates(self):
        coordinates = []
        if self.orientation == "H":
            for i in range(self.size):
                coordinates.append((self.start_x, self.start_y + i))
        else:  # Vertical orientation
            for i in range(self.size):
                coordinates.append((self.start_x + i, self.start_y))
        return coordinates

    # Function of a Ship
    # Check is all of a ship's coordinates have been marked as a hit, if so then the ship has been sunk
    def is_sunk(self, hits):
        return all(coord in hits for coord in self.coordinates)



# Function not belonging to a class
# Converts all user input into board incdices
def input_to_index(input_str):
    column = ord(input_str[0].upper()) - ord('A')
    row = int(input_str[1:]) - 1
    return row, column

# Not a function belonging to a class
# Validate the input for ship orientation (H or V)
def validate_orientation():
    while True:
        ship_orientation = input("Enter orientation (H for horizontal, V for vertical): ").strip().upper()
        if ship_orientation in ['H', 'V']:
            return ship_orientation
        else:
            print("Invalid orientation! Please enter 'H' or 'V'.")

# Not a function belonging to a class
# Validate the position input, ensuring format is correct (A-J and 1-10)
def validate_position():
    while True:
        start_position = input("Enter the starting position (e.g., A1): ").strip().upper()
        if len(start_position) < 2 or len(start_position) > 3:
            print("Invalid position! Position must be a letter (A-J) followed by a number (1-10).")
            continue
            # Validates start position

        column_letter = start_position[0]
        if column_letter < 'A' or column_letter > 'J':
            print("Invalid position! The letter must be between A and J.")
            continue
            # Validates the column letter is between A-J

        try:
            row_number = int(start_position[1:])
            if row_number < 1 or row_number > 10:
                print("Invalid position! The number must be between 1 and 10.")
                continue
                # Validates the row number is between 1-10
        except ValueError:
            print("Invalid position! The number must be a valid integer.")
            continue
            # Raise an error if invalid coordinates are provided.

        return start_position # Starts the process over again

#Asks the user to select their desired gamemode, and returns the option as an int
def getGamemode():
    gameMode = int(input("\nPlease Choose the Gamemode: \n1) 1-Player vs. AI\n2) 2-Player Pass-And-Play\n\nEnter your selection: "))

    if(gameMode == 1 or gameMode == 2):
        return gameMode
    else:
        print("Invalid Option, Please Try Again!")
        getGamemode()

def getDifficulty():
    aiDifficulty = int(input("\nPlease Choose the AI's Difficulty: \n1) Easy\n2) Medium\n3) Hard\n\nEnter your selection: "))

    if(aiDifficulty == 1 or aiDifficulty == 2 or aiDifficulty == 3):
        return aiDifficulty
    else:
        print("Invalid Option, Please Try Again!")
        getDifficulty()

# Not a function belonging to a class
# Validate the number of ships each player will have, ensure input is between 1-5
def validate_numships():
    while True:
        ship_num = int(input("\nEnter the number of ships each player will get (minimum of 1, maximum of 5): "))
        if ship_num in [1,2,3,4,5]:
            return ship_num
        else:
            print("Invalid number of ships! Please enter a number between 1 and 5")

# Not a function belonging to a class
# Sets up ships on player's board
# User is notified to place their ships by providing orientation and position
def setup_ships(player, num_ships):
    print(f"{player.name}'s turn to place ships!")

    print(f"{player.name}'s current board:")
    player.board.display()

    ship_sizes = list(range(1, num_ships + 1))

    # Iterate through ship_sizes for valid input and placement without overlapping
    # If a valid position is found, the ship is placed abd the loop continues
    # Else the player is asked to try again
    for size in ship_sizes:
        while True:
            ship_orientation = validate_orientation()
            start_position = validate_position()
            start_x, start_y = input_to_index(start_position)
            ship = Ship(size, ship_orientation, start_x, start_y)
            if player.board.is_valid_position(ship):
                player.board.place_ship(ship)
                print(f"{player.name} placed a ship of size {size}.")
                print(f"{player.name}'s board: ")
                player.board.display()
                break
            else:
                print("Invalid position! Please choose another location")

    def activate_ac130(self, opponent_board):
        # Ask the player if they want to hit a row or column
        choice = input("AC130 activated! Do you want to target a row or a column? (R/C): ").upper()

        if choice == 'R':  # Target row
            row = int(input("Enter the row number (1-10): ")) - 1
            for col in range(opponent_board.size):
                if opponent_board.grid[row][col] == "S":
                    opponent_board.grid[row][col] = "\033[31mX\033[0m"
                    opponent_board.hits.append((row, col))
                    print(f"Hit at {chr(col + ord('A'))}{row + 1}!")
                else:
                    opponent_board.grid[row][col] = "O"
        elif choice == 'C':  # Target column
            col = int(input("Enter the column letter (A-J): ").upper()) - ord('A')
            for row in range(opponent_board.size):
                if opponent_board.grid[row][col] == "S":
                    opponent_board.grid[row][col] = "\033[31mX\033[0m"
                    opponent_board.hits.append((row, col))
                    print(f"Hit at {chr(col + ord('A'))}{row + 1}!")
                else:
                    opponent_board.grid[row][col] = "O"

        print("AC130 strike completed!")

def plane_animation_with_payload():
    frames = [
        [
            "      __|__         ",
            "-----o--(_)--o-----  ",
            "        | |         ",
            "         O          "
        ],
        [
            "         __|__            ",
            "    ----o--(_)--o-----     ",
            "            | |           ",
            "            O             ",
            "           |              "
        ],
        [
            "            __|__                ",
            "       ----o--(_)--o------        ",
            "               | |               ",
            "               O                 ",
            "              /|\\                "
        ]
    ]

    # Clear the screen and display the plane flying and payload dropping
    for frame in frames:
        clear_screen()
        for line in frame:
            print(line)
        time.sleep(0.67)  # Pause to create a frame

    clear_screen()  # Clear the screen


# Function not belonging to a class
# Main game loop
# Both players take turns playing the game. The game ends when one player's ships are all sunk.
def play_game(player1, player2, is_ai=False, aiDifficulty=1):
    while True:
        player1.take_turn(player2)
        if player2.board.all_ships_sunk():
            print(f"{player1.name} wins!")
            break

        # Give player 1 time to see their shot result before switching
        time.sleep(3)
        clear_screen()

        if is_ai:
            print("AI's turn!")
            # Call the AI method based on selected difficulty
            if aiDifficulty == 1:
                result, ship_sunk = player2.easyModeAI(player1.board)
            elif aiDifficulty == 2:
                result, ship_sunk = player2.medModeAI(player1.board)
            elif aiDifficulty == 3:
                result, ship_sunk = player2.hardModeAI(player1.board)  # Assuming a hardModeAI method exists

            print(f"AI fired and it was a {result}!")
            if ship_sunk:
                print("AI has sunk a ship!")
            if player1.board.all_ships_sunk():
                print("AI wins!")
                break
        else:
            print("Please switch players!")
            time.sleep(5)  # Pause to allow players to switch without rushing
            clear_screen()
            player2.take_turn(player1)
            time.sleep(3)  # Allow Player 2 to see their shot result before clearing the screen
            clear_screen()
            print("Please switch players!")
            time.sleep(5)  # Pause to allow players to switch without rushing
            if player1.board.all_ships_sunk():
                print(f"{player2.name} wins!")
                break

        clear_screen()

# Function not belonging to a class
# Clear screen for cleaner experience and to delete previous players data from the screen to hide it from next player.
def clear_screen():
   os.system('cls' if os.name == 'nt' else 'clear')
