from django.contrib.auth import get_user_model
from django.db.models import Count, OuterRef, Subquery, Value
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.v1.permissions import IsStudentOrIsAdmin, ReadOnlyOrIsAdmin
from api.v1.serializers.course_serializer import (CourseSerializer,
                                                  CreateCourseSerializer,
                                                  CreateGroupSerializer,
                                                  CreateLessonSerializer,
                                                  GroupSerializer,
                                                  LessonSerializer)
from api.v1.serializers.user_serializer import SubscriptionSerializer
from courses.models import Course, Group, Lesson
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
        return (course.groups
                .select_related('course')
                .prefetch_related('students'))


class CourseViewSet(viewsets.ModelViewSet):
    """Курсы."""

    queryset = Course.objects.select_related(
        'author').prefetch_related('lessons')

    permission_classes = (ReadOnlyOrIsAdmin,)

    def get_queryset(self):
        student_count_subquery = Subscription.objects.filter(
            course=OuterRef('pk')
        ).values(
            'course'
        ).annotate(
            count=Count('user')
        ).values('count')

        group_count_subquery = Group.objects.filter(
            course=OuterRef('pk')
        ).values(
            'course'
        ).annotate(
            count=Count('pk')
        ).values('count')

        lesson_count_subquery = Lesson.objects.filter(
            course=OuterRef('pk')
        ).values(
            'course'
        ).annotate(
            count=Count('pk')
        ).values('count')

        queryset = super().get_queryset().annotate(
            students_count=Coalesce(
                Subquery(student_count_subquery), Value(0)
            ),
            groups_count=Coalesce(
                Subquery(group_count_subquery), Value(0)
            ),
            lessons_count=Coalesce(
                Subquery(lesson_count_subquery), Value(0)
            ),
        )
        user = self.request.user
        if user.is_authenticated:
            queryset = queryset.exclude(students__user=user)
        return queryset

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve',]:
            return CourseSerializer
        elif self.action in ('pay', ):
            return SubscriptionSerializer
        return CreateCourseSerializer

    def get_serializer_context(self):
        total_users_count = User.objects.filter(is_active=True).count()
        context = super().get_serializer_context()
        context['total_users_count'] = total_users_count
        return context

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
