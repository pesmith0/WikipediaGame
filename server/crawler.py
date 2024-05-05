import time
import requests
from bs4 import BeautifulSoup
import re
from termcolor import cprint

TIMEOUT = 3600  # time limit in seconds for the search
depth_first_category_search = True
print_color = "green"

def tcprint(*args, color=None):
    print_str = ""
    for arg in args:
        print_str = print_str + str(arg)
    cprint(print_str, color or print_color)

def get_links(page_url):
    tcprint(f"Fetching page: {page_url}")
    response = requests.get(page_url)
    tcprint(f"Finished fetching page: {page_url}")
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
    
    # chop off everything after Help:Category, return separately
    if help_category_index != -1:
        after_help_category = category_links[help_category_index + 1 : len(category_links)]
        del category_links[help_category_index : len(category_links)]
        tcprint(f"Found {len(after_help_category)} links after Help:Categories")
    else:
        after_help_category = []
        tcprint("Did not find Help:Categories")

    tcprint(f"Found {len(links)} links on page: {page_url}")
    tcprint(f"Found {len(category_links)} category links on page: {page_url}\n")

    # print(category_links)
    # exit()

    # if depth_first_category_search:
    #     category_links.reverse()
    #     after_help_category.reverse()

    return (after_help_category, category_links + links)

def filter_links(links : list, discovered : set):
    links_without_duplicates_or_discovered = []
    links_in_get_links = {}
    # (after_help_categories, rest_of_links) = get_links(vertex)
    for link in links:
        # ignore discovered when getting to midpoint by depth-first-searching right after Help:Categories
        # but don't ignore discovered if we're reversing
        # ignore_discovered : bool = depth_first_category_search and not reverse
        if (link in links_in_get_links) or (link in discovered):
            pass
        else:
            links_in_get_links[link] = None
            links_without_duplicates_or_discovered.append(link)

    return links_without_duplicates_or_discovered

def find_path(start_page, finish_page):
    """Returns (path, logs, elapsed_time, len(visited))"""
    global print_color
    ARTICLES = "https://en.wikipedia.org/wiki/Category:Articles"

    print_color = "light_green"
    path_to_articles_ret = find_path_helper(start_page, ARTICLES)

    print_color = "light_cyan"
    opposite_path_to_midpoint_ret = find_path_helper(finish_page, ARTICLES, opposite_with_path = path_to_articles_ret[0])

    print_color = "green"
    midpoint = opposite_path_to_midpoint_ret[0][-1]
    reversed_opposite_path_ret = find_path_helper(midpoint, finish_page, reverse_with_path = opposite_path_to_midpoint_ret[0])

    # edit first path so it stops before reaching the midpoint
    path_a = []
    for link in path_to_articles_ret[0]:
        if link == midpoint:
            break
        path_a += [link]

    logs_sum = path_to_articles_ret[1] + opposite_path_to_midpoint_ret[1] + reversed_opposite_path_ret[1]
    time_sum = path_to_articles_ret[2] + opposite_path_to_midpoint_ret[2] + reversed_opposite_path_ret[2]
    visited_sum = path_to_articles_ret[3] + opposite_path_to_midpoint_ret[3] + reversed_opposite_path_ret[3]
    return (path_a + reversed_opposite_path_ret[0], logs_sum, time_sum, visited_sum)

    # return find_path_helper(start_page, finish_page)

