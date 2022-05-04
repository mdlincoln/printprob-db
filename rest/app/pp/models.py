from django.db import models
from django.contrib.auth.models import User
import uuid
from datetime import date
from django.conf import settings
from abc import abstractmethod


class uuidModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=True)
    label = models.CharField(max_length=200, default="", editable=False, blank=True)

    class Meta:
        abstract = True

    @abstractmethod
    def labeller(self) -> None:
        raise NotImplementedError

    def save(self, *args, **kwargs):
        self.label = self.labeller()
        super(uuidModel, self).save(*args, **kwargs)

    def __str__(self):
        return self.label


class Run(uuidModel):
    # Use string interpolation of the child class field
    book = models.ForeignKey(
        "Book", on_delete=models.CASCADE, related_name="%(class)ss"
    )
    date_started = models.DateTimeField(auto_now_add=True)
    script_version = models.CharField(max_length=200, default="", blank=True)

    class Meta:
        abstract = True
        ordering = ["-date_started"]

    def labeller(self):
        return f"{str(self.id)} - {self.date_started}"


class PageRun(Run):
    @abstractmethod
    def pages(self):
        raise NotImplementedError

    def component_count(self):
        return self.pages.count()


class LineRun(Run):
    @abstractmethod
    def lines(self):
        raise NotImplementedError

    def component_count(self):
        return self.lines.count()


class CharacterRun(Run):
    @abstractmethod
    def characters(self):
        raise NotImplementedError

    def component_count(self):
        return self.characters.count()


class Book(uuidModel):
    # Fields that should not be editable when is_eebo_book==TRUE
    EEBO_ONLY = [
        "eebo",
        "vid",
        "tcp",
        "estc",
        "zipfile",
        "zip_path",
        "pq_url",
        "pq_year_verbatim",
        "pq_year_early",
        "pq_year_late",
        "tx_year_early",
        "tx_year_late",
    ]

    eebo = models.PositiveIntegerField(
        db_index=True, null=True, blank=True, help_text="EEBO ID number"
    )
    vid = models.PositiveIntegerField(
        db_index=True, null=True, blank=True, help_text="Proquest ID number"
    )
    tcp = models.CharField(db_index=True, blank=True, help_text="TCP ID", max_length=50)
    estc = models.CharField(
        db_index=True,
        blank=True,
        help_text="English Short Title Catalogue Number",
        max_length=50,
    )
    pq_title = models.CharField(
        max_length=2000, db_index=True, help_text="Title (as cataloged by EEBO)"
    )
    pq_publisher = models.CharField(
        blank=True,
        max_length=2000,
        help_text="Publisher (as cataloged by EEBO)",
    )
    pq_author = models.CharField(
        blank=True,
        max_length=2000,
        help_text="Author (as cataloged by EEBO)",
    )
    pq_year_verbatim = models.CharField(
        max_length=2000,
        blank=True,
        help_text="Date string from EEBO, may contain non-numeric values",
    )
    pq_year_early = models.PositiveIntegerField(
        db_index=True,
        null=True,
        help_text="Proquest early year",
    )
    pq_year_late = models.PositiveIntegerField(
        db_index=True,
        null=True,
        help_text="Proquest late year",
    )
    tx_year_early = models.PositiveIntegerField(
        db_index=True,
        null=True,
        help_text="Texas A&M early year",
    )
    tx_year_late = models.PositiveIntegerField(
        db_index=True,
        null=True,
        help_text="Texas A&M late year",
    )
    pq_url = models.URLField(
        max_length=1000,
        blank=True,
        help_text="ProQuest URL",
    )
    pp_publisher = models.CharField(
        blank=True, max_length=2000, help_text="Publisher as asserted by P&P team"
    )
    pp_author = models.CharField(
        blank=True, max_length=2000, help_text="Author as asserted by P&P team"
    )
    pdf = models.CharField(
        blank=True,
        max_length=1500,
        help_text="relative file path to root directory containing pdfs",
    )
    date_early = models.DateField(
        default=date(year=1550, month=1, day=1),
        db_index=True,
        help_text="The earliest date this book may have been printed",
    )
    date_late = models.DateField(
        default=date(year=1800, month=12, day=12),
        db_index=True,
        help_text="The latest date this book may have been printed",
    )
    zipfile = models.CharField(
        max_length=1000,
        blank=True,
        null=False,
        help_text="Location of ZIP file of images on Bridges, for EEBO books only",
    )
    starred = models.BooleanField(
        default=False,
        db_index=True,
        help_text="This book has been maunally starred by a  user",
    )
    ignored = models.BooleanField(
        default=False,
        db_index=True,
        help_text="This book has been marked as ignored by a user, and won't show up in search results",
    )
    is_eebo_book = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Are these book images from ProQuest EEBO?",
    )
    prefix = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        unique=True,
        help_text="Prefix to most Bridges files for this book, e.g. `thodgkin` for thodgkin_xxxxx_yyyyy_00height_caesarsF.txt",
    )
    n_spreads = models.PositiveIntegerField(
        default=0,
        help_text="Number of spread images for this book. Only used for EEBO images.",
    )
    repository = models.CharField(
        max_length=1000,
        blank=True,
        null=True,
        default="",
        db_index=True,
        help_text="Name of the library/collection where these book images came from, e.g. 'British Library'",
    )
    pp_printer = models.CharField(
        blank=True,
        max_length=2000,
        help_text="Printer as asserted by P&P team",
        default="",
        db_index=True,
    )
    colloq_printer = models.CharField(
        blank=True,
        max_length=2000,
        help_text="Commonly-held printer identification",
        default="",
        db_index=True,
    )
    pp_notes = models.TextField(
        blank=True, help_text="Free notes by the P&P team", default=""
    )

    class Meta:
        ordering = ["pq_title"]

    def labeller(self):
        return f"({self.vid}) {self.pq_title[:30]}..."

    def all_runs(self):
        return {
            "pages": self.pageruns.all(),
            "lines": self.lineruns.all(),
            "characters": self.characterruns.all(),
        }

    def most_recent_runs(self):
        return {
            "page": self.pageruns.first(),
            "line": self.lineruns.first(),
            "character": self.characterruns.first(),
        }

    def most_recent_pages(self):
        """
        Get all pages for this book based on the most recent run in the database
        """
        return self.pageruns.first().pages.all()

    def cover_spread(self):
        return self.spreads.first()

    def cover_page(self):
        return Page.objects.filter(created_by_run__book=self).first()

    @property
    def zip_path(self):
        return f"{self.zipfile}/{self.vid}/*.tif"


