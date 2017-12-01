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


def to_bytes(size_str):
    unit_multiplier = {
        'Ki': 1024,
        'Mi': 1024 ** 2,
        'Gi': 1024 ** 3,
        'Ti': 1024 ** 4
    }

    return int(size_str[:-2]) * unit_multiplier.get(size_str[-2:], 1)


class NodeLifeCycle(object):
    UNKNOWN = UNKNOWN
    READY = 'Ready'
    NOT_READY = 'NotReady'
    DELETED = 'Deleted'

    CHOICES = (
        (UNKNOWN, UNKNOWN),
        (READY, READY),
        (NOT_READY, NOT_READY),
        (DELETED, DELETED)
    )


class NodeRoles(object):
    MASTER = 'Master'
    WORKER = 'Worker'

    CHOICES = (
        (MASTER, MASTER),
        (WORKER, WORKER)
    )


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
    CONTAINER_CREATING = 'ContainerCreating'
    PENDING = 'Pending'
    RUNNING = 'Running'
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
    """Experiment lifecycle

    Props:
        * CREATED: created.
        * BUILDING: This includes time before being bound to a node,
                    as well as time spent pulling images onto the host.
        * RUNNING: The pod has been bound to a node and all of the containers have been started.
        * SUCCEEDED: All containers in the pod have voluntarily terminated with a
                     container exit code of 0, and the system is
                     not going to restart any of these containers.
        * FAILED: All containers in the pod have terminated,
                  and at least one container has terminated in a failure.
        * DELETED: was deleted/killed
        * UNKNOWN: For some reason the state of the pod could not be obtained,
                   typically due to an error in communicating with the host of the pod.
    """
    CREATED = 'Created'
    BUILDING = 'Building'
    RUNNING = 'Running'
    SUCCEEDED = 'Succeeded'
    FAILED = 'Failed'
    DELETED = 'Deleted'
    UNKNOWN = UNKNOWN

    CHOICES = (
        (CREATED, CREATED),
        (BUILDING, BUILDING),
        (RUNNING, RUNNING),
        (SUCCEEDED, SUCCEEDED),
        (FAILED, FAILED),
        (DELETED, DELETED),
        (UNKNOWN, UNKNOWN),
    )

    STARTING_STATUS = [CREATED, BUILDING]
    RUNNING_STATUS = [BUILDING, RUNNING]
    DONE_STATUS = [FAILED, DELETED, SUCCEEDED]

    @classmethod
    def is_starting(cls, status):
        return status in cls.STARTING_STATUS

    @classmethod
    def is_running(cls, status):
        return status in cls.RUNNING_STATUS

    @classmethod
    def is_deletable(cls, status):
        return not cls.is_done(status)

    @classmethod
    def is_done(cls, status):
        return status in cls.DONE_STATUS


class ExperimentLifeCycle(object):
    """Experiment lifecycle

    Props:
        * CREATED: created and waiting to be scheduled
        * SCHEDULED: scheduled waiting to be picked
        * STARTING: picked and is starting (jobs are created/building/pending)
        * RUNNING: one or all jobs is still running
        * SUCCEEDED: master and workers have finished successfully
        * FAILED: one of the jobs has failed
        * DELETED: was deleted/killed
        * UNKNOWN: unknown state
    """
    CREATED = 'Created'
    SCHEDULED = 'Scheduled'
    STARTING = 'Starting'
    RUNNING = 'Running'
    SUCCEEDED = 'Succeeded'
    FAILED = 'Failed'
    DELETED = 'Deleted'
    UNKNOWN = UNKNOWN

    CHOICES = (
        (CREATED, CREATED),
        (SCHEDULED, SCHEDULED),
        (STARTING, STARTING),
        (RUNNING, RUNNING),
        (SUCCEEDED, SUCCEEDED),
        (FAILED, FAILED),
        (DELETED, DELETED),
        (UNKNOWN, UNKNOWN),
    )

    RUNNING_STATUS = [STARTING, RUNNING]
    DONE_STATUS = [FAILED, DELETED, SUCCEEDED]

    @staticmethod
    def is_starting(job_statuses):
        return any([True for job_status in job_statuses if JobLifeCycle.is_starting(job_status)])

    @staticmethod
    def is_running(job_statuses):
        return any([True for job_status in job_statuses if JobLifeCycle.is_running(job_status)])

    @staticmethod
    def is_succeeded(job_statuses):
        return all([True for job_status in job_statuses if job_status == JobLifeCycle.SUCCEEDED])

    @staticmethod
    def is_failed(job_statuses):
        return any([True for job_status in job_statuses if job_status == JobLifeCycle.FAILED])

    @staticmethod
    def is_deleted(job_statuses):
        return any([True for job_status in job_statuses if job_status == JobLifeCycle.DELETED])

    @staticmethod
    def is_deletable(job_statuses):
        return all([True for job_status in job_statuses if JobLifeCycle.is_deletable(job_status)])

    @classmethod
    def is_running(cls, status):
        return status in cls.RUNNING_STATUS

    @classmethod
    def is_done(cls, status):
        return status in cls.DONE_STATUS
