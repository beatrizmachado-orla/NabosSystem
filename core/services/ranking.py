from decimal import Decimal
from collections import defaultdict
from catches.models import Catch
from members.models import Member

def calc_catch_points(c: Catch) -> Decimal:
    # se abaixo do mínimo, não conta
    if c.length_cm is None or c.species is None:
        return Decimal("0")
    if Decimal(c.length_cm) < Decimal(c.species.min_length_cm or 0):
        return Decimal("0")

    return Decimal(c.length_cm) * Decimal(c.species.points_per_cm or 0)

def build_ranking(top_n=10):
    # carrega capturas com espécie e membro
    catches = (
        Catch.objects
        .select_related("member", "species")
        .all()
    )

    # guarda pontos válidos por membro
    points_by_member = defaultdict(list)

    for c in catches:
        pts = calc_catch_points(c)
        if pts > 0:
            points_by_member[c.member_id].append(pts)

    # soma as 2 melhores por membro
    member_points = []
    for m in Member.objects.all():
        pts_list = sorted(points_by_member.get(m.id, []), reverse=True)[:2]
        total = sum(pts_list, Decimal("0"))
        member_points.append((m, total))

    # ordena: maior pontuação, depois nome
    member_points.sort(key=lambda x: (-x[1], x[0].name.lower()))

    # top N
    ranking = [
        {"member": m, "points": pts, "pos": i + 1}
        for i, (m, pts) in enumerate(member_points[:top_n])
    ]
    return ranking
