from django.apps import AppConfig


class ChatAppConfig(AppConfig):
    name = "ix.chat"

    def ready(self):
        # Connect the signal
        from ix.schema.subscriptions import ChatMessageSubscription
        from ix.task_log.models import TaskLogMessage
        from django.db.models.signals import post_save

        post_save.connect(
            ChatMessageSubscription.new_task_log_message, sender=TaskLogMessage
        )
