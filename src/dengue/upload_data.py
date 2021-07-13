"""Uploaded data to nuuuwan/dengue:data branch."""

from dengue import epid

if __name__ == '__main__':
    epid._scrape_and_dump()
    epid._dump_summary()
