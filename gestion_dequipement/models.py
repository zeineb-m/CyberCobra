from django.db import models


class Equipement(models.Model):
    class Statut(models.TextChoices):
        AUTORISE = 'AUTORISE', 'Autorisé'
        INTERDIT = 'INTERDIT', 'Interdit'
        SOUMIS = 'SOUMIS', 'Soumis à autorisation'

    id_equipement = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=255)
    statut = models.CharField(max_length=20, choices=Statut.choices, default=Statut.AUTORISE)
    date_ajout = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='equipements/', null=True, blank=True)
    image_hash = models.CharField(max_length=64, blank=True, null=True)
    phash = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        verbose_name = "Équipement"
        verbose_name_plural = "Équipements"
        ordering = ['-date_ajout']

    def __str__(self) -> str:
        return f"{self.nom} ({self.get_statut_display()})"
