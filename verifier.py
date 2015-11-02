import hashlib
import numpy as np

suits = ['Heart', 'Diamond', 'Club', 'Spade']
vals = ['2', '3', '4', '5', '6', '7', '8', '9', '10',
        'Jack', 'Queen', 'King', 'Ace']
cards = ['{val} {suit}'.format(val=val, suit=suit)
         for suit in suits for val in vals]

def verify_global_committment(server_random,
                              initial_shuffle,
                              player_randoms,
                              global_committment):
    """ Validates the global committment. """
    player_randoms_array = player_randoms.split(',')
    player_committments = [hashlib.sha256(player_random).hexdigest()
                           for player_random in player_randoms_array]
    expected_global_committment = hashlib.sha256(
        server_random +
        initial_shuffle +
        ''.join(player_committments)).hexdigest()
    return expected_global_committment == global_committment


def compute_final_shuffle(initial_shuffle, server_random, player_randoms):
    """ Computes the final shuffle. """
    final_shuffle = initial_shuffle.split('|')
    player_randoms_array = player_randoms.split(',')
    mersenne_twister_seed = hashlib.sha256(
        server_random + ''.join(player_randoms_array)).hexdigest()
    mersenne_twister_seed = int(mersenne_twister_seed, 16) % (2 ** 32)
    # Mersenne Twister initialization
    print 'Will seed the Mersenne Twister generator with {seed}'.format(
        seed=mersenne_twister_seed)
    np.random.seed(int(mersenne_twister_seed))
    # Fisher-Yates shuffle
    for i in xrange(len(final_shuffle) - 1, 0, -1):
        j = np.random.randint(0, 4294967296) % (i + 1)
        final_shuffle[i], final_shuffle[j] = final_shuffle[j], final_shuffle[i]
    return final_shuffle


def main():
    """ Collects user input and runs verification """
    player_randoms = raw_input("Enter Players randoms - must include yours: ")
    verify_your_random = None
    server_random = raw_input('Enter Server random: ')
    initial_shuffle = raw_input('Enter the Initial Shuffle: ')
    global_committment = raw_input(
        'Enter the global committment as it was ' +
        ' sent before you published your secret random: ')
    if not verify_global_committment(server_random, initial_shuffle,
                                     player_randoms, global_committment):
        print 'Global committment verification failed'
    else:
        print 'Global committment verified'
    cards_num = int(raw_input('Enter how many cards you observed: '))
    players_num = int(raw_input('How many players were there on the table: '))
    assert cards_num >= (1 + players_num) * 2
    final_shuffle = compute_final_shuffle(
        initial_shuffle, server_random, player_randoms)[:cards_num]
    final_shuffle = [cards[int(symbol)]for symbol in final_shuffle]
    print 'The round must have been run in the following manner:'
    for p in xrange(players_num):
        print 'Player {player_num} got the cards: {cards}'.format(
            player_num=p,
            cards=', '.join([final_shuffle[p],
                            final_shuffle[players_num + p + 1]]))
    print 'Dealer got the cards: {cards}'.format(
        cards=', '.join([final_shuffle[players_num],
                         final_shuffle[players_num * 2 + 1]]))
    print 'More cards were dealt in this order: {cards}'.format(
        cards=', '.join(final_shuffle[players_num * 2 + 2:cards_num]))


if __name__ == '__main__':
    main()
