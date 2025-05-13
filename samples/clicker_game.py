import random

class Card:
    SUITS_DISPLAY = {"S": "♠", "H": "♥", "D": "♦", "C": "♣"}
    REGULAR_RANKS_ORDER = ['2','3','4','5','6','7','8','9','T','J','Q','K','A']
    SPADES_SUIT_RANKS_ORDER = ['3','4','5','6','7','8','9','T','J','Q','K','A','2']

    TRUMP_POWER_MAP = {rank: i for i, rank in enumerate(SPADES_SUIT_RANKS_ORDER)}
    TRUMP_POWER_MAP["LJ"] = len(SPADES_SUIT_RANKS_ORDER)
    TRUMP_POWER_MAP["BJ"] = len(SPADES_SUIT_RANKS_ORDER) + 1

    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
        self.is_trump = (self.suit == "S") or (self.suit == "JOKER")

    def __str__(self):
        if self.suit == "JOKER":
            return "Little Joker" if self.rank == "LJ" else "Big Joker"
        return f"{self.rank}{self.SUITS_DISPLAY.get(self.suit, self.suit)}"

    def __repr__(self):
        return self.__str__()

    def get_power(self, led_suit_for_trick):
        if self.is_trump:
            return (2, self.TRUMP_POWER_MAP[self.rank])
        if self.suit == led_suit_for_trick:
            if self.rank in self.REGULAR_RANKS_ORDER:
                 return (1, self.REGULAR_RANKS_ORDER.index(self.rank))
            else:
                 return (0, -1)
        return (0, -1)

    def sort_key(self):
        suit_priority = {"C": 0, "D": 1, "H": 2, "S": 3, "JOKER": 3}
        if self.is_trump:
            rank_power = self.TRUMP_POWER_MAP[self.rank]
        else:
            if self.rank in self.REGULAR_RANKS_ORDER:
                rank_power = self.REGULAR_RANKS_ORDER.index(self.rank)
            else:
                rank_power = -1
        return (suit_priority.get(self.suit, -1), rank_power)

class Deck:
    def __init__(self):
        self.cards = []
        self.build()

    def build(self):
        self.cards = []
        for suit_val in ["H", "D", "C"]:
            for rank_val in Card.REGULAR_RANKS_ORDER:
                self.cards.append(Card(suit_val, rank_val))
        for rank_val in Card.SPADES_SUIT_RANKS_ORDER:
            self.cards.append(Card("S", rank_val))
        self.cards.append(Card("JOKER", "LJ"))
        self.cards.append(Card("JOKER", "BJ"))

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self, num_cards):
        dealt_cards = []
        for _ in range(num_cards):
            if self.cards:
                dealt_cards.append(self.cards.pop())
            else:
                break
        return dealt_cards

class Player:
    def __init__(self, name, is_human=True):
        self.name = name
        self.hand = []
        self.bid = 0 
        self.tricks_won_this_round = 0
        self.partner = None
        self.team_id = None 
        self.is_human = is_human

    def add_card_to_hand(self, card):
        self.hand.append(card)

    def add_cards_to_hand(self, cards_list):
        self.hand.extend(cards_list)
        self.sort_hand()

    def sort_hand(self):
        self.hand.sort(key=lambda card: card.sort_key())

    def display_hand(self, team_score_info=""): 
        self.sort_hand()
        # This print is direct to the player, not via Rashieme
        print(f"\n{self.name}'s hand {team_score_info}:")
        if not self.hand:
            print("  Hand is empty.")
            return
        for i, card in enumerate(self.hand):
            print(f"  {i+1}: {card}")
        print("-" * 20)


    def play_card(self, card_index_or_card_obj, current_trick_cards=None, led_suit_for_trick=None):
        card_to_play = None
        if isinstance(card_index_or_card_obj, int):
            if 1 <= card_index_or_card_obj <= len(self.hand):
                card_to_play = self.hand[card_index_or_card_obj - 1]
            else:
                # This message is direct feedback to player, not Rashieme
                print("Invalid card index.")
                return None
        elif isinstance(card_index_or_card_obj, Card):
            if card_index_or_card_obj in self.hand:
                card_to_play = card_index_or_card_obj
            else:
                print("Card not in hand.") # Direct feedback
                return None
        else:
            print("Invalid parameter for playing card.") # Direct feedback
            return None

        # Validation logic (direct feedback for invalid play)
        if led_suit_for_trick and card_to_play.suit != led_suit_for_trick and card_to_play.suit != "JOKER":
            can_follow_suit = any(c.suit == led_suit_for_trick for c in self.hand)
            if can_follow_suit and card_to_play.suit != "S":
                is_spade_led = (led_suit_for_trick == "S")
                has_non_spade_of_led_suit = any(c.suit == led_suit_for_trick and c.suit != "S" for c in self.hand)
                if not is_spade_led and has_non_spade_of_led_suit:
                    # Direct feedback for invalid play
                    print(f"Invalid play. You must follow the led suit ({led_suit_for_trick}) if possible with a non-Spade card.")
                    return None
        
        self.hand.remove(card_to_play)
        return card_to_play

