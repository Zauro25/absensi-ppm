# backend/pengurus_app/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField
import uuid
import json

def santri_photo_upload_path(instance, filename):
    # auto rename file: SANTRI_<santri_id>_<timestamp>.jpg
    ext = filename.split('.')[-1]
    filename = f"SANTRI_{instance.santri_id}_{int(timezone.now().timestamp())}.{ext}"
    return f"santri_photos/{filename}"

class Santri(models.Model):
    JENIS_CHOICES = [('L','Laki-laki'), ('P','Perempuan')]
    SEKTOR_CHOICES = [('kepuh','Kepuh'), ('sidobali','Sidobali')]

    santri_id = models.CharField(max_length=50, unique=True)
    nama = models.CharField(max_length=150)
    asal_daerah = models.CharField(max_length=150, blank=True, null=True)
    sektor = models.CharField(max_length=20, choices=SEKTOR_CHOICES, blank=True, null=True)
    angkatan = models.CharField(max_length=50, blank=True, null=True)
    jenis_kelamin = models.CharField(max_length=1, choices=JENIS_CHOICES, default='L')
    foto = models.ImageField(upload_to=santri_photo_upload_path, null=True, blank=True)
    face_encoding = models.JSONField(null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="santri_profile", null=True, blank=True)

    def __str__(self):
        return f"{self.santri_id} - {self.nama}"


class Absensi(models.Model):
    SESI_CHOICES = [('Subuh','Subuh'), ('Sore','Sore'), ('Malam','Malam')]
    STATUS_CHOICES = [('Hadir','Hadir'),('T1','T1'),('T2','T2'),('T3','T3')]

    santri = models.ForeignKey(Santri, on_delete=models.CASCADE)
    tanggal = models.DateField()
    sesi = models.CharField(max_length=10, choices=SESI_CHOICES)
    waktu_scan = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)  # pengurus yang mencatat

    class Meta:
        unique_together = ('santri', 'tanggal', 'sesi')  # satu santri satu kali per sesi

    def __str__(self):
        return f"{self.santri} - {self.tanggal} {self.sesi} - {self.status}"
class SuratIzin(models.Model):
    SESI_CHOICES = [('Subuh','Subuh'), ('Sore','Sore'), ('Malam','Malam')]
    santri = models.ForeignKey(Santri, on_delete=models.CASCADE)
    tanggal = models.DateField()
    sesi = models.CharField(max_length=10, choices=SESI_CHOICES)
    file = models.FileField(upload_to='surat_izin/')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    uploaded_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, default='Disetujui')  # langsung sah
    note = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('santri', 'tanggal', 'sesi')

    def __str__(self):
        return f"Izin {self.santri} - {self.tanggal} {self.sesi} - {self.status}"
