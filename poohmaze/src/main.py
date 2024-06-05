from game import PoohMaze

def start_game():
    app = PoohMaze.create()
    app.start()


if __name__=='__main__':
    start_game()