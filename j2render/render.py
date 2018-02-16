from param import ParamTree

from jinja2 import Environment, FileSystemLoader
import os
import logging


class RenderError(Exception):
    pass

def get_system_params(prefix="J2RENDER_"):

    system = {}

    env = os.environ

    for variable, value in os.environ.items():
        if variable.startswith(prefix):
            trimmed_variable = variable[len(prefix):]
            if trimmed_variable:
                system[trimmed_variable] = value
            else:
                logging.warning("Empty trimmed variable name for {0}={1}".format(variable, value))

    return system


class Render():

    TMPL_EXT = ['j2']

    def __init__(self, resources_path, params_path):
        self.resources_path = resources_path
        self.params_path = params_path

        self.resources = os.listdir(self.resources_path)
        self.param_tree = ParamTree(fileroot=self.params_path)

        self.system_params = get_system_params()

    def render_item(self, target, resource, item, **kwargs):
        if resource not in self.resources:
            raise RenderError("No resource {0}".format(resource))

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

        item_params.update(self.system_params)

        rendered_data = []

        for template in J2Env.list_templates(extensions=self.TMPL_EXT):
            output_filename = os.path.join(
                    resource,
                    os.path.splitext(item)[0],
                    os.path.splitext(template)[0],
            )
            output_data = J2Env.get_template(template).render(
                target=target_params,
                item=item_params,
                **kwargs
            )

            rendered_data.append((output_filename, output_data))

        return rendered_data
