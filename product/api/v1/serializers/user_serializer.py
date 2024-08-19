from django.contrib.auth import get_user_model
from django.db import transaction
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.serializers import ValidationError
from rest_framework.validators import UniqueTogetherValidator

from api.v1.serializers.course_serializer import MiniGroupSerializer
from product.constants import (ALREADY_SUBSCRIBE_COURSE, NO_BALANCE,
                               NOT_ENOUGH_BONUSES)
from users.models import Balance, Subscription


User = get_user_model()


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

    balance = serializers.SerializerMethodField(read_only=True)
    in_groups = MiniGroupSerializer(
        read_only=True,
        many=True,
    )

    def get_balance(self, obj):
        return obj.balance.bonuses

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
            'in_groups',
            'balance',
        )


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
                message=ALREADY_SUBSCRIBE_COURSE
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
                    'errors': NO_BALANCE,
                }
            )
        user_bonuses = user_balance.bonuses
        price = course.price
        if price > user_bonuses:
            raise ValidationError(
                {
                    'errors': NOT_ENOUGH_BONUSES,
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
