import copy
import string
from typing import Union

#################################################
# Functions for you to write
# For all problems, DO NOT hardcode the test cases at the bottom into your solution!
#################################################

"""
This is the first part of a larger project to code a fully functional chess game.
Let a chess board be defined by a 2-dimensional list as follows:
[[' ', ' ', '♖', ' '],
[' ', ' ', ' ', ' '],
[' ', '♘', ' ', ' '],
[' ', ' ', ' ', ' ']]
White pieces start from the bottom row, and black pieces start 
Pieces are represented by the Unicode Chess Piece symbols as shown below:
♛♚♝♞♜♟
♙♖♘♗♕♔
Blank spaces are represented by a single space.
For this section, write a function that can find all possible moves for chess pieces
on a given board, special moves like en passant and castling excluded. 
Write the helper functions getValidPawnMoves, getValidBishopMoves, getValidQueenMoves,
getValidKnightMoves, getValidRookMoves that take a given position and board and 
give all valid moves for the specified piece from that position.
Here is a link to chess rules: https://en.wikipedia.org/wiki/Rules_of_chess
"""

def pieceType(board: list, row: int, col: int) -> tuple:
    '''
    Given a board and the specified location, 
    return a tuple consisting of which side 
    the piece is on and which piece it is. 
    Returns None if the location has no piece.
    '''
    #print(row, col)
    piece = board[row][col]
    output = [None, None]
    if piece in '♛♚♝♞♜♟': output[0] = 'black'
    elif piece in '♙♖♘♗♕♔': output[0] = 'white'
    if piece in '♜♖': output[1] = 'rook'
    elif piece in '♞♘': output[1] = 'knight'
    elif piece in '♗♝': output[1] = 'bishop'
    elif piece in '♕♛': output[1] = 'queen'
    elif piece in '♔♚': output[1] = 'king'
    elif piece in '♙♟': output[1] = 'pawn'
    return tuple(output)

def validLinePositions(board:list, row:int, col:int, 
                       line:list, side: str) -> list:
    """
    given the position of a piece and a list of positions (in tuples) 
    it can go to on a single line (e.g. a list of all positions that a 
    rook can go to in one move if it can only move upwards), return a list of 
    possible moves on that list that are not blocked by another piece. 
    Checks by using a boolean to determine if a piece blocks the remainder of
    the line.
    """
    validLineMoves = []
    blockingPiece = False

    for position in line:
        if blockingPiece == False:
            if pieceType(board, position[0], position[1])[0] == None:
                validLineMoves.append((position[0], position[1]))
            elif pieceType(board, position[0], position[1])[0] == side:
                blockingPiece = True
            elif pieceType(board, position[0], position[1])[0] != side:
                #since a piece can capture an opposing piece, it can move onto 
                #the position occupied by an opposing piece 
                validLineMoves.append((position[0], position[1]))
                blockingPiece = True
    return validLineMoves    

def getAllPawnMoves(board: list, row: int, 
                    col: int, vertDirection: int) -> list:
    """
    Given a chess board, a pawn's position, and which way the pawn is headed, 
    return all moves for a pawn (including captures without an opposing piece 
    captured).
    vertDirection is 1 for black pawns and -1 for white pawns.
    """
    allPawnMoves = []
    if 0 <= row+vertDirection < len(board):
        allPawnMoves.append((row+vertDirection, col))
        if col+1 < len(board[0]):
            allPawnMoves.append((row+vertDirection, col+1))
        if col-1 >= 0:
            allPawnMoves.append((row+vertDirection, col-1))
    return allPawnMoves

def isValidPawnMove(board: list, row: int, 
                    col: int, pawnMove: tuple, opposingSide: str) -> bool:
    """
    given a pawn move, the location of a pawn, a chess board, and the opposing
    side(which side the pawn is NOT on) return whether or not a pawn can 
    move there.
    """
    if col == pawnMove[1] and \
       pieceType(board, pawnMove[0], pawnMove[1])[0] == None:
       return True
    if (col + 1 == pawnMove[1] or col - 1 == pawnMove[1]) and \
        pieceType(board, pawnMove[0], pawnMove[1])[0] == opposingSide:
        return True
    return False
    
