from django.db import models


class Mesure(models.Model):
    patient = models.CharField(max_length=100)
    age = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    laterality = models.CharField(max_length=10, null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    time = models.TimeField(null=True, blank=True)
    sbp = models.IntegerField(null=True, blank=True)
    dbp = models.IntegerField(null=True, blank=True)
    ftptt = models.FloatField(null=True, blank=True)
    ftptt_cv = models.FloatField(null=True, blank=True)
    ftpwv = models.FloatField(null=True, blank=True)
    ftpwv_cv = models.FloatField(null=True, blank=True)
    heart_rate = models.IntegerField(null=True, blank=True)
    heart_rate_cv = models.FloatField(null=True, blank=True)
    finger_signal_amp = models.FloatField(null=True, blank=True)
    toe_signal_amp = models.FloatField(null=True, blank=True)
    valid_pulses_pairs_nbr = models.IntegerField(null=True, blank=True)
    si = models.FloatField(null=True, blank=True)
    csp = models.FloatField(null=True, blank=True)
    cdp = models.FloatField(null=True, blank=True)
    psp = models.FloatField(null=True, blank=True)
    pdp = models.FloatField(null=True, blank=True)
    tms_finger_aomi = models.FloatField(null=True, blank=True)
    tms_toe_aomi = models.FloatField(null=True, blank=True)
    ips = models.FloatField(null=True, blank=True)
    sr = models.IntegerField(null=True, blank=True)
    device = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.patient} ({self.date})"
