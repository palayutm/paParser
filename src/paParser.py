#! /usr/bin/env python3
import os
import json
import requests
import textwrap
from colorclass import Color
import time
import threading

import click
from terminaltables import GithubFlavoredMarkdownTable
from bs4 import BeautifulSoup

from .core import test_problem, parse_problem, archive_problem, write_problem
from .daemon import start_server, stop_server


@click.group()
def cli():
    pass


@click.command(help="Print recent contests")
@click.option("-n", "--number", default=10, type=int, help="Print N recent contests")
@click.option("-a", "--all", is_flag=True, help="Print ALL contests")
def contest(number, all):
    number = max(number, 1)
    data = json.loads(requests.get("http://codeforces.com/api/contest.list").text)
    contests = (
        data["result"][: min(len(data["result"]), number)]
        if not all
        else data["result"]
    )
    table_data = [["ID", "Contest Name", "Status"]]
    for x in contests:
        idx = str(x["id"])
        name = "\n".join(textwrap.wrap(x["name"], 50))
        data = [
            Color("{autogreen}" + idx + "{/autogreen}"),
            name,
            Color("{autored}" + x["phase"] + "{/autored}")
            if x["phase"] != "BEFORE"
            else Color(
                "{autogreen}"
                + time.strftime(
                    "%Y-%m-%d %H-%M-%S %Z", time.localtime(x["startTimeSeconds"])
                )
                + "{/autogreen}"
            ),
        ]
        table_data.append(data)
    print(GithubFlavoredMarkdownTable(table_data).table)


@click.command(help="Parse codeforces contests by CONTEST_ID")
@click.argument("contest_id")
def parse(contest_id):
    url = "http://codeforces.com/contest/%s" % contest_id
    res = requests.get(url)
    if res.url != url:
        raise Exception("Invaild Contest Id")
    page = BeautifulSoup(res.text, "lxml")
    tr = [_ for _ in page.find("table", attrs={"class": "problems"}).findAll("tr")]
    threads = []
    for i in range(1, len(tr)):
        td = [_ for _ in tr[i].findAll("td")]
        idx = td[0].text.strip()
        problem_url = url + "/problem/" + idx
        print("Parsing " + problem_url)
        threads.append(threading.Thread(target=parse_problem, args=(problem_url,)))
    for t in threads:
        t.start()
    for t in threads:
        t.join()


@click.command(help="Test code with sample file with indexes")
@click.argument("code_path", type=click.Path(exists=True))
@click.argument("samples", nargs=-1, type=str)
def test(code_path, samples):
    test_problem(code_path, samples)


@click.command(help="Move code and meta info to ../archive")
@click.argument("code_paths", nargs=-1, type=click.Path(exists=True))
def archive(code_paths):
    for path in code_paths:
        archive_problem(path)


@click.command(help="Start a daemon to listen chrome extention data")
def daemon():
    pid = os.fork()
    if pid == 0:
        try:
            start_server()
        except OSError:
            print("Can't start service, try to stop paParser daemon")
            stop_server()


@click.command(help="create a new problem")
@click.argument("problem_name")
@click.argument("contest_name", default="UNKNOWN CONTEST")
def create(problem_name, contest_name):
    content = {
        "contest_name": contest_name,
        "problem_name": problem_name,
        "file_name": problem_name,
    }
    content["date"] = time.strftime("%Y-%m-%d", time.localtime())
    print(write_problem(content))


def main():
    cli.add_command(contest)
    cli.add_command(parse)
    cli.add_command(test)
    cli.add_command(daemon)
    cli.add_command(archive)
    cli.add_command(create)
    cli()


if __name__ == "__main__":
    main()
