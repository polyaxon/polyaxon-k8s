# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

K8S_API_VERSION_V1 = 'v1'
K8S_API_VERSION_V1_BETA1 = 'extensions/v1beta1'
K8S_PERSISTENT_VOLUME_KIND = 'PersistentVolume'
K8S_PERSISTENT_VOLUME_CLAIM_KIND = 'PersistentVolumeClaim'
K8S_CONFIG_MAP_KIND = 'ConfigMap'
K8S_POD_KIND = 'Pod'
K8S_POD_TEMPLATE_KIND = 'PodTemplate'
K8S_DEPLOYMENT_KIND = 'Deployment'
K8S_SERVICE_KIND = 'Service'
K8S_INGRESS_KIND = 'Ingress'

UNKNOWN = 'UNKNOWN'


class EventTypes(object):
    ADDED = 'ADDED'
    MODIFIED = 'MODIFIED'
    DELETED = 'DELETED'
    ERROR = 'ERROR'


class ContainerStatuses(object):
    RUNNING = 'running'
    WAITING = 'waiting'
    TERMINATED = 'terminated'


class PodConditions(object):
    READY = 'Ready'
    INITIALIZED = 'Initialized'
    SCHEDULED = 'PodScheduled'


class PodLifeCycle(object):
    RUNNING = 'Running'
    PENDING = 'Pending'
    CONTAINER_CREATING = 'ContainerCreating'
    SUCCEEDED = 'Succeeded'
    FAILED = 'Failed'
    UNKNOWN = UNKNOWN

    CHOICES = (
        (RUNNING, RUNNING),
        (PENDING, PENDING),
        (CONTAINER_CREATING, CONTAINER_CREATING),
        (SUCCEEDED, SUCCEEDED),
        (FAILED, FAILED),
    )


class JobLifeCycle(object):
    CREATED = 'Created'
    BUILDING = 'Building'
    PENDING = 'Pending'
    RUNNING = 'Running'
    PAUSING = 'Pausing'
    SUCCEEDED = 'Succeeded'
    FAILED = 'Failed'
    DELETED = 'Deleted'
    UNKNOWN = UNKNOWN

    CHOICES = (
        (CREATED, CREATED),
        (BUILDING, BUILDING),
        (PENDING, PENDING),
        (RUNNING, RUNNING),
        (PAUSING, PAUSING),
        (SUCCEEDED, SUCCEEDED),
        (FAILED, FAILED),
        (DELETED, DELETED),
        (UNKNOWN, UNKNOWN),
    )

    RUNNING_STATUS = [BUILDING, PENDING, RUNNING]
    DONE_STATUS = [FAILED, DELETED, SUCCEEDED]

    @classmethod
    def is_running(cls, status):
        return status in cls.RUNNING_STATUS

    @classmethod
    def is_deletable(cls, status):
        return not cls.is_done(status)

    @classmethod
    def is_done(cls, status):
        return status in cls.DONE_STATUS


class ExperimentLifeCycle(JobLifeCycle):
    SCHEDULED = 'Scheduled'
    STARTING = 'Starting'

    CHOICES = (
        (JobLifeCycle.CREATED, JobLifeCycle.CREATED),  # XP created to be executed
        (SCHEDULED, SCHEDULED),  # XP scheduled to be started
        (JobLifeCycle.BUILDING, JobLifeCycle.BUILDING),  # XP scheduled to be started
        (STARTING, STARTING),  # one of the jobs is still not running
        (JobLifeCycle.PENDING, JobLifeCycle.PENDING),  # one of the jobs is still pending
        (JobLifeCycle.RUNNING, JobLifeCycle.RUNNING),  # one of the jobs is still running
        (JobLifeCycle.SUCCEEDED, JobLifeCycle.SUCCEEDED),  # master and workers have finished
        (JobLifeCycle.FAILED, JobLifeCycle.FAILED),  # one of the jobs has failed
        (JobLifeCycle.DELETED, JobLifeCycle.DELETED),  # XP was killed
        (JobLifeCycle.UNKNOWN, JobLifeCycle.UNKNOWN),  # XP was killed
    )
