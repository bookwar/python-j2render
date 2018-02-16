from param import ParamTree

from jinja2 import Environment, FileSystemLoader
import os
import logging


class Render():

    TMPL_EXT = ['j2']

    def __init__(self, resources_path, params_path):
        self.resources_path = resources_path
        self.params_path = params_path

        self.resources = next(os.walk(self.resources_path))[1]
        self.param_tree = ParamTree(fileroot=self.params_path)

        self.system_params = os.environ

    def render_item(self, target, resource, item, **kwargs):
        if not resource in self.resources:
            logging.error("No resource {0}".format(resource))
            return None

        templates_path = os.path.join(self.resources_path, resource)
        J2Env = Environment(loader=FileSystemLoader(templates_path))

        target_params = self.param_tree.get_target_params(
            target=target,
        )
        item_params = self.param_tree.get_item_params(
            target=target,
            resource=resource,
            item=item,
        )

        rendered_data = []

        for template in J2Env.list_templates(extensions=self.TMPL_EXT):
            output_filename = os.path.join(
                    resource,
                    os.path.splitext(item)[0],
                    os.path.splitext(template)[0],
            )
            output_data = J2Env.get_template(template).render(
                system=self.system_params,
                target=target_params,
                item=item_params,
                **kwargs
            )

            rendered_data.append((output_filename, output_data))

        return rendered_data

            

