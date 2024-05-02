import time
import requests
from bs4 import BeautifulSoup
import re

TIMEOUT = 3600  # time limit in seconds for the search
depth_first_category_search = True

def get_links(page_url):
    print(f"Fetching page: {page_url}")
    response = requests.get(page_url)
    print(f"Finished fetching page: {page_url}")
    soup = BeautifulSoup(response.text, 'html.parser')
    from urllib.parse import urljoin
    all_links = [urljoin(page_url, a['href']) for a in soup.find_all('a', href=True) if '#' not in a['href']]
    # print(f"All links found: {all_links}")
    links = [link for link in all_links if re.match(r'^https://en\.wikipedia\.org/wiki/[^:]*$', link) and '#' not in link]
    
    # category_links = [link for link in all_links if re.match(r'^https://en\.wikipedia\.org/wiki/Category:[^:?]*$', link) and '#' not in link]

    # compose list of categories and Help:Category
    category_links = []
    help_category_index = -1
    for link in all_links:
        if re.match(r'^https://en\.wikipedia\.org/wiki/Category:[^:?]*$', link) and '#' not in link:
            category_links.append(link)
        elif re.match(r'^https://en\.wikipedia\.org/wiki/Help:Category', link) and '#' not in link:
            category_links.append(link)
            help_category_index = len(category_links) - 1
    
    # chop off everything after Help:Category, move it to the front
    if help_category_index != -1:
        after_help_category = category_links[help_category_index + 1 : len(category_links)]
        del category_links[help_category_index : len(category_links)]
        category_links = after_help_category + category_links
        print(f"Moved {len(after_help_category)} links after Help:Categories to the front of category_links")
    else:
        print("Did not find Help:Categories")

    print(f"Found {len(links)} links on page: {page_url}")
    print(f"Found {len(category_links)} category links on page: {page_url}\n")

    # print(category_links)
    # exit()

    if depth_first_category_search:
        category_links.reverse()

    return category_links + links

def find_path(start_page, finish_page):
    ARTICLES = "https://en.wikipedia.org/wiki/Category:Articles"
    path_to_articles_ret = find_path_helper(start_page, ARTICLES)
    reverse_path_ret = find_path_helper(ARTICLES, start_page, True, path_to_articles_ret[0])

    return reverse_path_ret

    # return find_path_helper(start_page, finish_page)

def find_path_helper(start_page, finish_page, reverse = False, original_path : list = None):
    queue = [(start_page, [start_page], 0)] # (vertex, path, depth)
    category_queue = [] # uses same format
    discovered = set()
    # discovered_categories_after_help_categories = set()
    logs = []
    reverse_priority_list = [] # (priority, same format)

    # breadth or depth first search
    start_time = time.time()
    elapsed_time = time.time() - start_time
    while (category_queue or queue) and elapsed_time < TIMEOUT:
        if reverse_priority_list:
            reverse_priority_list.sort()
            (_, (vertex, path, depth)) = reverse_priority_list.pop(0)
        elif category_queue:
            if depth_first_category_search:
                pop_index = -1
            else:
                pop_index = 0
            (vertex, path, depth) = category_queue.pop(pop_index)
            # print("vertex: " + vertex) ###
        else:
            (vertex, path, depth) = queue.pop(0)

        # print(get_links(vertex))
        # import sys
        # sys.exit() ###

        links_without_duplicates_or_discovered = []
        links_in_get_links = {}
        for link in reversed(get_links(vertex)):
            # ignore discovered when getting to midpoint by depth-first-searching right after Help:Categories
            # but don't ignore discovered if we're reversing
            ignore_discovered : bool = depth_first_category_search and not reverse
            if (link in links_in_get_links) or (not ignore_discovered and link in discovered):
                pass
            else:
                links_in_get_links[link] = None
                links_without_duplicates_or_discovered.append(link)
        links_without_duplicates_or_discovered.reverse()

        # for next in set(get_links(vertex)) - discovered:
        for next in links_without_duplicates_or_discovered:
            if next == finish_page:
                log = f"Found finish page: {next}"
                print(log)
                logs.append(log)
                logs.append(f"Search took {elapsed_time} seconds.")
                print(f"Search took {elapsed_time} seconds.")  # Add a print statement to log the elapsed time
                logs.append(f"Discovered pages: {len(discovered)}")
                return path + [next], logs, elapsed_time, len(discovered) # return with success
            elif reverse and next in original_path:
                log = f"Adding link to reverse_priority_list: {next} (depth {depth})"
                # print(log)
                logs.append(log)
                discovered.add(next)

                reverse_priority_list.append((original_path.index(next), (next, path + [next], depth + 1)))
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