class Task(uuidModel):
    date_entered = models.DateTimeField(
        auto_now=True, help_text="Date this classification was made"
    )

    class Meta:
        abstract = True
        ordering = ["date_entered"]

    def labeller(self):
        return f"{self.date_entered}"


class ImagedModel(uuidModel):
    tif = models.CharField(
        max_length=2000,
        help_text="relative file path to root directory containing all images",
        blank=True,
    )

    @property
    def iiif_base(self):
        return f"{settings.IMAGE_BASEURL}{self.tif}"

    @property
    def web_url(self):
        return f"{self.iiif_base}/full/full/0/default.jpg"

    @property
    def thumbnail(self):
        return f"{self.iiif_base}/full/200,/0/default.jpg"

    @property
    def full_tif(self):
        return f"{self.iiif_base}/full/full/0/default.tif"

    @property
    def image(self):
        return {
            "tif": self.tif,
            "iiif_base": self.iiif_base,
            "web_url": self.web_url,
            "thumbnail": self.thumbnail,
            "full_tif": self.full_tif,
        }

    class Meta:
        abstract = True


class CroppedModel(uuidModel):
    @property
    def absolute_coords(self) -> dict:
        raise NotImplementedError

    @property
    def root_object(self) -> ImagedModel:
        raise NotImplementedError

    @property
    def region_string(self):
        ac = self.absolute_coords
        return f"{ac['x']},{ac['y']},{ac['w']},{ac['h']}"

    @property
    def buffer(self):
        ac = self.absolute_coords
        buffer = 50
        return f"{self.root_object.iiif_base}/{max(ac['x'] - buffer, 0)},{max(ac['y'] - buffer, 0)},{ac['w'] + (2 * buffer)},{ac['h'] + (2 * buffer)}/150,/0/default.jpg"

    @property
    def web_url(self):
        return f"{self.root_object.iiif_base}/{self.region_string}/full/0/default.jpg"

    @property
    def full_tif(self):
        return f"{self.root_object.iiif_base}/{self.region_string}/full/0/default.tif"

    @property
    def thumbnail(self):
        return f"{self.root_object.iiif_base}/{self.region_string}/500,/0/default.jpg"

    @property
    def image(self):
        return {
            "web_url": self.web_url,
            "thumbnail": self.thumbnail,
            "buffer": self.buffer,
        }

    class Meta:
        abstract = True


