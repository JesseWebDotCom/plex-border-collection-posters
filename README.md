# plex-border-collection-posters
Script which adds border outlines to all Plex collection posters (making them quickly/easlly visually distiniguishable from other posters).

<table>
<tr style="font-size:2vw"><td>Original</td><td>Modified</td></tr>
<tr><td><img src=original.png width=150px></td><td><img src=modified.png width=150px></td></tr>
</table>
You can then either manually update your collection posters in Plex or use Plex Meta Manager (PMM) to do this for you

## Script Origin

I found myself pausing to distinguish between collections and movies - this is expecially true when the poster for the collection is similar or identical to a movie poster or you just have a lot of movies/collections. Sure I can go to the 'Collections" Plex view to solve this problem, but I still wanted an exsy visual distinction for when I'm in library view, searching, etc.

I use Plex Meta Manager (PMM) and it does not have the ability to draw overlays on collections. I also didn't want to manually draw borders around every collection poster - so I made this script.
    
## What if you don't use PMM

Then just ignore any references I mention to it below.  The script will still download and create bordered posters - you will just have to manually update plex with these new posters.

## Requirements

- plex
- python
- script dependencies (run `pip install plexapi pillow`)
- pmm

## Setup

create your desired location to store the original and modified collection posters
ex. `D:\docker\plex-meta-manager\config\assets\collections\bordered\movies`

edit the script and set your `PLEX_URL` and `PLEX_TOKEN` values

set `assets_for_all` true for your library in your PMM config. ex.
```yaml
libraries:
    Movies:
        operations:
            assets_for_all: true
```

## Usage
   
1) run the script, ex.
```bash
python .\border_collection_posters.py --action upload --library-name Movies --asset-directory "D:\docker\plex-meta-manager\config\assets\collections\bordered\movies"
```

In your specified asset directory, downloaded posters will go the "originals" folder and bordered posters will go to the "modifued" folder (these folders will automatically be craeted for you)

2) run PMM operations on your library, ex.
```bash
python plex_meta_manager.py --run --ignore-schedules --run-libraries "Movies" --operations-only
```

## Options

* to only download posters, set action to `download`
* to only list collections, set action to `list`

### Customizing the borders

By default, the outer border is white with a small black inner border (which helps in case the post is mostly white, thus making the outer border invisible).
The borders are drawn relative in size to the original poster (2% for outer, 1% for inner). This makes them look all the same size in Plex.
If you want to change the color or relative percentage size, just add these aguments and change your desired values:

    `--outer-border-percent 2 --inner-border-percent 1 --outer-border-color white --inner-border-color black``


## Caching
To make the script run as quickly as possible, the script will 1) skip any collection poster already downloaded and 2) will not create a new bordered poster and or upload one if already exists.

You can clear these folders as needed manually and then script will repopulate them on next run.
    
This does not change how PMM caches and or when PMM decides to use these borded posters.

## Known issues / limitations
* you may have collections that appear to only have a top and bottom border in plex (but display perfect when manually viewing the poster in the "modified" folder).  This is likely plex cutting off the poster due to it being a non-standard size.
* pmm does not update your posters. Ex. lets say you run the script to create white thin bordered posters and then run pmm operations.  pmm successfully updates plex and your white thin bordered posters display fine in plex. 
    but you don't like the color and you delete this scripts cached files (i.e. "originals" and "modified" folders), and re-run pmm operations.  Plex still shows the old posters.
* posters for collections with non-alphanumeric characters in the name do not get updated. this is likely because PMM and this script replaces those characters with different values.  log a github issue showing the collection name from both PMM and this script's outputs/logs.
* probably more

## Support

I don't plan on addressing bugs, enhancement request, etc - but log them in Github anyway (I may change my mind)    