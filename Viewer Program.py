from tkinter import Tk, Canvas, Frame, BOTH, W
from tkinter import *
from tkinter.font import Font
import os
import time

#coordinate letters. In some sgf files, [tt] is used for "pass". Since we aren't annotating the game, we can just ignore those.
Q = {'a':0,'b':1,'c':2,'d':3,'e':4,'f':5,'g':6,'h':7,'i':8,'j':9,'k':10,'l':11,'m':12,'n':13,'o':14,'p':15,'q':16,'r':17,'s':18}#,'t':19}
goboard   = [
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
                ]


#-1 will be white, 1 will be black, 0 will be empty

basePath = os.sys.path[0] + "\\badukmovies-pro-collection"



#----------------- SCAN FOR SGF FILES
#if first scan, navigate through root, get first file, keep path record
#subsequent scans, search through to recorded path, then proceed and grab next
#if user requests special path, replace current path with special path

#currentPath #stores the full path to the file, not including the file name
#currentFile #stores the full path to the file, including the file name
#lastFound   #is the current path in search the most recently opened path?

#try reading the last opened game, so we can pick up where we left off.
#if the cache file doesn't exist, leave it blank and we'll create it later.
try:
    with open(basePath + "\\Last_Game.txt", 'r') as file:
        currentFile = file.read()
        currentPath = ""
        for j in currentFile.split("\\")[:-1]:
            currentPath += j + "\\"
        currentPath = currentPath[:-1]
        lastFound = False
        file.close()
except:
    currentPath = "" 
    currentFile = "" 
    lastFound = True  


def browsepath(startpath):
    global currentPath
    global currentFile
    global lastFound
    global basePath
    #print("-----------------")
    #print(str(lastFound) + ": current path: " + currentPath)

    #walk through files until you find the one which was most recently opened. Then open the next one.    
    for root, dirs, files in os.walk(startpath):
        for name in files:
            if lastFound: #runs immediately the first time, and subsequently after finding the current path
                if name.lower().endswith(".sgf"):
                    currentPath = str(root)
                    currentFile = currentPath + "\\" + str(name)
                    lastFound = False
                    #print("opening: " + currentFile)
                    with open(basePath + "\\Last_Game.txt", 'w') as file:
                        file.write(currentFile)
                        file.close()
                    #print("-----------------")
                    return
            else:
                #print("name: " + name)
                #print("currentFile: " + currentFile)
                #print(name == currentFile)
                #print("dirs: " + dirs)
                if (currentPath == root) and (currentFile == currentPath + "\\" + name):
                    #print( "root: " + str(root))
                    lastFound = True
   # print("-----------------")

#----------------- INTERPRET SFG FILES

#  Collection = GameTree { GameTree }
#  GameTree   = "(" Sequence { GameTree } ")"
#  Sequence   = Node { Node }
#  Node       = ";" { Property }
#  Property   = PropIdent PropValue { PropValue }
#  PropIdent  = UcLetter { UcLetter }
#  PropValue  = "[" CValueType "]"
#  CValueType = (ValueType | Compose)
#  ValueType  = (None | Number | Real | Double | Color | SimpleText |
#		Text | Point  | Move | Stone)

#two upper case letters per property identifier
#do not rely on the order of properties or property values
#be sure to add code to skip unknown properties (and maybe issue a warning)

#properties are...
#- move (focused on the move made, not on the position arrived at by the move. may not be mixed with setup properties)
#- setup (focused on what's happening at a position. may not be mixed with moved properties)
#- root (may only appear in root nodes, not in parenthesized nodes)
#- game-info (sometimes multiple games are merged into a tree, and this info may appear at the divergence point for a unique game. Only one of these may appear per tree)

#a property may be set to "inherit", which causes it to affect all subsequent nodes

#in text, there are no tabs. Linebreaks with \ are escaped (converted to "")

#rectangles of coordinate points can be compressed by specifying top-left and bottom-right

#coordinates are lowercase lettered (a-t) and given in pairs (e.g. "qd" is a star point)

#we can ignore commands LB and L

