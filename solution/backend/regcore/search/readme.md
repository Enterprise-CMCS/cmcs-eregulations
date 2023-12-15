# Regulations Search
Regulations search uses Django's integration with Postgres search to allow full text search on a sequential database.  The recommended database version for this is Postgres 15 since its capabilities are much higher for this than previous versions.

For our use for full text search we created an index model based off of the Part model and its pieces within it.

## Model Construction
The index model that exist outside of the Part model.  The part model is where all the information in text for our regulations exist.  There is a post save hook that whenever a Part is updated or created that adds into the search index.  If a part is removed it is consequentially removed from the Index as well to not preserve old data within search.  If we wanted to search specific versions of parts some additional changes will have to be applied.

The index then takes seperate pieces of meta data from the part and applies weights to the different fields; A, B, C, or D.  These weights are applied to individual fields and then addded to a computed column in postgres that exist outside of the index model itself in postgres.  Django does not support computed columns on model tables but it can access them through annotation.  This field is cacluated automatically whenever the model is updated.  It truncates words into an easily searchable vector that allows efficiency in searching.

## Updating the index
Since this is a calculated column you cannot just change its calculations.  In order to do so the column must be dropped off of the index and then added back on with the new calculations.  Add a migration in django to run the raw sql command.

    ALTER TABLE search_searchindexv2 DROP COLUMN vector_column;


then add the column back on with whatever weights from the columns of the model you want to use.

    ALTER TABLE search_searchindexv2 ADD COLUMN vector_column tsvector GENERATED ALWAYS AS (
      setweight(to_tsvector('english', coalesce(section_string, '')), 'A') ||
      setweight(to_tsvector('english', coalesce(section_title,'')), 'A') ||
      setweight(to_tsvector('english', coalesce(part_title,'')), 'A') ||
      setweight(to_tsvector('english', coalesce(content,'')), 'B')
    ) STORED;
    CREATE INDEX search_index ON search_searchindexv2 USING GIN (vector_column);

## What ends up happening
In the following snippet it pulls in the columns section_string, section_title and part_title and gives them a weight of "A" and then for content gives it a weight of B.  And then creates a GIN index fo the new vector column to allow faster processing.

When a query is done it takes this index, annotates the vector column to the table.  It then takes the query and converts to a tsvector which then is applied as a filter to the vector column producing the results.
