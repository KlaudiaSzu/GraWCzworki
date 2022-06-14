import os
import random
import numpy as np
import pandas as pd
import time
import json
from datetime import datetime
from os.path import exists

clear = lambda: os.system('cls')
colors = ('czerwony', 'zielony')

def showTopPlayers():
    df = pd.read_csv("playersDatabase.csv")
    df.sort_values(["GamesWon","GamesPlayed"],axis=0, ascending=False,inplace=True,na_position='first')
    print(df)

def saveStats(player,id, result):
    df = pd.read_csv("playersDatabase.csv")

    if not df.loc[df['Name'] == player].empty:
        index = df.loc[df['Name'] == player].index.tolist()[0]
        gamesPlayed = df.loc[df['Name'] == player].GamesPlayed.tolist()[0]
        gamesWon = df.loc[df['Name'] == player].GamesWon.tolist()[0]
        gamesTied = df.loc[df['Name'] == player].GamesTied.tolist()[0]
        gamesLost = df.loc[df['Name'] == player].GamesLost.tolist()[0]

        #updateowanie danych
        df.loc[index, 'GamesPlayed'] = gamesPlayed + 1
        if result == id:
            df.loc[index, 'GamesPlayed'] = gamesWon + 1
        elif result == 2:
            df.loc[index, 'GamesTied'] = gamesTied + 1
        else:
            df.loc[index, 'GamesLost'] = gamesLost + 1

        df.to_csv("playersDatabase.csv", index=False)

    else:
        gamesWon=0
        gamesTied=0
        gamesLost=0
        if result == id:
            gamesWon = 1
        elif result == 2:
            gamesTied = 1
        else:
            gamesLost = 1
        pd.DataFrame([[player,1,gamesWon,gamesTied,gamesLost]]).to_csv('playersDatabase.csv', mode='a', header=None, index=False)

def menu():
    while True:
        clear()

        print("GRA W CZWORKI\n")
        print("1: Nowa Gra")
        print("2: Importuj Gre")
        print("3: Pokaz ranking")
        print("\n0: Wyjscie")

        opcja = int(input())

        if opcja >=0 and opcja <=3:
            return opcja
        else:
            message = "Wybierz opcje 1, 2, 3 lub 0\n"

def create_board(width, height):
    board = np.zeros((width,height))
    return board

def print_board(board):
   print(np.rot90(board))
   #print(board)

def winning_move(board, piece, width, height):
    #check horizontal locations
    for c in range(width-3):
        for r in range(height):
            if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2]==piece and board[r][c+3] == piece:
                return True
    # vertical locations
    for c in range(width):
        for r in range(height-3):
            if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c]==piece and board[r+3][c] == piece:
                return True
    # posit slop
    for c in range(width-3):
        for r in range(height-3):
            if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2]==piece and board[r+3][c+3] == piece:
                return True

    # negative slop
    for c in range(width-3):
        for r in range(3, height):
            if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2]==piece and board[r-3][c+3] == piece:
                return True

def get_row(board, column, height):
    for r in range(height):
        if board[column][r]==0:
            return r
    return -1

def put_piece(board, column, row, piece):
    board[column][row] = piece


def tie(board):
    result = np.where(board==0)
    if len(result):
        return 0
    else:
        return 1

