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
            api_client = client.api_client.ApiClient(configuration=k8s_config)

        self.k8s_api = client.CoreV1Api(api_client)
        self.k8s_beta_api = client.ExtensionsV1beta1Api(api_client)
        self.k8s_version_api = client.VersionApi(api_client)
        self._namespace = namespace

    @property
    def namespace(self):
        return self._namespace

    def set_namespace(self, namespace):
        self._namespace = namespace

    def get_version(self, reraise=False):
        try:
            return self.k8s_version_api.get_code().to_dict()
        except ApiException as e:
            logger.error("K8S error: {}".format(e))
            if reraise:
                raise PolyaxonK8SError(e)

    def _list_namespace_resource(self, labels, resource_api, reraise=False, **kwargs):
        try:
            res = resource_api(self.namespace, label_selector=labels, **kwargs)
            return [p for p in res.items]
        except ApiException as e:
            logger.error("K8S error: {}".format(e))
            if reraise:
                raise PolyaxonK8SError(e)
            return []

    def list_nodes(self, reraise=False):
        try:
            res = self.k8s_api.list_node()
            return [p for p in res.items]
        except ApiException as e:
            logger.error("K8S error: {}".format(e))
            if reraise:
                raise PolyaxonK8SError(e)
            return []

    def list_pods(self, labels, include_uninitialized=True, reraise=False):
        return self._list_namespace_resource(labels=labels,
                                             resource_api=self.k8s_api.list_namespaced_pod,
                                             reraise=reraise,
                                             include_uninitialized=include_uninitialized)

    def list_services(self, labels, reraise=False):
        return self._list_namespace_resource(labels=labels,
                                             resource_api=self.k8s_api.list_namespaced_service,
                                             reraise=reraise)

    def list_deployments(self, labels, reraise=False):
        return self._list_namespace_resource(
            labels=labels,
            resource_api=self.k8s_beta_api.list_namespaced_deployment,
            reraise=reraise)

    def list_ingresses(self, labels, reraise=False):
        return self._list_namespace_resource(labels=labels,
                                             resource_api=self.k8s_beta_api.list_namespaced_ingress,
                                             reraise=reraise)

    def update_node_labels(self, node, labels, reraise=False):
        body = {'metadata': {'labels': labels}, 'namespace': self.namespace}
        try:
            return self.k8s_api.patch_node(node, body=body)
        except ApiException as e:
            logger.error("K8S error: {}".format(e))
            if reraise:
                raise PolyaxonK8SError(e)

    def create_or_update_config_map(self, name, body, reraise=False):
        found = False
        try:
            self.k8s_api.read_namespaced_config_map(name, self.namespace)
            found = True
            logger.debug('A config map with name `{}` was found'.format(name))
            resp = self.k8s_api.patch_namespaced_config_map(name, self.namespace, body)
            logger.debug('Config map `{}` was patched'.format(name))
        except ApiException as e:
            if found:  # Config map was found but could not update, we need to raise
                logger.error("K8S error: {}".format(e))
                if reraise:
                    raise PolyaxonK8SError(e)
                resp = None
            else:
                resp = self.k8s_api.create_namespaced_config_map(self.namespace, body)
                logger.debug('Config map `{}` was created'.format(name))
        return resp, not found

    def create_or_update_secret(self, name, body, reraise=False):
        found = False
        try:
            self.k8s_api.read_namespaced_secret(name, self.namespace)
            found = True
            logger.debug('A secret with name `{}` was found'.format(name))
            resp = self.k8s_api.patch_namespaced_secret(name, self.namespace, body)
            logger.debug('Secret `{}` was patched'.format(name))
        except ApiException as e:
            if found:  # Secret was found but could not update, we need to raise
                logger.error("K8S error: {}".format(e))
                if reraise:
                    raise PolyaxonK8SError(e)
                resp = None
            else:
                resp = self.k8s_api.create_namespaced_secret(self.namespace, body)
                logger.debug('Secret `{}` was created'.format(name))
        return resp, not found

    def create_or_update_service(self, name, data, reraise=False):
        found = False
        try:
            self.k8s_api.read_namespaced_service(name, self.namespace)
            found = True
            logger.debug('A service with name `{}` was found'.format(name))
            resp = self.k8s_api.patch_namespaced_service(name, self.namespace, data)
            logger.debug('Service `{}` was patched'.format(name))
        except ApiException as e:
            if found:
                logger.error('Could not create service `{}`'.format(name))
                if reraise:
                    raise PolyaxonK8SError(e)
                resp = None
            else:
                resp = self.k8s_api.create_namespaced_service(self.namespace, data)
                logger.debug('Service `{}` was created'.format(name))
        return resp, not found

    def create_or_update_pod(self, name, data, reraise=False):
        found = False
        try:
            self.k8s_api.read_namespaced_pod(name, self.namespace)
            found = True
            logger.debug('A pod with name `{}` was found'.format(name))
            resp = self.k8s_api.patch_namespaced_pod(name, self.namespace, data)
            logger.debug('Pod `{}` was patched'.format(name))
        except ApiException as e:
            if found:
                logger.error('Could not create pod `{}`'.format(name))
                if reraise:
                    raise PolyaxonK8SError(e)
                resp = None
            else:
                resp = self.k8s_api.create_namespaced_pod(self.namespace, data)
                logger.debug('Pod `{}` was created'.format(name))
        return resp, not found

    def create_or_update_deployment(self, name, data, reraise=False):
        found = False
        try:
            self.k8s_beta_api.read_namespaced_deployment(name, self.namespace)
            found = True
            logger.info('A deployment with name `{}` was found'.format(name))
            resp = self.k8s_beta_api.patch_namespaced_deployment(name, self.namespace, data)
            logger.info('Deployment `{}` was patched'.format(name))
        except ApiException as e:
            if found:
                logger.error('Could not create deployment `{}`'.format(name))
                if reraise:
                    raise PolyaxonK8SError(e)
                resp = None
            else:
                resp = self.k8s_beta_api.create_namespaced_deployment(self.namespace, data)
                logger.info('Deployment `{}` was created'.format(name))
        return resp, not found

    def create_or_update_volume(self, name, data, reraise=False):
        found = False
        try:
            self.k8s_api.read_persistent_volume(name)
            found = True
            logger.debug('A Persistent volume with name `{}` was found'.format(name))
            resp = self.k8s_api.patch_persistent_volume(name, data)
            logger.debug('Persistent volume `{}` was patched'.format(name))
        except ApiException as e:
            if found:
                logger.error('Could not create volume `{}`'.format(name))
                if reraise:
                    raise PolyaxonK8SError(e)
                resp = None
            else:
                resp = self.k8s_api.create_persistent_volume(data)
                logger.debug('Persistent volume `{}` was created'.format(name))
        return resp, not found

    def create_or_update_volume_claim(self, name, data, reraise=False):
        found = False
        try:
            self.k8s_api.read_namespaced_persistent_volume_claim(name, self.namespace)
            found = True
            logger.debug('A volume claim with name `{}` was found'.format(name))
            resp = self.k8s_api.patch_namespaced_persistent_volume_claim(name,
                                                                         self.namespace,
                                                                         data)
            logger.debug('Volume claim `{}` was patched'.format(name))
        except ApiException as e:
            if found:
                logger.error('Could not create volume claim `{}`'.format(name))
                if reraise:
                    raise PolyaxonK8SError(e)
                resp = None
            else:
                resp = self.k8s_api.create_namespaced_persistent_volume_claim(self.namespace, data)
                logger.debug('Volume claim `{}` was created'.format(name))
        return resp, not found

    def create_or_update_ingress(self, name, data, reraise=False):
        found = False
        try:
            self.k8s_beta_api.read_namespaced_ingress(name, self.namespace)
            found = True
            logger.debug('An ingress with name `{}` was found'.format(name))
            resp = self.k8s_beta_api.patch_namespaced_ingress(name, self.namespace, data)
            logger.debug('Ingress `{}` was patched'.format(name))
        except ApiException as e:
            if found:
                logger.error('Could not create ingress `{}`'.format(name))
                if reraise:
                    raise PolyaxonK8SError(e)
                resp = None
            else:
                resp = self.k8s_beta_api.create_namespaced_ingress(self.namespace, data)
                logger.debug('ingress `{}` was created'.format(name))
        return resp, not found

    def get_config_map(self, name, reraise=False):
        try:
            return self.k8s_api.read_namespaced_config_map(name, self.namespace)
        except ApiException as e:
            if reraise:
                raise PolyaxonK8SError(e)
            return None

    def get_secret(self, name, reraise=False):
        try:
            return self.k8s_api.read_namespaced_secret(name, self.namespace)
        except ApiException as e:
            if reraise:
                raise PolyaxonK8SError(e)
            return None

    def get_service(self, name, reraise=False):
        try:
            return self.k8s_api.read_namespaced_service(name, self.namespace)
        except ApiException as e:
            if reraise:
                raise PolyaxonK8SError(e)
            return None

    def get_pod(self, name, reraise=False):
        try:
            return self.k8s_api.read_namespaced_pod(name, self.namespace)
        except ApiException as e:
            if reraise:
                raise PolyaxonK8SError(e)
            return None

    def get_deployment(self, name, reraise=False):
        try:
            return self.k8s_beta_api.read_namespaced_deployment(name, self.namespace)
        except ApiException as e:
            if reraise:
                raise PolyaxonK8SError(e)
            return None

    def get_volume(self, name, reraise=False):
        try:
            return self.k8s_api.read_persistent_volume(name)
        except ApiException as e:
            if reraise:
                raise PolyaxonK8SError(e)
            return None

    def get_volume_claim(self, name, reraise=False):
        try:
            return self.k8s_api.read_namespaced_persistent_volume_claim(name, self.namespace)
        except ApiException as e:
            if reraise:
                raise PolyaxonK8SError(e)
            return None

    def get_ingress(self, name, reraise=False):
        try:
            return self.k8s_beta_api.read_namespaced_ingress(name, self.namespace)
        except ApiException as e:
            if reraise:
                raise PolyaxonK8SError(e)
            return None

    def delete_config_map(self, name, reraise=False):
        found = False
        try:
            self.k8s_api.read_namespaced_config_map(name, self.namespace)
            found = True
            self.k8s_api.delete_namespaced_config_map(
                name,
                self.namespace,
                client.V1DeleteOptions(api_version=constants.K8S_API_VERSION_V1))
            logger.debug('Config map `{}` Deleted'.format(name))
        except ApiException as e:
            if found:
                logger.error('Could not delete config map `{}`'.format(name))
                if reraise:
                    raise PolyaxonK8SError(e)
            else:
                logger.debug('Config map `{}` was not found'.format(name))

    def delete_secret(self, name, reraise=False):
        found = False
        try:
            self.k8s_api.read_namespaced_secret(name, self.namespace)
            found = True
            self.k8s_api.delete_namespaced_secret(
                name,
                self.namespace,
                client.V1DeleteOptions(api_version=constants.K8S_API_VERSION_V1))
            logger.debug('secret `{}` Deleted'.format(name))
        except ApiException as e:
            if found:
                logger.error('Could not delete secret `{}`'.format(name))
                if reraise:
                    raise PolyaxonK8SError(e)
            else:
                logger.debug('secret `{}` was not found'.format(name))

    def delete_service(self, name, reraise=False):
        found = False
        try:
            self.k8s_api.read_namespaced_service(name, self.namespace)
            found = True
            self.k8s_api.delete_namespaced_service(name, self.namespace)
            logger.debug('Service `{}` deleted'.format(name))
        except ApiException as e:
            if found:
                logger.error('Could not delete service `{}`'.format(name))
                if reraise:
                    raise PolyaxonK8SError(e)
            else:
                logger.debug('Service `{}` was not found'.format(name))

    def delete_pod(self, name, reraise=False):
        found = False
        try:
            self.k8s_api.read_namespaced_pod(name, self.namespace)
            found = True
            self.k8s_api.delete_namespaced_pod(
                name,
                self.namespace,
                client.V1DeleteOptions(api_version=constants.K8S_API_VERSION_V1))
            logger.debug('Pod `{}` deleted'.format(name))
        except ApiException as e:
            if found:
                logger.error('Could not delete pod `{}`'.format(name))
                if reraise:
                    raise PolyaxonK8SError(e)
            else:
                logger.debug('Pod `{}` was not found'.format(name))

    def delete_deployment(self, name, reraise=False):
        found = False
        try:
            self.k8s_beta_api.read_namespaced_deployment(name, self.namespace)
            found = True
            self.k8s_beta_api.delete_namespaced_deployment(
                name,
                self.namespace,
                client.V1DeleteOptions(api_version=constants.K8S_API_VERSION_V1_BETA1,
                                       propagation_policy='Foreground'))
            logger.debug('Deployment `{}` deleted'.format(name))
        except ApiException as e:
            if found:
                logger.error('Could not delete deployment `{}`'.format(name))
                if reraise:
                    raise PolyaxonK8SError(e)
            else:
                logger.debug('Deployment `{}` was not found'.format(name))

    def delete_volume(self, name, reraise=False):
        found = False
        try:
            self.k8s_api.read_persistent_volume(name)
            found = True
            self.k8s_api.delete_persistent_volume(
                name,
                client.V1DeleteOptions(api_version=constants.K8S_API_VERSION_V1))
            logger.debug('Volume `{}` Deleted'.format(name))
        except ApiException as e:
            if found:
                logger.error('Could not delete volume `{}`'.format(name))
                if reraise:
                    raise PolyaxonK8SError(e)
            else:
                logger.debug('Volume `{}` was not found'.format(name))

    def delete_volume_claim(self, name, reraise=False):
        found = False
        try:
            self.k8s_api.read_namespaced_persistent_volume_claim(name, self.namespace)
            found = True
            self.k8s_api.delete_namespaced_persistent_volume_claim(
                name,
                self.namespace,
                client.V1DeleteOptions(api_version=constants.K8S_API_VERSION_V1))
            logger.debug('Volume claim `{}` Deleted'.format(name))
        except ApiException as e:
            if found:
                logger.error('Could not delete volume claim `{}`'.format(name))
                if reraise:
                    raise PolyaxonK8SError(e)
            else:
                logger.debug('Volume claim `{}` was not found'.format(name))

    def delete_ingress(self, name, reraise=False):
        found = False
        try:
            self.k8s_beta_api.read_namespaced_ingress(name, self.namespace)
            found = True
            self.k8s_beta_api.delete_namespaced_ingress(
                name,
                self.namespace,
                client.V1DeleteOptions(api_version=constants.K8S_API_VERSION_V1_BETA1,
                                       propagation_policy='Foreground'))
            logger.debug('Ingress `{}` deleted'.format(name))
        except ApiException as e:
            if found:
                logger.error('Could not delete Ingress `{}`'.format(name))
                if reraise:
                    raise PolyaxonK8SError(e)
            else:
                logger.debug('Ingress `{}` was not found'.format(name))

    def delete_pods(self, labels, include_uninitialized=True, reraise=False):
        objs = self.list_pods(labels=labels,
                              include_uninitialized=include_uninitialized,
                              reraise=reraise)
        for obj in objs:
            self.delete_pod(name=obj.metadata.name, reraise=reraise)

    def delete_services(self, labels, reraise=False):
        objs = self.list_services(labels=labels, reraise=reraise)
        for obj in objs:
            self.delete_service(name=obj.metadata.name, reraise=reraise)

    def delete_deployments(self, labels, reraise=False):
        objs = self.list_deployments(labels=labels, reraise=reraise)
        for obj in objs:
            self.delete_deployment(name=obj.metadata.name, reraise=reraise)

    def delete_ingresses(self, labels, reraise=False):
        objs = self.list_services(labels=labels, reraise=reraise)
        for obj in objs:
            self.delete_ingress(name=obj.metadata.name, reraise=reraise)
