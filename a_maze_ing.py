try:
    from mazegen.maze_gen import MazeGenerator
except ImportError as e:
    print(e)
    exit(0)


def main() -> None:
    MazeGenerator()


if __name__ == "__main__":
    main()
