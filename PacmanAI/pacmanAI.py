import pygame
import sys
import itertools
import heapq

pygame.init()

black = (0, 0, 0)
white = (255, 255, 255)
screenHeight = 600
screenWeight = 600
cellSize = 30

gameFrame = pygame.display.set_mode((screenWeight, screenHeight))
pygame.display.set_caption("PacManAI")
fontOfMessages = pygame.font.Font(None, 70)

pacmanIcon = pygame.image.load("pacman.png")
wallIcon = pygame.image.load("brick-wall.png")
coinIcon = pygame.image.load("dollar.png")

pacmanIcon = pygame.transform.scale(pacmanIcon, (cellSize, cellSize))
wallIcon = pygame.transform.scale(wallIcon, (cellSize, cellSize))
coinIcon = pygame.transform.scale(coinIcon, (cellSize, cellSize))

maze = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 2, 1],
    [1, 0, 1, 2, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1],
    [1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1],
    [1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 2, 1, 0, 1],
    [1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1],
    [1, 2, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]

pacmanX = 1
pacmanY = 1

directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def aStarAlgorithm(maze, start, target):
    openSet = []
    heapq.heappush(openSet, (0, start))
    cameFrom = {}
    gScore = {start: 0}
    fScore = {start: heuristic(start, target)}

    while openSet:
        _, current = heapq.heappop(openSet)

        if current == target:
            path = []
            while current in cameFrom:
                path.append(current)
                current = cameFrom[current]
            return path[::-1]

        for dx, dy in directions:
            neighbor = (current[0] + dx, current[1] + dy)
            if 0 <= neighbor[0] < len(maze) and 0 <= neighbor[1] < len(maze[0]):
                if maze[neighbor[0]][neighbor[1]] != 1:
                    tentativegScore = gScore[current] + 1
                    if tentativegScore < gScore.get(neighbor, float('inf')):
                        cameFrom[neighbor] = current
                        gScore[neighbor] = tentativegScore
                        fScore[neighbor] = tentativegScore + heuristic(neighbor, target)
                        heapq.heappush(openSet, (fScore[neighbor], neighbor))
    return []

def coinLocations():
    coins = []
    for row in range(len(maze)):
        for col in range(len(maze[row])):
            if maze[row][col] == 2:
                coins.append((row, col))
    return coins

def shortestPath(maze, start, coins):
    minPath = None
    minDistance = float('inf')
    for perm in itertools.permutations(coins):
        totalDistance = 0
        pacmanLocation = start
        for target in perm:
            totalDistance += len(aStarAlgorithm(maze, pacmanLocation, target))
            pacmanLocation = target

        if totalDistance < minDistance:
            minDistance = totalDistance
            minPath = perm
    return minPath

clock = pygame.time.Clock()
isGameOver = False
path = []
coinSequence = []
stepCount = 0  
score = 10000 

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    if not isGameOver:
        if not path:
            coins = coinLocations()
            if coins:
                if not coinSequence:
                    coinSequence = shortestPath(maze, (pacmanY, pacmanX), coins)
                target = coinSequence[0]
                path = aStarAlgorithm(maze, (pacmanY, pacmanX), target)
                coinSequence = coinSequence[1:]
            else:
                isGameOver = True
        else:
            nextStep = path.pop(0)
            pacmanY, pacmanX = nextStep
            stepCount += 1  

        if maze[pacmanY][pacmanX] == 2:
            maze[pacmanY][pacmanX] = 0

        score = max(10000 - stepCount * 10, 0)  

    gameFrame.fill(black)

    for row in range(len(maze)):
        for col in range(len(maze[row])):
            x = col * cellSize
            y = row * cellSize

            if maze[row][col] == 1:
                gameFrame.blit(wallIcon, (x, y))
            elif maze[row][col] == 2:
                gameFrame.blit(coinIcon, (x, y))

    gameFrame.blit(pacmanIcon, (pacmanX * cellSize, pacmanY * cellSize))

    if isGameOver:
        messageText = fontOfMessages.render("GAME OVER!", True, white)
        scoreText = fontOfMessages.render(f"Score: {score}", True, white)
        gameFrame.blit(
            messageText,
            ((screenWeight - messageText.get_width()) // 2, (screenHeight - messageText.get_height()) // 2),
        )
        gameFrame.blit(
            scoreText,
            ((screenWeight - scoreText.get_width()) // 2, (screenHeight + messageText.get_height()) // 2),
        )

    pygame.display.flip()
    clock.tick(10)
