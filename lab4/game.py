from cards import Deck, hand_value, is_blackjack


class Blackjack:
    def __init__(self, starting_chips=100):
        self.chips = starting_chips
        self.deck = Deck()

    def show(self, player, dealer, hide=True):
        if hide:
            shown_dealer = [f"{dealer[0][0]}{dealer[0][1]}"] + ["??"] * (len(dealer) - 1)
            print("Dealer:", " ".join(shown_dealer))
        else:
            shown_dealer = [f"{r}{s}" for r, s in dealer]
            print("Dealer:", " ".join(shown_dealer), "=", hand_value(dealer))
        print("Player:", " ".join(f"{r}{s}" for r, s in player), "=", hand_value(player))

    def get_wager(self):
        """Prompt for and validate the player's wager."""
        while True:
            raw = input(f"\nCurrent chips: {self.chips}\nEnter wager (1-{self.chips}) [or 'q' to quit]: ").strip()
            if raw.lower() == "q":
                return None
            try:
                wager = int(raw)
            except ValueError:
                print("Invalid wager. Please enter a valid whole number.")
                continue

            if wager <= 0:
                print("Invalid wager. Bet must be at least 1 chip.")
            elif wager > self.chips:
                print(f"Invalid wager. You cannot bet more than your current bankroll ({self.chips} chips).")
            else:
                return wager

    def round(self):
        if len(self.deck) < 15:
            self.deck.reset()

        wager = self.get_wager()
        if wager is None:
            return False

        player = [self.deck.draw(), self.deck.draw()]
        dealer = [self.deck.draw(), self.deck.draw()]

        print("\n--- Dealing Cards ---")
        self.show(player, dealer, hide=True)

        player_bj = is_blackjack(player)
        dealer_bj = is_blackjack(dealer)

        # Check natural blackjack
        if player_bj or dealer_bj:
            print("\n--- Blackjack Check ---")
            self.show(player, dealer, hide=False)
            if player_bj and dealer_bj:
                print("Both player and dealer have Blackjack! Push.")
            elif player_bj:
                payout = int(wager * 1.5)
                self.chips += payout
                print(f"Blackjack! Player wins {payout} chips.")
            else:
                self.chips -= wager
                print(f"Dealer has Blackjack! Player loses {wager} chips.")
            print(f"Current chips: {self.chips}")
            return True

        # Player turn
        while hand_value(player) < 21:
            key = input("\n[h]it [s]tand [q]uit: ").strip().lower()
            if key == "q":
                print("Quitting current game.")
                return False
            if key == "s":
                print(f"Player stands at {hand_value(player)}.")
                break
            if key == "h":
                card = self.deck.draw()
                player.append(card)
                print(f"Player drew {card[0]}{card[1]}.")
                self.show(player, dealer, hide=True)
                if hand_value(player) > 21:
                    print(f"\nPlayer busts ({hand_value(player)})! Dealer wins.")
                    self.chips -= wager
                    print(f"-{wager} chips. Current chips: {self.chips}")
                    return True
                if hand_value(player) == 21:
                    print("Player reached 21!")
                    break
            else:
                print("Invalid command. Please enter 'h' to hit, 's' to stand, or 'q' to quit.")

        # Dealer turn
        print("\n--- Dealer's Turn ---")
        self.show(player, dealer, hide=False)
        while hand_value(dealer) < 17:
            card = self.deck.draw()
            dealer.append(card)
            print(f"Dealer draws {card[0]}{card[1]}.")
            self.show(player, dealer, hide=False)

        # Final showdown
        pv, dv = hand_value(player), hand_value(dealer)
        print("\n--- Final Result ---")
        if dv > 21:
            print(f"Dealer busts ({dv})! Player wins.")
            self.chips += wager
            print(f"+{wager} chips. Current chips: {self.chips}")
        elif pv > dv:
            print(f"Player wins ({pv} vs {dv})!")
            self.chips += wager
            print(f"+{wager} chips. Current chips: {self.chips}")
        elif pv < dv:
            print(f"Dealer wins ({dv} vs {pv})!")
            self.chips -= wager
            print(f"-{wager} chips. Current chips: {self.chips}")
        else:
            print(f"Push ({pv} vs {dv})! Wager returned.")
            print(f"Current chips: {self.chips}")

        return True

    def run(self):
        print("=" * 40)
        print("Blackjack — starting chips:", self.chips)
        print("=" * 40)
        while self.chips > 0:
            if not self.round():
                print(f"\nExiting game. Final chips: {self.chips}")
                return
            if self.chips <= 0:
                print("\nYou ran out of chips! Game over.")
                return
            while True:
                play_again = input("\nPlay again? [y/n]: ").strip().lower()
                if play_again in {"y", "yes"}:
                    break
                elif play_again in {"n", "no"}:
                    print(f"\nCash out! Final chips: {self.chips}. Thanks for playing!")
                    return
                else:
                    print("Please enter 'y' to play again or 'n' to exit.")

