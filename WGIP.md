# Wikipedia Game Improvement Proposal
Group: Peter Smith

## Improvement Description
The wikipedia game currently conducts a breadth-first search of all hyperlinks on each page, starting from the starting page and finishes when it expands the target page. The two major changes to improve this are:

1) The searches will be conducted in the category pages first and only default to the random hyperlinks on each starting page if that search fails. In order to do this, move all links with titles that start with the string "Category:" to the top of the frontier. Also, whenever adding a page to the frontier, check if it is the target, so that a direct link to the target page inside of a category page is caught.
2) Conduct a second simultaneous search starting from the target page and searching for the starting page. Additionally, both of the searches will check if a new page they are discovering has already been discovered by the other search, and if this occurs, move the page to the top of their frontier, meaning they will expand it next (this is because if they both discover links to the same category, there is almost certainly a link to the target page inside of that category). Note: there is almost always a two-way path if we are searching inside of category pages, because every page lists its categories at the bottom.
NOTE 5-1-24: After some testing I discovered that my previous plan probably wouldn't be a good optimization in many cases, but I thought of a much better and more reliable idea, based on the guarantee from Wikipedia that any page has a path to Category:Articles, and Category:Articles has a path to any page. I will fully describe this plan later, but I have switched to implementing it instead of my previous one, which means my previous milestones are out of date, so I am changing them now.

## Pseudo-Code
```
# these lines are generally duplicated so that there are two simultaneous searches -- could also use multithreading as an optimization
while true:
    #### first run existing code that conducts a breadth first search, adding nodes to the bottom of a frontier (defines local variable called node), and breaks if a path is found
    if node.text starts with "Category:"
        # move node to top of frontier, but below any existing nodes that start with "Category:"
    if other_search.discovered.has(node):
        # move node to top of frontier
        continue
```

## Milestones
1) Implement part 1 of the improvement (conduct search in category pages first). (deadline can be April 10th)
2) May 1st -- discovered problem with old design, came up with new one, implemented a bunch of it (can reliably find a path to Category:Articles from any starting page, and can almost always reverse that path).
3) Finish optimization so I can present. (deadline is May 9th)
4) If I have extra time, add multi threading optimization, colored text, etc.

## Details for milestones
The programming language is python. I will use a colored text printing library called termcolor, to make it easier to read the program output. If I do the multithreading optimization, I will use the Python threading module.
