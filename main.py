from pipeline import landing
from pipeline.download import download


def main() -> None:
    download()
    landing.split()


if __name__ == "__main__":
    main()
