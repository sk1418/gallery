#!/bin/python
import  os, sys, glob, shutil, re
from PIL import Image
from os import path
from glob import glob
from time import gmtime, strftime
from datetime import datetime

THUMBNAIL_SIZE = 150,150
IMAGE_STORE = 'store'
THUMBNAIL_DIR_NAME = "thumbnail"
tmp_dir = "template"
#template files
tmp_image_file = path.join(tmp_dir, "photo.tmp")
tmp_gallery_file = path.join(tmp_dir, "gallery.tmp")
tmp_main_file = path.join(tmp_dir, "main.tmp")
tmp_nav_file = path.join(tmp_dir, "nav_item.tmp")

TMP_IMAGE=""
TMP_GALLERY=""
TMP_MAIN=""
TMP_NAV=""

#place holders
ph_main_gallery = "#GALLERY#"
ph_main_nav = "#NAV_ITEMS#"
ph_image_thumbnail="#THUMBNAIL#"
ph_image_original="#ORIGINAL#"
ph_image_desc="#DESC#"

ph_gallery_album = "#ALBUM#"
ph_gallery_desc="#DESC#"
ph_gallery_photos="#PHOTOLIST#"

ph_nav_active="#ACTIVE#"
ph_nav_item="#ITEM#"
ph_nav_link="#LINK#"

TIME_PATTERN=r'\d\d-\d\d-\d\d \d\d \d\d \d\d'
TIME_PATTERN2=r'\d\d.\d\d.\d\d, \d\d \d\d \d\d'

def load_templates():
    global TMP_IMAGE, TMP_MAIN, TMP_GALLERY, TMP_NAV
    with open(tmp_image_file, 'r') as tmp_file:
        TMP_IMAGE=tmp_file.read()

    with open(tmp_gallery_file, 'r') as tmp_file:
        TMP_GALLERY=tmp_file.read()

    with open(tmp_main_file, 'r') as tmp_file:
        TMP_MAIN=tmp_file.read()

    with open(tmp_nav_file, 'r') as tmp_file:
        TMP_NAV=tmp_file.read()

    log("All templates have been loaded" )

def remove_all_htmls():
    for html in glob("*.html"):
        os.remove(html)
        log("%s has been removed." % html)


def create_thumbnail(image_file):
    img = Image.open(image_file)
    img.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)
    thumbnail_dir = path.join(path.dirname(image_file), THUMBNAIL_DIR_NAME)
    if not path.isdir(thumbnail_dir):
        os.makedirs(thumbnail_dir)
    thumbnail_file = path.join(thumbnail_dir, path.basename(image_file))
    img.save(thumbnail_file, "JPEG")


def get_date_taken(image_file):
    try:
        return datetime.strptime(Image.open(image_file)._getexif()[36867], '%Y:%m:%d %H:%M:%S') 
    except: 
        #check filename pattern first
        tmp = re.search(TIME_PATTERN, image_file)
        tmp2 = re.search(TIME_PATTERN2, image_file)
        if tmp: 
            return datetime.strptime(tmp.group(0), '%d-%m-%y %H %M %S')
        elif tmp2:
            return datetime.strptime(tmp2.group(0), '%d.%m.%y, %H %M %S')
        else:
            return datetime.fromtimestamp(path.getmtime(image_file))

def remove_orphaned_thumnails(image_dir):
    for thumnail in glob(path.join(image_dir , THUMBNAIL_DIR_NAME +"/*")):
        filename = path.basename(thumnail)
        if not path.isfile(path.join(image_dir, filename)):
            log("    > removing orphaned thumnail: %s" % thumnail)
            os.remove(thumnail)

def process_image_dir(image_dir, incremental = False):
    image_htmls = []
    log("    creating thumnails for %s %s" % (image_dir, "*incrementally*" if incremental else "" ))
    thumnail_dir = path.join(image_dir, THUMBNAIL_DIR_NAME)

    if not incremental and path.isdir(thumnail_dir): #re-create all thumbnails
        shutil.rmtree(thumnail_dir)
    images = glob(image_dir + "*.jpg")
    images.sort(key=lambda x: get_date_taken(x), reverse=True)
    thumnail_cnt = 0
    for infile in images: 
        thumbnail_file = path.join(image_dir, THUMBNAIL_DIR_NAME, path.basename(infile))
        if not incremental or (incremental and not path.isfile(thumbnail_file)):
            create_thumbnail(infile)
            thumnail_cnt += 1
        #handle html
        html = TMP_IMAGE.replace(ph_image_thumbnail, thumbnail_file)
        html = html.replace(ph_image_original, infile)
        html = html.replace(ph_image_desc, "Created on:%s" % get_date_taken(infile))
        image_htmls.append(html)

    if incremental:
        remove_orphaned_thumnails(image_dir)

    log ("    > %d thumnails have been created" % thumnail_cnt)
    log ("    > %d images have been processed" % len(image_htmls))
    return image_htmls


def create_gallery_html(image_dir, incremental = False):
    #gallery/album name
    gallery_name = image_dir.split('/')[-2]
    image_htmls = process_image_dir(image_dir, incremental)
    gallery_html = TMP_GALLERY.replace(ph_gallery_desc, "Last update: %s" % strftime("%Y-%m-%d %H:%M:%S", gmtime()))
    gallery_html = gallery_html.replace(ph_gallery_photos, "\n".join(image_htmls))
    gallery_html = gallery_html.replace(ph_gallery_album, "%s (%d)" % (gallery_name, len(image_htmls)))
    log ('    > Gallery Html codes for "%s" was generated' % gallery_name)

    return gallery_html

def get_main_html_dict(incremental = False):
    all_htmls = {}
    for image_dir in sorted(glob(IMAGE_STORE + "/*/"), reverse=True):
        log ("Creating gallery for " + image_dir)
        gallery_html = create_gallery_html(image_dir, incremental)
        #images
        html = TMP_MAIN.replace(ph_main_gallery, gallery_html)

        #gallery/album name
        gallery_name = image_dir.split('/')[-2]
        all_htmls[gallery_name] = html
    return all_htmls

def create_htmls(incremental = False):
    all_htmls = get_main_html_dict(incremental)
    #apply nav_items, and create htmls
    index_required = True
    link={}

    log ("All html codes were generated, now apply for the navigation bar and write html to file")
    log()
    for current in all_htmls.keys():
        items = []
        if index_required:
            html_file = 'index.html' 
            link[current] = html_file
        else:
            html_file = '%s.html'% current
        index_required = False
        for item in all_htmls.keys():
            item_html = TMP_NAV.replace(ph_nav_item, item)
            item_html = item_html.replace(ph_nav_active, "active" if current == item else "")
            item_html = item_html.replace(ph_nav_link, link[item] if item in link else "%s.html" % item)
            items.append(item_html)
        html = all_htmls[current].replace(ph_main_nav,  '\n'.join(items))
        log ("Writing html file %s " % html_file)
        with open( html_file, 'w') as file:
            file.write(html)


def log(text="="*77):
    print ("[INFO] %s" % text)

def usage():
    usage = """
    # normal usage:

    build.py

    # incremental generating (only generating new thumnails for new images)

    build.py -i
    """
    print (usage)

if __name__ == '__main__':
    incr = False
    if sys.argv.__len__() >2 or (sys.argv.__len__() ==2 and sys.argv[1]!="-i"):
        usage()
        sys.exit(1)
    else: 
        incr = sys.argv.__len__() == 2
        log("Start building gallery site %s..." % "*incrementally*" if incr else "")
        log()
        load_templates()
        log()
        remove_all_htmls()
        log()
        create_htmls(incr)
        log()
        log("Done!")

