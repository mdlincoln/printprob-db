from pp import models
from uuid import uuid4
import random

models.Book.objects.all().delete()
models.Image.objects.all().delete()

b1 = models.Book.objects.create(estc=1234, vid=231, title="ipsum")
b2 = models.Book.objects.create(estc=5678, vid=987, title="lorem")
books = [b1, b2]


def quickimage():
    return models.Image.objects.create(
        jpg=str(uuid4()), tif=str(uuid4()), jpg_md5=uuid4(), tif_md5=uuid4()
    )


for book in books:
    for i in range(0, 3):
        models.Spread.objects.create(book=book, sequence=i, image=quickimage())

for book in books:
    page_run = models.PageRun.objects.create(
        book=book,
        params=f"param text {uuid4()}",
        script_path=f"path",
        script_md5=uuid4(),
    )
    for spread in book.spreads.all():
        for s in ["l", "r"]:
            models.Page.objects.create(
                spread=spread,
                created_by_run=page_run,
                side=s,
                image=quickimage(),
                x_min=random.randrange(0, 500),
                x_max=random.randrange(0, 500),
            )

for book in books:
    line_run = models.LineRun.objects.create(
        book=book,
        params=f"param text {uuid4()}",
        script_path=f"path",
        script_md5=uuid4(),
    )
    for page in models.Page.objects.filter(spread__book=book).all():
        for i in range(0, 4):
            models.Line.objects.create(
                page=page,
                created_by_run=line_run,
                image=quickimage(),
                sequence=i,
                y_min=random.randrange(0, 500),
                y_max=random.randrange(0, 500),
            )

for book in books:
    linegroup_run = models.LineGroupRun.objects.create(
        book=book,
        params=f"param text {uuid4()}",
        script_path=f"path",
        script_md5=uuid4(),
    )
    for page in models.Page.objects.filter(spread__book=book).all():
        for i in range(0, 2):
            lg = models.LineGroup.objects.create(
                page=page, created_by_run=linegroup_run
            )
            for line in models.Line.objects.filter(page=page).order_by("?")[:1]:
                lg.lines.add(line)

for cc in ["a", "b", "c"]:
    models.CharacterClass.objects.create(classname=cc)

for book in books:
    character_run = models.CharacterRun.objects.create(
        book=book,
        params=f"param text {uuid4()}",
        script_path=f"path",
        script_md5=uuid4(),
    )
    for line in models.Line.objects.filter(page__spread__book=book).all():
        for i in range(0, 4):
            randclass = models.CharacterClass.objects.order_by("?")[0]
            models.Character.objects.create(
                line=line,
                created_by_run=character_run,
                image=quickimage(),
                sequence=i,
                x_min=random.randrange(0, 500),
                x_max=random.randrange(0, 500),
                character_class=randclass,
                class_probability=random.random(),
            )
