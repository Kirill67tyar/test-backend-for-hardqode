from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.serializers import ValidationError
from rest_framework.validators import UniqueTogetherValidator

from courses.models import Course, Group, Lesson
from product.constants import (COURSE_ALREADY_EXISTS, GROUP_ALREADY_EXISTS,
                               LESSON_ALREADY_EXISTS, MAX_QUANTITY_GROUPS)


User = get_user_model()


class LessonSerializer(serializers.ModelSerializer):
    """Список уроков."""

    course = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Lesson
        fields = (
            'title',
            'link',
            'course'
        )


class CreateLessonSerializer(serializers.ModelSerializer):
    """Создание уроков."""

    class Meta:
        model = Lesson
        fields = (
            'title',
            'link',
            'course'
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Lesson.objects.all(),
                fields=('title', 'course',),
                message=LESSON_ALREADY_EXISTS
            ),
        ]


class StudentSerializer(serializers.ModelSerializer):
    """Студенты курса."""

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
        )


class StudentSerializer(serializers.ModelSerializer):
    """Студенты курса."""

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
        )


class GroupSerializer(serializers.ModelSerializer):
    """Список групп."""

    course = serializers.SerializerMethodField(read_only=True)
    students = StudentSerializer(
        read_only=True,
        many=True,
    )

    class Meta:
        model = Group
        fields = (
            'title',
            'course',
            'students',
        )

    def get_course(self, obj):
        return obj.course.title


class CreateGroupSerializer(serializers.ModelSerializer):
    """Создание групп."""

    class Meta:
        model = Group
        fields = (
            'title',
            'course',
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Group.objects.all(),
                fields=('title', 'course',),
                message=GROUP_ALREADY_EXISTS
            ),
        ]

    def validate(self, data):
        course = data.get('course')
        if course.groups.count() == 10:
            raise ValidationError(
                {
                    'errors': MAX_QUANTITY_GROUPS,
                }
            )
        return data


class MiniLessonSerializer(serializers.ModelSerializer):
    """Список названий уроков для списка курсов."""

    class Meta:
        model = Lesson
        fields = (
            'title',
        )


class MiniGroupSerializer(serializers.ModelSerializer):
    """Список id групп в которых числится студент."""

    class Meta:
        model = Group
        fields = (
            'id',
            'course',
        )


class CourseSerializer(serializers.ModelSerializer):
    """Список курсов."""

    author = serializers.SerializerMethodField(read_only=True)
    lessons = MiniLessonSerializer(many=True, read_only=True)
    lessons_count = serializers.SerializerMethodField(read_only=True)
    students_count = serializers.SerializerMethodField(read_only=True)
    groups_filled_percent = serializers.SerializerMethodField(read_only=True)
    demand_course_percent = serializers.SerializerMethodField(read_only=True)

    def get_author(self, obj):
        """Количество уроков в курсе."""

        return (f'{obj.author.first_name.title()} '
                f'{obj.author.first_name.title()}')

    def get_lessons_count(self, obj):
        """Количество уроков в курсе."""

        return obj.lessons_count

    def get_students_count(self, obj):
        """Общее количество студентов на курсе."""

        return obj.students_count

    def get_groups_filled_percent(self, obj):
        """Процент заполнения групп, если в группе максимум 30 чел.."""

        if obj.groups_count > 0:
            return round(obj.students_count / (obj.groups_count * 30 / 100), 2)
        return 0.0

    def get_demand_course_percent(self, obj):
        """Процент приобретения курса."""

        return round(
            obj.students_count / self.context['total_users_count'] * 100,
            ndigits=2
        )

    class Meta:
        model = Course
        fields = (
            'id',
            'author',
            'title',
            'start_date',
            'price',
            'lessons_count',
            'lessons',
            'demand_course_percent',
            'students_count',
            'groups_filled_percent',
        )


class CreateCourseSerializer(serializers.ModelSerializer):
    """Создание курсов."""

    class Meta:
        model = Course
        fields = (
            'author',
            'title',
            'start_date',
            'price',
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Course.objects.all(),
                fields=('title', 'author',),
                message=COURSE_ALREADY_EXISTS
            ),
        ]
