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

    def create_or_update_config_map(self, name, body, namespace=None, reraise=False):
        namespace = namespace or self.namespace
        config_map_found = False
        try:
            self.k8s_api.read_namespaced_config_map(name, namespace)
            config_map_found = True
            logger.debug('A config map with name `{}` was found'.format(name))
            self.k8s_api.patch_namespaced_config_map(name, namespace, body)
            logger.debug('Config map `{}` was patched'.format(name))
        except ApiException as e:
            if config_map_found:  # Config map was found but could not update, we need to raise
                logger.error("K8S error: {}".format(e))
                if reraise:
                    raise PolyaxonK8SError(e)
            else:
                self.k8s_api.create_namespaced_config_map(namespace, body)
                logger.debug('Config map `{}` was created'.format(name))

    def delete_config_map(self, name, namespace=None, reraise=False):
        namespace = namespace or self.namespace
        config_map_found = False
        try:
            self.k8s_api.read_namespaced_config_map(name, namespace)
            config_map_found = True
            self.k8s_api.delete_namespaced_config_map(
                name,
                namespace,
                client.V1DeleteOptions(api_version=constants.K8S_API_VERSION_V1))
            logger.debug('Config map `{}` Deleted'.format(name))
        except ApiException as e:
            if config_map_found:
                logger.error('Could not delete config map `{}`'.format(name))
                if reraise:
                    raise PolyaxonK8SError(e)
            else:
                logger.debug('Config map `{}` was not found'.format(name))

    def create_or_update_service(self, name, data, namespace=None, reraise=False):
        namespace = namespace or self.namespace
        service_found = False
        try:
            self.k8s_api.read_namespaced_service(name, namespace)
            service_found = True
            logger.debug('A service with name `{}` was found'.format(name))
            self.k8s_api.patch_namespaced_service(name, namespace, data)
            logger.debug('Service `{}` was patched'.format(name))
        except ApiException as e:
            if service_found:
                logger.error('Could not create service `{}`'.format(name))
                if reraise:
                    raise PolyaxonK8SError(e)
            self.k8s_api.create_namespaced_service(namespace, data)
            logger.debug('Service `{}` was created'.format(name))

    def create_or_update_pod(self, name, data, namespace=None, reraise=False):
        namespace = namespace or self.namespace
        pod_found = False
        try:
            self.k8s_api.read_namespaced_pod(name, namespace)
            pod_found = True
            logger.debug('A pod with name `{}` was found'.format(name))
            self.k8s_api.patch_namespaced_pod(name, namespace, data)
            logger.debug('Pod `{}` was patched'.format(name))
        except ApiException as e:
            if pod_found:
                logger.error('Could not create pod `{}`'.format(name))
                if reraise:
                    raise PolyaxonK8SError(e)
            self.k8s_api.create_namespaced_pod(namespace, data)
            logger.debug('Pod `{}` was created'.format(name))

    def create_or_update_deployment(self, name, data, namespace=None, reraise=False):
        namespace = namespace or self.namespace
        deployment_found = False
        try:
            self.k8s_beta_api.read_namespaced_deployment(name, namespace)
            deployment_found = True
            logger.info('A deployment with name `{}` was found'.format(name))
            self.k8s_beta_api.patch_namespaced_deployment(name, namespace, data)
            logger.info('Deployment `{}` was patched'.format(name))
        except ApiException as e:
            if deployment_found:
                logger.error('Could not create deployment `{}`'.format(name))
                if reraise:
                    raise PolyaxonK8SError(e)
            self.k8s_beta_api.create_namespaced_deployment(namespace, data)
            logger.info('Deployment `{}` was created'.format(name))

    def delete_service(self, name, namespace=None, reraise=False):
        namespace = namespace or self.namespace
        service_found = False
        try:
            self.k8s_api.read_namespaced_service(name, namespace)
            service_found = True
            self.k8s_api.delete_namespaced_service(name, namespace)
            logger.debug('Service `{}` deleted'.format(name))
        except ApiException as e:
            if service_found:
                logger.error('Could not delete service `{}`'.format(name))
                if reraise:
                    raise PolyaxonK8SError(e)
            else:
                logger.debug('Service `{}` was not found'.format(name))

    def delete_pod(self, name, namespace=None, reraise=False):
        namespace = namespace or self.namespace
        pod_found = False
        try:
            self.k8s_api.read_namespaced_pod(name, namespace)
            pod_found = True
            self.k8s_api.delete_namespaced_pod(
                name,
                namespace,
                client.V1DeleteOptions(api_version=constants.K8S_API_VERSION_V1))
            logger.debug('Pod `{}` deleted'.format(name))
        except ApiException as e:
            if pod_found:
                logger.error('Could not delete pod `{}`'.format(name))
                if reraise:
                    raise PolyaxonK8SError(e)
            else:
                logger.debug('Pod `{}` was not found'.format(name))

    def delete_deployment(self, name, namespace, reraise=False):
        namespace = namespace or self.namespace
        deployment_found = False
        try:
            self.k8s_beta_api.read_namespaced_deployment(name, namespace)
            deployment_found = True
            self.k8s_beta_api.delete_namespaced_deployment(
                name,
                namespace,
                client.V1DeleteOptions(api_version=constants.K8S_API_VERSION_V1_BETA1,
                                       propagation_policy='Foreground'))
            logger.debug('Deployment `{}` deleted'.format(name))
        except ApiException as e:
            if deployment_found:
                logger.error('Could not delete deployment `{}`'.format(name))
                if reraise:
                    raise PolyaxonK8SError(e)
            else:
                logger.debug('Deployment `{}` was not found'.format(name))

    def create_or_update_volume(self, name, data, reraise=False):
        volume_found = False
        try:
            self.k8s_api.read_persistent_volume(name)
            volume_found = True
            logger.debug('A Persistent volume with name `{}` was found'.format(name))
            self.k8s_api.patch_persistent_volume(name, data)
            logger.debug('Persistent volume `{}` was patched'.format(name))
        except ApiException as e:
            if volume_found:
                logger.error('Could not create volume `{}`'.format(name))
                if reraise:
                    raise PolyaxonK8SError(e)
            self.k8s_api.create_persistent_volume(data)
            logger.debug('Persistent volume `{}` was created'.format(name))

    def create_or_update_volume_claim(self, name, data, namespace=None, reraise=False):
        namespace = namespace or self.namespace
        volume_claim_found = False
        try:
            self.k8s_api.read_namespaced_persistent_volume_claim(name, namespace)
            volume_claim_found = True
            logger.debug('A volume claim with name `{}` was found'.format(name))
            self.k8s_api.patch_namespaced_persistent_volume_claim(name,
                                                                  namespace,
                                                                  data)
            logger.debug('Volume claim `{}` was patched'.format(name))
        except ApiException as e:
            if volume_claim_found:
                logger.error('Could not create volume claim `{}`'.format(name))
                if reraise:
                    raise PolyaxonK8SError(e)
            self.k8s_api.create_namespaced_persistent_volume_claim(namespace, data)
            logger.debug('Volume claim `{}` was created'.format(name))

    def delete_volume(self, name, reraise=False):
        volume_found = False
        try:
            self.k8s_api.read_persistent_volume(name)
            volume_found = True
            self.k8s_api.delete_persistent_volume(
                name,
                client.V1DeleteOptions(api_version=constants.K8S_API_VERSION_V1))
            logger.debug('Volume `{}` Deleted'.format(name))
        except ApiException as e:
            if volume_found:
                logger.error('Could not delete volume `{}`'.format(name))
                if reraise:
                    raise PolyaxonK8SError(e)
            else:
                logger.debug('Volume `{}` was not found'.format(name))

    def delete_volume_claim(self, name, namespace=None, reraise=False):
        namespace = namespace or self.namespace
        volume_claim_found = False
        try:
            self.k8s_api.read_namespaced_persistent_volume_claim(name, namespace)
            volume_claim_found = True
            self.k8s_api.delete_namespaced_persistent_volume_claim(
                name,
                namespace,
                client.V1DeleteOptions(api_version=constants.K8S_API_VERSION_V1))
            logger.debug('Volume claim `{}` Deleted'.format(name))
        except ApiException as e:
            if volume_claim_found:
                logger.error('Could not delete volume claim `{}`'.format(name))
                if reraise:
                    raise PolyaxonK8SError(e)
            else:
                logger.debug('Volume claim `{}` was not found'.format(name))
