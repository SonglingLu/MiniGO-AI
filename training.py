from tqdm import tqdm
from host import GO
from random_player import RandomPlayer
from my_player3 import MyPlayer

if __name__ == "__main__":
    N = 5
    player1 = RandomPlayer()
    myplayer = MyPlayer()


    # play as black
    myplayer_player1 = []
    for i in tqdm (range (30), desc="Playing as Black..."):
        go = GO(N)
        myplayer_player1.append(go.play(myplayer, player1, False))
    
    # play as white
    player1_myplayer = []
    for i in tqdm (range (30), desc="Playing as White..."):
        go = GO(N)
        player1_myplayer.append(go.play(player1, myplayer, False))

    print(myplayer_player1.count(1))
    print(player1_myplayer.count(2))
