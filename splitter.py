import PIL
from PIL import Image
from PIL.ExifTags import TAGS
import time
import shutil
import os

def get_field(exif,field):
  for (k,v) in exif.iteritems():
     if TAGS.get(k) == field:
        return v


def get_original_date(img_path):
    img = PIL.Image.open(img_path)
    exif_data = img._getexif()
    return get_field(exif_data, 'DateTimeOriginal')


def main(source, dest):
    for root, dirs, files in os.walk(source):
        for f in files:
            if os.path.splitext(f)[1].lower() == '.jpg':
                img_path = os.path.join(root, f)
                date_str = get_original_date(img_path)

                if not date_str:
                    print "Date original is None ", img_path
                    continue

                date = time.strptime(date_str, "%Y:%m:%d %H:%M:%S")

                dest_folder = os.path.join(dest, str(date.tm_year), time.strftime('%m.%d', date))
                if not os.path.exists(dest_folder):
                    os.makedirs(dest_folder)

                skipBecauseFilesEquals = False
                dest_image_path = os.path.join(dest_folder, f)
                while os.path.exists(dest_image_path):
                    if os.stat(dest_image_path).st_size == os.stat(img_path).st_size and \
                        get_original_date(dest_image_path) == date_str:
                        skipBecauseFilesEquals = True
                        break

                    (name, ext) = os.path.splitext(dest_image_path)
                    dest_image_path = "%s_DUPLICATE%s" % (name, ext)


                if skipBecauseFilesEquals:
                    print "DUPLICATED: %s == %s" % (dest_image_path, img_path)
                    continue

                shutil.move(img_path, dest_image_path)


if __name__ == "__main__":
    source = 'e:\\!personal\\!photo\\2015\\source - Copy'
    dest = 'e:\\!personal\\!photo\\2015\\result'
    main(source, dest)