class Spread(ImagedModel):
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="spreads",
        help_text="Book to which this spread belongs",
    )
    sequence = models.PositiveIntegerField(
        db_index=True, help_text="Sequence of this page in a given book"
    )

    class Meta:
        ordering = ("book", "sequence")

    def labeller(self):
        return f"{self.book} spread {self.sequence}"

    def most_recent_pages(self):
        return self.book.pageruns.first().pages.filter(spread=self)

    def save(self, *args, **kwargs):
        """
        Update book spread count on save
        """
        response = super().save(*args, **kwargs)
        self.book.n_spreads = self.book.spreads.count()
        self.book.save()
        return response


class Page(ImagedModel):
    """
    The definition of a page may change between runs in this model, since it depends on splitting spreads, therefore it is a subclass of an Attempt.
    """

    SPREAD_SIDE = (("s", "single"), ("l", "left"), ("r", "right"))
    sequence = models.PositiveIntegerField(default=0)
    side = models.CharField(
        max_length=1,
        choices=SPREAD_SIDE,
        help_text="Side of the spread this has been segmented to",
    )
    x = models.FloatField(null=True)
    y = models.FloatField(null=True)
    w = models.FloatField(null=True)
    h = models.FloatField(null=True)
    rot1 = models.FloatField(null=True)
    rot2 = models.FloatField(null=True)
    created_by_run = models.ForeignKey(
        PageRun,
        on_delete=models.CASCADE,
        help_text="Which pipeline run created this object instance",
        related_name="pages",
    )

    class Meta:
        ordering = ["created_by_run", "sequence"]

    def labeller(self):
        return f"{self.created_by_run.book} p. {self.sequence}-{self.side}"

    def n_lines(self):
        return self.lines.count()

    def most_recent_lines(self):
        return self.created_by_run.book.lineruns.first().lines.filter(page=self)

    def book(self):
        return self.created_by_run.book


class Line(CroppedModel):
    """
    The definition of a line may change between runs in this model, since it depends on splitting page spreads, therefore it is a subclass of an Attempt.
    """

    page = models.ForeignKey(
        Page,
        on_delete=models.CASCADE,
        related_name="lines",
        help_text="Page ID of this line",
    )
    sequence = models.PositiveIntegerField(
        db_index=True, help_text="Order on page, from top to bottom"
    )
    y_min = models.PositiveIntegerField(
        help_text="Y-axis index for the start of this line on the Page image"
    )
    y_max = models.PositiveIntegerField(
        help_text="Y-axis index for the end of this line on the Page image"
    )
    created_by_run = models.ForeignKey(
        LineRun,
        on_delete=models.CASCADE,
        help_text="Which pipeline run created this object instance",
        related_name="lines",
    )

    class Meta:
        ordering = ["created_by_run", "page", "sequence"]

    def labeller(self):
        return f"{self.page} l. {self.sequence}"

    def n_chars(self):
        return self.characters.count()

    def most_recent_characters(self):
        return self.page.created_by_run.book.characterruns.first().characters.filter(
            line=self
        )

    @property
    def root_object(self):
        return self.page

    @property
    def absolute_coords(self):
        x = 0
        y = self.y_min
        w = 9999
        h = self.height
        return {"x": x, "y": y, "w": w, "h": h}

    @property
    def height(self):
        return self.y_max - self.y_min

    def page_side(self):
        return self.page.side


