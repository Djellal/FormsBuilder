from django.db import models


class Etablissement(models.Model):
    nom = models.CharField(max_length=255)
    adresse = models.TextField(blank=True)

    class Meta:
        ordering = ['nom']

    def __str__(self):
        return self.nom


class Faculte(models.Model):
    nom = models.CharField(max_length=255)
    etablissement = models.ForeignKey(
        Etablissement, on_delete=models.CASCADE, related_name='facultes', null=True, blank=True
    )

    class Meta:
        ordering = ['nom']

    def __str__(self):
        return self.nom


class Domaine(models.Model):
    nom = models.CharField(max_length=255)
    faculte = models.ForeignKey(Faculte, on_delete=models.CASCADE, related_name='domaines')

    class Meta:
        ordering = ['nom']

    def __str__(self):
        return f"{self.nom} ({self.faculte.nom})"
