from django import forms


class BangumiDetailForm(forms.Form):
    rss = forms.CharField(label="RSS", max_length=600, widget=forms.TextInput(attrs={'class': 'form-control'}))
    rule = forms.CharField(label="规则", max_length=600, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    bgm_id = forms.IntegerField(label="Bangumi ID", widget=forms.NumberInput(attrs={'class': 'form-control'}))

    template_name = "AniQuest/forms/bangumi_detail.html"


class NewSubscriptionForm(forms.Form):
    name = forms.CharField(label="番剧名", max_length=400, widget=forms.TextInput(attrs={'class': 'form-control'}))
    rss = forms.CharField(label="RSS", max_length=600, widget=forms.TextInput(attrs={'class': 'form-control'}))
    rule = forms.CharField(label="规则", max_length=600, widget=forms.TextInput(attrs={'class': 'form-control'}))
    bgm_id = forms.IntegerField(label="Bangumi ID", widget=forms.NumberInput(attrs={'class': 'form-control'}))

    template_name = "AniQuest/forms/new_subscription.html"
