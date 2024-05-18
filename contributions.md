## Description of optimizations to the original Wikipedia Game

The original wikipedia game conducts a breadth-first search of all hyperlinks on each page, starting from the starting page and finishing when it expands the target page.

The main idea behind my optimization is Wikipedia's own guarantee that all pages have a path to Category:Articles and Category:Articles has a path to all pages. This is expressed on [Category:Articles](https://en.wikipedia.org/wiki/Category:Articles). The simplest and most reliable human technique for finding this path is to go to the list of categories at the bottom of a page (listed after a link to Help:Categories) and repeatedly click on the first one (in other words, a depth first search). This will always lead to Category:Articles in only a few seconds unless someone made a mistake while categorizing pages.

This means a complete path between a starting and target page could be formed by searching for the path between each of them to Category:Articles and then combining those two paths. Additionally, if the second search reaches a page that was already part of the first path before it reaches Category:Articles, we can stop here because it will serve as the midpoint between the two paths. However, it is harder for an algorithm to efficiently make the "reverse path" (from the midpoint to the target page) than the path from a page to the midpoint. The easiest way to do so is to make a path from the target page to the midpoint, and then "reverse" it afterwards.

Reversing a path from a page to the midpoint involves performing a smart search from the midpoint to that page, in which we already know the nodes we expect to take and the algorithm deliberately chooses them until it completes the search (this is possible due to the guarantee that there is always a path from Category:Articles to any page).

To get the final path, three searches must be done:

1) From starting page to Category:Articles

2) From target page to Category:Articles; however, if any earlier midpoint page is reached that was already part of the first path, terminate there instead

3) From that midpoint page to the target page (using the results of the second search to smartly choose the right path)

Then, the path from the 1st and 3rd searches need only be concatenated (after removing the redundant parts from the 1st one). This will finally end with a complete path from the starting page to the target page, which may be rather long in terms of node count, but will almost always be found in less than 15 seconds.

There are a few flaws which had to be addressed due to Wikipedia editor errors. Ironically, one of them is demonstrated on Martin Wirsing, and one of them is demonstrated on David Hilbert.

For Martin Wirsing, somebody forgot to add him to Category:German_computer_scientists, even though this is the first category listed at the bottom of his page. It's not a problem to go from Martin Wirsing to Category:Articles, but attempting to smartly reverse this path would fail. To overcome this, we will have to hope that there is at least some category on Martin Wirsing's page that actually includes him. While performing search #2, we simply must check every page for a backlink to the previous page before we progress onto it.

For David Hilbert, some pages can be found during the search that lack categories, even though Wikipedia's guidelines state that every page should have at least one category. However, the depth first search should deal with this fine by just backtracking if it finds a dead end. However, if the algorithm continues to use a "discovered" list to avoid infinite loops, we will fail to reach Category:Articles when coming from David Hilbert. This is because we have to follow the first link in the list of categories at the bottom of each page to reach the end, and one of the pages in this sequence is inevitably the page right before Category:Articles, Category:Main_topic_classifications. However, this category can be seen in the categories list more than once during this particular search, so it will be "discovered" and then skipped at the critical moment, preventing the search from finishing. To fix this, instead of using a "discovered" list that includes any nodes considered for expansion, we will just use a "visited" list that only includes nodes we actually expand. This will prevent infinite loops like a discovered list, but avoids the aforementioned problem.

## Testing

My fork works identically to the original repo in terms of UI. The output is colored according to which of the three searches is being done. The elapsed time is summed from all three searches.

The default starting and target pages, Martin Wirsing to David Hilbert, are a working test. Another working path is Bee to Eiffel_Tower, which is a very long path because of insects belonging to a very long category hierarchy (however, it should still only take a few seconds to compute). A much shorter path can be found between United_States and Russia, because they both occupy the countries category. Eiffel_Tower to Eiffel_Tower also works.

During development I tested many other paths and with the current version, never found one that doesn't work.

Be careful not to put a redirect URL as the target page. For example, Bee to Eiffel_Tower will work, but Bee to Eiffel_tower will not work. This is because no links to "Eiffel_tower" can be found on the pages, but links to "Eiffel_Tower" can be found, even though actually visiting "Eiffel_tower" in the browser will redirect you to "Eiffel_Tower". Making this mistake will cause the search to enter an infinite loop during the cyan output stage.

## Sample inputs

Martin_Wirsing, David_Hilbert
Bee, Eiffel_Tower
United_States, Russia
Eiffel_Tower, Eiffel_Tower