import logging

from regulations.views.errors import NotInSubpart


logger = logging.getLogger(__name__)


def find_subpart(section, node, subpart=None):
    value = None
    if node['type'] == 'section' and node['identifier'][1] == section:
        if subpart is None:
            raise NotInSubpart()
        return subpart
    elif node['type'] == 'subpart' and node['children'] is not None:
        for child in node['children']:
            value = find_subpart(section, child, node['identifier'][0])
            if value is not None:
                break
    elif node['children'] is not None:
        for child in node['children']:
            value = find_subpart(section, child, subpart)
            if value is not None:
                break
    return value


def different(one, two):
    return one['identifier'] != two['identifier']


def merge_children(one, two):
    if different(one[len(one)-1], two):
        one.append(two)
        return
    merge_children(one[len(one)-1]['children'], two['children'][0])


def get_structure(parts):
    structure = [parts[0]['structure']]
    for part in parts[1:]:
        merge_children(structure, part['structure'])
    return structure
