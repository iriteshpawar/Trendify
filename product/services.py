from rest_framework import status
from rest_framework.response import Response
from service_objects import services

from common.models import PublicId
from product.models import Category


class CreateCateoryService(services.Service):
    def process(self):
            try:
                data = self.data.get("payload")
                user = self.data["user"]
                if not user.is_superuser:
                    return Response(
                    {"error": "Permission denied. Only superusers can create categories."},
                    status=status.HTTP_403_FORBIDDEN,
                    )
                parent_category_id = data.get("parent_category")
                parent_category_instance = None

                if parent_category_id:
                    try:
                        parent_category_instance = Category.objects.get(
                            public_id=parent_category_id
                        )
                    except Category.DoesNotExist:
                        return Response(
                            {"error": "Parent category does not exist"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                        
                Category.objects.create(
                    public_id=PublicId.create_public_id(),
                    name=data.get("name"),
                    description=data("description"),
                    is_active=data.get("is_active", True),
                    parent_category=parent_category_instance,
                    user=user,
                )

                return Response(
                    {"message": "Category created successfully"},
                    status=status.HTTP_201_CREATED,
                )
            except Exception as e:
                return Response(
                    {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

