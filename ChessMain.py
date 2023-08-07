import pygame as p
import ChessEngine

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 30
IMAGES = {}

def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color('white'))
    gs = ChessEngine.GameState()
    validMoves = gs.getAllValidMoves()
    moveMade = False
    animate = False
    loadImages()
    running = True
    sqSelected = ()
    playerClicks = []
    gameOver = False
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()
                col = location[0]//SQ_SIZE
                row = location[1]//SQ_SIZE
                if sqSelected == (row, col):
                    sqSelected = ()
                    playerClicks = []
                else:
                    sqSelected = (row, col)
                    playerClicks.append(sqSelected)
                if len(playerClicks) == 2:
                    move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                    for i in range(len(validMoves)):
                        if move == validMoves[i]:
                            gs.makeMove(validMoves[i])
                            moveMade = True
                            animate = True
                            #print(move.getChessNotation())
                            sqSelected = ()
                            playerClicks = []
                    if not moveMade:
                        playerClicks = [sqSelected]
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undoMove()
                    moveMade = True
                    animate = False
                if e.key == p.K_r:
                    gs = ChessEngine.GameState()
                    validMoves = gs.getAllValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False
        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock, gs)
            validMoves = gs.getAllValidMoves()
            moveMade = False
            animate = False

        drawGameState(screen, gs, validMoves, sqSelected)

        if gs.checkmate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen, 'Black wins by checkmate')
            else:
                drawText(screen, 'White wins by checkmate')
        elif gs.stalemate:
            gameOver = True
            drawText(screen, 'Stalemate')

        clock.tick(MAX_FPS)
        p.display.flip()

def loadImages():
    pieces = ["bR", "bN", "bB", "bQ", "bK", "bP",
              "wR", "wN", "wB", "wQ", "wK", "wP",]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))

def extraHighlight(screen, gs):
    if gs.inCheck:
        s = p.Surface((SQ_SIZE, SQ_SIZE))
        s.set_alpha(100)
        s.fill(p.Color('red'))
        if gs.whiteToMove:
            screen.blit(s, (gs.whiteKingLocation[1] * SQ_SIZE, gs.whiteKingLocation[0] * SQ_SIZE))
        else:
            screen.blit(s, (gs.blackKingLocation[1] * SQ_SIZE, gs.blackKingLocation[0] * SQ_SIZE))
    if len(gs.moveLog) != 0:
        s = p.Surface((SQ_SIZE, SQ_SIZE))
        s.set_alpha(110)
        s.fill(p.Color('yellow'))
        screen.blit(s, (gs.moveLog[-1].startCol * SQ_SIZE, gs.moveLog[-1].startRow * SQ_SIZE))
        screen.blit(s, (gs.moveLog[-1].endCol * SQ_SIZE, gs.moveLog[-1].endRow * SQ_SIZE))

def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    s = p.Surface((SQ_SIZE, SQ_SIZE))
                    s.set_alpha(80)
                    color = colors[(move.endRow + move.endCol) % 2]
                    s.fill(color)
                    if gs.board[move.endRow][move.endCol] == '--':
                        p.draw.circle(s, p.Color('black'), (SQ_SIZE / 2, SQ_SIZE / 2), SQ_SIZE / 5)
                    else:
                        p.draw.circle(s, p.Color('black'), (SQ_SIZE / 2, SQ_SIZE / 2), SQ_SIZE / 2)
                        p.draw.circle(s, color, (SQ_SIZE / 2, SQ_SIZE / 2), SQ_SIZE / 2 - 6)
                    screen.blit(s, (move.endCol*SQ_SIZE, move.endRow*SQ_SIZE))
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(110)
            s.fill(p.Color('yellow'))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))

def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen)
    highlightSquares(screen, gs, validMoves, sqSelected)
    extraHighlight(screen, gs)
    drawPieces(screen, gs.board)

def drawBoard(screen):
    global colors
    colors = [p.Color('#eeeed2'), p.Color('#769656')]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r + c) % 2]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def animateMove(move, screen, board, clock, gs):
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    frameCount = 12
    # framesPerSquare = 20
    # frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount + 1):
        r, c = (move.startRow + dR * frame / frameCount, move.startCol + dC * frame / frameCount)
        drawBoard(screen)
        drawPieces(screen, board)
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        if move.pieceCaptured != '--':
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)

def drawText(screen, text):
    font = p.font.SysFont("Helvitca", 40, True, False)
    textObject = font.render(text, 0, p.Color('Black'))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color('Gray'))
    screen.blit(textObject, textLocation.move(2, 2))

if __name__ == "__main__":
    main()