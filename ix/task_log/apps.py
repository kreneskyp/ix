from django.apps import AppConfig


class TaskAppConfig(AppConfig):
    name = "ix.task_log"

    def ready(self):
        from django.db.models.signals import post_save
        from ix.schema.subscriptions import ChatArtifactSubscription
        from ix.task_log.models import Artifact

        # attach signal handler to report new artifacts to subscribed chat clients
        post_save.connect(ChatArtifactSubscription.new_artifact, sender=Artifact)
