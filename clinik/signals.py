from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Vente, RapportMensuel

@receiver(post_save, sender=Vente)
def actualiser_rapport_mensuel(sender, instance, created, **kwargs):
    if created:
        RapportMensuel.actualiser_rapport_pour_vente(instance)