#important properties:
# B, W, AB, AE, AW, GM, SZ, RE
#note: for B and W, pass is [] or, if board size < 19x19, [tt]

#desirable properties
# BR, DT, PB, PC, PW, WR, KM
#br(black rank),dt(date),

#optional properties:
# TM, HA, TB, TW

#properties which require care to escape:
# C, N, VW, AP, CA, AN, BT, CP, GN, GC, ON, OT, RO, RU, SO, US, WT

nodes = []
#nodes is a list of tuples: (a,b), where a is a list of propertyies, and b is a list of applicable branch numbers.
#properties are: (c,d), where c is the property identity string, and d is a list of property values
currentNode = -1
branchStack = [] #alternative game sequences
nodeBranches = []
currentBranch = -1

firstChars = ['B','W','A','G','S','R']
singleCharProps = ['B','W']
secondChars = [
    [], #B
    [], #W
    ['B','E','W'], #A
    ['M'], #G
    ['Z'], #S
    ['E'] #R
    ]

def readCurrentFile():
    #these are initialized above. We reset them here for the new file.
    global nodes
    global currentNode
    global branchStack
    global nodeBranches
    global currentBranch
    global firstChars
    global singleCharProps
    global secondChars
    
    nodes = []
    currentNode = -1
    branchStack = [] 
    nodeBranches = []
    currentBranch = -1
    
    with open(currentFile, encoding="utf8") as f:
        #print ("in file" + str(currentFile))
        lines = f.readlines()
        for i in range(0,len(lines)):
            lines[i] = str(lines[i]).strip()
            j = 0
            #print ("reading line: " + str(i) + " length: " + str(len(lines[i])))
            #print (lines[i])
            while j < len(lines[i]):
                #print("at char: " + str(j))
                if lines[i][j] == "(":
                    #detect alternative game sequences (branches)
                    currentBranch += 1
                    branchStack.append(currentBranch)
                    j += 1
                elif lines[i][j] == ")" and len(branchStack) > 0:
                    #detect alternative game sequences (branches)
                    branchStack.pop()
                    j += 1
                elif lines[i][j] == ";":
                    #detect nodes
                    nodes.append(([],branchStack))
                    currentNode += 1
                    j += 1
                elif (lines[i][j] in firstChars):
                    propValid = True
                    pident = lines[i][j] #get identity name
                    if lines[i][j+1] in secondChars[firstChars.index(lines[i][j])]:
                        j += 1 #this is a valid two character property. increment j and update identity
                        pident += lines[i][j] 
                    elif lines[i][j] not in singleCharProps:
                        #this is not a valid single char property. Carefully parse to the end of the property, set j at the start of the next property, and get out of this if statement.
                        propValid = False
                        while j < len(lines[i]):
                            j += 1
                            if (lines[i][j] == ']') and (lines[i][j-1] != '\\'):
                                j += 1 #set j to start of next property
                                break
                    #else: this is a valid single-character property.

                    #print("subject property: " + pident + " " + str(propValid))
                    
                    if propValid:
                        j += 1
                        
                        if (lines[i][j] != '['):
                            #if the next character isn't an opening bracket, then there's a syntax error in the sgf. Just screw it and skip to the end of the next node.
                            #print("sjf syntax error at: " + str(pident) + " , " + str(lines[i][j]))
                            while j < len(lines[i]):
                                j += 1
                                if (lines[i][j] == ']') and (lines[i][j-1] != '\\'):
                                    j += 1 #set j to start of next property
                                    break
                        else:
                            #we're not gonna check if the value is a valid value. Once we've confirmed a valid property, we just store the values.
                            pval = ""
                            pvals = []
                            propEnd = False
                            while j < len(lines[i]):
                                if propEnd and lines[i][j] != '[':
                                    #if the previous property ended, and this one isn't another value on that property, then end the property.
                                    break
                                elif (lines[i][j] == ']') and (lines[i][j-1] != '\\'):
                                    #if the property value ended, then append it to the property value list and signify that it ended.
                                    pvals.append(pval)
                                    pval = ""
                                    propEnd = True
                                elif lines[i][j] == '[':
                                    #if the current character opens up a new property value, reset the end-of-property flag
                                    propEnd = False
                                else:
                                    #otherwise, we're in the middle of the property value. just keep appending data to the value.
                                    pval += lines[i][j]
                                j += 1
                            #We're done parsting the property! Add the current property identity and its values to the node
                            #print("found node: " + str((pident, pvals)))
                            nodes[currentNode][0].append((pident, pvals))
                else:
                    #this property is not tolerable. ignore it.
                    while j < len(lines[i]):
                        j += 1
                        if (lines[i][j] == ']') and (lines[i][j-1] != '\\'):
                            j += 1 #set j to start of next property
                            break

