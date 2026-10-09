import random

RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
SUITS = ["C", "D", "H", "S"]


class Deck:
    def __init__(self):
        self.cards = []
        self.reset()

    def reset(self):
        self.cards = [(rank, suit) for suit in SUITS for rank in RANKS]
        random.shuffle(self.cards)

    def draw(self):
        if not self.cards:
            self.reset()
        return self.cards.pop() if self.cards else None

    def __len__(self):
        return len(self.cards)


def hand_value(hand):
    """
    Calculate blackjack hand score.
    Aces count as 11 unless that causes the hand to exceed 21,
    in which case Aces count as 1.
    """
    value = 0
    aces = 0
    for rank, _ in hand:
        if rank == "A":
            aces += 1
            value += 11
        elif rank in {"J", "Q", "K"}:
            value += 10
        else:
            value += int(rank)

    while value > 21 and aces > 0:
        value -= 10
        aces -= 1

    return value


def is_blackjack(hand):
    """Check if hand is a natural blackjack (2 cards totaling 21)."""
    return len(hand) == 2 and hand_value(hand) == 21

