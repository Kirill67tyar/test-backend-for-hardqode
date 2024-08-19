from django.db.models import Count
from django.db.models.signals import post_save
from django.dispatch import receiver

from product.constants import NAME_AUTO_GROUP
from users.models import Subscription


@receiver(post_save, sender=Subscription)
def post_save_subscription(sender, instance: Subscription, created, **kwargs):

    if created:
        student = instance.user
        group_list = instance.course.groups.annotate(
            students_quantity=Count('students'))
        if group_list.count() == 0:
            min_group = instance.course.groups.create(
                title=NAME_AUTO_GROUP
            )
        else:
            min_group = min(
                group_list, key=lambda group: group.students_quantity
            )
        min_group.students.add(student)
