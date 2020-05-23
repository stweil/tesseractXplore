from hashlib import md5
from io import BytesIO
from os import makedirs
from os.path import isfile, join, splitext
from logging import getLogger

from PIL import Image
from naturtag.constants import THUMBNAILS_DIR, THUMBNAIL_SIZE, LG_THUMBNAIL_SIZE

logger = getLogger().getChild(__name__)


def get_thumbnail(image_path, large=False):
    """
    Get a cached thumbnail for an image, if one already exists; otherwise, generate a new one.

    Args:
        image_path (str): Path to source image
        largs (bool): Make it a 'larger' thumbnail

    Returns:
        str: Path to thumbnail image
    """
    thumbnail_path = get_thumbnail_path(image_path)
    if isfile(thumbnail_path):
        return thumbnail_path
    else:
        return generate_thumbnail(image_path, thumbnail_path, large)


def get_thumbnail_if_exists(image_path):
    """
    Get a cached thumbnail for an image, if one already exists, but if not, don't generate a new one
    """
    thumbnail_path = get_thumbnail_path(image_path)
    if isfile(thumbnail_path):
        logger.info(f'Found existing thumbnail for {image_path}')
        return thumbnail_path
    else:
        return None


def get_thumbnail_path(image_path):
    """ Determine the thumbnail filename based on a hash of the original file path """
    makedirs(THUMBNAILS_DIR, exist_ok=True)
    thumbnail_hash = md5(image_path.encode()).hexdigest()
    # Strip off request params if path is a URL
    image_path = image_path.split('?')[0]
    ext = splitext(image_path)[-1] or '.png'
    return join(THUMBNAILS_DIR, f'{thumbnail_hash}{ext}')


def cache_async_thumbnail(async_image, large=False):
    """ Get raw image data from an AsyncImage and cache a thumbnail for future usage """
    thumbnail_path = get_thumbnail_path(async_image.source)
    ext = splitext(thumbnail_path)[-1].replace('.', '')
    logger.info(f'Getting image data downloaded from {async_image.source}; format {ext}')

    # Load inner 'texture' bytes into a file-like object that PIL can read
    image_bytes = BytesIO()
    async_image._coreimage.image.texture.save(image_bytes, fmt=ext)
    image_bytes.seek(0)
    return generate_thumbnail(image_bytes, thumbnail_path, large=True, format=ext)


def generate_thumbnail(source, thumbnail_path, large=False, format=format):
    """
    Generate a new thumbnail from the source image, or just copy the image to the cache if it's
    already thumbnail size
    """
    logger.info(f'Generating new thumbnail for {source}:\n  {thumbnail_path}')
    target_size = LG_THUMBNAIL_SIZE if large else THUMBNAIL_SIZE
    try:
        image = Image.open(source)
        if image.size[0] > target_size[0] or image.size[1] > target_size[1]:
            image.thumbnail(target_size)
        else:
            logger.info(f'Image is already thumbnail size! ({image.size})')
        image.save(thumbnail_path)
        return thumbnail_path
    # If we're unable to generate a thumbnail, just use the original image
    except RuntimeError as e:
        logger.error('Failed to generate thumbnail:')
        logger.exception(e)
        return source
