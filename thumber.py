# Tiny Image Cacher
#
# By zourtney
# 2013-08-01
import os
import copy
import shutil
from wand.image import Image
import datetime
import weakref

class ThumberItem:
    """Controls a single image cache item, automatically creating thumbnails"""
    
    def __init__(self, filename, thumber):
        self.thumber = weakref.ref(thumber)  # weakref so `__del__` gets called on explicit delete (circular dep issue)
        self.src_filename = '%s/%s' % (thumber.src_path, filename)
        self.dest_filename = '%s/%s' % (thumber.dest_path, filename)
        
        # Create path and make downscaled image
        self.__get_or_make_directory(os.path.dirname(self.dest_filename))
        self.__create_thumbnail()

    #TODO: consider not deleting files on exit (faster startup)
    def __del__(self):
        if os.path.exists(self.dest_filename):
            print 'Deleting %s' % self.dest_filename
            os.remove(self.dest_filename)

    def __get_or_make_directory(self, directory):
        if not os.path.exists(directory):
            os.makedirs(directory)
        return directory

    def __create_thumbnail(self):
        if not os.path.isfile(self.dest_filename):
            res = self.thumber().resolution
            with Image(filename=self.src_filename) as img:
                # Resize to requested dimensions
                if res is not None and (res < img.width or res < img.height):
                    w = min((img.width * res) / img.height, res)
                    h = min((img.height * res) / img.width, res)
                    img.resize(w, h)
                # Write it out to disk
                print 'Saving @%i x %i, %s' % (img.width, img.height, self.dest_filename)
                img.save(filename=self.dest_filename)
    
    def touch(self):
        self.last_accessed = datetime.datetime.now()
    
    def serialize(self):
        ret = copy.copy(self.__dict__)
        del ret['thumber']
        return ret


class Thumber:
    """Controls a list of images to cache"""
    
    def __init__(self, src_path=None, dest_path=None, resolution=None, expiry_delta=datetime.timedelta(days=7)):
        self.src_path = src_path
        self.dest_path = dest_path
        self.resolution = resolution
        self.expiry_delta = expiry_delta
        self.items = {}

    def __del__(self):
        # Delete cache directory for a little cleanup
        #TODO: consider not doing this, for faster restarts
        shutil.rmtree(self.dest_path)

    def __get_slot(self, filename):
        if filename not in self.items:
            self.items[filename] = ThumberItem(filename=filename, thumber=self)
        return self.items[filename]

    def fetch(self, filename):
        if os.path.isfile('%s/%s' % (self.src_path, filename)):
            slot = self.__get_slot(filename)
            slot.touch()   # update `last_accessed` timestamp
            return slot
        return None

    def cull(self):
        expiry_time = datetime.datetime.now() - self.expiry_delta
        
        # Find items older than `expiry_time`
        items_to_remove = []
        for item_k, item_v in self.items.iteritems():
            if item_v.last_accessed < expiry_time:
                items_to_remove.append(item_k)

        # Delete them all
        while items_to_remove:
            del self.items[items_to_remove.pop()]

    def serialize(self):
        ret = copy.copy(self.__dict__)
        ret['items'] = dict((item_k, item_v.serialize()) for item_k, item_v in self.items.iteritems())
        return ret