import random
from collections import Counter
import itertools

class Player:
    def __init__(self, buyIn):
        self.buyIn = buyIn
        self.hand = []

    def get_cards(self, displayed_cards):
        value_list = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        suit_list = ['Hearts', 'Clubs', 'Spades', 'Diamonds']
        while True:
            card = (random.choice(value_list), random.choice(suit_list))
            if card not in displayed_cards:
                displayed_cards[card] = True
                return card

    def place_bet(self, amount):
        if amount > self.buyIn:
            return False
        self.buyIn -= amount
        return True

class Dealer:
    def __init__(self):
        self.hand = []

    def get_cards(self, displayed_cards):
        value_list = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        suit_list = ['Hearts', 'Clubs', 'Spades', 'Diamonds']
        while True:
            card = (random.choice(value_list), random.choice(suit_list))
            if card not in displayed_cards:
                displayed_cards[card] = True
                return card

class Game:
    def __init__(self, buy_in):
        self.player = Player(buy_in)
        self.dealer = Dealer()
        self.ante = buy_in // 30
        self.blind = self.ante
        self.pot = self.blind
        self.displayed_cards = {}
        self.community_cards = []
        self.action_stage = "pre-flop"
        self.has_bet = {"pre-flop": False, "flop": False, "turn": False}
        self.started = False

    def reset_for_new_hand(self):
        self.displayed_cards = {}
        self.community_cards = []
        self.player.hand = []
        self.dealer.hand = []
        self.pot = self.blind
        self.action_stage = "pre-flop"
        self.has_bet = {"pre-flop": False, "flop": False, "turn": False}
        self.started = True

    def start_hand(self):
        self.reset_for_new_hand()
        if self.player.buyIn < self.blind:
            return {"error": "Insufficient balance to start a new hand."}
        self.player.hand = [self.player.get_cards(self.displayed_cards), self.player.get_cards(self.displayed_cards)]
        self.dealer.hand = [self.dealer.get_cards(self.displayed_cards), self.dealer.get_cards(self.displayed_cards)]
        self.player.buyIn -= self.blind
        return {
            "player_hand": self.player.hand,
            "dealer_hand": [],
            "balance": self.player.buyIn,
            "pot": self.pot,
            "stage": self.action_stage
        }

    def place_bet(self, multiplier):
        if not self.started:
            return {"success": False, "message": "Game not started"}
        amount = multiplier * self.ante
        if not self.player.place_bet(amount):
            return {"success": False, "message": "Not enough balance"}
        self.pot += amount
        self.has_bet[self.action_stage] = True
        if len(self.community_cards) < 3:
            self.deal_flop()
        while len(self.community_cards) < 5:
            self.deal_turn_or_river()
        self.action_stage = "complete"
        result = self.determine_winner()
        return {
            "success": True,
            "pot": self.pot,
            "balance": self.player.buyIn,
            "player_hand": self.player.hand,
            "dealer_hand": self.dealer.hand,
            "community_cards": self.community_cards,
            "winner": result["winner"],
            "dealer_hand_type": result["dealer_hand_type"],
            "player_hand_type": result["player_hand_type"],
            "message": result["message"]
        }

    def check(self):
        if not self.started:
            return {"error": "Game not started"}
        if self.action_stage == "river" or self.has_bet.get(self.action_stage):
            return {"error": "Cannot check at this stage."}
        if self.action_stage == "pre-flop":
            cards = self.deal_flop()
            self.action_stage = "flop"
            return {"cards": cards, "stage": self.action_stage}
        elif self.action_stage == "flop":
            card = self.deal_turn_or_river()
            return {"card": card, "stage": self.action_stage}
        elif self.action_stage == "turn":
            card = self.deal_turn_or_river()
            self.action_stage = "complete"
            result = self.determine_winner()
            return {
                "card": card,
                "stage": "complete",
                "dealer_hand": self.dealer.hand,
                "player_hand": self.player.hand,
                "community_cards": self.community_cards,
                "winner": result["winner"],
                "balance": result["balance"],
                "dealer_hand_type": result["dealer_hand_type"],
                "player_hand_type": result["player_hand_type"],
                "message": result["message"]
            }

    def deal_flop(self):
        for _ in range(3):
            self.community_cards.append(self.player.get_cards(self.displayed_cards))
        self.action_stage = "flop"
        return self.community_cards

    def deal_turn_or_river(self):
        self.community_cards.append(self.player.get_cards(self.displayed_cards))
        if len(self.community_cards) == 5:
            self.action_stage = "river"
        else:
            self.action_stage = "turn"
        return self.community_cards[-1]

    def fold(self):
        if not self.started:
            return {"error": "Game not started"}
        return {"winner": "dealer", "balance": self.player.buyIn}

    def evaluate_hand(self, cards):
        values_dict = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
                       '7': 7, '8': 8, '9': 9, '10': 10,
                       'J': 11, 'Q': 12, 'K': 13, 'A': 14}
        best_rank = -1
        best_type = ""
        best_values = []

        for combo in itertools.combinations(cards, 5):
            values = sorted([values_dict[c[0]] for c in combo], reverse=True)
            suits = [c[1] for c in combo]
            value_counts = Counter(values)
            unique_vals = sorted(set(values), reverse=True)

            is_flush = len(set(suits)) == 1
            is_straight = len(unique_vals) == 5 and (unique_vals[0] - unique_vals[4] == 4)
            is_royal = values == [14, 13, 12, 11, 10]

            if is_flush and is_royal:
                rank = 9; hand_type = "Royal Flush"
            elif is_flush and is_straight:
                rank = 8; hand_type = "Straight Flush"
            elif 4 in value_counts.values():
                rank = 7; hand_type = "Four of a Kind"
            elif 3 in value_counts.values() and 2 in value_counts.values():
                rank = 6; hand_type = "Full House"
            elif is_flush:
                rank = 5; hand_type = "Flush"
            elif is_straight:
                rank = 4; hand_type = "Straight"
            elif 3 in value_counts.values():
                rank = 3; hand_type = "Three of a Kind"
            elif list(value_counts.values()).count(2) == 2:
                rank = 2; hand_type = "Two Pair"
            elif 2 in value_counts.values():
                rank = 1; hand_type = "One Pair"
            else:
                rank = 0; hand_type = "High Card"

            if rank > best_rank or (rank == best_rank and values > best_values):
                best_rank = rank
                best_type = hand_type
                best_values = values

        return best_rank, best_values, best_type

    def determine_winner(self):
        player_score, player_vals, player_type = self.evaluate_hand(self.player.hand + self.community_cards)
        dealer_score, dealer_vals, dealer_type = self.evaluate_hand(self.dealer.hand + self.community_cards)

        dealer_qualifies = dealer_score >= 1 and dealer_vals[0] >= 4  # Pair of 4s or better

        result = {
            "player_hand_type": player_type,
            "dealer_hand_type": dealer_type
        }

        if not dealer_qualifies:
            self.player.buyIn += self.pot
            result.update({
                "winner": "player",
                "balance": self.player.buyIn,
                "message": "Dealer did not qualify. Bets returned to player."
            })
        elif player_score > dealer_score or (player_score == dealer_score and player_vals > dealer_vals):
            self.player.buyIn += self.pot
            result.update({
                "winner": "player",
                "balance": self.player.buyIn,
                "message": f"Player wins with {player_type}."
            })
        elif dealer_score > player_score or (player_score == dealer_score and dealer_vals > player_vals):
            result.update({
                "winner": "dealer",
                "balance": self.player.buyIn,
                "message": f"Dealer wins with {dealer_type}."
            })
        else:
            self.player.buyIn += self.pot
            result.update({
                "winner": "tie",
                "balance": self.player.buyIn,
                "message": "It's a tie."
            })

        return result