#by this point, we should have a list of interpretable branch/node/property/value data with all the bad data filtered out.
#the nodes are in no particular order, however, and have not been translated into usable machine data.

#----------------- INTERPRET NODES
#Parse the node list and pull out all properties related to the game metadata.
#we aren't dealing with move data in this section, because we're assuming that all move data is already in move-order.

#"nodes" is a list of tuples: (a,b), where a is a list of propertyies, and b is a list of applicable branch numbers.
#properties are: (c,d), where c is the property identity string, and d is a list of property values

#   command     example     meaning
#   B           ;B[qd]      black move
#   W           ;W[dd]      white move
#   AB          ;AB[ab][bb][cd] add list of black pieces. [do:gq] to fill rectangle
#   AE          ;AE[ab][cc][de] remove list of points on the board. [do:gq] for rectangle
#   AW          ;AW[ab][bb][cd] add list of white pieces. [do:gq] to fill rectangle
#x   GM          ;GM[1]      says this is a Baduk game (not chess). Must be 1.
#x   SZ          ;SZ[19]     board size ([19] means 19x19, otherwise sz[13][15])
#X   RE          ;RE[0]      defines game result. [0] is draw
#   "           ;RE[jigo]    defines game result. [jigo] is draw
#   "           ;RE[B+64]   black wins by 64. also [W+45] white wins by 45
#   "           ;RE[B+R]    black wins by resign. also [W+R] for white
#   "           ;RE[B+Resign] "
#               ;RE[B+T]    black wins by timeout. also [W+T]
#               ;RE[B+Time] "
#               ;RE[B+F]    black wins by forfeit. also [W+F]
#               ;RE[B+Forfeit] "
#               ;RE[Void]   no result or suspended play
#               ;RE[]       "
#               ;RE[?]      unknown result

#Variables to fill
size = None
gameResult = None
Moves = []
isBaduk = True

def interpretNodes():
    global size
    global gameResult
    global Moves
    global isBaduk
    global nodes
    size = None
    gameResult = None
    Moves = []
    isBaduk = True
    
    for node in nodes:
        for prop in node[0]:
            if (prop[0] == "GM") and (prop[1][0] != 1):
                isBaduk = False
            elif (prop[0] == "SZ"):
                if len(prop[1]) > 1:
                    size = (prop[1][0],prop[1][1])
                else:
                    size = (prop[1][0],prop[1][0])
            elif prop[0] == "RE":
                gameResult = prop[1]


#now the move data is in nodes, and the rest is in these other vars.

#----------------- SHOW THE GAME
#in this section we will create a game object, passing it the interpreted node information.
#the game object will include a function to show all the game data, and a looping function (with "after") to show the game sequence
#at the end of the game sequence, the game object should terminate and somehow trigger the whole program to start over, finding the next file etc.


#functions we have available now:
# - browsePath(basePath)   browses and gets the next file
# - readCurrentFile()       reads the file from browsePath into the node list
# - interpretNodes()        grabs metadata out of the node list

stoneMatrix = [] #contains graphic (circles) for the stones
goLinesH = [] #contains the horizontal lines of the go board
goLinesV = [] #contains the vertical lines of the go board
winnerStone = None #winner stuff is for showing who won the last game
winnerLabel = None
winnerColor = None
winnerStones = []
winnerLinesH = []
winnerLinesV = []

