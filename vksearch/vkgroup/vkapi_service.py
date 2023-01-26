from datetime import date
from os.path import join

from vksearch.settings import TOKENS_DIR, VK_API_VERSION

from .models import AgeRange, AudienceProfile, Community, Country

# communities
MAX_GROUPS_COUNT_PER_REQUEST = 500
# MAX_GROUPS_COUNT = 100000
MAX_GROUPS_COUNT = 50000

URL_PATTERN_GROUPS_BY_ID = (
    "https://api.vk.com/method/groups.getById?group_ids={ids}&"
    "fields=type,is_closed,name,description,members_count,status,verified,site,age_limits&"
    "v={version}&access_token={token}"
)

# audience
MAX_REQUESTS_PER_EXECUTE_METHOD = 25
MAX_GROUPS_MEMBERS_COUNT_PER_REQUEST = 1000

URL_PATTERN_GROUPS_MEMBERS = (
    "https://api.vk.com/method/execute?code={code}&v={version}&access_token={token}"
)

CODE = 'API.groups.getMembers({"group_id":"%s","offset":%d,"count":%d,"sort":"id_asc","fields":"sex,bdate,country,city,last_seen"})'

# countries
MAX_COUNTRIES_COUNT = 237

URL_PATTERN_COUNTRIES_BY_ID = (
    "https://api.vk.com/method/database.getCountriesById?country_ids={ids}&"
    "v={version}&access_token={token}"
)


def get_token_list():
    token_list = []
    path = TOKENS_DIR
    with open(join(path, "tokens.txt")) as f:
        for line in f:
            token_list.append(str(line).rstrip("\n"))
    return token_list


class VkApiCommunity:
    def __init__(self):
        self.pattern = URL_PATTERN_GROUPS_BY_ID
        self.offset = MAX_GROUPS_COUNT_PER_REQUEST

    def build_community_url_list(self, min_id):
        url_list = []
        token_list = get_token_list()
        for token in token_list:
            ids = ",".join(
                str(id) for id in range(int(min_id), int(min_id + self.offset))
            )
            url_list.append(
                self.pattern.format(ids=ids, version=VK_API_VERSION, token=token)
            )
            min_id += self.offset
        return url_list, min_id


class VkApiAudience:
    def __init__(self):
        self.aud_pattern = URL_PATTERN_GROUPS_MEMBERS
        self.country_pattern = URL_PATTERN_COUNTRIES_BY_ID
        self.count = MAX_GROUPS_MEMBERS_COUNT_PER_REQUEST
        self.step = MAX_GROUPS_MEMBERS_COUNT_PER_REQUEST
        self.max_requests = MAX_REQUESTS_PER_EXECUTE_METHOD
        self.countries_list = self.get_countries_from_db()

    def build_countries_url(self):
        token_list = get_token_list()
        self.country_pattern = URL_PATTERN_COUNTRIES_BY_ID
        ids = ",".join(str(id) for id in range(1, MAX_COUNTRIES_COUNT + 1))
        token = token_list[0]
        url = self.country_pattern.format(ids=ids, version=VK_API_VERSION, token=token)
        return url

    def build_audience_url_list(self, group_id, offset):
        url_list = []
        token_list = get_token_list()
        comm = Community.objects.get(vk_id=group_id)
        users = comm.members
        if not users:
            return url_list
        for token in token_list:
            uplimit = offset + self.step * self.max_requests
            code = ",".join(
                CODE % (str(group_id), offset_users, self.count)
                for offset_users in range(offset, uplimit, self.step)
            )
            code = "return [" + code + "];"
            url_list.append(
                self.aud_pattern.format(code=code, version=VK_API_VERSION, token=token)
            )
            offset += self.step * self.max_requests
        return url_list

    @staticmethod
    def get_countries_from_db():
        countries_list = []
        countries = Country.objects.all()
        for c in countries:
            countries_list.append(c.name)
        return countries_list

    @staticmethod
    def parse_bdate(data):
        bdate = data.get("bdate")
        if bdate is None:
            return AgeRange.AGE_UNKNOWN
        parts = bdate.split(".")
        if len(parts) != 3:
            return AgeRange.AGE_UNKNOWN
        try:
            bdate = date(int(parts[2]), int(parts[1]), int(parts[0]))
        except ValueError:
            return AgeRange.AGE_UNKNOWN
        now = date.today()
        if bdate > now:
            return AgeRange.AGE_UNKNOWN
        age = (now - bdate).days / 365.25
        if age < 16:
            return AgeRange.AGE_16_YOUNGER
        if age < 19:
            return AgeRange.AGE_16_18
        if age < 25:
            return AgeRange.AGE_18_24
        if age < 30:
            return AgeRange.AGE_25_29
        if age < 35:
            return AgeRange.AGE_30_34
        if age < 45:
            return AgeRange.AGE_35_44
        if age < 55:
            return AgeRange.AGE_45_54
        if age < 65:
            return AgeRange.AGE_55_64
        return AgeRange.AGE_65_OLDER

    def parse_country(self, data):
        country = data.get("country")
        if country is None:
            return Country.UNKNOWN_COUNTRY
        country_name = country.get("title")
        if not country_name:
            return Country.UNKNOWN_COUNTRY
        if country_name in self.countries_list:
            return country_name
        else:
            return Country.UNKNOWN_COUNTRY

    @staticmethod
    def parse_sex(data):
        sex_id = data.get("sex")
        if sex_id not in (0, 1, 2):
            return AudienceProfile.SEX_UNKNOWN
        return sex_id
