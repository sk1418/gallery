# gallery

python script to generate a static html gallery site.

Example: https://sk1418.github.io/gallery

## Dependencies

- python
- python Pillow(PIL) library
- lightGallery (included)

## Features

- auto generating thumbnails
- auto create gallery site
- simple: single script, copy images files to sub-directory under `store`, done.
- optional incremental generation

## Usage:

- prepare template (under `template`)
- copy images as sub-directories under `store`

	./build.py

or for incremental thumbnails generation:

	./build.py -i  

Done.

## Todo:

- [x] cli option parser
