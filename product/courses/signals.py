from django.db.models import Count
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from users.models import Subscription
from courses.models import Group


# После того, как доступ к курсу открыт, пользователя необходимо равномерно распределить в одну из 10 групп студентов.
@receiver(post_save, sender=Subscription)
def post_save_subscription(sender, instance: Subscription, created, **kwargs):
    # sender    ==  <class 'users.models.Subscription'>
    # instance  ==  <Subscription: Подписка - 14>
    # created   ==  True
    a = 1

    """
    Распределение нового студента в группу курса.
    course = models.ForeignKey(
        to=Course,
        on_delete=models.CASCADE,
        related_name='groups',
        verbose_name='Курс',
    )
    students = models.ManyToManyField(
        to=User,
    """

    if created:
        student = instance.user
        group_list = instance.course.groups.annotate(students_quantity=Count('students'))
        if group_list.count() == 0:
            min_group = instance.course.groups.create(title='auto-created-group')
        else:
            min_group = min(group_list, key=lambda group: group.students_quantity)
        min_group.students.add(student)
