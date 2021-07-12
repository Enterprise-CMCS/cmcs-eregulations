# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

import mptt
import mptt.managers


def rebuild(apps, schema_editor):
    Regulation = apps.get_model('regcore', 'Regulation')
    Regulation.objects.filter(root=False).delete()

    # Bind manager
    manager = mptt.managers.TreeManager()
    manager.model = Regulation
    mptt.register(Regulation)
    manager.contribute_to_class(Regulation, 'objects')

    for root in Regulation.objects.all():
        serialized = {
            'text': root.text,
            'title': root.title,
            'label': root.label_string.split('-'),
            'node_type': root.node_type,
            'children': root.children,
        }
        root.delete()
        write_node(Regulation, serialized, root.version, root.label_string)


def write_node(Regulation, node, version, label_id):

    to_save = []
    labels_seen = set()

    def add_node(node, parent=None):
        label_tuple = tuple(node['label'])
        labels_seen.add(label_tuple)

        node['parent'] = parent
        to_save.append(node)
        for child in node['children']:
            add_node(child, parent=node)
    add_node(node)

    DMRegulations(Regulation).bulk_put(to_save, version, label_id)


def treeify(node, tree_id, pos=1, level=0):
    """Set tree properties in memory.
    """
    node['tree_id'] = tree_id
    node['level'] = level
    node['left'] = pos
    for child in node.get('children', []):
        pos = treeify(child, tree_id, pos=pos + 1, level=level + 1)
    pos = pos + 1
    node['right'] = pos
    return pos


def build_id(reg, version):
    return '{}:{}'.format(version, '-'.join(reg['label']))


class DMRegulations(object):
    def __init__(self, Regulation):
        self.Regulation = Regulation

    def _transform(self, reg, version):
        """Create the Django object"""
        return self.Regulation(
            id=build_id(reg, version),
            parent_id=(
                build_id(reg['parent'], version)
                if reg.get('parent')
                else None
            ),
            tree_id=reg['tree_id'],
            level=reg['level'],
            lft=reg['left'],
            rght=reg['right'],
            version=version,
            label_string='-'.join(reg['label']),
            text=reg['text'],
            title=reg.get('title', ''),
            node_type=reg['node_type'],
            root=(len(reg['label']) == 1),
        )

    def bulk_put(self, regs, version, root_label):
        """Store all reg objects"""
        # This does not handle subparts. Ignoring that for now
        self.Regulation.objects.filter(
            version=version,
            label_string__startswith=root_label).delete()
        treeify(regs[0], self.Regulation.objects._get_next_tree_id())
        self.Regulation.objects.bulk_create(
            [self._transform(r, version) for r in regs],
            batch_size=25)


class Migration(migrations.Migration):

    dependencies = [
        ('regcore', '0002_mptt_add_fields'),
    ]

    operations = [
#        migrations.RunPython(rebuild),
    ]
