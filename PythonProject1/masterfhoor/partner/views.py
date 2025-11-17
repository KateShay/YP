from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.urls import reverse_lazy
from django.db.models import Sum
from .models import Partner, SalesHistory, PartnerType, ProductType, MaterialType
from .forms import PartnerForm, SalesHistoryFilterForm


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


class PartnerListView(ListView):
    model = Partner
    template_name = 'partners/partner_list.html'
    context_object_name = 'partners'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        partner_type = self.request.GET.get('partner_type')
        search = self.request.GET.get('search')

        if partner_type:
            queryset = queryset.filter(partner_type_id=partner_type)
        if search:
            queryset = queryset.filter(name__icontains=search)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['partner_types'] = PartnerType.objects.all()
        return context


class PartnerCreateView(CreateView):
    model = Partner
    form_class = PartnerForm
    template_name = 'partners/partner_form.html'
    success_url = reverse_lazy('partners:partner_list')

    def form_valid(self, form):
        messages.success(self.request, 'Партнер успешно добавлен')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Пожалуйста, исправьте ошибки в форме')
        return super().form_invalid(form)


class PartnerUpdateView(UpdateView):
    model = Partner
    form_class = PartnerForm
    template_name = 'partners/partner_form.html'
    success_url = reverse_lazy('partners:partner_list')

    def form_valid(self, form):
        messages.success(self.request, 'Данные партнера успешно обновлены')
        return super().form_valid(form)


class SalesHistoryView(DetailView):
    model = Partner
    template_name = 'partners/sales_history.html'
    context_object_name = 'partner'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        partner = self.get_object()

        sales_history = SalesHistory.objects.filter(partner=partner)

        form = SalesHistoryFilterForm(self.request.GET)
        if form.is_valid():
            date_from = form.cleaned_data.get('date_from')
            date_to = form.cleaned_data.get('date_to')

            if date_from:
                sales_history = sales_history.filter(sale_date__gte=date_from)
            if date_to:
                sales_history = sales_history.filter(sale_date__lte=date_to)

        context['sales_history'] = sales_history
        context['filter_form'] = form
        context['total_sales'] = sales_history.aggregate(total=Sum('quantity'))['total'] or 0
        context['current_discount'] = partner.calculate_discount()

        return context


def calculate_discount_api(request, partner_id):
    partner = get_object_or_404(Partner, id=partner_id)
    discount = partner.calculate_discount()
    return JsonResponse({'discount': discount})


def calculate_material_api(request):
    try:
        product_type_id = int(request.GET.get('product_type_id', 0))
        material_type_id = int(request.GET.get('material_type_id', 0))
        product_quantity = int(request.GET.get('product_quantity', 0))
        param1 = float(request.GET.get('param1', 0))
        param2 = float(request.GET.get('param2', 0))

        result = calculate_material_required(
            product_type_id, material_type_id, product_quantity, param1, param2
        )

        return JsonResponse({'material_required': result})

    except (ValueError, TypeError):
        return JsonResponse({'error': 'Неверные параметры'}, status=400)
