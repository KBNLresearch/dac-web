# DAC Web Interface

Web interface to manually annotate named entity mentions in newspaper articles with the correct DBpedia link(s), if any. Produces labeled data sets for training and evaluating the [DAC Entity Linker](https://github.com/jlonij/dac).

## Usage

To start the web applicaton, run:

```
./web.py
```

This will start a Bottle web server listening on `http://localhost:5001`. To work on a specific data set, add the set name, e.g. `tve`, to the URL:

```
http://localhost:5001/tve
```

The training application will automatically show the first example from the requested set that hasn't been labeled yet.

In order to request a specific example from a data set, use either `id` (unique identifier) or `index` (index number within the set) as a parameter:

```
http://localhost:5001/tve?index=1
```
Selecting one or more candidates from the user interface as the correct links and navigating to the next example using the menu in the upper right corner will save the selection.

## Editing a set

Adding a new article to the set:

```
http://localhost:5001/tve/edit?action=add&url=http://resolver.kb.nl/resolve?urn=ddd:010734861:mpeg21:a0002:ocr
```

Adding a specific named entity to the set:

```
http://localhost:5001/tve/edit?action=add&url=http://resolver.kb.nl/resolve?urn=ddd:010734861:mpeg21:a0002:ocr&ne=Einstein
```
Removing an article from the set:

```
http://localhost:5001/tve/edit?action=delete&url=http://resolver.kb.nl/resolve?urn=ddd:010734861:mpeg21:a0002:ocr
```
