from enum import Enum


class BanReason(Enum):
    OTHER = None
    RUDE = 1
    SPAM = 2
    TOPIC = 3


BAN_REASON_CHOICES = (
    (BanReason.RUDE.value, 'Rude'),
    (BanReason.SPAM.value, 'Spam'),
    (BanReason.TOPIC.value, 'Offtopic (Wrong area)'),

    (BanReason.OTHER.value, 'Other'),  # Keep at the button
)


FlagReason = BanReason
FLAG_REASON_CHOICES = BAN_REASON_CHOICES
