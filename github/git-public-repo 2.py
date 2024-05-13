#!/usr/bin/env python

from github import Github

__author__ = "Aniruddha Biyani"
__version__ = "1.0.0"
__maintainer__ = "Aniruddha Biyani"
__email__ = "contact@anirudbiyani.com"
__status__ = "Active"

def main():
    token = "" #Your GitHub Token

    g = Github(token)
    repo = g.search_repositories(query="org:<Your Organization's Name> fork:only")
    for r in repo:
        ro = g.get_repo(str(r)[22:-2])
        print ro.name

if __name__ == '__main__':
    main()
