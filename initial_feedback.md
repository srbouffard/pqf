Some feedback to investigate:

## Portfolio Overview

- The Gold/Silver/Bronze/Unrated button/components should be of identical width. Most likely matching Bronze which is the longest.

### Products Table

- I am unsure of the usefulness of the DIRFT column given if there is a mismatch between current and target it's defacto marked as Remediating and only transitions to Overdue when past deadline. So everything is on track, its an empty column. So maybe something a little less intrusive like a small highlllight somewhere or an appropriatly colored explamation mark with a popover saying its remediating or overdue?
- I noticed everything is marked as unrated too is that normal?
- Maybe instead have the squad as a column (AMER/EMEA/APAC) given it can be searched for?
- I wonder if lifecycle should be in the Product table as a column? If everything or most everything is stable, is it really providing information?
- The Target column doesnt seem to be sortable. At least the header does not react to a click.


## Dimensions Pages

- Would be nice if below the dimension title, we had a short description section.
- Similarly, would be nice if for each criteria we have its proper name and a short description of what it measures, how it measures it? What's the output type/range. Maybe worth having a section specific to the criterias as I expect some dimensions to have quite a few! And its one thing we can expeact users to be curious about, understand how a given dimension's metrics are computed. I assume we can get much of the information from the config, if something is missing, I think its worth investigating if we should at it to the schema 
- Is the Product scores table in the dimensions page giving the current and target medal of the overall product (all dimensions?) Because the target medal configured for the product is and its not clear if the medal in that table is the dimension specific rating or the product medal.
- Here too I question is there is maybe a more useful info to show that the drift column, maybe the dimension drift with the info on when? That could be more useful. To investigate.

### Product Pages

- The place which lists which squad owns the product, it could and should be a link to the corresponding team in Github, example Americas is https://github.com/orgs/canonical/teams/platform-engineering-amer and we have similar for each of EMEA and APAC. What we could do is make it so the product info schema ownership squad is changed to ownership team where one can reference a githob team like `canonical/platform-engineering-amer` which we can convert to a proper link.
- However, when displayed in a table, like in the overview page, we should make sure it doesnt take too much space. 
- Why have the target as a column in the Product' Dimensions table if the target is at the product level and displayed at the top of the page?
- Why not instead improve the evidence/criterais column to show the current computed value and the difference between the expected value to match the target (with red/grey/green highlights to make ti clearer?)
