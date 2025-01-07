import re
from typing import Any
import json

import requests

"""
According to rfc-editor

  ####  Title of RFC.  Author 1, Author 2, Author 3.  Issue date.
        (Format: ASCII) (Obsoletes xxx) (Obsoleted by xxx) (Updates xxx)
        (Updated by xxx) (Also FYI ####) (Status: ssssss) (DOI: ddd)
or
  ####  Not Issued.

For example:
  1129 Internet Time Synchronization: The Network Time Protocol. D.L.
       Mills. October 1989. (Format: TXT, PS, PDF, HTML) (Also RFC1119) 
       (Status: INFORMATIONAL) (DOI: 10.17487/RFC1129) 

Key to citations:

#### is the RFC number.

Following the RFC number are the title, the author(s), and the
publication date of the RFC.  Each of these is terminated by a period.

Following the number are the title (terminated with a period), the
author, or list of authors (terminated with a period), and the date
(terminated with a period).

The format follows in parentheses. One or more of the following formats 
are listed:  text (TXT), PostScript (PS), Portable Document Format 
(PDF), HTML, XML.

Obsoletes xxxx refers to other RFCs that this one replaces;
Obsoleted by xxxx refers to RFCs that have replaced this one.
Updates xxxx refers to other RFCs that this one merely updates (but
does not replace); Updated by xxxx refers to RFCs that have updated
(but not replaced) this one.  Generally, only immediately succeeding
and/or preceding RFCs are indicated, not the entire history of each
related earlier or later RFC in a related series.

The (Also FYI ##) or (Also STD ##) or (Also BCP ##) phrase gives the
equivalent FYI, STD, or BCP number if the RFC is also in those
document sub-series.  The Status field gives the document's
current status (see RFC 2026).  The (DOI ddd) field gives the
Digital Object Identifier.
"""

BRACKETS_EXTRACT = re.compile(r'\((.*?)\)')

def sync_index() -> str:
    """ Fetch RFC Index from rfc-editor.org """
    return requests.get("https://www.rfc-editor.org/rfc-index.txt").text.split("---------")[2].strip()

def parse(src: str) -> dict[int, tuple[str, list[str], str, dict[str, Any]]]:
    """ Magic """
    result = {}
    kv = {int(__[:4]): __[5:-1] for __ in [_.replace("\n     ", " ") for _ in src.split("\n\n")]}

    for k, v in kv.items():
        if v != "Not Issued.":
            result[k] = parse_title(v)

    return result

def parse_title(title_src: str):
    """ Parse only, not checking whether issued"""
    # Get Title
    title = title_src[:(sep_1:=title_src.find("."))]
    print(title)
    authors, date = title_src[sep_1 + 2:][:title_src[sep_1 + 2:].find("(") - 2].rsplit(".", 1)
    authors = authors.split(",")
    date = date.strip()
    infos_src = re.findall(BRACKETS_EXTRACT, title_src[title_src.find("("):])

    infos = {}

    for item in infos_src:
        if item.startswith("Format"):
            infos["format"] = item[8:].split(", ")
        elif item.startswith("Obsoletes"):
            infos["obsoletes"] = item[10:].split(", ")
        elif item.startswith("Obsoleted"):
            infos["obsoleted"] = item[13:].split(", ")
        elif item.startswith("Updates"):
            infos["updates"] = item[8:].split(", ")
        elif item.startswith("Updated"):
            infos["updated"] = item[11:].split(", ")
        elif item.startswith("Also"):
            infos["also"] = item[6:].split(", ")
        elif item.startswith("Status"):
            infos["status"] = item[8:]
        elif item.startswith("DOI"):
            infos["doi"] = item[5:]
        else:
            print("Invalid Tag")

    return title, authors, date, infos

def main():
    with open("res.json", mode="w") as f:
        f.write(json.dumps(parse(sync_index())))

if __name__ == "__main__":
    main()
