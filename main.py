import os
from flask import Flask, abort, send_file
from apscheduler.scheduler import Scheduler
from thumber import Thumber
import datetime

CUR_PATH = os.path.dirname(os.path.realpath(__file__))
SRC_PATH = '%s/%s' % (CUR_PATH, 'public')
DEST_PATH = '%s/%s' % (CUR_PATH, 'cache')

app = Flask(__name__)
app.debug = True

caches = {}

"""
Simple scheduled task that cleans up old thumbnails periodically.
"""
scheduler = Scheduler()
@scheduler.interval_schedule(seconds=5)
def destroy_old_thumbnails():
    for cache in caches.values():
        cache.cull()


"""
Web interface that takes a target image size and filepath
"""
@app.route('/<size>/<path:filename>/')
def view_image(size, filename):
    try:
        res = int(size)
        if not res in caches:
            # Create new thumber to handle this resolution
            caches[res] = Thumber(src_path=SRC_PATH,
                               dest_path='%s/%s' % (DEST_PATH, res),
                               resolution=res,
                               expiry_delta=datetime.timedelta(seconds=30))

            # Get info and return file, if possible
            slot = caches[res].fetch(filename)
            if slot is None:
                return abort(404)
            print 'Sending downsized %s' % slot.dest_filename
            return send_file(slot.dest_filename)
    except:
        # Pass back original
        print 'Resorting to original %s/%s' % (SRC_PATH, filename)
        return send_file('%s/%s' % (SRC_PATH, filename))


"""
Entry point
"""
if __name__ == '__main__':
    print 'Initializing image caching using:'
    print '  src_path:  %s\n  dest_path: %s' % (SRC_PATH, DEST_PATH)
    print 'Starting ...'
    scheduler.start()
    print 'Starting web interface on http://localhost:5000'
    app.run()