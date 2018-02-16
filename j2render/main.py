from render import Render

import argparse
import logging
import errno
import os


def write_file(filepath, data):
    '''Write data to file, creating folders if don't exist'''

    logging.info("Writing {0}".format(filepath))

    try:
        os.makedirs(os.path.dirname(filepath))
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    with open(filepath, 'w') as fd:
        fd.write(data)
        fd.write("\n")


def configure():

    parser = argparse.ArgumentParser(
        description='Render resource templates with items',
    )

    parser.add_argument('-v', '--verbose', action='store_true',
                        help='enable debug output')

    parser.add_argument('-o', '--output', default='_output',
                        help='path to results')
    parser.add_argument('-r', '--resources', default='resources',
                        help='path to resource templates')
    parser.add_argument('-t', '--targets', default='targets',
                        help='path to targets')
    parser.add_argument('-T', '--target',
                        help='resource to render')
    parser.add_argument('-R', '--resource',
                        help='resource to render')
    parser.add_argument('-I', '--item',
                        help='name of the item file')

    args = parser.parse_args()

    return args


if __name__ == "__main__":

    args = configure()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    R = Render(
        resources_path=args.resources,
        params_path=args.targets,
    )

    rendered_data = R.render_item(
        item=args.item,
        target=args.target,
        resource=args.resource,
    )

    for filename, data in rendered_data:
        filepath = os.path.join(args.output, filename)
        logging.debug("Writing {0}".format(filepath))
        write_file(filepath, data)
