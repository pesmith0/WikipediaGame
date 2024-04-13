import time
import requests
from bs4 import BeautifulSoup
import re

TIMEOUT = 3600  # time limit in seconds for the search

def get_links(page_url):
    print(f"Fetching page: {page_url}")
    response = requests.get(page_url)
    print(f"Finished fetching page: {page_url}")
    soup = BeautifulSoup(response.text, 'html.parser')
    from urllib.parse import urljoin
    all_links = [urljoin(page_url, a['href']) for a in soup.find_all('a', href=True) if '#' not in a['href']]
    # print(f"All links found: {all_links}")
    links = [link for link in all_links if re.match(r'^https://en\.wikipedia\.org/wiki/[^:]*$', link) and '#' not in link]
    
    category_links = [link for link in all_links if re.match(r'^https://en\.wikipedia\.org/wiki/Category:[^:?]*$', link) and '#' not in link]

    print(f"Found {len(links)} links on page: {page_url}")
    print(f"Found {len(category_links)} category links on page: {page_url}")
    return category_links + links

def find_path(start_page, finish_page):
    queue = [(start_page, [start_page], 0)] # (vertex, path, depth)
    category_queue = [] # uses same format
    discovered = set()
    logs = []

    # breadth first search
    start_time = time.time()
    elapsed_time = time.time() - start_time
    while (category_queue or queue) and elapsed_time < TIMEOUT:
        if category_queue:
            (vertex, path, depth) = category_queue.pop(0)
            # print("vertex: " + vertex) ###
        else:
            (vertex, path, depth) = queue.pop(0)

        # print(get_links(vertex))
        # import sys
        # sys.exit() ###

        for next in set(get_links(vertex)) - discovered:
            if next == finish_page:
                log = f"Found finish page: {next}"
                print(log)
                logs.append(log)
                logs.append(f"Search took {elapsed_time} seconds.")
                print(f"Search took {elapsed_time} seconds.")  # Add a print statement to log the elapsed time
                logs.append(f"Discovered pages: {len(discovered)}")
                return path + [next], logs, elapsed_time, len(discovered) # return with success
            else:
                log = f"Adding link to queue: {next} (depth {depth})"
                # print(log)
                logs.append(log)
                discovered.add(next)

                # PS
                # put all pages starting with "Category:" in the category queue (higher priority than normal queue)
                if next.startswith("https://en.wikipedia.org/wiki/Category:"):
                    category_queue.append((next, path + [next], depth + 1))
                    # print("appending category page" + next) ###
                else:
                    queue.append((next, path + [next], depth + 1))
                
                # if "Category" in next:
                #     print("Category in next: " + next) ###

        elapsed_time = time.time() - start_time
    logs.append(f"Search took {elapsed_time} seconds.")
    print(f"Search took {elapsed_time} seconds.")  # Add a print statement to log the elapsed time
    logs.append(f"Discovered pages: {len(discovered)}")
    raise TimeoutErrorWithLogs("Search exceeded time limit.", logs, elapsed_time, len(discovered))
class TimeoutErrorWithLogs(Exception):
    def __init__(self, message, logs, time, discovered):
        super().__init__(message)
        self.logs = logs
        self.time = time
        self.discovered = discovered
