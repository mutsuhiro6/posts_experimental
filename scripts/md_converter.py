import os
import json
import re
import datetime
from markdown import Markdown

PROJECT_ROOT = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), os.pardir)
METADATA_JSON = os.path.join(PROJECT_ROOT, 'metadata.json')
HTML_DIR = os.path.join(PROJECT_ROOT, 'html')
IMAGE_DIR = os.path.join(PROJECT_ROOT, 'image')
MARKDOWN_DIR = os.path.join(PROJECT_ROOT, 'markdown')
NEW_DIR = os.path.join(PROJECT_ROOT, 'new')
NEW_IMAGE_DIR = os.path.join(NEW_DIR, 'image')


def transform(md_filepath):
    parser = Markdown(extensions=['extra', 'meta', 'admonition'])
    with open(md_filepath, 'r', encoding='utf-8') as f:
        md_content = f.read()
        html = parser.convert(md_content)
        images = extractImagePaths(md_content)
    metadata = parser.Meta
    return html, metadata, images


def extractImagePaths(md_content):
    image_refs = re.findall(r'!\[.*\]\(.*\)|!\[.*\]', md_content)
    for ref in image_refs:
        print(re.sub('!\[.*\(|\)', '', ref))
    image_abspaths = [os.path.join(NEW_DIR,
                                   re.sub('!\[.*\(|\)', '', ref)) for ref in image_refs]
    return image_abspaths


def apendOutputMetadata(metadata):
    with open(METADATA_JSON, 'a', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False)


def addFilenamesToMetadata(metadata, filename_wo_ext):
    metadata['filename_html'] = filename_wo_ext + '.html'
    metadata['filename_md'] = filename_wo_ext + '.md'


def addCreatedDatetimeToMetadata(metadata, datetime):
    metadata['created_at'] = datetime.strftime('%Y-%m-%d %H:%M:%S')


def outputHtml(html, output_filename):
    with open(os.path.join(HTML_DIR, output_filename), 'w', encoding='utf-8') as f:
        f.write(html)


def moveImage(src_image_abspath, dst_dirname):
    image_name = os.path.basename(src_image_abspath)
    dst_dirpath = os.path.join(IMAGE_DIR, dst_dirname)
    if not os.path.exists(dst_dirpath):
        os.mkdir(dst_dirpath)
    dest_image_abspath = os.path.join(IMAGE_DIR, dst_dirname, image_name)
    os.replace(src_image_abspath, dest_image_abspath)


def moveMarkdown(src_md_abspath, dst_md_filename):
    dst_md_abspath = os.path.join(MARKDOWN_DIR, dst_md_filename)
    os.replace(src_md_abspath, dst_md_abspath)


def flattenArrayValueDict(dict):
    for key, val in dict.items():
        if len(val) == 1:
            dict[key] = val[0]


def main():
    md_filepaths = [os.path.join(NEW_DIR, md_filename) for md_filename in os.listdir(
        NEW_DIR) if md_filename.endswith('.md')]
    timestamp = datetime.datetime.today()
    output_filename_base = timestamp.strftime('%Y%m%d-%H%M%S') + '_'
    i = 0
    for md_filepath in md_filepaths:
        (html, metadata, images) = transform(md_filepath)
        filename = os.path.basename(md_filepath)
        if 'draft' in metadata:
            print('The file: ' + filename + ' is draft.')
            break
        number = '{:0>2}'.format(i)
        output_name = output_filename_base + number
        # print(html)
        outputHtml(html, output_name + '.html')
        moveMarkdown(md_filepath, output_name + '.md')
        for image in images:
            print(image)
            moveImage(image, output_name)
        addCreatedDatetimeToMetadata(metadata, timestamp)
        addFilenamesToMetadata(metadata, output_name)
        flattenArrayValueDict(metadata)
        print(metadata)
        apendOutputMetadata(metadata)


if __name__ == '__main__':
    main()
