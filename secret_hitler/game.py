"""Game runner for secret hitler."""
import random

from secret_hitler.exceptions import (
    InvalidPolicyType,
    GameEnded,
    GameInProgress,
    GameNotStarted,
    NotEnoughPlayers,
    NotPresidentTurn,
    PlayerLimitReached,
    VetoNotAllowed,
)

class Game:
    """Game runner for secret hitler."""
    # pylint: disable=too-many-instance-attributes

    stage = 'General election'
    round_stage = None
    end_state = None

    player_ids = []
    # Store player count separately because of executions
    player_count = 0
    hitler = None
    hitler_knows_fascists = False
    fascists = []
    liberals = []

    policies = []

    policy_deck = (
        ['Liberal' for i in range(6)] + ['Fascist' for i in range(11)]
    )

    discard_deck = []

    president = None
    chancellor = None
    next_president = None
    special_election = None
    term_limited = []
    player_votes = {}
    election_failures = 0
    presidential_power = None
    president_policies = []
    chancellor_policies = []
    veto_request = False
    investigated = []

    name_mappings = {}

    def add_player(self, player_id, name_mapping=None):
        """Add a player to a game that is being prepared.
        :param player_id: The string ID of the player to be added.

        :raises GameInProgress: If the game has already been launched.
        :raises PlayerLimitReached: If the maximum players have joined."""
        if player_id in self.player_ids:
            return

        if self.stage != 'General election':
            raise GameInProgress(
                'Parliament is already in session and is not accepting new '
                'ministers.'
            )

        if len(self.player_ids) == 10:
            raise PlayerLimitReached(
                'There are already 10 ministers. Too many will spoil the '
                "country. You don't want to ruin democracy, do you?"
            )

        self.player_ids.append(player_id)

        if name_mapping:
            self.name_mappings[player_id] = name_mapping
        else:
            self.name_mappings[player_id] = player_id

    def remove_player(self, player_id):
        """Remove a player from a game that is being prepared.
        :param player_id: The string ID of the player to be removed.

        :raises GameInProgress: If the game has already been launched."""
        if self.stage != 'General election':
            raise GameInProgress(
                'Parliament is already in session and is not accepting new '
                'ministers.'
            )

        if player_id in self.player_ids:
            self.player_ids.remove(player_id)
            self.name_mappings.pop(player_id)
        # If not then the player isn't in the game, so... mission accomplished

    def launch_game(self):
        """Launch the game, if we have enough players!

        :raises GameInProgress: If the game has already started.
        :raises GameEnded: If the game has already finished.
        :raises NotEnoughPlayers: If there are not enough players to start."""
        if self.stage == 'Parliament in session':
            raise GameInProgress(
                'Parliament is already in session. Are you a troublemaker?'
            )

        if self.end_state:
            raise GameEnded(
                'This term of Parliament has already ended. Open elections '
                'again before you start again.'
            )

        self.player_count = len(self.player_ids)
        if self.player_count < 5:
            raise NotEnoughPlayers(
                'There must be at least 5 ministers for parliament to enter '
                'session.'
            )

        random.shuffle(self.policy_deck)
        self.assign_roles()
        self.stage = 'Parliament in session'
        return self.start_election()

    def assign_roles(self):
        """Assign roles to players ready to play the game."""
        fascist_count = {
            5: 2,
            6: 2,
            7: 3,
            8: 3,
            9: 4,
            10: 4,
        }[self.player_count]
        self.fascists = random.sample(self.player_ids, fascist_count)
        self.liberals = [player for player in self.player_ids
                         if player not in self.fascists]
        self.hitler = random.choice(self.fascists)
        self.hitler_knows_fascists = self.player_count < 7

    def get_starting_knowledge(self, player_id):
        """Describe the role of a player and their knowledge.
        :param player_id: The string ID of the player to be added.

        :return: A string giving the knowledge a player starts with.

        :raises GameNotStarted: If the game hasn't started yet."""
        if self.stage == 'General election':
            raise GameNotStarted(
                "Parliament is not in session yet, and voter integrity "
                "regulations mean that we can't reveal who you are."
            )

        if player_id in self.liberals:
            return (
                "{minister}, you are a liberal. You suspect there are "
                "{fascist_count} fascists in this parliament. Be "
                "vigilant!".format(
                    minister=self.name_mappings[player_id],
                    fascist_count=len(self.fascists),
                )
            )

        if player_id == self.hitler:
            message = "{minister}, you are hitler! "
            if self.hitler_knows_fascists:
                message += (
                    "Fortunately, you know your fellow ne'er-do-well: "
                    "{fascists}"
                )
            else:
                message += (
                    "You suspect you have {other_fascist_count} allies."
                )
            return message.format(
                minister=self.name_mappings[player_id],
                fascists=', '.join([self.name_mappings[fascist]
                                    for fascist in self.fascists
                                    if fascist != player_id]),
                other_fascist_count=len(self.fascists) - 1,
            )

        return (
            "{minister}, you are a fascist. Your glorious(ly evil) leader is "
            "{hitler}. Your fellow fascists are: {fascists}".format(
                minister=self.name_mappings[player_id],
                fascists=', '.join([self.name_mappings[fascist]
                                    for fascist in self.fascists
                                    if fascist not in (player_id,
                                                       self.hitler)]),
                hitler=self.name_mappings[self.hitler],
            )
        )

    def get_finished_state(self):
        """Return the finished state of the game.
        :return: None if the game is not finished, otherwise the winning
        state."""
        return self.end_state

    def start_election(self):
        """Start the next round.
        :return: A message indicating that the president should nominate
                 a chancellor."""
        self.chancellor = None
        self.player_votes = {}
        self.presidential_power = None

        if self.special_election:
            self.president = self.special_election
            self.special_election = None
        else:
            if self.next_president:
                self.president = self.next_president
            else:
                # First round
                self.president = random.choice(self.player_ids)
            self.next_president = self.player_ids[
                (self.player_ids.index(self.president) + 1)
                % len(self.player_ids)
            ]

        ineligible = [minister for minister in self.term_limited
                      if minister != self.president]
        self.round_stage = 'Election'

        message = "President {president} must now select their chancellor."

        if len(ineligible) > 0:
            message += (
                "The following minister(s) are term limited: {ineligible}"
            )

        return (
            message.format(
                president=self.name_mappings[self.president],
                ineligible=', '.join([self.name_mappings[minister]
                                      for minister in ineligible]),
            )
        )

    def nominate_chancellor(self, player_id):
        """Nominate a chancellor for this round.
        :param player_id: The string ID of the player to be added.

        :return: A message indicating that players should vote.

        :raises IneligibleChancellor: If the chancellor is term limited."""
        eligible = [minister for minister in self.player_ids
                    if minister != self.president
                    and minister not in self.term_limited]
        if player_id not in self.player_ids:
            return (
                'A living minister must be selected. Eligible Chancellors '
                'are: {eligible}'.format(
                    eligible=', '.join([self.name_mappings[minister]
                                        for minister in eligible]),
                )
            )
        if player_id not in eligible:
            return (
                'The previous or current President and the previous '
                'Chancellor are not eligible to become chancellor. '
                'Eligible Chancellors are: {eligible}'.format(
                    eligible=', '.join([self.name_mappings[minister]
                                        for minister in eligible]),
                )
            )

        self.chancellor = player_id

        return (
            'A government has been proposed: President {president} with '
            'Chancellor {chancellor}. Ministers should discuss and vote on '
            'this proposal.'.format(
                president=self.name_mappings[self.president],
                chancellor=self.name_mappings[self.chancellor],
            )
        )

    def cast_vote(self, player_id, vote):
        """Cast a player's vote regarding the current proposed government.
        :return: If the voting is complete, a message indicating the result
                 will be returned.

        :param player_id: The string ID of the player to be added.
        :param vote: Boolean: True for Ja, False for Nein"""
        self.player_votes[player_id] = vote

        if len(self.player_votes) == len(self.player_ids):
            yes_votes = [self.name_mappings[minister]
                         for minister in self.player_ids
                         if self.player_votes[minister]]
            no_votes = [self.name_mappings[minister]
                        for minister in self.player_ids
                        if not self.player_votes[minister]]

            message = 'Voting complete! '
            if len(yes_votes) > 0:
                message += 'Ja votes: {} ; '.format(', '.join(yes_votes))
            if len(no_votes) > 0:
                message += 'Nein votes: {} ; '.format(', '.join(no_votes))

            if yes_votes > no_votes:
                if (
                        self.policies.count('Fascist') >= 3
                        and self.chancellor == self.hitler
                ):
                    self.end_state = 'Fascist win (chancellor Hitler)'
                    return 'Hitler was elected Chancellor, fascists win!'

                message += 'Government formed! '
                self.term_limited = [self.president, self.chancellor]
                message += (
                    'The President must now propose policies to the '
                    'Chancellor.'
                )
                self.president_policies = [
                    self.policy_deck.pop(),
                    self.policy_deck.pop(),
                    self.policy_deck.pop(),
                ]
                self.round_stage = 'Legislative Session'
            else:
                return self._check_failing_government()
            return  message
        return "{}/{} votes cast!".format(
            len(self.player_votes),
            len(self.player_ids),
        )

    def _check_failing_government(self):
        """Determine whether the government is failing enough to cause chaos.
        :return: A message indicating the government state."""
        self.election_failures += 1
        if self.election_failures >= 3:
            policy = self.policy_deck.pop()
            ended = self.assign_policy(policy, skip_power=True)
            if ended:
                return ended
            return (
                'The country is in chaos! The parliament passes a '
                'reactionary {policy} policy! {election}'.format(
                    policy=policy,
                    election=self.start_election()
                )
            )

        message = 'The parliament argues, but takes no action. '
        if self.election_failures == 1:
            message += 'The Media ridicules selected ministers. '
        else:
            message += (
                'The people are grumbling. Parliament would be '
                'wise to reach an agreement in the next session! '
            )
        message += '{election}'
        return message.format(election=self.start_election())

    def get_fascist_policy_powers(self):
        """Get a list of the Fascist policy powers.
        :returns: A list of powers granted for fascist powers as they are
                  passed.

        :raises GameNotStarted: Powers cannot be determined until the player
                                count is known."""
        if self.stage == 'General Election':
            raise GameNotStarted(
                'Fascist policy effects cannot be determined until we know '
                'how large the Parliament is.'
            )

        if self.player_count < 7:
            powers = [
                None,
                None,
                'Policy Peek',
                'Execution',
                'Execution',
            ]
        elif self.player_count < 9:
            powers = [
                None,
                'Investigate Loyalty',
                'Call Special Election',
                'Execution',
                'Execution',
            ]
        else:
            powers = [
                'Investigate Loyalty',
                'Investigate Loyalty',
                'Call Special Election',
                'Execution',
                'Execution',
            ]
        return powers

    def assign_policy(self, policy, skip_power=False):
        """Assign a policy, as selected by the Chancellor or due to failures
        of the Parliament.
        :return: Message indicating if the game has just ended."""
        self.policies.append(policy)

        fascist_policies = self.policies.count('Fascist')
        liberal_policies = self.policies.count('Liberal')

        if fascist_policies == 6:
            self.end_state = 'Fascist win (policies)'
            return (
                'Parliament has elected to create an entirely fascist state. '
                'I hope you are proud of yourselves.'
            )
        if liberal_policies == 5:
            self.end_state = 'Liberal win (policies)'
            return (
                'Well done! The country has remained liberal despite the '
                'dastardly machinations of scoundrels!'
            )

        if policy == 'Fascist' and not skip_power and fascist_policies > 1:
            powers = self.get_fascist_policy_powers()
            self.presidential_power = powers[fascist_policies - 1]

        self.election_failures = 0

        if len(self.policy_deck) < 3:
            self.policy_deck = self.policy_deck + self.discard_deck
            random.shuffle(self.policy_deck)
            self.discard_deck = []
        return ""

    def discard_policy(self, policy):
        """Discard one of the policies received by the president.
        :param policy: The type of policy to discard.

        :return: A message confirming what was discarded.

        :raises InvalidPolicyType: There are only two, get it right.
        :raises NotPresidentTurn: If it is not time for the president to
                                  discard policies."""
        if not self.president_policies:
            raise NotPresidentTurn(
                'It is not time for the President to decide upon policies.'
            )

        if policy not in ('Liberal', 'Fascist'):
            raise InvalidPolicyType(
                'There are only Liberal and Fascist policies.'
            )

        if policy not in self.president_policies:
            self.discard_deck.append(self.president_policies.pop())
            message = (
                'Nice try, but there are no {policy} policies. '
                'One of the available policies was discarded.'.format(
                    policy=policy,
                )
            )
        else:
            self.discard_deck.append(policy)
            self.president_policies.remove(policy)
            message = '{policy} discarded.'.format(policy=policy)

        self.chancellor_policies = [
            self.president_policies.pop(),
            self.president_policies.pop(),
        ]

        return message

    def veto(self):
        """State that a chancellor wishes to veto the policy.

        :raises VetoNotAllowed: Veto can only be exercised after 5 fascist
                                policies pass."""
        if self.policies.count('Fascist') < 5:
            raise VetoNotAllowed(
                'Veto is only an option after 5 Fascist policies pass.'
            )

        self.veto_request = True

    def veto_confirm(self):
        """Confirm that the president is happy to veto the policy.
        :return: A message revealing the result of the veto.

        :raises VetoNotAllowed: Veto can only be confirmed when requested by
                                the chancellor."""
        if not self.veto_request:
            raise VetoNotAllowed(
                'Veto can only be confirmed after the Chancellor requests it.'
            )

        self.veto_request = False

        self.discard_deck.extend([
            self.chancellor_policies.pop(),
            self.chancellor_policies.pop(),
        ])

        return 'The veto is passed. ' + self._check_failing_government()

    def select_policy(self, policy):
        """Select one of the policies received by the Chancellor.
        :param policy: A policy name.

        :return: A message indicating the result."""
        if policy not in self.chancellor_policies:
            # Nice try.
            policy = self.chancellor_policies[0]

        ended = self.assign_policy(policy)
        if ended:
            return ended

        self.chancellor_policies.remove(policy)
        self.discard_deck.append(self.chancellor_policies.pop())

        message = 'A {policy} policy was passed! '.format(policy=policy)

        if self.presidential_power:
            self.round_stage = 'Executive Action'
            message += (
                "New powers have been granted to the president, who must: "
                "{action}".format(action=self.presidential_power)
            )
        else:
            message += 'It is time to elect the next Government! '
            message += self.start_election()

        return message

    def enact_power(self, player_id):
        """Enact a presidential power.
        :param player_id: The player to be targeted by this power.

        :return: The private and public result statements."""
        if player_id and player_id not in self.player_ids:
            return "A specific player must be chosen.", ""

        return {
            'Investigate Loyalty': self._investigate,
            'Call Special Election': self._special_election,
            'Policy Peek': self._peek,
            'Execution': self._execute,
        }[self.presidential_power](player_id)

    def _investigate(self, player_id):
        """Enact the Investigate Loyalty power.
        :param player_id: The player to be targeted by this power.

        :return: The private and public result statements."""
        if not player_id:
            return "Please choose someone to investigate.", ""
        if player_id in self.investigated:
            return (
                '{} has already been investigated. Choose again.'.format(
                    self.name_mappings[player_id],
                ), ""
            )
        self.investigated.append(player_id)
        if player_id in self.fascists:
            private = "{} is a Fascist.".format(self.name_mappings[player_id])
        else:
            private = "{} is a Liberal.".format(self.name_mappings[player_id])
        return (
            private,
            "The President has investigated {}. ".format(
                self.name_mappings[player_id]
            ) + self.start_election(),
        )

    def _special_election(self, player_id):
        """Enact the Call Special Election power.
        :param player_id: The player to be targeted by this power.

        :return: The private and public result statements."""
        if player_id == self.president:
            return "You cannot nominate yourself.", ""
        self.special_election = player_id
        return (
            "",
            "The President has elected {}. ".format(
                self.name_mappings[player_id]
            ) + self.start_election(),
        )

    def _peek(self, _):
        """Enact the Policy Peek power.
        :param _: Ignored, provided to have compatible interface with other
                  powers.

        :return: The private and public result statements."""
        return (
            "The next three policies are: {}".format(
                ", ".join(self.policy_deck[:3]),
            ),
            "The President has been advised on upcoming policies. " +
            self.start_election(),
        )

    def _execute(self, player_id):
        """Enact the Execution power.
        :param player_id: The player to be targeted by this power.

        :return: The private and public result statements."""
        if player_id == self.hitler:
            self.end_state = 'Liberal win (killed Hitler)'
            return (
                "",
                (
                    "The President formally executes {}. "
                    "Hitler has been executed, the Liberals win. "
                    "(with blood on their hands).".format(
                        self.name_mappings[player_id],
                    )
                ),
            )
        self.player_ids.pop(player_id)
        return (
            "",
            (
                "The President formally executes {minister}."
                "Seances are not allowed in this game, so {minister} "
                "should not share any useful information until the end "
                "of the game. ".format(
                    minister=self.name_mappings[player_id]
                ) + self.start_election()
            )
        )
