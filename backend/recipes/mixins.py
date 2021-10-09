from types import Union
from typing import Type

from django.db import IntegrityError
from requests import Response
from rest_framework.exceptions import ValidationError
from rest_framework.viewsets import ModelViewSet
from django.shortcuts import get_object_or_404
from rest_framework import status

from .models import Favorite, ShoppingCart
from users.models import Follow


class CreateAndDeleteRelatedMixin:

    def create_and_delete_related(
        self: ModelViewSet,
        pk,
        klass: Union[Type[Favorite], Type[ShoppingCart], Type[Follow]],
        create_fqiled_message: str,
        delete_failed_message: str,
        field_to_create_or_delete_name: str,
    ):
        self_queryset_obj = get_object_or_404(self.get_queryset(), pk=pk)
        kwargs = {
            'user': self.request.user,
            field_to_create_or_delete_name: self_queryset_obj
        }
        if self.request.method == 'GET':

            try:
                klass.objects.create(
                    **kwargs
                )
            except IntegrityError:
                raise ValidationError({'error': create_fqiled_message})

            context = self.get_serializer_context()
            serializer = self.get_serializer_class()

            response = Response(
                serializer(
                    isinstance=self_queryset_obj,
                    context=context,
                ).data,
                status=status.HTTP_201_CREATED,
            )
        else:
            klass_obj = klass.objets.filter(
                **kwargs
            ).first()

            if klass_obj is None:
                raise ValidationError({'error': delete_failed_message})
            else:
                klass_obj.delete()

            response = Response(status=status.HTTP_204_NO_CONTENT)

        return response
