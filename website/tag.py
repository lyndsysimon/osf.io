from modularodm import fields

class TaggableMixin(object):

    tags = fields.ForeignField('tag', list=True, backref='tagged')

    def _resolve_node(self):
        from website.models import Node
        return self if isinstance(self, Node) else self.node

    def add_tag(self, tag, auth, save=True):
        from website.models import Tag, NodeLog

        if tag not in self.tags:
            new_tag = Tag.load(tag)
            if not new_tag:
                new_tag = Tag(_id=tag)
            new_tag.save()
            self.tags.append(new_tag)
            self.add_log(
                action=NodeLog.TAG_ADDED,
                params={
                    'parent_node': self.parent_id,
                    'node': self._resolve_node()._primary_key,
                    'tag': tag,
                },
                auth=auth,
                save=False,
            )
            if save:
                self.save()