def initUI():#put together all the graphical objects. at end of initUI, call resetUI and nextGame
    global stoneMatrix
    global goLinesH
    global goLinesV
    global winnerStone
    global winnerLabel
    global winnerStones, winnerLinesH, winnerLinesV
    global canvas
    global smallDim, bigDim
    global goboard
    global myFont, fontHeight
    windowgap = 50
    linegap = (smallDim - (windowgap*2)) / 18
    stonesize = linegap - 2
    
    #draw the board lines    
    for row in range(len(goboard)):
        stoneMatrix.append([])
        x1 = (linegap * row) + windowgap
        y1 = windowgap
        x2 = (linegap * row) + windowgap
        y2 = smallDim - windowgap
        goLinesH.append(canvas.create_line(y1,x1,y2,x2, fill="black"))
        goLinesV.append(canvas.create_line(x1,y1,x2,y2, fill="black"))
    #draw the stones, but leave them hidden. We'll show them when they're placed.
    for row in range(len(goboard)):
        for col in range(len(goboard[row])):
            goboard[row][col] = 0
            x1 = windowgap + ((linegap) * row) - (stonesize/2)
            y1 = windowgap + ((linegap) * col) - (stonesize/2)
            stoneMatrix[row].append(canvas.create_oval(x1,y1,x1+stonesize,y1+stonesize,fill = "white",outline="gray",width=1,state='hidden')) #'normal' when shown

    linegap = (bigDim - smallDim - (windowgap*2)) / 18
    stonesize = linegap - 2
    #draw the recap board, for showing the winner of the last game
    for row in range(len(goboard)):
        winnerStones.append([])
        x1 = (linegap * row) + windowgap
        y1 = windowgap
        x2 = (linegap * row) + windowgap
        y2 = bigDim - smallDim - windowgap
        winnerLinesH.append(canvas.create_line(smallDim+y1,50+x1,smallDim+y2,50+x2, fill="black"))
        winnerLinesV.append(canvas.create_line(smallDim+x1,50+y1,smallDim+x2,50+y2, fill="black"))
    #draw the stones, but leave them hidden. We'll show them when they're placed.
    for row in range(len(goboard)):
        for col in range(len(goboard[row])):
            goboard[row][col] = 0
            x1 = windowgap + smallDim + ((linegap) * row) - (stonesize/2)
            y1 = windowgap + 50 + ((linegap) * col) - (stonesize/2)

            winnerStones[row].append(canvas.create_oval(x1,y1,x1+stonesize,y1+stonesize,fill = "white",outline="gray",width=1,state='hidden')) #'normal' when shown
            

    winPos = smallDim+25
    winnerStone = canvas.create_oval(winPos, 30, winPos+fontHeight, 30+fontHeight, fill = "white",outline="gray",width=1,state='hidden')
    winnerLabel = canvas.create_text(winPos+fontHeight+5, 30, anchor=NW, font=myFont, text="")
    canvas.pack(fill=BOTH, expand=1)

def resetUI():#hide stuff as if it's the start of a new game
    global winnerLabel
    global stoneMatrix
    global winnerStone, winnerStones
    global winnerColor
    global canvas
    global goboard
        
    #hide all stones on the board.
    for row in range(len(goboard)):
        for col in range(len(goboard[row])):
            #print("old: " + str(goboard[row][col]))
            goboard[row][col] = 0
            #print("new: " + str(goboard[row][col]))
    #print(goboard)
    for row in stoneMatrix:
        for stone in row:
            canvas.itemconfigure(stone, state='hidden')

def nextGame():#get all the stuff for the next game
    global isBaduk
    global basePath
    #print("nextGame:browsepath")
    browsepath(basePath)    #browses and gets the next file
    #print("nextGame:readCurrentFile")
    readCurrentFile()       #reads the file from browsePath into the node list
    #print("nextGame:interpretNodes")
    interpretNodes()        #grabs metadata out of the node list
    if not isBaduk:
        nextGame()