def getValidPawnMoves(board: list, startRow: int, startCol: int) -> list:
    """
    Given a chess board represented by a 2d list and a position, return all
    possible moves for a pawn in that position
    """
    validMoves = []
    pawnSide = pieceType(board, startRow, startCol)[0]

    if pawnSide == 'white':   
        for whiteMove in getAllPawnMoves(board, startRow, startCol, -1):
            if isValidPawnMove(board, startRow, startCol, whiteMove, 'black'):
                validMoves.append(whiteMove)
    elif pawnSide == 'black': 
        for blackMove in getAllPawnMoves(board, startRow, startCol, 1):
            if isValidPawnMove(board, startRow, startCol, blackMove, 'white'):
                validMoves.append(blackMove)
    return validMoves

def getStraightLine(board: list, row: int, col: int, direction: str) -> list:
    """
    return a list of positions for a horizontal/vertical line in the specified 
    direction. Checks if a position is inside the board before adding it to the 
    output list.
    """
    positionList = []
    if direction == 'up':
        #use insert instead of append so that the positions closest to the piece
        #will be evaluated first in validLinePositions()
        for upDistance in range(row, 0, -1):
            positionList.insert(0,(row - upDistance, col))
    elif direction == 'down': 
        for downDistance in range(1, len(board) - row):
            positionList.append((row + downDistance, col))
    elif direction == 'left':
        for leftDistance in range(col, 0, -1):
            positionList.insert(0,(row, col - leftDistance))
    elif direction == 'right':
        for rightDistance in range(1, len(board[0]) - col):
            positionList.append((row, col + rightDistance))
    return positionList
                
def getStraightLines(board: list, row: int, col: int) -> list:
    """
    given a board and a position, return a list of lists with all possible
    vertical and horizontal moves.
    The list is split into moves upwards, downwards, towards the left, and 
    towards the right.
    """
    return [getStraightLine(board, row, col, 'up'), 
            getStraightLine(board, row, col, 'down'), 
            getStraightLine(board, row, col, 'left'), 
            getStraightLine(board, row, col, 'right')]

def getValidRookMoves(board: list, startRow: int, startCol: int) -> list:
    """
    Given a chess board represented by a 2d list and a position, return all
    possible moves for a rook in that position. Starts by finding all possible 
    "lines" for the chess piece to move if the board was empty and then 
    checks to see if pieces would obstruct each line. 
    """
    validMoves = []
    rookSide = pieceType(board, startRow, startCol)[0]
    rookMoves = getStraightLines(board, startRow, startCol)

    for line in rookMoves:
        validMoves.extend(validLinePositions(board, startRow, 
                                             startCol, line, rookSide))
    return validMoves


def getSingleDiagonalLine(rowDirection:int, colDirection:int, board:list, 
                          row:int, col:int) -> list:
    """
    Given a direction, the chess board, and an initial starting position, return 
    a list of positions along the specified direction until the edge of the 
    board.
    rowDirection and colDirection should be 1, 0, or -1.
    rowDirection is vertical change, while colDirection is horizontal change.
    """
    lineList = []
    dRow = rowDirection
    dCol = colDirection
    while 0 <= row+dRow < len(board) and 0 <= col+dCol < len(board[0]):
        lineList.append((row+dRow, col+dCol))
        dRow += rowDirection 
        dCol += colDirection
    return lineList

def getDiagonalLine(board: list, row: int, col: int, 
                    up: bool, right: bool) -> list:
    """
    return a list of positions for a diagonal in the specified direction
    direction is determined by the two boolean inputs (up/down, left/right).
    Checks if a position is inside the board before adding it to the 
    output list while increasing the distance by one.
    """
    positionList = []
    if up and right:
        #distance from the position to be added to the given position
        positionList.extend(getSingleDiagonalLine(1, 1, board, row, col))
    elif up and not right:
        positionList.extend(getSingleDiagonalLine(1, -1, board, row, col))
    elif not up and right:
        positionList.extend(getSingleDiagonalLine(-1, 1, board, row, col))
    elif not up and not right:
        positionList.extend(getSingleDiagonalLine(-1, -1, board, row, col))
    return positionList
                
