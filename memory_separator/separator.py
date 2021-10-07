import os
import time
import shutil

from collections import Set
from pathlib import Path
from typing import Iterator

from entity import Entity
from logger import g_logger


def walk_in_folder(source_dir: Path, ignore_ext: Set[str]) -> Iterator[Path]:
    for root, dirs, files in os.walk(source_dir):
        r = Path(root)
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext in ignore_ext:
                g_logger.debug('Skip: %s' % f)
                continue

            yield r.joinpath(f)


def separate(context):
    for img_path in walk_in_folder(source_dir=context.source, ignore_ext=context.extentions):
        entity = Entity(img_path)
        date = entity.get_original_date()

        if date is None:
            g_logger.warning("Original Date did not detect: %s" % img_path)
            continue

        pattern = time.strftime(context.path_pattern, date.timetuple())
        dest_folder = context.output.joinpath(pattern)
        dest_img_path = dest_folder.joinpath(entity.filename)

        skip_because_files_equals = False
        while os.path.exists(dest_img_path):
            target_entity = Entity(dest_img_path)

            if entity.is_equal(target_entity):
                skip_because_files_equals = True
                break

            (name, ext) = os.path.splitext(dest_img_path)
            dest_img_path = "%s_DUPLICATE%s" % (name, ext)  # new name

        if skip_because_files_equals:
            g_logger.warning("DUPLICATED: %s == %s" % (dest_img_path, img_path))
            try:
                context.transfer_policy.delete_duplicated(img_path)
            except Exception as e:
                g_logger.error(e)
            continue

        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder)

        try:
            context.transfer_policy.copy(img_path, dest_img_path)
        except Exception as e:
            g_logger.error(e)


def remove_duplicated(context):
    size_duplication = {}
    for img_path in walk_in_folder(source_dir=context.source, ignore_ext=context.extentions):
        entity = Entity(img_path)
        size_duplication.setdefault(entity.size, []).append(entity)

    duplicated_files = {}
    for duplicate_candidate in size_duplication.values():
        if len(duplicate_candidate) == 1:
            continue

        for entity in duplicate_candidate:
            duplicated_files.setdefault(entity.hexdigest, []).append(entity)

    for k, v in duplicated_files.items():
        if len(v) == 1:
            continue

        to_remove = v[1:]
        g_logger.info(to_remove)

        dest = os.path.join(context.output, os.path.relpath(v[0], context.source))
        dest_folder = os.path.abspath(os.path.join(dest, os.pardir))
        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder)

        g_logger.info('Copy {} to {}'.format(v[0], dest))
        shutil.copy(v[0], dest)
        for img in to_remove:
            g_logger.info('Remove {}'.format(img))
            # os.remove(img)
