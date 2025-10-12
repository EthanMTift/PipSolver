# PipSolver

This is a **Python** project that solves the New York Times Game "Pips"

Upon starting the program, it will prompt the user for a file. Please give it an image of the Pips board you would like to solve.
Make sure that the image includes all the dominos as well. You will also need to specify the grid size (row x col). Input as two numbers with a space between them.

The program will prompt you to select the top left and bottom right of a rectangle that envelops the board. Make sure that the rectangle is bigger than the board and does not include the domino's or anything else for the best results.

The program will then prompt you to select the domino area. Click the top left and bottom right of the rectangle that covers all the dominos.

There are 3 solver options:

**Visual**: This shows the entire backtrack process. Since it renders the board for each placement, this can take quite a while to finish.

**Final Only**: Does the backtrack behind the scenes, then renders the finished board.

**Replay**: Renders only the steps taken on the optimal solution path, so every step places a domino correctly.

If it fails to solve, it will print you a message telling you so. All Pips have a solution, so if that happens, either the OCR failed or you didnt specify the grid/dominos properly.