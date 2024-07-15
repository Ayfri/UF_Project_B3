import dotenv
dotenv.load_dotenv()

from pprint import pprint

from bq.queries import get_events


def main() -> None:
    events = get_events(19, year=2010)

    for row in events:
        pprint(row)


if __name__ == "__main__":
    main()