class BreakageType(uuidModel):
    pass


class CharacterClass(models.Model):
    LOWERCASE = "cl"
    UPPERCASE = "cu"
    NUMBER = "nu"
    PUNCTUATION = "pu"
    CHARACTER_GROUPS = [
        (LOWERCASE, "Lowercase"),
        (UPPERCASE, "Uppercase"),
        (NUMBER, "Number"),
        (PUNCTUATION, "Punctuation"),
    ]

    classname = models.CharField(
        primary_key=True,
        max_length=50,
        help_text="Unique Ocular identifier",
    )
    label = models.CharField(
        max_length=50, default="", help_text="Human-readable label"
    )
    group = models.CharField(
        max_length=2, choices=CHARACTER_GROUPS, default=LOWERCASE, db_index=True
    )

    class Meta:
        ordering = ["group", "classname"]

    def __str__(self):
        return self.classname


class Character(CroppedModel):
    """
    The definition of a character may change between runs in this model, since it depends on line segmentation, therefore it is a subclass of an Attempt.
    """

    line = models.ForeignKey(Line, on_delete=models.CASCADE, related_name="characters")
    sequence = models.PositiveIntegerField(
        db_index=True, help_text="Sequence of characters on the line"
    )
    x_min = models.IntegerField(
        help_text="X-axis index for the start of this character on the page image"
    )
    x_max = models.IntegerField(
        help_text="X-axis index for the end of this character on the page image"
    )
    y_min = models.IntegerField(
        null=True,
        help_text="Y-axis index for the start of this character on the page image",
    )
    y_max = models.IntegerField(
        null=True,
        help_text="Y-axis index for the end of this character on the page image",
    )
    character_class = models.ForeignKey(
        CharacterClass, on_delete=models.CASCADE, related_name="assigned_to"
    )
    human_character_class = models.ForeignKey(
        CharacterClass,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="human_assigned_to",
    )
    class_probability = models.FloatField(db_index=True)
    created_by_run = models.ForeignKey(
        CharacterRun,
        on_delete=models.CASCADE,
        help_text="Which pipeline run created this object instance",
        related_name="characters",
    )
    exposure = models.IntegerField(default=0)
    offset = models.IntegerField(default=0)
    breakage_types = models.ManyToManyField(
        BreakageType,
        related_name="characters",
        help_text="Types of breakage exhibited by this character.",
    )
    damage_score = models.FloatField(
        db_index=True,
        null=True,
        blank=True,
        help_text="Machine-generated score for the level of damage of the character.",
    )

    class Meta:
        ordering = ["created_by_run", "line"]

    def labeller(self):
        return f"{self.line} c. {self.sequence}"

    def book(self):
        return self.line.page.created_by_run.book

    def page(self):
        return self.line.page

    @property
    def y(self):
        if self.y_min is not None:
            return self.y_min
        else:
            return self.line.y_min

    @property
    def width(self):
        return self.x_max - self.x_min

    @property
    def height(self):
        if self.y_max is not None and self.y_min is not None:
            return self.y_max - self.y_min
        else:
            return self.line.height

    @property
    def absolute_coords(self):
        x = max(self.x_min, 0)
        y = max(self.y, 0)
        w = self.width
        h = self.height
        return {"x": x, "y": y, "w": w, "h": h}

    @property
    def root_object(self):
        return self.line.page


# User-based models
class UserBasedModel(uuidModel):
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="%(class)ss"
    )
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ["created_by", "-date_created"]


class CharacterGrouping(UserBasedModel):
    label = models.CharField(
        max_length=200,
        help_text="A descriptive label (will appear in menus etc)",
        unique=True,
    )
    notes = models.TextField(
        max_length=10000,
        blank=True,
        null=False,
        help_text="A description or notes about the grouping",
    )
    characters = models.ManyToManyField(
        Character, related_name="charactergroupings", blank=True
    )

    def labeller(self):
        return self.label
