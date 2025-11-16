from django.db import models
from .models import ProductType, MaterialType


def calculate_material_required(product_type_id, material_type_id, product_quantity, param1, param2):

    try:
        product_type = ProductType.objects.get(id=product_type_id)
        material_type = MaterialType.objects.get(id=material_type_id)
        if (product_quantity <= 0 or param1 <= 0 or param2 <= 0 or
                not isinstance(product_quantity, int)):
            return -1

        material_per_unit = param1 * param2 * product_type.coefficient
        total_material = material_per_unit * product_quantity
        defect_factor = 1 + (material_type.defect_percentage / 100)
        total_material_with_defect = total_material * defect_factor

        return int(total_material_with_defect) + (1 if total_material_with_defect % 1 > 0 else 0)

    except (ProductType.DoesNotExist, MaterialType.DoesNotExist, ValueError):
        return -1