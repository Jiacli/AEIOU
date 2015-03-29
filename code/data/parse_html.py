import os, sys
import re


def main(args):
    input_path = sys.argv[1]
    output_path = sys.argv[2]

    file_list = list_all_file(input_path)

    for filename in file_list:
        print 'parsing file:', filename
        parse_html_file(filename, output_path)
    print 'done.'


def parse_html_file(filename, output_dir):
    title = ''
    sent_list = []
    with open(filename) as f:
        for line in f.readlines():
            if len(line.strip()) == 0:
                continue
            if line.startswith('<title>'):
                tmp = re.sub('<[^>]+>', '', line.strip())
                title = re.sub(r'\s+', '_', tmp)
                print 'title:', title
            elif line.startswith('<p>'):
                line = re.sub('<[^>]+>', '', line.strip())
                if len(line) > 0:
                    sent_list.append(line)
    if not output_dir.endswith('/'):
        output_dir += '/'
    with open(output_dir + title, 'w') as g:
        for line in sent_list:
            g.write(line + '\n')


def list_all_file(dir):
    file_list = []
    for root, dirnames, filenames in os.walk(dir):
        for filename in filenames:
            if 'DS_Store' in filename:
                continue
            file_list.append(os.path.join(root,filename))
    return file_list


if __name__ == '__main__':
    # usage
    if len(sys.argv) != 3:
        print 'Usage: python parse_html.py <input dir> <output dir>'
        sys.exit(-1)
    main(sys.argv)