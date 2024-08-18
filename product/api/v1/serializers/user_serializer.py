from django.contrib.auth import get_user_model
# from django.db.models.fields import RelatedObjectDoesNotExist
from djoser.serializers import UserSerializer, UserCreateSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from rest_framework.serializers import ValidationError
from django.db import transaction

from users.models import Subscription, Balance
from api.v1.serializers.course_serializer import MiniGroupSerializer


User = get_user_model()


class BalanceSerializer(serializers.ModelSerializer):
    """Сериализатор баланса."""

    class Meta:
        model = Balance
        fields = (
            'bonuses',
        )


class CustomUserCreateSerializer(UserCreateSerializer):

    def create(self, validated_data):
        with transaction.atomic():
            user = super().create(validated_data)
            Balance.objects.create(
                owner=user,
                bonuses=1000,
            )
            return user


class CustomUserSerializer(UserSerializer):
    """Сериализатор пользователей."""
    """
        реализовать сериалайзер для групп
        реализовать сериалайзер для курсов
        "subscribed_to_courses": []
        "groups": [],
    """
    balance = serializers.SerializerMethodField(read_only=True)
    in_groups = MiniGroupSerializer(
        read_only=True,
        many=True,
    )
    def get_balance(self, obj):
        return obj.balance.bonuses
    # subscribed_to_courses = TagModelSerializer(
    #     read_only=True,
    #     many=True,
    # )
    class Meta:
        model = User
        fields = (
            'id',
            'last_login',
            'is_superuser',
            'username',
            'first_name',
            'last_name',
            'is_staff',
            'is_active',
            'date_joined',
            'email',
            'in_groups', # m2m
            'balance', # o2o
            # 'subscribed_to_courses',  # как m2m но модель Subscription
        )

# Реализовать API оплаты продукты за бонусы. Назовем его …/pay/ (3 балла)
# По факту оплаты и списания бонусов с баланса пользователя должен быть открыт доступ к курсу. (2 балла)


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор подписки."""

    class Meta:
        model = Subscription
        fields = (
            'user',
            'course',
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'course',),
                message='Ошибка: вы уже записаны на этот курс'
            ),
        ]

    def validate(self, data):
        user = data.get('user')
        course = data.get('course')
        try:
            user_balance = user.balance
        except User.balance.RelatedObjectDoesNotExist:
            raise ValidationError(
                {
                    'errors': (
                        'Баланс ещё не создан '
                        'напишите в техподдержку.'
                    ),
                }
            )
        user_bonuses = user_balance.bonuses
        price = course.price
        if price > user_bonuses:
            raise ValidationError(
                {
                    'errors': (
                        'Не хватает бонусов на счету '
                        'для оплаты курса, пополните счёт'
                    ),
                }
            )
        return data


    def create(self, validated_data):
        with transaction.atomic():
            instance = super().create(validated_data)
            user = validated_data.get('user')
            course = validated_data.get('course')
            balance = user.balance
            price = course.price
            balance.bonuses -= price
            balance.save()
            return instance