#check a group of stones to see if they need to be removed. This is because my SGFs aren't doing it for me.
#   this function is called by gameLoop
def checkGroup(x0,y0,target):
    #x0 and y0 are adjacent to the stone just placed. target is the color of the stone just placed.
    global goboard
    global canvas
    global stoneMatrix
    
    #if the stone here is the same color as the stone just placed, or is empty, or off the board, ignore it.
    if (not (0 <= x0 < 19)) or (not (0 <= y0 < 19)):
        return
    thisColor = goboard[x0][y0]
    if (thisColor == target) or (thisColor == 0):
        return
    inGroup = [(x0,y0)]
    checked = []
    toCheck = [(x0,y0)]
    
    def cp(x,y):#cp for check point.
        #Checks a single stone.
        #Returns 1 if stone is an open space.
        #if stone is the same color as the group, adds it to appropriate lists
        nonlocal inGroup
        nonlocal checked
        nonlocal toCheck
        nonlocal thisColor
        global goboard
        if (0 <= x < 19) and (0 <= y < 19) and ((x,y) not in checked):
            if goboard[x][y] == 0:
                #this stone is adjacent to an open space
                return 1
            elif goboard[x][y] == thisColor:
                inGroup.append((x,y))
                toCheck.append((x,y))
            checked.append((x,y))
        return 0

    while len(toCheck) > 0:
        #print("stones to check: " + str(len(toCheck)))
        x = toCheck[0][0]
        y = toCheck[0][1]
        #print("current stone: " + str(x) + "," + str(y))
        if (cp(x-1,y)+cp(x+1,y)+cp(x,y-1)+cp(x,y+1)) > 0:
            #if any of the surrounding stones made life
            return
        #remove this stone from the toCheck list. the cp function adds neighboring stones to the list as needed.
        del toCheck[0]
    #print("group is dead. Len: " + str(len(inGroup)))
    #print(goboard)
    for point in inGroup:
        #print("point to delete: " + str(point) + " ("+str(point[0])+","+str(point[1]) +")")
        goboard[point[0]][point[1]] = 0
        canvas.itemconfigure(stoneMatrix[point[0]][point[1]], state='hidden')


def showWinner():
    #   RE          ;RE[0]      defines game result. [0] is draw
    #   "           ;RE[jigo]    defines game result. [jigo] is draw
    #   "           ;RE[B+64]   black wins by 64. also [W+45] white wins by 45
    #   "           ;RE[B+R]    black wins by resign. also [W+R] for white
    #   "           ;RE[B+Resign] "
    #               ;RE[B+T]    black wins by timeout. also [W+T]
    #               ;RE[B+Time] "
    #               ;RE[B+F]    black wins by forfeit. also [W+F]
    #               ;RE[B+Forfeit] "
    #               ;RE[Void]   no result or suspended play
    #               ;RE[]       "
    #               ;RE[?]      unknown result
    global gameResult
    global stoneMatrix, winnerStones, winnerLabel, winnerStone
    global canvas
    global window
    global winnerColor
    goboard2 = [row[:] for row in goboard]#make a copy of the board from the previous game
    resetUI()#this resets the main board
    GR = gameResult[0]
    #print("game result: " + str(gameResult))
    drawResults = ["0","jigo", "draw"]
    badResults = ["Void","","?"]
    unknownResult = [(7,4),(8,3),(9,3),(10,3),(11,4),(11,5),(11,6),(10,7),(9,8),(9,9),(9,10),(9,11),(9,14)]
    wintype = ""
    if len(GR) > 2 and GR[1] == '+':
        #print(GR)
        if GR[2].lower() == 'r':
            wintype = " by resignation"
        elif GR[2].lower() == 't':
            wintype = " by timeout"
        elif GR[2].lower == 'f':
            wintype = " by forfeit"
        elif GR[2:].replace('.','').isdigit():
            wintype = " by " + GR[2:] + " points"
    #if the game was a draw, fill the board with half black half white
    if (GR.lower() in drawResults):
        winnerColor = 'draw'
        canvas.itemconfigure(winnerLabel, text="Previous game was a draw!")
        canvas.itemconfigure(winnerStone, fill='gray', state='normal')
        for row in range(19):
            if row < 9:
                for stone in stoneMatrix[row]:
                    canvas.itemconfigure(stone, state='normal')
                    canvas.itemconfigure(stone, fill = "black")
            if row > 9:
                for stone in stoneMatrix[row]:
                    canvas.itemconfigure(stone, state='normal')
                    canvas.itemconfigure(stone, fill = "white")
    elif GR[0:2] == "B+":
        winnerColor = 'black'
        canvas.itemconfigure(winnerLabel, text="Previous game: Black wins" + wintype + "!")
        canvas.itemconfigure(winnerStone, fill='black', state='normal')
        for x in range(6,13):
            for y in range(6,13):
                canvas.itemconfigure(stoneMatrix[x][y], state='normal')
                canvas.itemconfigure(stoneMatrix[x][y], fill = "black")
    elif GR[0:2] == "W+":
        winnerColor = 'white'
        canvas.itemconfigure(winnerLabel, text="Previous game: White wins"  + wintype + "!")
        canvas.itemconfigure(winnerStone, fill='white', state='normal')
        for x in range(6,13):
            for y in range(6,13):
                canvas.itemconfigure(stoneMatrix[x][y], state='normal')
                canvas.itemconfigure(stoneMatrix[x][y], fill = "white")
    else:
        winnerColor = 'unknown'
        canvas.itemconfigure(winnerLabel, text="Previous game winner unknown.")
        canvas.itemconfigure(winnerStone, fill='gray', state='normal')
        toggle = False
        for p in unknownResult:
            if toggle:
                canvas.itemconfigure(stoneMatrix[p[0]][p[1]], state='normal')
                canvas.itemconfigure(stoneMatrix[p[0]][p[1]], fill = "black")
            else:
                canvas.itemconfigure(stoneMatrix[p[0]][p[1]], state='normal')
                canvas.itemconfigure(stoneMatrix[p[0]][p[1]], fill = "white")
            toggle = not toggle
    #show the board from the previous game
    for row in range(len(goboard)):
        for col in range(len(goboard[row])):
            if goboard2[row][col] == -1: #white
                canvas.itemconfigure(winnerStones[row][col], state='normal', fill='white')
            if goboard2[row][col] == 1: #black
                canvas.itemconfigure(winnerStones[row][col], state='normal', fill='black')
            if goboard2[row][col] == 0: #empty
                canvas.itemconfigure(winnerStones[row][col], state='hidden')
    window.update_idletasks()
    window.update()
    time.sleep(3)
        

