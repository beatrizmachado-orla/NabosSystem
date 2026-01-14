# core/views.py
from django.shortcuts import get_object_or_404, render
from django.db.models import Count, Q

from core.services.ranking import build_ranking
from members.models import Member
from catches.models import Catch, Species
from supporters.models import Supporter


def home(request):
    # últimos 9 registros (feed)
    recent_catches = (
        Catch.objects
        .select_related("member", "species")
        .order_by("-caught_at")[:9]
    )

    # stats do topo
    stats = {
        "members": Member.objects.count(),
        "catches": Catch.objects.count(),
        "species": Species.objects.count(),
        "supporters": Supporter.objects.count(),
    }

    # apoiadores para a faixa da home (limita para não ficar gigante)
    supporters = Supporter.objects.all()[:16]

    # podium (top 3) usando seu ranking oficial
    podium = build_ranking(top_n=3)

    return render(request, "core/home.html", {
        "recent_catches": recent_catches,
        "stats": stats,
        "supporters": supporters,
        "podium": podium,
    })


def group(request):
    q = (request.GET.get("q") or "").strip()
    selected_gender = (request.GET.get("gender") or "").strip()   # "F" | "M" | "O" | ""
    selected_age = (request.GET.get("age") or "").strip()         # "lt18" | "18_29" | etc.

    qs = (
        Member.objects
        .annotate(catches_count=Count("catches"))
        .order_by("name")
    )

    # busca por nome ou apelido
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(nickname__icontains=q))

    # filtro gênero
    if selected_gender in ("F", "M", "O"):
        qs = qs.filter(gender=selected_gender)

    # filtro idade (faixas)
    if selected_age:
        if selected_age == "lt18":
            qs = qs.filter(age__lt=18)
        elif selected_age == "18_29":
            qs = qs.filter(age__gte=18, age__lte=29)
        elif selected_age == "30_39":
            qs = qs.filter(age__gte=30, age__lte=39)
        elif selected_age == "40_49":
            qs = qs.filter(age__gte=40, age__lte=49)
        elif selected_age == "50_mais":
            qs = qs.filter(age__gte=50)

    return render(request, "core/group.html", {
        "members": qs,
        "q": q,
        "selected_gender": selected_gender,
        "selected_age": selected_age,
    })


def member_detail(request, pk: int):
    member = get_object_or_404(Member, pk=pk)
    catches = (
        member.catches
        .select_related("species")
        .order_by("-caught_at")
    )
    return render(request, "core/member_detail.html", {
        "member": member,
        "catches": catches
    })


def supporters(request):
    supporters_qs = Supporter.objects.all()
    return render(request, "core/supporters.html", {"supporters": supporters_qs})


def ranking(request):
    ranking_list = build_ranking(top_n=10)

    podium_1 = ranking_list[0] if len(ranking_list) > 0 else None
    podium_2 = ranking_list[1] if len(ranking_list) > 1 else None
    podium_3 = ranking_list[2] if len(ranking_list) > 2 else None

    return render(request, "core/ranking.html", {
        "podium_1": podium_1,
        "podium_2": podium_2,
        "podium_3": podium_3,
        "ranking_list": ranking_list,
    })
