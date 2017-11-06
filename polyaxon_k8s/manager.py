# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from kubernetes import client, config
from kubernetes.client.rest import ApiException

from polyaxon_k8s import constants
from polyaxon_k8s.exceptions import PolyaxonK8SError
from polyaxon_k8s.logger import logger


class K8SManager(object):
    def __init__(self, k8s_config=None, namespace='default', in_cluster=False):
        if not k8s_config:
            if in_cluster:
                config.load_incluster_config()
            else:
                config.load_kube_config()
            api_client = None
        else:
            api_client = client.api_client.ApiClient(config=k8s_config)

        self.k8s_api = client.CoreV1Api(api_client)
        self.k8s_beta_api = client.ExtensionsV1beta1Api(api_client)
        self.k8s_version_api = client.VersionApi(api_client)
        self.namespace = namespace

    def get_version(self, reraise=False):
        try:
            return self.k8s_version_api.get_code().to_dict()
        except ApiException as e:
            logger.error("K8S error: {}".format(e))
            if reraise:
                raise PolyaxonK8SError(e)

    def get_node_items(self, reraise=False):
        try:
            res = self.k8s_api.list_node()
            return [p for p in res.items]
        except ApiException as e:
            logger.error("K8S error: {}".format(e))
            if reraise:
                raise PolyaxonK8SError(e)

    def update_node_labels(self, node, labels, reraise=False):
        body = {'metadata': {'labels': labels}}
        try:
            self.k8s_api.patch_node(node, body=body)
        except ApiException as e:
            logger.error("K8S error: {}".format(e))
            if reraise:
                raise PolyaxonK8SError(e)

    def create_or_update_config_map(self, name, body, reraise=False):
        config_map_found = False
        try:
            self.k8s_api.read_namespaced_config_map(name, self.namespace)
            config_map_found = True
            logger.debug('A config map with name `{}` was found'.format(name))
            self.k8s_api.patch_namespaced_config_map(name, self.namespace, body)
            logger.debug('Config map `{}` was patched'.format(name))
        except ApiException as e:
            if config_map_found:  # Config map was found but could not update, we need to raise
                logger.error("K8S error: {}".format(e))
                if reraise:
                    raise PolyaxonK8SError(e)
            else:
                self.k8s_api.create_namespaced_config_map(self.namespace, body)
                logger.debug('Config map `{}` was created'.format(name))

    def delete_config_map(self, name, reraise=False):
        config_map_found = False
        try:
            self.k8s_api.read_namespaced_config_map(name, self.namespace)
            config_map_found = True
            self.k8s_api.delete_namespaced_config_map(
                name,
                self.namespace,
                client.V1DeleteOptions(api_version=constants.K8S_API_VERSION_V1))
            logger.debug('Config map `{}` Deleted'.format(name))
        except ApiException as e:
            if config_map_found:
                logger.warning('Could not delete config map `{}`'.format(name))
                if reraise:
                    raise PolyaxonK8SError(e)
            else:
                logger.debug('Config map `{}` was not found'.format(name))