def getDiagonals(board: list, row: int, col: int) -> list:
    """
    given a board and a position, return a list of lists with the diagonals.
    The list is split into up diagonals and 
    down diagonals and further split
    into positions higher than the position 
    and positions lower than the position.
    """
    return [getDiagonalLine(board, row, col, True, True), 
            getDiagonalLine(board, row, col, True, False), 
            getDiagonalLine(board, row, col, False, True), 
            getDiagonalLine(board, row, col, False, False)]

def getValidBishopMoves(board: list, startRow: int, startCol: int) -> list:
    """
    Given a chess board represented by a 2d list and a position, return all
    possible moves for a bishop in that position
    """
    validMoves = []
    allBishopMoves = getDiagonals(board, startRow, startCol)
    bishopSide = pieceType(board, startRow, startCol)[0]

    for line in allBishopMoves:
        validMoves.extend(validLinePositions(board, startRow, 
                                             startCol, line, bishopSide))      
    return validMoves


def getValidQueenMoves(board: list, startRow: int, startCol: int) -> list:
    """
    Given a chess board represented by a 2d list and a position, return all
    possible moves for a queen in that position
    """
    validMoves = []
    allQueenMoves = getDiagonals(board, startRow, startCol)
    allQueenMoves.extend(getStraightLines(board, startRow, startCol))
    queenSide = pieceType(board, startRow, startCol)[0]

    for line in allQueenMoves:
        validMoves.extend(validLinePositions(board, startRow, 
                                             startCol, line, queenSide))        
    return validMoves   

def getKnightPositions(board: list, row: int, col: int) -> list:
    """
    gets all positions for moving a knight in a given board
    """
    #allJumps contains all possible "jumps" the knight can do (2 moves in 1
    #cardinal direction, 1 in another)
    allJumps = [(2,1),(1,2),(-1,2),(-2, 1),(-2,-1),(-1,-2),(1,-2),(2,-1)]
    possiblePositions = []

    for move in allJumps:
        if 0 <= row+move[0] < len(board) and 0 <= col+move[1] < len(board[0]):
            possiblePositions.append((row+move[0], col+move[1]))
    return possiblePositions

def getValidKnightMoves(board: list, startRow: int, startCol: int) -> list:
    """
    Given a chess board represented by a 2d list and a position, return all
    possible moves for a knight in that position
    """
    validMoves = []
    allKnightMoves = getKnightPositions(board, startRow, startCol)
    knightSide = pieceType(board, startRow, startCol)[0]

    for move in allKnightMoves:
        if pieceType(board, move[0], move[1])[0] != knightSide:
            validMoves.append(move)
    return validMoves

def getKingPositions(board: list, row: int, col: int) -> list:
    """
    gets all positions for moving a king located at (row, col) in a given board
    """
    allMoves = [(0,1), (0,-1), (1,1), (1,0), (1,-1), (-1,1), (-1,0), (-1,-1)]
    possiblePositions = []

    for move in allMoves:
        if 0 <= row+move[0] < len(board) and 0 <= col+move[1] < len(board[0]):
            possiblePositions.append((row+move[0], col+move[1]))
    return possiblePositions

def getValidKingMoves(board: list, startRow: int, startCol: int) -> list:
    """
    Given a chess board represented by a 2d list and a position, return all
    possible moves for a king in that position
    """
    validMoves = []
    allKingMoves = getKingPositions(board, startRow, startCol)
    kingSide = pieceType(board, startRow, startCol)[0]

    for move in allKingMoves:
        if pieceType(board, move[0], move[1])[0] != kingSide:
            validMoves.append(move)
    return validMoves


def getValidChessMoves(board: list, startRow:int, startCol:int) -> list:
    """
    Given a chess board represented by a 2d list and a position, return a list 
    of tuples detailing all possible moves for the chess piece on the given 
    position. Checks the type of the piece in the given function and applies the
    correct function to obtain the valid moves.
    """
    piece = pieceType(board, startRow, startCol)[1]
    validChessMoves = []

    if piece == 'rook':
        validChessMoves = getValidRookMoves(board, startRow, startCol)
    elif piece == 'knight':
        validChessMoves = getValidKnightMoves(board, startRow, startCol)
    elif piece == 'bishop':
        validChessMoves = getValidBishopMoves(board, startRow, startCol)
    elif piece == 'queen':
        validChessMoves = getValidQueenMoves(board, startRow, startCol)
    elif piece == 'king':
        validChessMoves = getValidKingMoves(board, startRow, startCol) 
    elif piece == 'pawn':
        validChessMoves = getValidPawnMoves(board, startRow, startCol)    
    return validChessMoves

