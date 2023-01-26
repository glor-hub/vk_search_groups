import logging

from django.core.paginator import Paginator
from django.shortcuts import render
from django.views.decorators.http import require_GET

from .forms import CommunitiesSearchForm
from .models import Community
from .tasks import check_for_update_data_from_vk

logger = logging.getLogger(__name__)

COMMUNITIES_PER_PAGE = 20
COMMUNITIES_LIMIT = 10 * COMMUNITIES_PER_PAGE


@require_GET
def communities_view(request):
    check_for_update_data_from_vk()
    context = {
        "title": "Result",
    }
    form = CommunitiesSearchForm(request.GET)
    if form.is_valid():
        communities = Community.profile_objects.select(
            form.cleaned_data["countries"],
            form.cleaned_data["age_ranges"],
            form.cleaned_data["sexes"],
            form.cleaned_data["min_members"],
            form.cleaned_data["max_members"],
            form.cleaned_data["min_sex_perc"],
            form.cleaned_data["max_sex_perc"],
            form.cleaned_data["min_audience"],
            form.cleaned_data["max_audience"],
            form.cleaned_data["min_audience_perc"],
            form.cleaned_data["max_audience_perc"],
            form.cleaned_data["ordering"],
            form.cleaned_data["inverted"],
        )[:COMMUNITIES_LIMIT]
        paginator = Paginator(communities, COMMUNITIES_PER_PAGE)
        page_number = request.GET.get("page")
        communities = paginator.get_page(page_number)
    else:
        communities = []
    context["form"] = form
    context["communities"] = communities

    return render(request, "communities.html", context)
