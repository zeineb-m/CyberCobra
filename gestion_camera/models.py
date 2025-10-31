from django.db import models


class Camera(models.Model):
    class Status(models.TextChoices):
        RECORDING = 'RECORDING', 'Recording'
        OFFLINE = 'OFFLINE', 'Offline'
        MAINTENANCE = 'MAINTENANCE', 'Maintenance'

    id_camera = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, verbose_name="Nom de la caméra")
    zone = models.CharField(max_length=255, verbose_name="Zone")
    ip_address = models.GenericIPAddressField(protocol='both', verbose_name="Adresse IP")
    resolution = models.CharField(max_length=50, default='1080p', verbose_name="Résolution")
    status = models.CharField(
        max_length=20, 
        choices=Status.choices, 
        default=Status.RECORDING,
        verbose_name="Statut"
    )
    date_ajout = models.DateTimeField(auto_now_add=True, verbose_name="Date d'ajout")

    class Meta:
        verbose_name = "Caméra"
        verbose_name_plural = "Caméras"
        ordering = ['-date_ajout']

    def __str__(self) -> str:
        return f"{self.name} - {self.zone} ({self.get_status_display()})"