class Game:
    def __init__(self, player_names, target_score=500):
        if len(player_names) != 4:
            raise ValueError("Partnership game currently supports exactly 4 players.")

        self.players = []
        for i, name in enumerate(player_names):
            player = Player(name, is_human=(i == 0)) 
            player.team_id = 1 if i % 2 == 0 else 2  
            self.players.append(player)

        self.players[0].partner = self.players[2]
        self.players[2].partner = self.players[0]
        self.players[1].partner = self.players[3]
        self.players[3].partner = self.players[1]
        
        self.deck = Deck()
        self.kitty = []
        
        self.current_round_individual_bids = {} 
        self.current_round_team_contracts = {1: {'bid': 0, 'nil_players': []}, 
                                             2: {'bid': 0, 'nil_players': []}}
        self.team_tricks_this_round = {1: 0, 2: 0}
        self.team_scores = {1: 0, 2: 0}

        self.dealer_index = 0 
        self.target_score = target_score
        self.current_round_number = 0
        self.game_over = False
        self.winning_team_id = None
        self.scorekeeper_name = "Rashieme"

    def announce(self, message):
        print(f"{self.scorekeeper_name}: {message}")

    def get_players_in_team(self, team_id):
        return [p for p in self.players if p.team_id == team_id]

    def get_player_names_for_team(self, team_id):
        return ", ".join([p.name for p in self.get_players_in_team(team_id)])

    def deal_cards_and_reveal_kitty(self):
        self.deck.build()
        self.deck.shuffle()

        self.team_tricks_this_round = {1: 0, 2: 0}
        self.current_round_team_contracts = {1: {'bid': 0, 'nil_players': []}, 
                                             2: {'bid': 0, 'nil_players': []}}
        self.current_round_individual_bids = {}
        for player in self.players:
            player.hand = []
            player.bid = 0 
            player.tricks_won_this_round = 0
        self.kitty = []

        num_total_cards = len(self.deck.cards)
        num_players = len(self.players)
        if num_players == 0: return

        num_kitty_cards = 2
        if num_total_cards < num_kitty_cards:
            self.announce("Not enough cards to form a full kitty!")
            self.kitty = [self.deck.cards.pop() for _ in range(len(self.deck.cards))]
            if self.kitty: self.kitty.reverse()
            return

        self.kitty = [self.deck.cards.pop() for _ in range(num_kitty_cards)]
        self.kitty.reverse()

        self.announce("Alright folks, the last two cards of the deal are flipped up to form the kitty!")
        for card_idx, card in enumerate(self.kitty): 
            self.announce(f"  Kitty card {card_idx+1}: {card}")
        self.announce("-" * 20)


        num_cards_for_players = len(self.deck.cards)
        cards_per_player_base = num_cards_for_players // num_players
        extra_cards = num_cards_for_players % num_players
        
        deal_order_indices = [(self.dealer_index + 1 + i) % num_players for i in range(num_players)]

        for _ in range(cards_per_player_base):
            for player_idx_in_deal_order in deal_order_indices:
                if self.deck.cards:
                    self.players[player_idx_in_deal_order].add_card_to_hand(self.deck.cards.pop())
        
        for i in range(extra_cards):
            player_idx_in_deal_order = deal_order_indices[i]
            if self.deck.cards:
                self.players[player_idx_in_deal_order].add_card_to_hand(self.deck.cards.pop())

        for player_obj in self.players: player_obj.sort_hand() # Changed 'player' to 'player_obj' to avoid conflict
        self.announce("Card dealing is complete!")

    def bidding_phase(self):
        self.announce("\n--- Time for Bidding! ---")
        self.announce(f"The kitty revealed earlier was: {self.kitty}")

        bidding_order_indices = [(self.dealer_index + 1 + i) % len(self.players) for i in range(len(self.players))]
        max_possible_tricks_per_player = (54 - 2) // len(self.players) if self.players else 0

        for player_idx in bidding_order_indices:
            current_player_obj = self.players[player_idx] # Changed 'player' to 'current_player_obj'
            team_id = current_player_obj.team_id
            team_score_info = f"(Team {team_id} Score: {self.team_scores[team_id]})"
            self.announce(f"Bidding is on {current_player_obj.name} (Team {team_id}).")

            if current_player_obj.is_human:
                current_player_obj.display_hand(team_score_info) # Used current_player_obj
                valid_bid = False
                while not valid_bid:
                    try:
                        bid_input = input(f"{current_player_obj.name}, enter your bid (0 to {max_possible_tricks_per_player}): ")
                        bid = int(bid_input)
                        if 0 <= bid <= max_possible_tricks_per_player:
                            current_player_obj.bid = bid
                            self.announce(f"{current_player_obj.name} bids {bid}.")
                            valid_bid = True
                        else:
                            print(f"Invalid bid. Must be between 0 and {max_possible_tricks_per_player}.")
                    except ValueError: print("Invalid input. Enter a number.") 
            else: 
                bid_points = sum(1 for card in current_player_obj.hand if card.is_trump and card.rank in ["BJ", "LJ", "2", "A", "K"]) + \
                             sum(0.5 for card in current_player_obj.hand if card.is_trump and card.rank in ["Q", "J", "T"])
                ai_estimated_bid = round(bid_points / 1.5) if bid_points > 0 else random.randint(0,2) 
                current_player_obj.bid = max(0, min(ai_estimated_bid, max_possible_tricks_per_player))
                self.announce(f"{current_player_obj.name} (AI) bids: {current_player_obj.bid}")
            
            self.current_round_individual_bids[current_player_obj.name] = current_player_obj.bid

        for player_obj in self.players: # Changed 'player' to 'player_obj'
            if player_obj.bid == 0: 
                self.current_round_team_contracts[player_obj.team_id]['nil_players'].append(player_obj)
            else:
                self.current_round_team_contracts[player_obj.team_id]['bid'] += player_obj.bid
        
        self.announce("\n--- Team Contracts for the Round ---")
        for team_id, contract_info in self.current_round_team_contracts.items():
            team_players_str = self.get_player_names_for_team(team_id)
            nil_info_list = [p.name for p in contract_info['nil_players']]
            nil_display = f" (Nil bids from: {', '.join(nil_info_list)})" if nil_info_list else ""
            self.announce(f"Team {team_id} ({team_players_str}): Contract Bid {contract_info['bid']} tricks{nil_display}")


    def play_round(self):
        self.announce("\n--- Let's Play the Hand! ---")
        num_tricks_to_play = (54-2) // len(self.players) if self.players else 0
        
        current_leader_idx = (self.dealer_index + 1) % len(self.players) if self.players else 0

        for i in range(num_tricks_to_play):
            leader_name = self.players[current_leader_idx].name
            self.announce(f"\nPlaying Book {i+1} of {num_tricks_to_play}. It's on {leader_name} (Team {self.players[current_leader_idx].team_id}) to lead.")
            trick_cards = [] 
            led_suit_for_trick = None
            actual_led_suit_for_power = None 

            for j in range(len(self.players)):
                player_idx = (current_leader_idx + j) % len(self.players)
                current_player = self.players[player_idx] # This is the correct current player object
                played_card = None
                team_id = current_player.team_id
                team_score_info = f"(Team {team_id} Score: {self.team_scores[team_id]})"

                if current_player.is_human:
                    if j > 0 : self.announce(f"Current book: {[(p.name, c) for p,c in trick_cards]}")
                    if led_suit_for_trick and j > 0: self.announce(f"Led suit is: {led_suit_for_trick}")
                    current_player.display_hand(team_score_info) # CORRECTED: Was 'player.display_hand'
                    
                    valid_choice = False
                    while not valid_choice:
                        try:
                            choice = input(f"{current_player.name} (Team {team_id}), choose card (1-{len(current_player.hand)}): ")
                            played_card_obj = current_player.play_card(int(choice), [c for _, c in trick_cards], led_suit_for_trick) 
                            if played_card_obj:
                                played_card = played_card_obj
                                valid_choice = True
                        except (ValueError, IndexError): print("Invalid choice. Try again.")
                else: 
                    card_to_play_ai = None
                    if led_suit_for_trick:
                        for potential_card in sorted(current_player.hand, key=lambda c: c.sort_key()):
                            if potential_card.suit == led_suit_for_trick:
                                card_to_play_ai = potential_card; break
                    if not card_to_play_ai:
                        sorted_hand_for_ai = sorted(current_player.hand, key=lambda c: (c.is_trump, c.sort_key()))
                        if sorted_hand_for_ai: card_to_play_ai = sorted_hand_for_ai[0]

                    if card_to_play_ai:
                        played_card = current_player.play_card(card_to_play_ai, [c for _, c in trick_cards], led_suit_for_trick)
                    
                    if not played_card and current_player.hand: 
                         played_card = current_player.play_card(1, [c for _,c in trick_cards], led_suit_for_trick) 
                
                if played_card: 
                    self.announce(f"{current_player.name} (Team {current_player.team_id}) plays: {played_card}")
                    trick_cards.append((current_player, played_card))
                    if j == 0: 
                        led_suit_for_trick = played_card.suit
                        actual_led_suit_for_power = played_card.suit
                        if played_card.is_trump: 
                            actual_led_suit_for_power = "S" 
                            if played_card.suit == "JOKER": led_suit_for_trick = "S" 
                else: 
                    self.announce(f"Error! {current_player.name} could not play a card.")
                    continue 
            
            if not trick_cards: self.announce("No cards played in this book, something is wrong."); continue

            winning_card_obj = trick_cards[0][1]
            trick_winner = trick_cards[0][0]
            if actual_led_suit_for_power is None and trick_cards: 
                 actual_led_suit_for_power = trick_cards[0][1].suit
            
            for player_obj, card_obj in trick_cards[1:]: # Changed 'player' to 'player_obj'
                if card_obj.get_power(actual_led_suit_for_power) > winning_card_obj.get_power(actual_led_suit_for_power):
                    winning_card_obj = card_obj
                    trick_winner = player_obj
            
            trick_winner.tricks_won_this_round += 1 
            self.announce(f"Book {i+1} goes to {trick_winner.name} (Team {trick_winner.team_id}) with the {winning_card_obj}!")
            current_leader_idx = self.players.index(trick_winner) 
        
        self.team_tricks_this_round = {1:0, 2:0} 
        for p_obj in self.players: # Changed 'p' to 'p_obj'
            self.team_tricks_this_round[p_obj.team_id] += p_obj.tricks_won_this_round

        self.score_round()

    def score_round(self):
        self.announce("\n--- Round Over - Let's Tally the Scores! ---")

        if self.current_round_number == 1:
            self.announce("First Round Scoring (10 points per book for the team):")
            for team_id in [1, 2]:
                tricks_taken_by_team = self.team_tricks_this_round[team_id]
                score_this_round = tricks_taken_by_team * 10
                self.team_scores[team_id] += score_this_round
                team_players_str = self.get_player_names_for_team(team_id)
                self.announce(f"  Team {team_id} ({team_players_str}): Won {tricks_taken_by_team} books = {score_this_round} pts. Total: {self.team_scores[team_id]}")
        else:
            self.announce("Bidding Round Scoring (Teams):")
            for team_id in [1, 2]:
                team_players_str = self.get_player_names_for_team(team_id)
                contract_info = self.current_round_team_contracts[team_id]
                contract_bid = contract_info['bid']
                nil_players_in_team = contract_info['nil_players']
                tricks_taken_by_team = self.team_tricks_this_round[team_id]
                
                team_score_from_contract = 0
                team_score_from_nil = 0

                if contract_bid > 0: 
                    if tricks_taken_by_team >= contract_bid:
                        team_score_from_contract = (contract_bid * 10) + (tricks_taken_by_team - contract_bid)
                        self.announce(f"  Team {team_id} ({team_players_str}): Made contract (bid {contract_bid}, won {tricks_taken_by_team}). Score: {team_score_from_contract} pts.")
                    else:
                        team_score_from_contract = contract_bid * -10 
                        self.announce(f"  Team {team_id} ({team_players_str}): Failed contract (bid {contract_bid}, won {tricks_taken_by_team}). Score: {team_score_from_contract} pts.")
                
                for nil_bidder in nil_players_in_team:
                    if nil_bidder.tricks_won_this_round == 0:
                        team_score_from_nil += 100 
                        self.announce(f"    {nil_bidder.name} (Team {team_id}): Successful Nil bid! +100 pts for team.")
                    else:
                        team_score_from_nil -= 100 
                        self.announce(f"    {nil_bidder.name} (Team {team_id}): Failed Nil bid ({nil_bidder.tricks_won_this_round} books taken). -100 pts for team.")
                
                total_round_score_for_team = team_score_from_contract + team_score_from_nil
                self.team_scores[team_id] += total_round_score_for_team
                self.announce(f"  Team {team_id} ({team_players_str}) total for round: {total_round_score_for_team}. New Team Score: {self.team_scores[team_id]}")

        for team_id_check in [1, 2]:
            if self.team_scores[team_id_check] >= self.target_score:
                self.game_over = True
                if self.winning_team_id is None or self.team_scores[team_id_check] > self.team_scores.get(self.winning_team_id, -float('inf')):
                    self.winning_team_id = team_id_check
                elif self.winning_team_id is not None and self.team_scores[team_id_check] == self.team_scores.get(self.winning_team_id, -float('inf')): # Use .get for safety
                     pass 
        
        self.announce("\nCurrent Team Standings:")
        self.announce(f"  Team 1 ({self.get_player_names_for_team(1)}): {self.team_scores[1]} points")
        self.announce(f"  Team 2 ({self.get_player_names_for_team(2)}): {self.team_scores[2]} points")

    def start_game(self, target_score_override=None):
        if target_score_override: self.target_score = target_score_override
        
        self.announce(f"Welcome! I'm {self.scorekeeper_name}, and I'll be your scorekeeper.")
        self.announce(f"This is a Partnership Game! We're playing to {self.target_score} points.")
        self.announce(f"Team 1: {self.get_player_names_for_team(1)}")
        self.announce(f"Team 2: {self.get_player_names_for_team(2)}")

        self.current_round_number = 0
        self.game_over = False
        self.winning_team_id = None
        self.team_scores = {1: 0, 2: 0} 

        while not self.game_over:
            self.current_round_number += 1
            dealer_name = self.players[self.dealer_index].name
            self.announce(f"\n{'='*10} Starting Round {self.current_round_number} (Dealer: {dealer_name} - Team {self.players[self.dealer_index].team_id}) {'='*10}")
            
            self.deal_cards_and_reveal_kitty()

            if not any(p.hand for p in self.players) and not self.kitty:
                self.announce("Failed to deal cards. Ending game."); self.game_over = True; break

            if self.current_round_number == 1:
                self.announce("--- First Round: No Bidding! Team books are worth 10 points each. ---")
                for player_obj in self.players: player_obj.bid = -1 # Changed 'player' to 'player_obj'
                self.current_round_team_contracts = {tid: {'bid': 0, 'nil_players': []} for tid in [1,2]}
            else:
                self.bidding_phase()
            
            self.play_round() 

            if self.game_over:
                self.announce(f"\n{'!'*10} GAME OVER! {'!'*10}")
                if self.winning_team_id and self.team_scores.get(self.winning_team_id, -float('inf')) >= self.target_score: # Use .get for safety
                    winning_players_str = self.get_player_names_for_team(self.winning_team_id)
                    self.announce(f"Congratulations! The Winning Team is Team {self.winning_team_id} ({winning_players_str}) with {self.team_scores[self.winning_team_id]} points!")
                else: 
                    self.announce(f"Target score of {self.target_score} reached or exceeded. Let's check final scores.")
                
                self.announce("\nFinal Team Scores:")
                self.announce(f"  Team 1 ({self.get_player_names_for_team(1)}): {self.team_scores[1]} points")
                self.announce(f"  Team 2 ({self.get_player_names_for_team(2)}): {self.team_scores[2]} points")
                break 
            
            self.dealer_index = (self.dealer_index + 1) % len(self.players) 
        
        if not self.game_over: self.announce("\n--- Game Ended (Unexpected: Loop finished without game over condition) ---")

# --- Example Usage ---
if __name__ == "__main__":
    player_names = ["Human (P0, T1)", "AI Bot 1 (P1, T2)", "AI Bot 2 (P2, T1)", "AI Bot 3 (P3, T2)"]
    
    game = Game(player_names, target_score=200) 
    game.start_game()