#"nodes" is a list of tuples: (a,b), where a is a list of propertyies, and b is a list of applicable branch numbers.
#properties are: (c,d), where c is the property identity string, and d is a list of property values
#   B           ;B[qd]      black move
#   W           ;W[dd]      white move
#   AB          ;AB[ab][bb][cd] add list of black pieces. [do:gq] to fill rectangle
#   AE          ;AE[ab][cc][de] remove list of points on the board. [do:gq] for rectangle
#   AW          ;AW[ab][bb][cd] add list of white pieces. [do:gq] to fill rectangle
gameDone = True
def gameLoop(i):#the game sequence, show all that stuff. at end of game sequence, call resetUI and nextGame
    #firstmovebranch = -1
    #for each node in nodes
    #   if firstmovebranch == this_node_branch or firstmovebranch == -1
    #       for each property in node
    #          if property is move
    #               change goboard to color
    #               change sontematrix to color and to visible
    #
    #after parsing all the nodes, set victory color and visible
    mainbranch = []
    global nodes
    global Q #the coordinate dictionary
    global stoneMatrix
    global goboard
    global canvas
    global window
    global gameDone
    
    #properties are in node[0]
    #branchstack is in node[1]
    #print ("Number of nodes: " + str(len(nodes)))
    #print ("nodes: " + str(nodes))
    bx = -1
    by = -1
    #print ("i="+str(i))
    nodetime = 1#short wait to start the game
    if i < len(nodes):
        node = nodes[i]
        if all(item in node[1] for item in mainbranch):
            #print ("in the main branch")
            mainbranch = node[1]
            nodeAction = False #was a stone placed or removed on this node?
            #print("in the main branch")
            for prop in node[0]:
                #print(prop)
                target = -10
                #decide what color to put on the board
                if (prop[0] == "B") or (prop[0] == "AB"):
                    target = 1
                elif (prop[0] == "W") or (prop[0] == "AW"):
                    target = -1
                elif (prop[0] == "AE"):
                    target = 0
                #if a color was assigned, add/remove stones.
                #print("target = " + str(target))
                if target != -10:
                    #print("target = " + str(target))
                    for loc in prop[1]:
                        #print("loca: " + str(loc))
                        if (len(loc) == 2) and (loc[0] in Q) and (loc[1] in Q):
                            bx = Q[loc[0]]
                            by = Q[loc[1]]
                            goboard[bx][by] = target
                            if target == 1:
                                #print("placing black stone at " + str(bx) + "," + str(by))
                                canvas.itemconfigure(stoneMatrix[bx][by], state='normal')
                                canvas.itemconfigure(stoneMatrix[bx][by], fill = "black")
                            if target == -1:
                                #print("placing white stone at " + str(bx) + "," + str(by))
                                canvas.itemconfigure(stoneMatrix[bx][by], state='normal')
                                canvas.itemconfigure(stoneMatrix[bx][by], fill = "white")
                            if target == 0:
                                #print("removing stone at " + str(bx) + "," + str(by))
                                canvas.itemconfigure(stoneMatrix[bx][by], state='hidden')
                            #check surrounding stones and automatically remove dead groups
                            #print("checking groups")
                            checkGroup(bx-1,by,target)
                            checkGroup(bx+1,by,target)
                            checkGroup(bx,by-1,target)
                            checkGroup(bx,by+1,target)
                            nodeAction = True
            if nodeAction:
                #print("node action")
                window.update_idletasks()
                window.update()
                nodetime = 30 #longer wait between moves in a game
            #print("waiting for " + str(nodetime))
            window.after(nodetime, lambda: gameLoop(i+1))
    else:
        #print("gameDone")
        time.sleep(3000)#pause between games
        showWinner()
        gameDone = True
        
        
                                

