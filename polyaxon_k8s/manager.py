# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from kubernetes import client, config
from kubernetes.client.rest import ApiException

from polyaxon_k8s import constants
from polyaxon_k8s.exceptions import PolyaxonK8SError
from polyaxon_k8s.logger import logger


class K8SManager(object):
    def __init__(self, k8s_config=None, namespace="default", in_cluster=False):
        if not k8s_config:
            if in_cluster:
                config.load_incluster_config()
            else:
                config.load_kube_config()
            api_client = None
        else:
            api_client = client.api_client.ApiClient(configuration=k8s_config)

        self.k8s_api = client.CoreV1Api(api_client)
        self.k8s_batch_api = client.BatchV1Api(api_client)
        self.k8s_apps_api = client.AppsV1Api(api_client)
        self.networking_v1_beta1_api = client.NetworkingV1beta1Api(api_client)
        self.k8s_custom_object_api = client.CustomObjectsApi()
        self.k8s_version_api = client.VersionApi(api_client)
        self.namespace = namespace
        self.in_cluster = in_cluster

    def set_namespace(self, namespace):
        self.namespace = namespace

    def get_version(self, reraise=False):
        try:
            return self.k8s_version_api.get_code().to_dict()
        except ApiException as e:
            logger.error("K8S error: {}".format(e))
            if reraise:
                raise PolyaxonK8SError(e)

    def _list_namespace_resource(self, labels, resource_api, reraise=False, **kwargs):
        try:
            res = resource_api(
                namespace=self.namespace, label_selector=labels, **kwargs
            )
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
        return self._list_namespace_resource(
            labels=labels,
            resource_api=self.k8s_api.list_namespaced_pod,
            reraise=reraise,
            include_uninitialized=include_uninitialized,
        )

    def list_jobs(self, labels, include_uninitialized=True, reraise=False):
        return self._list_namespace_resource(
            labels=labels,
            resource_api=self.k8s_batch_api.list_namespaced_job,
            reraise=reraise,
            include_uninitialized=include_uninitialized,
        )

    def list_custom_objects(self, labels, group, version, plural, reraise=False):
        return self._list_namespace_resource(
            labels=labels,
            resource_api=self.k8s_custom_object_api.list_namespaced_custom_object,
            reraise=reraise,
            group=group,
            version=version,
            plural=plural,
        )

    def list_services(self, labels, reraise=False):
        return self._list_namespace_resource(
            labels=labels,
            resource_api=self.k8s_api.list_namespaced_service,
            reraise=reraise,
        )

    def list_deployments(self, labels, reraise=False):
        return self._list_namespace_resource(
            labels=labels,
            resource_api=self.k8s_apps_api.list_namespaced_deployment,
            reraise=reraise,
        )

    def list_ingresses(self, labels, reraise=False):
        return self._list_namespace_resource(
            labels=labels,
            resource_api=self.networking_v1_beta1_api.list_namespaced_ingress,
            reraise=reraise,
        )

    def update_node_labels(self, node, labels, reraise=False):
        body = {"metadata": {"labels": labels}, "namespace": self.namespace}
        try:
            return self.k8s_api.patch_node(name=node, body=body)
        except ApiException as e:
            logger.error("K8S error: {}".format(e))
            if reraise:
                raise PolyaxonK8SError(e)

    def create_config_map(self, name, body):
        resp = self.k8s_api.create_namespaced_config_map(
            namespace=self.namespace, body=body
        )
        logger.debug("Config map `{}` was created".format(name))
        return resp

    def update_config_map(self, name, body):
        resp = self.k8s_api.patch_namespaced_config_map(
            name=name, namespace=self.namespace, body=body
        )
        logger.debug("Config map `{}` was patched".format(name))
        return resp

    def create_or_update_config_map(self, name, body, reraise=False):
        try:
            return self.create_config_map(name=name, body=body)
        except ApiException:
            try:
                return self.update_config_map(name=name, body=body)
            except ApiException as e:
                if reraise:
                    raise PolyaxonK8SError(e)
                else:
                    logger.error("K8S error: {}".format(e))

    def create_secret(self, name, body):
        resp = self.k8s_api.create_namespaced_secret(
            namespace=self.namespace, body=body
        )
        logger.debug("Secret `{}` was created".format(name))
        return resp

    def update_secret(self, name, body):
        resp = self.k8s_api.patch_namespaced_secret(
            name=name, namespace=self.namespace, body=body
        )
        logger.debug("Secret `{}` was patched".format(name))
        return resp

    def create_or_update_secret(self, name, body, reraise=False):
        try:
            return self.create_secret(name=name, body=body), True
        except ApiException:
            try:
                return self.update_secret(name=name, body=body), False
            except ApiException as e:
                if reraise:
                    raise PolyaxonK8SError(e)
                else:
                    logger.error("K8S error: {}".format(e))

    def create_service(self, name, body):
        resp = self.k8s_api.create_namespaced_service(
            namespace=self.namespace, body=body
        )
        logger.debug("Service `{}` was created".format(name))
        return resp

    def update_service(self, name, body):
        resp = self.k8s_api.patch_namespaced_service(
            name=name, namespace=self.namespace, body=body
        )
        logger.debug("Service `{}` was patched".format(name))
        return resp

    def create_or_update_service(self, name, body, reraise=False):
        try:
            return self.create_service(name=name, body=body), True
        except ApiException:
            try:
                return self.update_service(name=name, body=body), False
            except ApiException as e:
                if reraise:
                    raise PolyaxonK8SError(e)
                else:
                    logger.error("K8S error: {}".format(e))

    def create_pod(self, name, body):
        resp = self.k8s_api.create_namespaced_pod(namespace=self.namespace, body=body)
        logger.debug("Pod `{}` was created".format(name))
        return resp

    def update_pod(self, name, body):
        resp = self.k8s_api.patch_namespaced_pod(
            name=name, namespace=self.namespace, body=body
        )
        logger.debug("Pod `{}` was patched".format(name))
        return resp

    def create_or_update_pod(self, name, body, reraise=False):
        try:
            return self.create_pod(name=name, body=body), True
        except ApiException:
            try:
                return self.update_pod(name=name, body=body), False
            except ApiException as e:
                if reraise:
                    raise PolyaxonK8SError(e)
                else:
                    logger.error("K8S error: {}".format(e))

    def create_job(self, name, body):
        resp = self.k8s_batch_api.create_namespaced_job(
            namespace=self.namespace, body=body
        )
        logger.debug("Job `{}` was created".format(name))
        return resp

    def update_job(self, name, body):
        resp = self.k8s_batch_api.patch_namespaced_job(
            name=name, namespace=self.namespace, body=body
        )
        logger.debug("Job `{}` was patched".format(name))
        return resp

    def create_or_update_job(self, name, body, reraise=False):
        try:
            return self.create_job(name=name, body=body), True
        except ApiException:
            try:
                return self.update_job(name=name, body=body), False
            except ApiException as e:
                if reraise:
                    raise PolyaxonK8SError(e)
                else:
                    logger.error("K8S error: {}".format(e))

    def create_custom_object(self, name, group, version, plural, body):
        resp = self.k8s_custom_object_api.create_namespaced_custom_object(
            group=group,
            version=version,
            plural=plural,
            namespace=self.namespace,
            body=body,
        )
        logger.debug("Custom object `{}` was created".format(name))
        return resp

    def update_custom_object(self, name, group, version, plural, body):
        resp = self.k8s_custom_object_api.patch_namespaced_custom_object(
            name=name,
            group=group,
            version=version,
            plural=plural,
            namespace=self.namespace,
            body=body,
        )
        logger.debug("Custom object `{}` was patched".format(name))
        return resp

    def create_or_update_custom_object(
        self, name, group, version, plural, body, reraise=False
    ):
        try:
            return (
                self.create_custom_object(
                    name=name, group=group, version=version, plural=plural, body=body
                ),
                True,
            )

        except ApiException:
            try:
                return (
                    self.update_custom_object(
                        name=name,
                        group=group,
                        version=version,
                        plural=plural,
                        body=body,
                    ),
                    False,
                )
            except ApiException as e:
                if reraise:
                    raise PolyaxonK8SError(e)
                else:
                    logger.error("K8S error: {}".format(e))

    def create_deployment(self, name, body):
        resp = self.k8s_apps_api.create_namespaced_deployment(
            namespace=self.namespace, body=body
        )
        logger.debug("Deployment `{}` was created".format(name))
        return resp

    def update_deployment(self, name, body):
        resp = self.k8s_apps_api.patch_namespaced_deployment(
            name=name, namespace=self.namespace, body=body
        )
        logger.debug("Deployment `{}` was patched".format(name))
        return resp

    def create_or_update_deployment(self, name, body, reraise=False):
        try:
            return self.create_deployment(name=name, body=body), True
        except ApiException:
            try:
                return self.update_deployment(name=name, body=body), False
            except ApiException as e:
                if reraise:
                    raise PolyaxonK8SError(e)
                else:
                    logger.error("K8S error: {}".format(e))

    def create_volume(self, name, body):
        resp = self.k8s_api.create_persistent_volume(body=body)
        logger.debug("Persistent volume `{}` was created".format(name))
        return resp

    def update_volume(self, name, body):
        resp = self.k8s_api.patch_persistent_volume(name=name, body=body)
        logger.debug("Persistent volume `{}` was patched".format(name))
        return resp

    def create_or_update_volume(self, name, body, reraise=False):
        try:
            return self.create_volume(name=name, body=body), True
        except ApiException as e:
            try:
                return self.update_service(name=name, body=body), False
            except ApiException as e:
                if reraise:
                    raise PolyaxonK8SError(e)
                else:
                    logger.error("K8S error: {}".format(e))

    def create_volume_claim(self, name, body):
        resp = self.k8s_api.create_namespaced_persistent_volume_claim(
            namespace=self.namespace, body=body
        )
        logger.debug("Volume claim `{}` was created".format(name))
        return resp

    def update_volume_claim(self, name, body):
        resp = self.k8s_api.patch_namespaced_persistent_volume_claim(
            name=name, namespace=self.namespace, body=body
        )
        logger.debug("Volume claim `{}` was patched".format(name))
        return resp

    def create_or_update_volume_claim(self, name, body, reraise=False):
        try:
            return self.create_volume_claim(name=name, body=body), True
        except ApiException:
            try:
                return self.update_volume_claim(name=name, body=body), False
            except ApiException as e:
                if reraise:
                    raise PolyaxonK8SError(e)
                else:
                    logger.error("K8S error: {}".format(e))

    def create_ingress(self, name, body):
        resp = self.networking_v1_beta1_api.create_namespaced_ingress(
            namespace=self.namespace, body=body
        )
        logger.debug("ingress `{}` was created".format(name))
        return resp

    def update_ingress(self, name, body):
        resp = self.networking_v1_beta1_api.patch_namespaced_ingress(
            name=name, namespace=self.namespace, body=body
        )
        logger.debug("Ingress `{}` was patched".format(name))
        return resp

    def create_or_update_ingress(self, name, body, reraise=False):
        try:
            return self.create_ingress(name=name, body=body), True
        except ApiException:
            try:
                return self.update_ingress(name=name, body=body), False
            except ApiException as e:
                if reraise:
                    raise PolyaxonK8SError(e)
                else:
                    logger.error("K8S error: {}".format(e))

    def get_config_map(self, name, reraise=False):
        try:
            return self.k8s_api.read_namespaced_config_map(
                name=name, namespace=self.namespace
            )
        except ApiException as e:
            if reraise:
                raise PolyaxonK8SError(e)
            return None

    def get_secret(self, name, reraise=False):
        try:
            return self.k8s_api.read_namespaced_secret(
                name=name, namespace=self.namespace
            )
        except ApiException as e:
            if reraise:
                raise PolyaxonK8SError(e)
            return None

    def get_service(self, name, reraise=False):
        try:
            return self.k8s_api.read_namespaced_service(
                name=name, namespace=self.namespace
            )
        except ApiException as e:
            if reraise:
                raise PolyaxonK8SError(e)
            return None

    def get_pod(self, name, reraise=False):
        try:
            return self.k8s_api.read_namespaced_pod(name=name, namespace=self.namespace)
        except ApiException as e:
            if reraise:
                raise PolyaxonK8SError(e)
            return None

    def get_job(self, name, reraise=False):
        try:
            return self.k8s_batch_api.read_namespaced_job(
                name=name, namespace=self.namespace
            )
        except ApiException as e:
            if reraise:
                raise PolyaxonK8SError(e)
            return None

    def get_custom_object(self, name, group, version, plural, reraise=False):
        try:
            return self.k8s_custom_object_api.get_namespaced_custom_object(
                name=name,
                group=group,
                version=version,
                plural=plural,
                namespace=self.namespace,
            )
        except ApiException as e:
            if reraise:
                raise PolyaxonK8SError(e)
            return None

    def get_deployment(self, name, reraise=False):
        try:
            return self.k8s_apps_api.read_namespaced_deployment(
                name=name, namespace=self.namespace
            )
        except ApiException as e:
            if reraise:
                raise PolyaxonK8SError(e)
            return None

    def get_volume(self, name, reraise=False):
        try:
            return self.k8s_api.read_persistent_volume(name=name)
        except ApiException as e:
            if reraise:
                raise PolyaxonK8SError(e)
            return None

    def get_volume_claim(self, name, reraise=False):
        try:
            return self.k8s_api.read_namespaced_persistent_volume_claim(
                name=name, namespace=self.namespace
            )
        except ApiException as e:
            if reraise:
                raise PolyaxonK8SError(e)
            return None

    def get_ingress(self, name, reraise=False):
        try:
            return self.networking_v1_beta1_api.read_namespaced_ingress(
                name=name, namespace=self.namespace
            )
        except ApiException as e:
            if reraise:
                raise PolyaxonK8SError(e)
            return None

    def delete_config_map(self, name, reraise=False):
        try:
            self.k8s_api.delete_namespaced_config_map(
                name=name,
                namespace=self.namespace,
                body=client.V1DeleteOptions(api_version=constants.K8S_API_VERSION_V1),
            )
            logger.debug("Config map `{}` Deleted".format(name))
        except ApiException as e:
            if reraise:
                raise PolyaxonK8SError(e)
            else:
                logger.debug("Config map `{}` was not found".format(name))

    def delete_secret(self, name, reraise=False):
        try:
            self.k8s_api.delete_namespaced_secret(
                name=name,
                namespace=self.namespace,
                body=client.V1DeleteOptions(api_version=constants.K8S_API_VERSION_V1),
            )
            logger.debug("secret `{}` Deleted".format(name))
        except ApiException as e:
            if reraise:
                raise PolyaxonK8SError(e)
            else:
                logger.debug("secret `{}` was not found".format(name))

    def delete_service(self, name, reraise=False):
        try:
            self.k8s_api.delete_namespaced_service(
                name=name,
                namespace=self.namespace,
                body=client.V1DeleteOptions(api_version=constants.K8S_API_VERSION_V1),
            )
            logger.debug("Service `{}` deleted".format(name))
        except ApiException as e:
            if reraise:
                raise PolyaxonK8SError(e)
            else:
                logger.debug("Service `{}` was not found".format(name))

    def delete_pod(self, name, reraise=False):
        try:
            self.k8s_api.delete_namespaced_pod(
                name=name,
                namespace=self.namespace,
                body=client.V1DeleteOptions(api_version=constants.K8S_API_VERSION_V1),
            )
            logger.debug("Pod `{}` deleted".format(name))
        except ApiException as e:
            if reraise:
                raise PolyaxonK8SError(e)
            else:
                logger.debug("Pod `{}` was not found".format(name))

    def delete_job(self, name, reraise=False):
        try:
            self.k8s_batch_api.delete_namespaced_job(
                name=name,
                namespace=self.namespace,
                body=client.V1DeleteOptions(api_version=constants.K8S_API_VERSION_V1),
            )
            logger.debug("Pod `{}` deleted".format(name))
        except ApiException as e:
            if reraise:
                raise PolyaxonK8SError(e)
            else:
                logger.debug("Pod `{}` was not found".format(name))

    def delete_custom_object(self, name, group, version, plural, reraise=False):
        try:
            self.k8s_custom_object_api.delete_namespaced_custom_object(
                name=name,
                group=group,
                version=version,
                plural=plural,
                namespace=self.namespace,
                body=client.V1DeleteOptions(),
            )
            logger.debug("Custom object `{}` deleted".format(name))
        except ApiException as e:
            if reraise:
                raise PolyaxonK8SError(e)
            else:
                logger.debug("Custom object `{}` was not found".format(name))

    def delete_deployment(self, name, reraise=False):
        try:
            self.k8s_apps_api.delete_namespaced_deployment(
                name=name,
                namespace=self.namespace,
                body=client.V1DeleteOptions(
                    api_version=constants.K8S_API_VERSION_APPS_V1,
                    propagation_policy="Foreground",
                ),
            )
            logger.debug("Deployment `{}` deleted".format(name))
        except ApiException as e:
            if reraise:
                raise PolyaxonK8SError(e)
            else:
                logger.debug("Deployment `{}` was not found".format(name))

    def delete_volume(self, name, reraise=False):
        try:
            self.k8s_api.delete_persistent_volume(
                name=name,
                body=client.V1DeleteOptions(api_version=constants.K8S_API_VERSION_V1),
            )
            logger.debug("Volume `{}` Deleted".format(name))
        except ApiException as e:
            if reraise:
                raise PolyaxonK8SError(e)
            else:
                logger.debug("Volume `{}` was not found".format(name))

    def delete_volume_claim(self, name, reraise=False):
        try:
            self.k8s_api.delete_namespaced_persistent_volume_claim(
                name=name,
                namespace=self.namespace,
                body=client.V1DeleteOptions(api_version=constants.K8S_API_VERSION_V1),
            )
            logger.debug("Volume claim `{}` Deleted".format(name))
        except ApiException as e:
            if reraise:
                raise PolyaxonK8SError(e)
            else:
                logger.debug("Volume claim `{}` was not found".format(name))

    def delete_ingress(self, name, reraise=False):
        try:
            self.networking_v1_beta1_api.delete_namespaced_ingress(
                name=name,
                namespace=self.namespace,
                body=client.V1DeleteOptions(
                    api_version=constants.K8S_API_VERSION_NETWORKING_V1_BETA1,
                    propagation_policy="Foreground",
                ),
            )
            logger.debug("Ingress `{}` deleted".format(name))
        except ApiException as e:
            if reraise:
                raise PolyaxonK8SError(e)
            else:
                logger.debug("Ingress `{}` was not found".format(name))

    def delete_pods(self, labels, include_uninitialized=True, reraise=False):
        objs = self.list_pods(
            labels=labels, include_uninitialized=include_uninitialized, reraise=reraise
        )
        for obj in objs:
            self.delete_pod(name=obj.metadata.name, reraise=reraise)

    def delete_jobs(self, labels, include_uninitialized=True, reraise=False):
        objs = self.list_jobs(
            labels=labels, include_uninitialized=include_uninitialized, reraise=reraise
        )
        for obj in objs:
            self.delete_job(name=obj.metadata.name, reraise=reraise)

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
