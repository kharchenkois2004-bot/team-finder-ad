from django.core.paginator import Paginator

from team_finder.constants import GIT_URL, ITEMS_PER_PAGE


def form_clean_github_url(form):
    url = form.cleaned_data.get('github_url')
    if url and GIT_URL not in url:
        raise form.ValidationError('Ссылка должна вести на GitHub.')
    return url


def paginator_get_page(objects, request, items_num=ITEMS_PER_PAGE):
    paginator = Paginator(objects, items_num)
    return paginator.get_page(request.GET.get('page'))
