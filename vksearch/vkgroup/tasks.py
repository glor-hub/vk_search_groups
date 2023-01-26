from __future__ import absolute_import, unicode_literals

from datetime import datetime

import requests
from celery import group, shared_task
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.db.models import F, Q

from vksearch.settings import (VK_REQ_CONNECT_TIMEOUT, VK_REQ_READ_TIMEOUT,
                               VK_UPDATE_DATA_PERIOD)

from . import vkapi_service
from .models import (AgeRange, Audience, AudienceProfile, Community,
                     CommunityType, Country)
from .vkapi_service import VkApiAudience, VkApiCommunity


def check_for_update_data_from_vk():
    vk_community = VkApiCommunity()
    try:
        comm = Community.objects.get(vk_id=1)
        if (datetime.now() - comm.update_at).total_seconds() > float(
            VK_UPDATE_DATA_PERIOD
        ):
            get_communities_data(vk_community, update_flag=True)
            get_audience_data()
    except ObjectDoesNotExist:
        get_communities_data(vk_community, update_flag=False)
        get_countries_data()
        AgeRange.create_table_with_data()
        get_audience_data()


def get_communities_data(vk_community, update_flag=False):
    min_id = 1
    CommunityType.create_table_with_data()
    while True:
        url_list, min_id_next = vk_community.build_community_url_list(min_id)
        if update_flag:
            res = (
                group(task_update_and_store_communities.s(url) for url in url_list)
                .apply_async()
                .get()
            )
        else:
            res = (
                group(task_load_and_store_communities.s(url) for url in url_list)
                .apply_async()
                .get()
            )
        for i in range(len(res)):
            if res[i] == "Task completed":
                return
        min_id = min_id_next


@shared_task(
    default_retry_delay=1,
    autoretry_for=(Exception,),
    max_retries=3,
)
def task_load_and_store_communities(url):
    r = requests.get(url, timeout=(VK_REQ_CONNECT_TIMEOUT, VK_REQ_READ_TIMEOUT))
    data_list = r.json().get("response")
    if data_list:
        for data in data_list:
            vk_id = data.get("id")
            if vk_id > vkapi_service.MAX_GROUPS_COUNT:
                return "Task completed"
            dtype = data.get("type")
            c_type, _ = CommunityType.objects.get_or_create(name=dtype)
            params = {
                "vk_id": vk_id,
                "type": c_type,
                "deactivated": bool(data.get("deactivated")),
                "description": data.get("description"),
                "verified": data.get("verified"),
                "age_vk": data.get("age_limits"),
                "name": data.get("name"),
                "site": data.get("site"),
                "members": data.get("members_count"),
                "status": data.get("status"),
            }
            try:
                comm, created = Community.objects.get_or_create(**params)
                if created:
                    comm.type = c_type
                    comm.save()
            except IntegrityError:
                pass
    # time.sleep(0.1)
    return "Task in progress"


@shared_task(
    default_retry_delay=1,
    autoretry_for=(Exception,),
    max_retries=3,
)
def task_update_and_store_communities(url):
    r = requests.get(url, timeout=(VK_REQ_CONNECT_TIMEOUT, VK_REQ_READ_TIMEOUT))
    data_list = r.json().get("response")
    if data_list:
        for data in data_list:
            vk_id = data.get("id")
            if vk_id > vkapi_service.MAX_GROUPS_COUNT:
                return "Task completed"
            dtype = data.get("type")
            c_type, _ = CommunityType.objects.get_or_create(name=dtype)
            comm = Community.objects.get(vk_id=vk_id)
            comm.type = c_type
            comm.deactivated = bool(data.get("deactivated"))
            comm.description = data.get("description")
            comm.verified = data.get("verified")
            comm.age_vk = data.get("age_limits")
            comm.name = data.get("name")
            comm.site = data.get("site")
            comm.members = data.get("members_count")
            comm.status = data.get("status")
            comm.update_at = datetime.now()
            comm.save()
    return "Task in progress"


def get_countries_data():
    task_load_and_store_countries.delay()


@shared_task(
    default_retry_delay=1,
    autoretry_for=(Exception,),
    max_retries=3,
)
def task_load_and_store_countries():
    vk_audience = VkApiAudience()
    url = vk_audience.build_countries_url()
    r = requests.get(url, timeout=(VK_REQ_CONNECT_TIMEOUT, VK_REQ_READ_TIMEOUT))
    data_list = r.json().get("response")
    if data_list:
        for data in data_list:
            id = data.get("id")
            params = {"pk": id, "name": data.get("title")}
            try:
                c, _ = Country.objects.get_or_create(**params)
            except IntegrityError:
                c = Country.objects.get(id=id)
                c.name = data.get("title")
                c.save()
    c = Country(id=238, name=Country.UNKNOWN_COUNTRY)
    c.save()
    return "Task completed"


def get_audience_data():
    comms = (
        Community.objects.filter(deactivated=False)
        .exclude(Q(members__isnull=True) | Q(members__exact=0))
        .order_by("vk_id")
    )
    for comm in comms:
        vk_id = comm.vk_id
        get_audience_data_for_group(vk_id)


def get_audience_data_for_group(g_id):
    vk_audience = VkApiAudience()
    users_offset = 0
    while True:
        url_list = vk_audience.build_audience_url_list(g_id, users_offset)
        if not url_list:
            return
        res = (
            group(task_load_users_for_community.s(url, g_id) for url in url_list)
            .apply_async()
            .get()
        )
        for i in range(len(res)):
            if res[i] == "Task completed":
                return
        users_offset += (
            len(vk_audience.token_list) * vk_audience.step * vk_audience.max_requests
        )


@shared_task(
    default_retry_delay=5,
    autoretry_for=(Exception,),
    max_retries=3,
)
def task_load_users_for_community(url, g_id):
    vk_audience = VkApiAudience()
    r = requests.get(url, timeout=(VK_REQ_CONNECT_TIMEOUT, VK_REQ_READ_TIMEOUT))
    if not r:
        return "Task completed"
    response = r.json().get("response")
    for resp in response:
        if not resp:
            return "Task completed"
        data_list = resp.get("items")
        if not data_list:
            return "Task completed"
        for data in data_list:
            country = vk_audience.parse_country(data)
            age = AgeRange.objects.get(range=vk_audience.parse_bdate(data))
            country = Country.objects.get(name=country)
            params = {
                "age_range": age,
                "sex": vk_audience.parse_sex(data),
                "country": country,
            }
            try:
                profile, _ = AudienceProfile.objects.get_or_create(**params)
            except IntegrityError:
                profile, _ = AudienceProfile.objects.get(**params)
            params = {"community": Community(vk_id=g_id), "profile": profile}
            audience, _ = Audience.objects.get_or_create(**params)
            audience.count = F("count") + 1
            audience.save(update_fields=["count"])

    return "Task in progress"
