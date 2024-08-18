from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Avg, Count

from api.v1.permissions import IsStudentOrIsAdmin, ReadOnlyOrIsAdmin
from api.v1.serializers.course_serializer import (CourseSerializer,
                                                  CreateCourseSerializer,
                                                  CreateGroupSerializer,
                                                  CreateLessonSerializer,
                                                  GroupSerializer,
                                                  LessonSerializer)
from api.v1.serializers.user_serializer import SubscriptionSerializer
from courses.models import Course
from users.models import Subscription


User = get_user_model()


class LessonViewSet(viewsets.ModelViewSet):
    """Уроки."""

    permission_classes = (IsStudentOrIsAdmin,)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return LessonSerializer
        return CreateLessonSerializer

    def perform_create(self, serializer):
        course = get_object_or_404(Course, id=self.kwargs.get('course_id'))
        serializer.save(course=course)

    def get_queryset(self):
        course = get_object_or_404(Course, id=self.kwargs.get('course_id'))
        return course.lessons.all()


class GroupViewSet(viewsets.ModelViewSet):
    """Группы."""

    permission_classes = (permissions.IsAdminUser,)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return GroupSerializer
        return CreateGroupSerializer

    def perform_create(self, serializer):
        course = get_object_or_404(Course, id=self.kwargs.get('course_id'))
        serializer.save(course=course)

    def get_queryset(self):
        course = get_object_or_404(Course, id=self.kwargs.get('course_id'))
        return course.groups.prefetch_related('students')


class CourseViewSet(viewsets.ModelViewSet):
    """Курсы """

    queryset = Course.objects.select_related(
        'author',
    ).annotate(
        students_count=Count('students'),
        lessons_count=Count('lessons'),
    ).prefetch_related('lessons')

    permission_classes = (ReadOnlyOrIsAdmin,)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve',]:
            return CourseSerializer
        elif self.action in ('pay', ):
            return SubscriptionSerializer
        return CreateCourseSerializer

    def get_queryset(self):
        a = 1
        user = self.request.user
        queryset = super().get_queryset().exclude(students__user=user)
        return queryset

    # @action(
    #     detail=False,
    #     methods=['get', ],
    #     url_path='courses',
    #     url_name='courses',
    #     permission_classes=[
    #         # permissions.IsAdminUser,
    #         permissions.IsAuthenticated,
    #         # permissions.AllowAny,
    #     ],
    # )
    # def courses(self, request):
    #     return self.list(request)


# Реализовать API оплаты продукты за бонусы. Назовем его …/pay/ (3 балла)
# По факту оплаты и списания бонусов с баланса пользователя должен быть открыт доступ к курсу. (2 балла)
# api/v1/courses/1/pay


    @action(
        methods=['post'],
        url_path='pay',
        detail=True,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def pay(self, request, pk):
        """Покупка доступа к курсу (подписка на курс)."""
        serializer = self.get_serializer(
            data={
                'user': request.user.pk,
                'course': pk,
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            data=serializer.data,
            status=status.HTTP_201_CREATED,
        )
