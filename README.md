Thumber
=========
A bare-bones, ignorant implementation of a thumbnailing web service.

How to "install"
-
To install, simply clone this repository, add some images to the `public` directory and run `main.py`. Can't be bothered with parsing the previous sentence? Well, here ya go:

    git clone https://github.com/zourtney/thumber.git
    cd thumber

    curl -L -o public/jefferson.png http://goo.gl/XCgTyY
    mkdir public/hike; curl -L -o public/hike/lookout.png http://goo.gl/Gs4IoY
    
    python main.py

**Dependencies**

You will need the following libraries, all of which can be installed via `pip` or `easy_install`.

  - [Flask](http://flask.pocoo.org/), for web service
  - [Wand](http://docs.wand-py.org/en/0.3.3/), for image manipulation
  - [APScheduler](http://pythonhosted.org/APScheduler/), for simple periodic tasks

How to use
-
Images in the `public` directory are accessed via `http://localhost:5000/[size]/[path]`. Where:

  - `[size]` is the longest side of target image's resolution.
  - `[path]` is the filename of the image to view. Subdirectories are fine.

Any non-numeric `[size]` value falls back to showing the full-size image

**Examples**

  - `http://localhost:5000/1024/jefferson.png`
  - `http://localhost:5000/full/hike/lookout.png`

All downsized images are saved to the `cache` directory. A periodic task removes images that have not been accessed for a while. These images (and related directories) are automatically destroyed upon exit. 

Speaking of exiting this application...to do so, just enlist your old pal `ctrl+c`.

Version
-
0.1 (as in pre-alpha)