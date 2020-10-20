from django.template import TemplateDoesNotExist
from django.template.loader import get_template, select_template
from regulations.generator.node_types import label_to_text

from regulations.generator.sidebar.base import SidebarBase
# @todo - seems like code in `generator` shouldn't reach in to `views`?
from regulations.views.utils import layer_names


class Guidance(SidebarBase):
    """Help info; composed of subtemplates defined by the active layers"""
    shorthand = 'guidance'

    def context(self, http_client, request):
        t = select_template([
            'guidance/%s.html' % self.label_id,
            'guidance/blank.html',
        ])
        return {
            'subtemplate': t.render({
                'human_label_id': label_to_text(
                    self.label_parts, include_marker=True),
            }),
        }