def displayBoard(playersText, playersColorsText, game):

    while True:
        clear()
        print(playersText)
        print(playersColorsText)
        print('{:>30}'.format("Ruch gracza " + game['players'][game['move']]))
        message = 'Wybierz kolumne od 1-7 lub nacisnij 0, aby cofnac ruch. Nacisnij 9 aby wyeksportowac gre.'

        print(message)

        print_board(game['board'])
        while True:
            ruch = int(input())
            if (ruch<=7 and ruch>=0) or ruch == 9:
                if ruch>0 and ruch!=9:
                    row = int(get_row(game['board'], ruch-1, game['height']))
                    if row != -1:
                        break
                    message = "Bledna wartosc. Wybierz kolumne od 1-7 lub nacisnij 0, aby cofnac ruch. Nacisnij 9 aby zaimportowac gre."

                elif ruch == 0:

                    if len(game['moves']) == 0:
                        message = "Nie wykonano jeszcze zadnego ruchu. Wybierz kolumne od 1-7"
                    else:
                        break
                else:
                    break

            print(message)
        if ruch == 0:
            last_element = game['moves'][-1]
            put_piece(game['board'], last_element['column']-1, last_element['row'], 0)
            game['moves'].pop()

        elif ruch == 9:
            print(game)
            game['board'] = game['board'].tolist()
            pythonJson = json.dumps(game)

            now = datetime.now()
            filename = now.strftime('%m%d%Y%H%M%S')
            f = open(filename + ".txt", 'w')
            f.write(pythonJson)
            f.close()

        else:
            put_piece(game['board'], ruch-1, row, game['move']+1)
            game['moves'].append({
                'player': game['move'],
                'column': ruch,
                'row': row
            })

            if winning_move(game['board'], game['move']+1, game['height'] ,7):

                # result
                # 0-player1
                # 1-player2
                # 2-remis
                result = game['move']
                break
            if tie(game['board']):

                result = 2
                break
        game['move'] = not game['move']
        game['move'] = int(game['move'])


    clear()
    print(playersText)
    print(playersColorsText)
    game['ended'] = 1
    if result<2:
        print('{:>30}'.format("WYGRAŁ GRACZ " + game['players'][game['move']]))
    else:
        print('{:>30}'.format("REMIS"))

    print_board(game['board'])
    saveStats(game['players'][0],0, result)
    saveStats(game['players'][1],1, result)
    return result


def newGame(player1, player2, height):
    clear()
    playersText = '{:<24} {:>24}'.format(player1, player2)
    #print(players)

    player1Color = random.randint(0, 1)
    player2Color = not player1Color
    playersColorsText = '{:<24} {:>24}'.format(colors[player1Color], colors[player2Color])
    #print(playersColors)
    players = (player1, player2)

    move = random.randint(0, 1)
#tworzenie boarda
    board = create_board(7,height)
#tworzenie przebiegu rundy
    game = {'players': players,
    'ended':0,
    'moves':[],
    'move': int(move),
    'board': board,
    'height': height
    }

    result = displayBoard(playersText, playersColorsText, game)

    #tu dodawanie wyniku do rankingu
    print("Program zakonczy dzialanie za 5 sekund")
    time.sleep(5)

def newLobby():
    clear()
    print('Nowa Gra\n')

    print('Wprowadz nazwe gracza 1')
    player1 = input()
    print('Wprowadz nazwe gracza 2')
    player2 = input()
    print('Wprowadz wysokosc planszy')
    height = int(input())

    newGame(player1,player2, height)



def importGame():
    clear()
    print("Importuj Gre")
    print("Wprowadz nazwe pliku gry z koncowka .txt")
    nazwaPlikuGry = input()
    file_exists = exists(nazwaPlikuGry)

    if file_exists:
        f = open(nazwaPlikuGry,"r")
        plik = f.read()
        plikList = json.loads(plik)
        plikList['board'] = np.array(plikList['board'])

        playersText = '{:<24} {:>24}'.format(plikList['players'][0], plikList['players'][1])
    #print(players)

        player1Color = random.randint(0, 1)
        player2Color = not player1Color
        playersColorsText = '{:<24} {:>24}'.format(colors[player1Color], colors[player2Color])
        displayBoard(playersText, playersColorsText, plikList)

        print("Program zakonczy dzialanie za 5 sekund")
        time.sleep(5)


    else:
        clear()
        print("Podany plik nie istnieje.")
        print("Program zakonczy dzialanie za 5 sekund")
        time.sleep(5)



def main():
    #tworzenie csv z graczami
    if not exists("playersDatabase.csv"):
        database = {
            'Name' : [],
            'GamesPlayed' : [],
            'GamesWon': [],
            'GamesTied': [],
            'GamesLost': []
        }
        pd.DataFrame(database).to_csv('playersDatabase.csv', index=False)


    wybor = menu()
    if wybor == 0:
        print('Program zakonczono')
        return 0

    match wybor:
        case 1:
            newLobby()
        case 2:
            importGame()
        case 3:
            showTopPlayers()

main()