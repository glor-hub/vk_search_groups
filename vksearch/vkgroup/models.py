from django.db import IntegrityError, models


class CommunityType(models.Model):
    GROUPS_TYPES = [("GROUP", "group"), ("PAGE", "page"), ("EVENT", "event")]
    data = [{"type": "group"}, {"type": "page"}, {"type": "event"}]
    name = models.TextField(choices=GROUPS_TYPES, default="GROUP", unique=True)
    objects = models.Manager()

    @classmethod
    def create_table_with_data(cls):
        type_instances = []
        for d in cls.data:
            type_instances.append(CommunityType(name=d["type"]))
        try:
            CommunityType.objects.bulk_create(type_instances)
        except IntegrityError:
            pass


class CommunityProfileManager(models.Manager):
    ORDERING_CHOICES = (
        ("members", "Members"),
        ("sex_perc", "Sex %"),
        ("audience_sum", "Audience"),
        ("audience_perc", "Audience %"),
    )

    def select(
        self,
        countries=None,
        age_ranges=None,
        sexes=None,
        min_members=None,
        max_members=None,
        min_sex_perc=None,
        max_sex_perc=None,
        min_audience=None,
        max_audience=None,
        min_audience_perc=None,
        max_audience_perc=None,
        ordering=None,
        inverted=None,
    ):

        if inverted:
            ordering = "-" + ordering

        profile_filter = {}
        if age_ranges:
            profile_filter["audience__profile__age_range__in"] = age_ranges
        if countries:
            profile_filter["audience__profile__country__in"] = countries
        if sexes:
            profile_filter["audience__profile__sex__in"] = sexes

        members_filter = {}
        if min_members is not None:
            members_filter["members__gte"] = min_members
        if max_members is not None:
            members_filter["members__lte"] = max_members

        audience_filter = {}
        if min_audience is not None:
            audience_filter["audience_sum__gte"] = min_audience
        if max_audience is not None:
            audience_filter["audience_sum__lte"] = max_audience

        sex_perc_filter = {}
        if min_sex_perc is not None:
            sex_perc_filter["sex_perc__gte"] = min_sex_perc
        if max_sex_perc is not None:
            sex_perc_filter["sex_perc__lte"] = max_sex_perc

        audience_perc_filter = {}
        if min_audience_perc is not None:
            audience_perc_filter["audience_perc__gte"] = min_audience_perc
        if max_audience_perc is not None:
            audience_perc_filter["audience_perc__lte"] = max_audience_perc

        return (
            self.filter(
                deactivated=False,
                **members_filter,
                **profile_filter,
            )
            .select_related("type")
            .annotate(
                audience_sum=models.Sum("audience__count"),
                sex_perc=100 * models.F("audience_sum") / models.F("members"),
            )
            .filter(
                audience_sum__isnull=False,
                **sex_perc_filter,
            )
            .annotate(
                audience_sum=models.Sum("audience__count"),
                audience_perc=100 * models.F("audience_sum") / models.F("members"),
            )
            .filter(
                audience_sum__isnull=False, **audience_filter, **audience_perc_filter
            )
            .order_by(ordering)
        )


class Community(models.Model):
    AGE_UNKNOWN = 1
    AGE_16_OLDER = 2
    AGE_18_OLDER = 3
    AGE_VK_TYPES = [(1, "0+"), (2, "16+"), (3, "18+")]
    vk_id = models.PositiveIntegerField(primary_key=True, null=False)
    type = models.ForeignKey("CommunityType", on_delete=models.CASCADE, null=True)
    deactivated = models.BooleanField()
    age_vk = models.PositiveIntegerField(choices=AGE_VK_TYPES, null=True)
    description = models.TextField(null=True)
    verified = models.BooleanField(null=True)
    name = models.TextField(null=True)
    site = models.TextField(null=True)
    members = models.PositiveIntegerField(blank=True, null=True)
    status = models.TextField(null=True)
    update_at = models.DateTimeField(auto_created=False, auto_now_add=True)

    objects = models.Manager()
    profile_objects = CommunityProfileManager()

    def __str__(self):
        return f"community: {self.name} id: {self.vk_id}"


class AgeRange(models.Model):
    AGE_UNKNOWN = 1
    AGE_16_YOUNGER = 2
    AGE_16_18 = 3
    AGE_18_24 = 4
    AGE_25_29 = 5
    AGE_30_34 = 6
    AGE_35_44 = 7
    AGE_45_54 = 8
    AGE_55_64 = 9
    AGE_65_OLDER = 10

    AGES_RANGE = [
        (AGE_UNKNOWN, "ALL"),
        (AGE_16_YOUNGER, "16-"),
        (AGE_16_18, "16-18"),
        (AGE_18_24, "18-24"),
        (AGE_25_29, "25-29"),
        (AGE_30_34, "30-34"),
        (AGE_35_44, "35-44"),
        (AGE_45_54, "45-54"),
        (AGE_55_64, "55-64"),
        (AGE_65_OLDER, "65+"),
    ]
    data = [
        {"age": AGE_UNKNOWN},
        {"age": AGE_16_YOUNGER},
        {"age": AGE_16_18},
        {"age": AGE_18_24},
        {"age": AGE_25_29},
        {"age": AGE_30_34},
        {"age": AGE_35_44},
        {"age": AGE_45_54},
        {"age": AGE_55_64},
        {"age": AGE_65_OLDER},
    ]
    range = models.PositiveIntegerField(
        choices=AGES_RANGE, default=AGE_UNKNOWN, unique=True
    )
    objects = models.Manager()

    @classmethod
    def create_table_with_data(cls):
        age_instances = []
        for datum in cls.data:
            age_instances.append(AgeRange(range=datum["age"]))
        AgeRange.objects.bulk_create(age_instances)

    def __str__(self):
        return f"age range: {self.range}"


class Country(models.Model):
    UNKNOWN_COUNTRY = "Неизвестная страна"
    name = models.TextField(unique=True, null=False)
    objects = models.Manager()

    def __str__(self):
        return self.name


class AudienceProfile(models.Model):
    SEX_UNKNOWN = 0
    SEX_FEMALE = 1
    SEX_MALE = 2
    SEX_CHOICES = ((SEX_UNKNOWN, "UNKNOWN"), (SEX_FEMALE, "Female"), (SEX_MALE, "Male"))
    country = models.ForeignKey(
        "Country", on_delete=models.CASCADE, null=False, default=1
    )
    age_range = models.ForeignKey(
        "AgeRange", on_delete=models.CASCADE, null=False, default=1
    )
    sex = models.SmallIntegerField(choices=SEX_CHOICES, default=SEX_UNKNOWN)
    objects = models.Manager()

    class Meta:
        unique_together = ("country", "age_range", "sex")


class Audience(models.Model):
    community = models.ForeignKey(
        Community, on_delete=models.CASCADE, null=False, default=1
    )
    profile = models.ForeignKey(
        AudienceProfile, on_delete=models.CASCADE, null=False, default=1
    )
    count = models.IntegerField(default=0)
    objects = models.Manager()

    class Meta:
        unique_together = ("community", "profile")

    def __str__(self):
        return f"audience id:{self.pk} of community {self.community.name}"
