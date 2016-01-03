# VacationPhotoSplitter
Separate photos (and not only) by placing them into folders according to the date of creation.

**Version: 0.1.0**


## Usage

Download an archive from the project's [releases page](https://github.com/zifter/VacationPhotoSplitter).

**separator.py --source PATH_TO_YOUR_PHOTO_ARCHIVE --output OUTPUT_FOLDER**

After script execution in output directory you will see folders separated by creation time.


### Command line

*-s, --source FOLDER*

    * Source folder with files, which needs to be separated.

*-o, --output FOLDER*

    * Output folder where separated files will be.
    * default: ./OUTPUT

*-m, --move*

    * Files will be moved from source folder into output folder.
    * It's default value.

*-c, --copy*

    * Files will be copied into output folder.

*-e, --extensions*

    * Log level for logger.
    * default: process all

*-p, --path_pattern*

    * Pattern for output file path.
    * default: %Y/%m.%d'. For example: OUTPUT/2016/12.01/Image.jpg
    * Other format argument you can see at [python doc](https://docs.python.org/2/library/time.html#time.strftime)

*-l, --log_level*

    * Log level for logger.
    * choices: debug, info, warning, error'
    * default: info

## Additional information

Creation time trying to spot two ways:

1. Extract from exif tag DateTimeOriginal
2. Extract from filename