def testGetValidPawnMoves():
    print("Testing getValidPawnMoves()...", end="")
    # TODO fill in the board such that the test case passes!
    board = [
        ['♟', '♟', '♟'],
        [' ', '♙', ' '],
        [' ', ' ', ' '],
    ]
    assert(getValidPawnMoves(board, 0, 1) == [])
    assert(sorted(getValidPawnMoves(board, 0, 0)) == [(1, 0), (1, 1)])
    assert(sorted(getValidPawnMoves(board, 1, 1)) == [(0, 0), (0, 2)]) 
    print("Passed!")


def testGetValidRookMoves():
    print("Testing getValidRookMoves()...", end="")
    board = [
        [' ', ' ', ' '],
        [' ', ' ', ' '],
        [' ', '♖', '♙'],
        [' ', ' ', ' '],
    ]
    assert(sorted(getValidRookMoves(board, 2, 1)) == [(0, 1), (1, 1), (2, 0),
                                                      (3, 1)])
    print("Passed!")


def testGetValidBishopMoves():
    print("Testing getValidBishopMoves()...", end="")
    # TODO fill in the board such that the test case passes!
    board = [
        [' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' '],
        [' ', '♗', ' ', ' '],
        [' ', ' ', '♙', ' '],
    ]
    assert(sorted(getValidBishopMoves(board, 2, 1)) == [(0, 3),
                                                        (1, 0), (1, 2),
                                                        (3, 0)])
    print("Passed!")


def testGetValidQueenMoves():
    print("Testing getValidQueenMoves()...", end="")
    # TODO fill in the board such that the test case passes!
    board = [
        [' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' '],
        [' ', '♕', ' ', ' '],
        [' ', ' ', '♙', ' '],
    ]
    assert(sorted(getValidQueenMoves(board, 2, 1)) == [(0, 1), (0, 3),
                                                       (1, 0), (1, 1), (1, 2),
                                                       (2, 0), (2, 2), (2, 3),
                                                       (3, 0), (3, 1)])
    print("Passed!")


def testGetValidKnightMoves():
    print("Testing getValidKnightMoves()...", end="")
    # TODO fill in the board such that the test case passes!
    board = [
        [' ', ' ', '♖', ' '],
        [' ', ' ', ' ', ' '],
        [' ', '♘', ' ', ' '],
        [' ', ' ', ' ', ' '],
    ]
    assert(sorted(getValidKnightMoves(board, 2, 1)) == [(0, 0), (1, 3), (3, 3)])
    print("Passed!")


def testGetValidKingMoves():
    print("Testing getValidKingMoves()...", end="")
    # TODO fill in the board such that the test case passes!
    board = [
        [' ', ' ', ' '],
        [' ', '♔', ' '],
        [' ', ' ', '♘'],
    ]
    assert(sorted(getValidKingMoves(board, 1, 1)) == [(0, 0), (0, 1), (0, 2),
                                                      (1, 0), (1, 2),
                                                      (2, 0), (2, 1)])
    print("Passed!")


def testGetValidChessMoves():
    testGetValidPawnMoves()
    testGetValidRookMoves()
    testGetValidBishopMoves()
    testGetValidQueenMoves()
    testGetValidKnightMoves()
    testGetValidKingMoves()
    print("Testing getValidChessMoves()...", end="")
    # sanity check
    board = [
        ['♟', '♟', '♟'],
        [' ', '♔', ' '],
        [' ', ' ', '♙'],
    ]
    assert(getValidChessMoves(board, 0, 0) == getValidPawnMoves(board, 0, 0))
    assert(getValidChessMoves(board, 1, 1) == getValidKingMoves(board, 1, 1))
    assert(getValidChessMoves(board, 1, 0) == []) # TODO
    print("Passed!")

#################################################
# testAll and main
#################################################


def testAll():
    testGetValidChessMoves()

def main():
    testAll()


if __name__ == '__main__':
    main()
