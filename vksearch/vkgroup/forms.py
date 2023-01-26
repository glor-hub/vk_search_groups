from django import forms

from .models import AgeRange, AudienceProfile, Community, Country


class CommunitiesSearchForm(forms.Form):
    countries = forms.ModelMultipleChoiceField(Country.objects.all(), required=False)
    age_ranges = forms.MultipleChoiceField(choices=AgeRange.AGES_RANGE, required=False)
    sexes = forms.MultipleChoiceField(
        choices=AudienceProfile.SEX_CHOICES, required=False
    )

    min_sex_perc = forms.IntegerField(
        required=False, min_value=0, max_value=100, label="Min sex%"
    )
    max_sex_perc = forms.IntegerField(
        required=False, min_value=0, max_value=100, label="Max sex%"
    )

    min_members = forms.IntegerField(required=False, min_value=0, label="Min members")
    max_members = forms.IntegerField(required=False, min_value=0, label="Max members")

    min_audience = forms.IntegerField(required=False, min_value=0, label="Min audience")
    max_audience = forms.IntegerField(required=False, min_value=0, label="Max audience")

    min_audience_perc = forms.IntegerField(
        required=False, min_value=0, max_value=100, label="Min audience %"
    )
    max_audience_perc = forms.IntegerField(
        required=False, min_value=0, max_value=100, label="Max audience %"
    )

    ordering = forms.ChoiceField(choices=Community.profile_objects.ORDERING_CHOICES)
    inverted = forms.BooleanField(required=False)

    def clean_age_ranges(self):
        return list(self.cleaned_data["age_ranges"])

    def clean_countries(self):
        return list(self.cleaned_data["countries"])

    def clean(self):
        super().clean()
        self.validate("min_members", "max_members")
        self.validate("min_audience", "max_audience")
        self.validate("min_audience_perc", "max_audience_perc")
        self.validate("min_sex_perc", "max_sex_perc")
        return self.cleaned_data

    def validate(self, min_field_name, max_field_name):
        min_value = self.cleaned_data.get(min_field_name)
        max_value = self.cleaned_data.get(max_field_name)
        if min_value is not None and max_value is not None:
            if min_value > max_value:
                raise forms.ValidationError(
                    '"{0}" and "{1}" must be validated'.format(
                        min_field_name, max_field_name
                    )
                )
