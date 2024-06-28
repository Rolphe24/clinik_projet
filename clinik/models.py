from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from datetime import datetime
from datetime import date
from django.db.models import Sum
from decimal import Decimal
class Service(models.Model):
    id = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=100)

class Patient(models.Model):
    id_patient = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=100)
    a_consulte = models.BooleanField(default=False)
    est_hospitalise = models.BooleanField(default=False)
    est_examine = models.BooleanField(default=False)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)

class Salle(models.Model):
    capacite = models.IntegerField(default=5)
    occupee = models.BooleanField(default=False)

class Examen(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    # Autres champs pour le modèle Examen

class Produit(models.Model):
    id_produit = models.AutoField(primary_key=True)
    designation = models.CharField(max_length=100)
    quantite = models.IntegerField()
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)

class Vente(models.Model):
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.IntegerField()
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    prix_de_vente = models.DecimalField(max_digits=10, decimal_places=2)
    date_vente = models.DateTimeField(auto_now_add=True)

    def calculer_benefice(self):
        return self.prix_de_vente - self.prix_unitaire
    # Calculer le bénéfice réalisé


class Utilisateur(models.Model):
    id = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=255)
    prenom = models.CharField(max_length=255)
    adresse = models.CharField(max_length=255)
    num_tel = models.CharField(max_length=15)
    password = models.CharField(max_length=255)

    def __str__(self):
        return self.nom

    def save(self, *args, **kwargs):
        # Hachage du mot de passe avant la sauvegarde
        self.password = make_password(self.password)
        super().save(*args, **kwargs)

class RapportMensuel(models.Model):
    mois = models.CharField(max_length=7, unique=True)
    patients_consultes = models.IntegerField(default=0)
    patients_hospitalises = models.IntegerField(default=0)
    patients_examines = models.IntegerField(default=0)
    montant_ventes = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    benefice_realise = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    @classmethod
    def generer_rapport(cls):
        mois_en_cours = datetime.now().replace(day=1)
        mois_formatte = mois_en_cours.strftime("%m/%Y")

        patients_consultes = Patient.objects.filter(a_consulte=True).count()
        patients_hospitalises = Patient.objects.filter(est_hospitalise=True).count()
        patients_examines = Patient.objects.filter(est_examine=True).count()

        ventes_mois_en_cours = Vente.objects.filter(date_vente__month=mois_en_cours.month)
        montant_ventes = ventes_mois_en_cours.aggregate(Sum('prix_de_vente'))['prix_de_vente__sum'] or Decimal('0.00')
        benefice_realise = sum(vente.calculer_benefice() for vente in ventes_mois_en_cours)

        rapport, created = cls.objects.get_or_create(
            mois=mois_formatte,
            defaults={
                'patients_consultes': patients_consultes,
                'patients_hospitalises': patients_hospitalises,
                'patients_examines': patients_examines,
                'montant_ventes': montant_ventes,
                'benefice_realise': benefice_realise,
            }
        )

        if not created:
            rapport.montant_ventes = montant_ventes
            rapport.benefice_realise = benefice_realise
            rapport.save()

        return rapport, mois_formatte

    @classmethod
    def actualiser_rapport_pour_vente(cls, vente):
        mois_formatte = vente.date_vente.strftime("%m/%Y")
        rapport, created = cls.objects.get_or_create(
            mois=mois_formatte,
            defaults={
                'montant_ventes': Decimal('0.00'),
                'benefice_realise': Decimal('0.00'),
            }
        )
        rapport.montant_ventes += Decimal(str(vente.prix_de_vente))
        rapport.benefice_realise += Decimal(str(vente.calculer_benefice()))
        rapport.save()