#now the "main" part of the code....

window = Tk()
canvasW = window.winfo_screenwidth() * 4 / 5
canvasH = window.winfo_screenheight() * 4 / 5
smallDim = 600
bigDim = 1000
if canvasW < canvasH:
    smallDim = canvasW
    bigDim = canvasH
else:
    smallDim = canvasH
    bigDim = canvasW
canvas = Canvas(window, width=canvasW, height=canvasH, bg="blanched almond")

windowPosX = 0
windowPosY = 0

window.title("Isaac's Baduk Viewer")

window.geometry('%dx%d+%d+%d' % (canvasW, canvasH, windowPosX, windowPosY))
canvas.pack(fill=BOTH, expand=1)
myFont = Font()
fontHeight = Font.metrics(myFont)["linespace"]


def doAllTheStuff():
    global gameDone
    global window
    if gameDone:
        gameDone = False #the game loop will continue in another thread, so we should wait.
        #print("resetUI")
        resetUI()#hide stuff as if it's the start of a new game
        #print("nextGame")
        nextGame()#get all the stuff for the next game
        #print("gameLoop")
        gameLoop(0)#the game sequence, show all that stuff. at end of game sequence, calls resetUI again and nextGame
    window.update_idletasks()
    window.update()
    window.after(5000, lambda: doAllTheStuff())#check every 5 seconds for a new game


#print("initUI")
initUI()#put together all the graphical objects. at end of initUI, call resetUI and nextGame
doAllTheStuff()
window.mainloop()

#we're gonna say that the baduk board takes the full height of the display, and is on the left.
#game metadata will be on the right, so that if strings get long they can just overflow off the screen.
#who even cares about metadata anyway.

#window = Tk()
#window.title("Hello World")
#lbl = Label(window, text = "Hello Worlds")
#lbl.grid(column=0, row=0)
#window.mainloop()

#show wishlist...
#X- board
#X- stones
#- prisoners
#- player names/ranks
#- date
#- location of game

#----------------- CONTROLS WISHLIST

#- next/previous step
#- next/previous game
#- increase/decrease speed
#- pause/play
#- colors (traditional, dark, calm pastel)
#- navigate to path (for a different game)
#- exit (require puzzle or question solution to exit)
