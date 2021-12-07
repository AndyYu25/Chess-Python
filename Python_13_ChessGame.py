import copy
import decimal
import string
import random

class ChessGame(object):
    def __init__(self, board: list, playerSide: str = 'white', 
                 playerCount: str = 2)->None:
        """initializes the class variables"""
        self.originalBoard = board #stores the starting position
        self.board = board
        self.takenBlackPieces = []
        self.takenWhitePieces = []
        self.currentPlayer = "white"
        #next 2 variables are 2d lists storing the initial position of a piece, 
        #the position where the piece moved to, the piece type, 
        #and the captured piece
        #example: white pawn at (1, 0) takes black knight at (2, 1)
        #movesMade entry: [1, 0, 2, 1, '♟', '♘]
        self.moveHistory = [] #stores the entire move history of the game
        self.undoneMoveHistory = [] #stores all undone moves
    def getOriginalBoard(self)->list: 
        """returns the original board at the start of the game"""
        return self.originalBoard
    def getBoard(self)->list:
        '''returns the current board state''' 
        return self.board
    def getWhiteTaken(self)->list: 
        '''returns the list of pieces black has captured'''
        return self.takenWhitePieces
    def getBlackTaken(self)->list: 
        '''returns the list of pieces white has captured'''
        return self.takenBlackPieces
    def getTurn(self)->str:
        '''returns whose turn it is'''
        return self.currentPlayer
    def switchTurns(self)->None:
        """switches the current player to the other player"""
        if self.currentPlayer == "white": self.currentPlayer = "black"
        elif self.currentPlayer == "black": self.currentPlayer = "white"
    def pieceType(self, board: list, row: int, col: int) -> tuple:
        '''
        Given a board and the specified location, 
        return a tuple consisting of which side 
        the piece is on and which piece it is. 
        Returns None if the location has no piece.
        '''
        if row >= len(board) or col >= len(board[0]): return (0, 0)
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
    def validLinePositions(self, board:list, row:int, col:int, 
                        line:list, side: str) -> list:
        """
        given the position of a piece and a list of positions (in tuples) 
        it can go to on a single line (e.g. a list of all positions that a 
        rook can go to in one move if it can only move upwards), return a list 
        of possible moves on that list that are not blocked by another piece. 
        Checks by using a boolean to determine if a piece blocks the remainder 
        of the line.
        """
        validLineMoves = []
        blockingPiece = False

        for position in line:
            if blockingPiece == False:
                if self.pieceType(board, position[0], position[1])[0] == None:
                    validLineMoves.append((position[0], position[1]))
                elif self.pieceType(board, position[0], position[1])[0] == side:
                    blockingPiece = True
                elif self.pieceType(board, position[0], position[1])[0] != side:
                    #since a piece can capture an opposing piece, it can move 
                    # onto the position occupied by an opposing piece 
                    validLineMoves.append((position[0], position[1]))
                    blockingPiece = True
        return validLineMoves    
    def getAllPawnMoves(self, board: list, row: int, 
                        col: int, vertDirection: int) -> list:
        """
        Given a chess board, a pawn's position, and which way the pawn is 
        headed, return all moves for a pawn (including captures without an 
        opposing piece captured).
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
    def isValidPawnMove(self, board: list, row: int, 
                        col: int, pawnMove: tuple, opposingSide: str) -> bool:
        """
        given a pawn move, the location of a pawn, a chess board, and the 
        opposing side(which side the pawn is NOT on) return whether or not a 
        pawn can move there.
        """
        if col == pawnMove[1] and \
        self.pieceType(board, pawnMove[0], pawnMove[1])[0] == None:
            return True
        if (col + 1 == pawnMove[1] or col - 1 == pawnMove[1]) and \
            self.pieceType(board, pawnMove[0], pawnMove[1])[0] == opposingSide:
            return True
        return False      
    def getValidPawnMoves(self, board:list, startRow:int, startCol:int) -> list:
        """
        Given a chess board represented by a 2d list and a position, return all
        possible moves for a pawn in that position
        """
        validMoves = []
        pawnSide = self.pieceType(board, startRow, startCol)[0]

        if pawnSide == 'white':   
            for whiteMove in self.getAllPawnMoves(board,startRow,startCol, -1):
                if self.isValidPawnMove(board,startRow,startCol,
                                        whiteMove,'black'):
                    validMoves.append(whiteMove)
        elif pawnSide == 'black': 
            for blackMove in self.getAllPawnMoves(board, startRow, startCol, 1):
                if self.isValidPawnMove(board, startRow, startCol, 
                                        blackMove, 'white'):
                    validMoves.append(blackMove)
        return validMoves
    def getStraightLine(self,board:list,row:int,col:int,direction:str)->list:
        """
        return a list of positions for a horizontal/vertical line in the 
        specified direction. Checks if a position is inside the board before
        adding it to the output list.
        """
        positionList = []
        if direction == 'up':
            #use insert instead of append so that the positions closest to the
            #piece will be evaluated first in validLinePositions()
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
    def getStraightLines(self, board: list, row: int, col: int) -> list:
        """
        given a board and a position, return a list of lists with all possible
        vertical and horizontal moves.
        The list is split into moves upwards, downwards, towards the left, and 
        towards the right.
        """
        return [self.getStraightLine(board, row, col, 'up'), 
                self.getStraightLine(board, row, col, 'down'), 
                self.getStraightLine(board, row, col, 'left'), 
                self.getStraightLine(board, row, col, 'right')]
    def getValidRookMoves(self, board:list, startRow:int, startCol:int) -> list:
        """
        Given a chess board represented by a 2d list and a position, return all
        possible moves for a rook in that position. Starts by finding all 
        possible "lines" for the chess piece to move if the board was empty and 
        then checks to see if pieces would obstruct each line. 
        """
        validMoves = []
        rookSide = self.pieceType(board, startRow, startCol)[0]
        rookMoves = self.getStraightLines(board, startRow, startCol)

        for line in rookMoves:
            validMoves.extend(self.validLinePositions(board, startRow, 
                                                startCol, line, rookSide))
        return validMoves
    def getSingleDiagonalLine(self, rowDirection:int, colDirection:int, 
                              board:list, row:int, col:int) -> list:
        """
        Given a direction, the chess board, and an initial starting position, 
        return a list of positions along the specified direction until the 
        edge of the board.
        rowDirection and colDirection should be 1, 0, or -1.
        rowDirection is vertical change, while colDirection is horizontal change
        """
        lineList = []
        dRow = rowDirection
        dCol = colDirection
        while 0 <= row+dRow < len(board) and 0 <= col+dCol < len(board[0]):
            lineList.append((row+dRow, col+dCol))
            dRow += rowDirection 
            dCol += colDirection
        return lineList
    def getDiagonalLine(self, board: list, row: int, col: int, 
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
            positionList.extend(self.getSingleDiagonalLine(1,1,board,row,col))
        elif up and not right:
            positionList.extend(self.getSingleDiagonalLine(1,-1, board,row,col))
        elif not up and right:
            positionList.extend(self.getSingleDiagonalLine(-1,1,board,row,col))
        elif not up and not right:
            positionList.extend(self.getSingleDiagonalLine(-1,-1,board,row,col))
        return positionList                   
    def getDiagonals(self, board: list, row: int, col: int) -> list:
        """
        given a board and a position, return a list of lists with the diagonals.
        The list is split into up diagonals and 
        down diagonals and further split
        into positions higher than the position 
        and positions lower than the position.
        """
        return [self.getDiagonalLine(board, row, col, True, True), 
                self.getDiagonalLine(board, row, col, True, False), 
                self.getDiagonalLine(board, row, col, False, True), 
                self.getDiagonalLine(board, row, col, False, False)]
    def getValidBishopMoves(self, board:list, startRow:int, startCol:int)->list:
        """
        Given a chess board represented by a 2d list and a position, return all
        possible moves for a bishop in that position
        """
        validMoves = []
        allBishopMoves = self.getDiagonals(board, startRow, startCol)
        bishopSide = self.pieceType(board, startRow, startCol)[0]

        for line in allBishopMoves:
            validMoves.extend(self.validLinePositions(board, startRow, 
                                                startCol, line, bishopSide))      
        return validMoves
    def getValidQueenMoves(self, board: list, 
                           startRow: int, startCol: int) -> list:
        """
        Given a chess board represented by a 2d list and a position, return all
        possible moves for a queen in that position
        """
        validMoves = []
        allQueenMoves = self.getDiagonals(board, startRow, startCol)
        allQueenMoves.extend(self.getStraightLines(board, startRow, startCol))
        queenSide = self.pieceType(board, startRow, startCol)[0]

        for line in allQueenMoves:
            validMoves.extend(self.validLinePositions(board, startRow, 
                                                startCol, line, queenSide))        
        return validMoves   
    def getKnightPositions(self, board: list, row: int, col: int) -> list:
        """
        gets all positions for moving a knight in a given board
        """
        #allJumps contains all possible "jumps" the knight can do (2 moves in 1
        #cardinal direction, 1 in another)
        allJumps = [(2,1),(1,2),(-1,2),(-2, 1),(-2,-1),(-1,-2),(1,-2),(2,-1)]
        possiblePositions = []

        for move in allJumps:
            if 0 <= row+move[0] < len(board) and \
                0 <= col+move[1] < len(board[0]):
                possiblePositions.append((row+move[0], col+move[1]))
        return possiblePositions
    def getValidKnightMoves(self, board: list, startRow: int, 
                            startCol: int) -> list:
        """
        Given a chess board represented by a 2d list and a position, return all
        possible moves for a knight in that position
        """
        validMoves = []
        allKnightMoves = self.getKnightPositions(board, startRow, startCol)
        knightSide = self.pieceType(board, startRow, startCol)[0]

        for move in allKnightMoves:
            if self.pieceType(board, move[0], move[1])[0] != knightSide:
                validMoves.append(move)
        return validMoves
    def getKingPositions(self, board: list, row: int, col: int) -> list:
        """
        gets all positions for moving a king located at (row, col)
        in a given board
        """
        allMoves=[(0,1), (0,-1), (1,1), (1,0), (1,-1), (-1,1), (-1,0), (-1,-1)]
        possiblePositions = []

        for move in allMoves:
            if 0 <= row+move[0] < len(board) and \
               0 <= col+move[1] < len(board[0]):
                possiblePositions.append((row+move[0], col+move[1]))
        return possiblePositions
    def getValidKingMoves(self, board: list, startRow: int, 
                          startCol: int) -> list:
        """
        Given a chess board represented by a 2d list and a position, return all
        possible moves for a king in that position
        """
        validMoves = []
        allKingMoves = self.getKingPositions(board, startRow, startCol)
        kingSide = self.pieceType(board, startRow, startCol)[0]

        for move in allKingMoves:
            if self.pieceType(board, move[0], move[1])[0] != kingSide:
                validMoves.append(move)
        return validMoves
    def getValidChessMoves(self, startRow:int, startCol:int) -> list:
        """
        Given a chess board represented by a 2d list and a position, 
        return a list of tuples detailing all possible moves for the chess piece 
        on the given position. Checks the type of the piece in the given 
        function and applies the correct function to obtain the valid moves.
        """
        piece = self.pieceType(self.board, startRow, startCol)[1]
        validChessMoves = []

        if piece == 'rook': validChessMoves = self.getValidRookMoves(
                                                self.board, startRow, startCol)
        elif piece == 'knight': validChessMoves = self.getValidKnightMoves(
                                                self.board, startRow, startCol)
        elif piece == 'bishop': validChessMoves = self.getValidBishopMoves(
                                                self.board, startRow, startCol)
        elif piece == 'queen': validChessMoves = self.getValidQueenMoves(
                                                self.board, startRow, startCol)
        elif piece == 'king': validChessMoves = self.getValidKingMoves(
                                                self.board, startRow, startCol) 
        elif piece == 'pawn': validChessMoves = self.getValidPawnMoves(
                                                self.board, startRow, startCol)    
        return validChessMoves
    def isValidMove(self, fromRow:int, fromCol:int, toRow:int, 
                    toCol:int)->bool:
        """give a start and end position, returns whether or not it is legal 
        for a piece on the start position to move to the end position"""
        if fromRow > len(board)-1 or toRow > len(board)-1:
            return False
        if fromCol > len(board[0])-1 or toCol > len(board[0])-1:
            return False
        allValidChessMoves = self.getValidChessMoves(fromRow, fromCol)
        return (toRow, toCol) in allValidChessMoves
    def makeMove(self, fromRow:int, fromCol:int, toRow:int, toCol:int)->bool:
        """moves pieces given a start position and end position.
        returns whether or not the move was made legally."""
        if self.isValidMove(fromRow, fromCol, toRow, toCol):
            movingPiece = self.pieceType(self.board, fromRow, fromCol)
            if movingPiece[0] != self.getTurn(): return False
            movingPieceImage = self.board[fromRow][fromCol]
            capturedPiece = self.pieceType(self.board, toRow, toCol)
            self.moveHistory.append([fromRow, fromCol, toRow, toCol, 
                        self.board[fromRow][fromCol], self.board[toRow][toCol]])
            self.board[fromRow][fromCol] = ' '
            if capturedPiece != (None, None):
                if capturedPiece[0]==movingPiece[0]: 
                    self.takenWhitePieces.append(self.board[toRow][toCol])
                else: self.takenBlackPieces.append(self.board[toRow][toCol])
            self.board[toRow][toCol] = movingPieceImage
            self.switchTurns()
            self.undoneMoveHistory = [] #resets undoneMoveHistory
            return True
        return False
    def checkMovesAvailable(self,color:str)->bool:
        """checks if one given side can move pieces other than the king."""
        for row in range(len(self.board)):
            for col in range(len(self.board[0])):
                if color == 'black' and self.board[row][col] in '♝♞♜♟♛':
                    #condition checks if the piece has any valid moves
                    if len(self.getValidChessMoves(row, col)) > 0:
                        return True
                elif color == 'white' and self.board[row][col] in '♙♖♘♗♕':
                    if len(self.getValidChessMoves(row, col)) > 0:
                        return True
        return False
    def checkGameOver(self)->tuple:
        """checks if game is over and returns if it is over and 
        who won in a tuple"""
        if not any('♔' in row for row in self.board) or \
           not self.checkMovesAvailable('white'):
            return (True, "black")
        elif not any('♚' in row for row in self.board) or \
           not self.checkMovesAvailable('black'):
            return (True, "white")
        return (False, "none")
    def undoMove(self)->bool:
        """undos a chess move and returns whether or not a move was
        successfully undone"""
        if len(self.moveHistory) > 0:
            lastMove = self.moveHistory.pop()
            self.undoneMoveHistory.append(lastMove)
            #undos move by switching pieces
            self.board[lastMove[0]][lastMove[1]] = self.board[
                                                    lastMove[2]][lastMove[3]]
            self.board[lastMove[2]][lastMove[3]] = lastMove[5]
            if lastMove[5] != ' ': #modifies the taken pieces lists
                if lastMove[5] in self.takenBlackPieces: 
                    self.takenBlackPieces.remove(lastMove[5])
                elif lastMove[5] in self.takenWhitePieces:
                    self.takenWhitePieces.remove(lastMove[5]) 
            self.switchTurns()
            return True
        return False
    def redoMove(self)->bool:
        """
        redos an undone chess move. 
        """ 
        if len(self.undoneMoveHistory) > 0:
            lastMove = self.undoneMoveHistory.pop()
            self.moveHistory.append(lastMove)
            #moves pices by swapping positions on the board
            self.board[lastMove[0]][lastMove[1]] = ' '
            self.board[lastMove[2]][lastMove[3]] = lastMove[4] 
            if lastMove[5] != ' ': #modifies the taken pieces lists
                if lastMove[5] in '♛♚♝♞♜♟': 
                    self.takenBlackPieces.append(lastMove[5])
                elif lastMove[5] in '♙♖♘♗♕♔':
                    self.takenWhitePieces.append(lastMove[5]) 
            self.switchTurns()
            return True
        return False
    #random move implementation
    def randomEngine(self,color:str)->None:
        """randomly moves a piece of the given color"""
        pieceMoved = False
        moveChance = 0.10 # chance that the engine will move a piece
        while pieceMoved == False:
            for row in range(len(self.board)):
                for col in range(len(self.board[0])):
                    if self.pieceType(self.board, row, col)[0] == color and \
                       random.random() < moveChance:
                        possibleMoves = self.getValidChessMoves(row, col)
                        if len(possibleMoves) > 0:
                            randomMove = possibleMoves[
                                        random.randrange(len(possibleMoves))]
                            self.makeMove(row, col, randomMove[0],randomMove[1])
                            pieceMoved = True
    #minimax implementation
    def makeAnyMove(self,fromRow:int, fromCol:int, toRow:int, toCol:int)->None:
        """makes a move from the given square to the given destination square
         without checking if it is legal."""
        #moves pices by swapping positions on the board
        movedPiece = self.board[fromRow][fromCol]
        takenPiece = self.board[toRow][toCol]
        self.board[fromRow][fromCol] = ' '
        self.board[toRow][toCol] = movedPiece
        if takenPiece != ' ': #modifies the taken pieces lists
            if takenPiece in '♛♚♝♞♜♟': 
                self.takenBlackPieces.append(takenPiece)
            elif takenPiece in '♙♖♘♗♕♔':
                self.takenWhitePieces.append(takenPiece) 
        self.moveHistory.append([fromRow, fromCol, toRow, toCol, 
                    movedPiece, takenPiece])
        self.switchTurns()
    def pieceWorth(self, piece:str)->int:
        """Give a piece as a string, returns the value of the piece
        Assumes traditional value of pieces. (queen is 
        9 points, rooks are 5 points, knights/bishops are 3 points, pawns are 1
        point). Since kings are a win condition, they have an extremely 
        high value"""
        pieceValue = 0
        if piece in '♜♖':  pieceValue = 5
        elif piece in '♞♘♗♝':  pieceValue = 3
        elif piece in '♕♛':  pieceValue = 9
        elif piece in '♔♚':  pieceValue = 9999 #king is a win condition
        elif piece in '♙♟':  pieceValue = 1
        return pieceValue
    def materialEvaluation(self, color:str)->int:
        """returns the material count of one given side (the value of the pieces
        remaining on the board). """
        totalPieceValue = 39#A single side starts with 39 points worth of pieces
        if color == 'white':
            #subtract captured piece values from the total piece value
            for piece in self.getWhiteTaken():
                totalPieceValue -= self.pieceWorth(piece)
        elif color == 'black':
            for piece in self.getBlackTaken():
                totalPieceValue -= self.pieceWorth(piece)   
        return totalPieceValue    
    def getBoardCenter(self)->list:
        """returns the center of the board, which is a list of either 1,2,or 4 
        positions. 1 position is returned if both the number of rows and columns 
        are odd, 2 positions are returned if either the number of rows or 
        columns are even, and 4 positions are returned if both are even.
        """
        middleRows, middleCols = [], []
        rowCount,colCount = len(self.board), len(self.board[0])
        if rowCount % 2 == 1:
            middleRows.append(rowCount//2)
        else:
            middleRows.extend([rowCount//2, rowCount//2 - 1])
        if colCount % 2 == 1:
            middleCols.append(colCount//2)
        else:
            middleCols.extend([colCount//2, colCount//2 - 1])
        middlePositions=[(row, col) for row in middleRows for col in middleCols]
        return middlePositions
    def getBoardEdges(self)->list:
        """returns list of squares adjacent to the center of the board"""
        edgeRows,edgeCols= [],[]
        rowCount,colCount = len(self.board), len(self.board[0])
        if rowCount % 2 == 1:
            edgeRows.extend([rowCount//2+1,rowCount//2-1])
        else:
            edgeRows.extend([rowCount//2+1, rowCount//2-2])
        if colCount % 2 == 1:
            edgeCols.extend([colCount//2+1,colCount//2-1])
        else:
            edgeCols.extend([colCount//2+1, colCount//2-2])
        edgePositions=[]
        for row in range(min(edgeRows), max(edgeRows)+1):
            for col in range(min(edgeCols), max(edgeCols)+1):
                edgePositions.append((row,col))
        for item in self.getBoardCenter(): #removes positions in the center
            if item in edgePositions:
                edgePositions.remove(item)
        return edgePositions
    def boardEvaluation(self)->float:
        """evaluates a given board by analyzing the material difference
        and control of the center. Assumes normal chess starting 
        position and the traditional value of pieces """
        score = self.materialEvaluation('white')
        score -= self.materialEvaluation('black')
        edgeScore = 0.1 #advantage of having a piece close to the center
        centerScore = 0.3 #advantage of having a piece in the center
        for row in range(len(self.board)): #loop evaluates positional advantage
            for col in range(len(self.board[0])):
                if self.pieceType(self.board, row, col)[0] == 'white':
                    if (row,col) in self.getBoardEdges(): score += edgeScore
                    elif (row,col) in self.getBoardCenter(): score+=centerScore
                elif self.pieceType(self.board, row, col)[0] == 'black':
                    if (row,col) in self.getBoardEdges(): score -= edgeScore
                    elif (row,col) in self.getBoardCenter(): score-=centerScore
        return score
    def createNode(self, parentIndex:int, allMoves:list,moveIndex:int)->tuple:
        """
        given a parent board, the list of moves that can be made, returns 
        a tuple consisting of the index of the parent, the score, and the move 
        made. 
        """
        nodeMove = allMoves[moveIndex]
        self.makeMove(nodeMove[0][0],nodeMove[0][1],
                      nodeMove[1][0],nodeMove[1][1])
        nodeScore = self.boardEvaluation()#evaluates the board after the move
        nodeMoveInfo = self.moveHistory[-1]#extracts the move info so that 
        #the entire board does not need to be replicated
        self.undoMove() #undos move to reset board
        return (parentIndex, nodeScore, nodeMoveInfo) 
    def getAllTurnMoves(self, position:list)->list:
        """returns a list of all possible moves in the form of a tuple 
        consisting of two coordinates"""
        allPossibleMoves = []
        for row in range(len(position)): # gets all possible moves for the turn
            for col in range(row):
                currentPiece = self.pieceType(position, row, col)
                if self.getTurn() == currentPiece[0]:
                    for pieceMove in self.getValidChessMoves(row,col):
                        allPossibleMoves.append(((row, col), pieceMove))
        return allPossibleMoves
    def createBranches(self,rootBoard:list,rootIndex:int)->list:
        """creates a tree of all possible moves with depth of 1 ply starting
        with the given board as the 'root'. root index is the index of the
        branch 'root' in the larger tree"""
        positionTree = [[], []]
        positionTree[0] = (rootBoard, 0, None)
        branchingMoves = self.getAllTurnMoves(rootBoard)
        for move in range(len(branchingMoves)): #iterates through all moves
            positionTree[1].append(self.createNode(rootIndex,
                                                   branchingMoves,move)) 
        return positionTree[1] 
    def createMoveTree(self, color:str, ply:int = 3)->None:
        """generates a tree of moves ply deep. Only works with ply = 1
        """
        moveTree = [(self.getBoard(), 0, None)] #initializes tree & 1st ply
        moveTree.append(self.createBranches(self.getBoard(), 0))
        self.currentPlayer = color
        for depth in range(ply):#creates tree up until it is ply deep
            moveTree.append([])#adds another ply
            for positions in moveTree[depth+1]:
                fromRow,fromCol,toRow,toCol = positions[-1][0:4]
                originalBoard = self.getBoard()
                self.makeAnyMove(fromRow,fromCol,toRow,toCol)
                branchBoard = self.getBoard()
                #self.undoMove() #resets board to past state
                moveTree[depth+2].extend(self.createBranches(branchBoard,
                                         moveTree[depth+1].index(positions)))
            self.switchTurns()
        return moveTree

    def onePlyEngine(self, color:str, ply:int = 3)->None:
        """A naive chess engine that generates all possible moves up until the
        given ply, finds the maximum value, and chooses the move is the parent
        node of the highest-scoring board position. Only works with ply = 1.
        """
        highestBoardScore = 0
        bestMove = []
        engineMoveTree = self.createMoveTree(color, ply)
        print(engineMoveTree)
        for i in self.getBoard():
            print(i)
        moveMade = False
        while moveMade == False:
            if color == self.getTurn():
                for possibleMove in engineMoveTree[1]:
                    if possibleMove[1] > highestBoardScore and color == 'white':
                        highestBoardScore = possibleMove[1]
                        bestMove = possibleMove[2]
                    if possibleMove[1] < highestBoardScore and color == 'black':
                        highestBoardScore = possibleMove[1]
                        bestMove = possibleMove[2]
                fromRow,fromCol,toRow,toCol = bestMove[0:4]
                print(bestMove)
                if self.makeMove(fromRow,fromCol,toRow,toCol) == True: break
            else: engineMoveTree[1].remove(bestMove)
        print(bestMove)
        #self.board = self.getOriginalBoard()


def isValidInput(L:list, board:list)->bool:
    """checks if all inputs are valid for the game.makeMove() method. 
    Takes in a list and outputs whether the variables are integers, whether 
    the inputs are within the dimensions of the chass board"""
    inputNum = 4
    for index in range(len(L)):
        if not L[index] in string.digits: return False
        if index % 2 == 0 and int(L[index]) > len(board)-1: return False
        elif index % 2 == 1 and int(L[index]) > len(board[0])-1: return False
    return len(L) == inputNum

def convertInput(L:list)->None:
    """Destructively converts elements in a list into integers. 
    Assumes isValidInput(L) is True."""
    for index in range(len(L)):
        L[index] = int(L[index])

def printChessBoard(chessBoard:list)->None:
    """given a 2D list, print all rows with line breaks for readability"""
    for row in chessBoard:
        print(row)

def choosePlayer(humanPlayers:int)->str:
    """allows players to choose which side they play on. Choice does not matter
    if there are 2 human players"""
    if int(humanPlayers) == 2:
        return "white"
    elif int(humanPlayers) == 0:
        return "none"
    playerSide = ''
    while not(playerSide == "black" or playerSide == "white"):
        playerSide = input("Choose either black or white to play as: ")
        if not(playerSide == "black" or playerSide == "white"):
            print("Invalid Input." + 
                  " Please type 'black' or 'white' in the console.")
    return playerSide

def determineInput(game:ChessGame,inputStr:str, color:str)->bool:
    """determines which action to take given an input. Returns nothing"""
    if inputStr == 'u': game.undoMove()
    elif inputStr == 'r': game.redoMove()
    elif inputStr == 'f': 
        print(color, "forfeited")
        return True
    elif inputStr == 'p': print(game.getBlackTaken(), game.getWhiteTaken())
    elif inputStr =='': print("Invalid input, genius.")
    else:
        moveInputs = inputStr.split(", ")
        if isValidInput(moveInputs,game.getBoard()):
            convertInput(moveInputs)
            moveMade = game.makeMove(moveInputs[0],moveInputs[1],
                                    moveInputs[2], moveInputs[3])
            if not moveMade:
                print("Move is not legal, genius.")
        else: print("Invalid input, genius.")
    return False
def computerMove(game:ChessGame,color:str,engineType:str)->None:
    """chooses which chess engine to run"""
    if engineType == 'random':
        game.randomEngine(color)
        print(color + ' has made a move')
    elif engineType == 'oneply':
        game.onePlyEngine(color)
        print(color + ' has made a move')
def chooseEngine(humanPlayers:str)->str:
    """allows the user to choose a chess engine to play against if there are
    less than 2 human players"""
    if int(humanPlayers) >= 2:
        return None
    engineInput = ''
    while not(engineInput== "random" or engineInput == "oneply"):
        engineInput = input("Choose a computer engine to play against"+
                            "(type random or oneply): ")
        if engineInput == 'random':
            print("You have chosen to play against the Random Engine.")
        elif engineInput == 'oneply':
            print("You have chosen to play against the One-Ply Engine.")
        else:
            print("Invalid Input. Please read the instructions thoroughly.")
    return engineInput

def checkColor(game: ChessGame, prevColor:str)->str:
    """checks if the last iteration's turn is the same as the current iteration
    """
    if prevColor == game.getTurn():
        game.switchTurns()
        return game.getTurn()
    else:
        return game.getTurn()
def runChess(board:list)->None:
    """given a starting board, start a simplified chess game on the console"""
    winner, humanPlayers = "none", input("How Many Players? Type an integer: ")
    chessEngine = chooseEngine(humanPlayers)
    humanPlayerSide = choosePlayer(humanPlayers)
    game = ChessGame(board, humanPlayerSide, humanPlayers)
    color = 'black'
    while winner == "none":
        printChessBoard(game.getBoard())
        prevColor = color  
        color = checkColor(game, prevColor)
        if int(humanPlayers) == 0: computerMove(game,color,chessEngine)
        elif int(humanPlayers) == 1 and color != humanPlayerSide:
            computerMove(game,color,chessEngine)
        else:  
            move = input(f"What does {color} want to do? ")   
            if determineInput(game, move, color):
                game.switchTurns()
                winner = game.getTurn()
                break
        winner = game.checkGameOver()[1]  
    print(winner, "won")

board = [
        ['♜','♞','♝','♛','♚','♝','♞','♜'],
        ['♟','♟','♟','♟','♟','♟','♟','♟'],
        [' ']*8,
        [' ']*8,
        [' ']*8,
        ['♙','♙','♙','♙','♙','♙','♙','♙'],
        ['♖','♘','♗','♕','♔','♗','♘','♖']
        ]

runChess(board)
