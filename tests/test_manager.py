# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from unittest import TestCase

from kubernetes import client

from polyaxon_k8s.manager import K8SManager
from tests import base


class TestPolyaxonK8sManager(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = base.get_e2e_configuration()

    def test_spawner(self):
        k8s_manager = K8SManager(k8s_config=self.config)

        assert isinstance(k8s_manager.k8s_api, client.CoreV1Api)
        assert isinstance(k8s_manager.k8s_beta_api, client.ExtensionsV1beta1Api)
        assert isinstance(k8s_manager.k8s_version_api, client.VersionApi)
