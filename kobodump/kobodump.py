import click
import os
import sqlite3

class Item(object):
    """
    A class representing one of: annotation, bookmark, or highlight.
    """

    ANNOTATION = "annotation"
    BOOKMARK = "bookmark"
    HIGHLIGHT = "highlight"

    def __init__(self, values):
        self.volumeid = values[0]
        self.text = values[1]
        self.annotation = values[2]
        self.extraannotationdata = values[3]
        self.datecreated = values[4] if values[4] is not None else u"1970-01-01T00:00:00.000"
        self.datemodified = values[5] if values[5] is not None else u"1970-01-01T00:00:00.000"
        self.booktitle = values[6]
        self.title = values[7]
        self.author = values[8]
        self.kind = self.BOOKMARK
        if (self.text is not None) and (self.text != "") and (self.annotation is not None) and (self.annotation != ""):
            self.kind = self.ANNOTATION
        elif (self.text is not None) and (self.text != ""):
            self.kind = self.HIGHLIGHT

    def __str__(self):
        acc = []
        sep = u"\n=== === ===\n"
        if self.kind == self.ANNOTATION:
            acc.append(u"Type: %s" % (self.kind))
            acc.append(u"Date created: %s" % (self.datecreated))
            acc.append(u"Annotation:%s%s%s" % (sep, self.annotation, sep))
            acc.append(u"Reference text:%s%s%s" % (sep, self.text, sep))
        if self.kind == self.HIGHLIGHT:
            acc.append(u"Type: %s" % (self.kind))
            acc.append(u"Date created: %s" % (self.datecreated))
            acc.append(u"Reference text:%s%s%s" % (sep, self.text, sep))
        return u"\n".join(acc)

def query(db_path, query):
    """
    Run the given query over the SQLite file.
    """
    if not os.path.exists(db_path):
        # Throw generic error indicating that the db path is invalid
        raise Exception("The specified database file '%s' does not exist." % (db_path))
    try:
        sql_connection = sqlite3.connect(db_path)
        sql_cursor = sql_connection.cursor()
        sql_cursor.execute(query)
        data = sql_cursor.fetchall()
        sql_cursor.close()
        sql_connection.close()
    except Exception as exc:
        raise Exception("Error running query '%s': %s" % (query, exc))
    return data

QUERY_ITEMS = (
    "SELECT "
    "Bookmark.VolumeID, "
    "Bookmark.Text, "
    "Bookmark.Annotation, "
    "Bookmark.ExtraAnnotationData, "
    "Bookmark.DateCreated, "
    "Bookmark.DateModified, "
    "content.BookTitle, "
    "content.Title, "
    "content.Attribution "
    "FROM Bookmark INNER JOIN content "
    "ON Bookmark.VolumeID = content.ContentID;"
)

def sanitize_obsidian_filename(filename):
    """
    Removes all characters in the set * " |/ < > : ? from the given filename string.
    """
    invalid_chars = ['*', '"', '|', '/', '<', '>', ':', '?']
    for char in invalid_chars:
        filename = filename.replace(char, '')
    return filename

def markdown_for_items(items, title, author):
    acc = []

    acc.append("# Meta")
    acc.append(f"Title: {title}")
    acc.append(f"Author: {author}")
    acc.append("")

    acc.append("# Notes")
    acc.append("")

    for item in items:
        acc.append(str(item))
        acc.append("")

    return "\n".join(acc)

def dump(db_file, output_directory):

    # Create the output directory if it does not already exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Query the database for all items
    items = [Item(d) for d in query(db_file, QUERY_ITEMS)]

    # Items by title
    items_by_title = {}

    for item in items:
        if item.title not in items_by_title:
            items_by_title[item.title] = []
        items_by_title[item.title].append(item)

    for (title, items) in items_by_title.items():
        author = items[0].author
        filename = f"Kobonotes - {sanitize_obsidian_filename(title)}"
        markdown = markdown_for_items(items, title, author)
        with open(os.path.join(output_directory, f"{filename}.md"), "w") as f:
            f.write(markdown)

@click.command()
@click.argument('db_file', type=click.Path(dir_okay=False, file_okay=True))
@click.argument('output_directory', type=click.Path(dir_okay=True, file_okay=False))
def kobodump(db_file, output_directory):
    """
    Extracts highlights and annotations from the kobo sqlite database file DB_FILE and writes them to OUTPUT_DIRECTORY as .md files
    """

    dump(db_file, output_directory)