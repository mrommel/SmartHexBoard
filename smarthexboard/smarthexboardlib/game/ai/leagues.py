class VoteCommitment:
	def __init__(self):
		self.resolutionID: int = -1
		voteChoice: int = -1
		numVotes: int = -1
		enact: bool = False


class LeagueAI:
	def __init__(self, player):
		self.player = player

	def desiredVoteCommitments(self, otherPlayer) -> [VoteCommitment]:
		return []