def find_path_helper(start_page, finish_page, reverse_with_path : list = None, opposite_with_path : list = None):
    reverse = bool(reverse_with_path)

    queue = [(start_page, [start_page], 0)] # (vertex, path, depth)
    category_queue = [] # uses same format
    discovered_categories_after_help_categories = set()
    discovered_rest = set()
    visited = set()
    logs = []
    reverse_priority_list = [] # (priority, same format)

    # breadth or depth first search
    start_time = time.time()
    elapsed_time = time.time() - start_time
    while (category_queue or queue or reverse_priority_list) and elapsed_time < TIMEOUT:
        category_queue_additions = []

        # print("category_queue\n", category_queue)
        # if category_queue:
        #     exit()

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

        # filter discovered and duplicates from links
        (after_help_categories, rest_of_links) = get_links(vertex)
        sum_of_links_unfiltered = after_help_categories + rest_of_links

        # after_help_categories_filtered = filter_links(after_help_categories, discovered_categories_after_help_categories)
        # rest_of_links_filtered = filter_links(rest_of_links, discovered_rest)
        # rest_of_links_filtered = filter_links(rest_of_links_filtered, discovered_categories_after_help_categories)

        after_help_categories_filtered = filter_links(after_help_categories, visited)
        rest_of_links_filtered = filter_links(rest_of_links, visited)
        visited.add(vertex)

        # category_domesticated_animals = "https://en.wikipedia.org/wiki/Category:Domesticated_animals"
        # print("len of after_help_categories_filtered: ", len(after_help_categories_filtered))
        # if category_domesticated_animals in after_help_categories_filtered:
        #     print("index of Category:Domesticated_animals: ", after_help_categories_filtered.index(category_domesticated_animals))
        # else:
        #     print("Category:Domesticated_animals not found")
        

        # check if this vertex has a link back to its parent (ensures that a reverse path will be found later)
        if not reverse and len(path) >= 2:
            found_backlink = False
            previous = path[-2]
            for next in sum_of_links_unfiltered:
                if next == previous:
                    found_backlink = True
                    tcprint("On " + vertex + ", found backlink to " + previous) ###
                    break
            if not found_backlink:
                tcprint("On " + vertex + ", no backlink found to " + previous, color="red") ###
                # print(sum_of_links_unfiltered) ###
                # print()
                # print(after_help_categories)
                # print()
                # print(rest_of_links)
                # exit()
                continue

        def process_links(links : list, discovered : set):
            for next in links:
                if next == finish_page or next in (opposite_with_path or []):
                    log = f"Found finish page: {next}"
                    tcprint(log)
                    logs.append(log)
                    logs.append(f"Search took {elapsed_time} seconds.")
                    tcprint(f"Search took {elapsed_time} seconds.")  # Add a print statement to log the elapsed time
                    # logs.append(f"Discovered pages: {len(discovered)}")
                    logs.append(f"Visited pages: {len(visited)}")
                    return path + [next], logs, elapsed_time, len(visited) # return with success
                elif reverse and next in reverse_with_path:
                    log = f"Adding link to reverse_priority_list: {next} (depth {depth})"
                    # print(log)
                    logs.append(log)
                    # discovered.add(next)

                    reverse_priority_list.append((reverse_with_path.index(next), (next, path + [next], depth + 1)))
                else:
                    log = f"Adding link to queue: {next} (depth {depth})"
                    # print(log)
                    logs.append(log)
                    # discovered.add(next)

                    # PS
                    # put all pages starting with "Category:" in the category queue (higher priority than normal queue)
                    if next.startswith("https://en.wikipedia.org/wiki/Category:"):
                        category_queue_additions.append((next, path + [next], depth + 1))
                        # print("appending category page" + next) ###
                    else:
                        queue.append((next, path + [next], depth + 1))
        
        process = process_links(after_help_categories_filtered, discovered_categories_after_help_categories)
        if process:
            return process
        process = process_links(rest_of_links_filtered, discovered_rest)
        if process:
            return process

        if depth_first_category_search:
            category_queue_additions.reverse()
        category_queue += category_queue_additions

        elapsed_time = time.time() - start_time
    logs.append(f"Search took {elapsed_time} seconds.")
    tcprint(f"Search took {elapsed_time} seconds.")  # Add a print statement to log the elapsed time
    logs.append(f"Discovered pages: {len(discovered_categories_after_help_categories)} after Help:Categories, {len(discovered_rest)} in rest of page")
    raise TimeoutErrorWithLogs("Search exceeded time limit.", logs, elapsed_time, len(discovered_categories_after_help_categories) + len(discovered_rest))
class TimeoutErrorWithLogs(Exception):
    def __init__(self, message, logs, time, discovered):
        super().__init__(message)
        self.logs = logs
        self.time = time
        self.discovered = discovered
