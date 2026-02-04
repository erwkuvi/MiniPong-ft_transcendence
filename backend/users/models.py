from django.contrib.auth.models import AbstractUser
from django.db import models
from .validators import validate_file_size

AUTH_PROVIDERS ={'email': 'email', '42api': '42api', 'google': 'Google'}
MATCH_MODE ={'regular': 'regular', 'tournament': 'tournament'}

class User(AbstractUser):
    email = models.EmailField(unique=True)
    auth_provider=models.CharField(max_length=50, default=AUTH_PROVIDERS.get("email"))
    otpauth_url = models.CharField(max_length=225, blank=True, null=True)#represents the value encoded into the generated QR code
    otp_base32 = models.CharField(max_length=255, null=True)#serves as a unique identifier for a user 
    qr_code = models.FileField(upload_to="qr/", blank=True, null=True)
    qr_code = models.ImageField(upload_to="qrcode/",blank=True, null=True)
    login_otp = models.CharField(max_length=255, null=True, blank=True)
    login_otp_used = models.BooleanField(default=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)
    otp_active = models.BooleanField(default=False)

class PlayerProfile(models.Model):
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('lt', 'Lithuanian'),
        ('pl', 'Polish'),
        ('es', 'Spanish'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=50, unique=True)
    avatar = models.ImageField(
        upload_to="avatars/",
        default='avatars\/avatar.png',
        null=True, blank=True,
        validators=[validate_file_size]
    )
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    friends = models.ManyToManyField("self", blank=True)
    in_tournament = models.BooleanField(default=False)
    is_host = models.BooleanField(default=False)
    tournament = models.ForeignKey('Tournament', related_name='player_profiles', on_delete=models.SET_NULL, null=True, blank=True)
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='en')
    mode = models.BooleanField(default=True)#True would be dark mode on frontend, False would be light mode
    curr_match = models.ForeignKey(
        'Match', related_name='current_players', on_delete=models.SET_NULL,
        null=True, blank=True)
    online = models.BooleanField(default=False)
    matches = models.ManyToManyField(
        'Match', through='PlayerMatch', related_name='stats', blank=True)

    def get_wins(self):
        return self.won_matches.count()

    def get_losses(self):
        total_matches = self.player1_matches.filter(winner__isnull=False).count() + self.player2_matches.filter(winner__isnull=False).count()
        won_matches = self.won_matches.count()
        total_losses = total_matches - won_matches
        #print(f"Total losses: {total_losses}")
        return total_losses

    @property
    def wins(self):
        return self.get_wins()

    @property
    def losses(self):
        return self.get_losses()

    def __str__(self):
        return str(self.user.id)

    #def __str__(self):
    #    return self.user.email  # This will display the email in the profile

class Tournament(models.Model):
    champion = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    host = models.ForeignKey(User, related_name='tournament_host', on_delete=models.CASCADE)


class Match(models.Model):
    MATCH_MODE_CHOICES = [
        ('regular', 'Regular'),
        ('tournament', 'Tournament'),
    ]
    tournament = models.ForeignKey(Tournament, related_name='matches', on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    mode = models.CharField(max_length=50, choices=MATCH_MODE_CHOICES, default='regular')
    idx = models.IntegerField(default=0)
    level = models.IntegerField(default=0)
    finished = models.BooleanField(default=False)
    player1 = models.ForeignKey(
        PlayerProfile, related_name='player1_matches',
        on_delete=models.CASCADE)
    player2 = models.ForeignKey(
        PlayerProfile, related_name='player2_matches',
        on_delete=models.CASCADE, null=True, blank=True)
    winner = models.ForeignKey(
        PlayerProfile, related_name='won_matches', on_delete=models.CASCADE, null=True, blank=True) 
    score_player1 = models.IntegerField(default=0)
    score_player2 = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.player1.display_name} vs {self.player2.display_name if self.player2 else "TBD"} on {self.date}'


class PlayerMatch(models.Model):
    player = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.player} played in match {self.match} on {self.date}"
