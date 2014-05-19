#This shall be the framework for farkle via python.
import os, sys
import random

#start the random generator with cryptographic seed material... Farkle is serious business.
random.seed(os.urandom(1024))

class Farkle:
	""" This class implements the facbook version of the popular game farkle.
	This is by no means considered perfect, but I think it works well enough
	for most cases.
	bots are called in the play function. The rest is merely for bookkeeping."""
	#member variables
	savedDice = []
	totScore = 0
	thisScore = 0
	thisRound = []
	rollNum = 0;
	roundCount = 0
	player = None
	farkleCount = 0

	def __init__(self):
		""" init the class"""
		self.savedDice = []
		self.totScore = 0
		self.thisScore = 0
		self.thisRound = []
		self.rollNum = 6
		self.roundCount = 0 #0-9
		self.player = None
		self.farkleCount = 0
		
	def roll(self):
		""" Gets a randomly generated roll. This relies on the random class"""
		rolled = []
		for i in range(self.rollNum):
			rolled.append(random.randint(1,6))
		return rolled
		
	def isFarkle(self, diceRolled=None):
		""" Checks the roll passed in for a farkle condition. Takes into account three pairs and three of a kind might not be 1's or 5's"""
		if diceRolled == None:
			diceRolled = self.roll()
		counts = [0,0,0,0,0,0]
		for i in range(len(diceRolled)):
			counts[diceRolled[i]-1] += 1
			
		#if we have either a 1 or a 5 it's not a farkle.
		if (counts[0] != 0) or (counts[4] != 0):
			return False
		
		#check for three of a kind not 1's or 5's
		for i in range(6):
			if counts[i] >= 3:
				return False
		
		#check for three pair
		pairs = 0
		for i in range(len(counts)):
			if counts[i] == 2:
				pairs += 1
		if pairs == 3:
			return False
			
		self.thisScore = 0
		self.farkleCount += 1
		if self.farkleCount >= 3:
			self.thisScore = -500
		self.bank(True) #farkle Bank.
		return True

	def updateFarkleCount(self):
		if self.farkleCount >= 3:
			self.farkleCount = 0
		
	def saveDice(self, roll, saveIndecies):
		""" This will save off the dice that were selected for further inspection later. 
			This also validates if you have made a valid selection.""" 
		for i in range(len(saveIndecies)):
			self.savedDice.append(roll[saveIndecies[i-1]-1])
		valid = self.validateSave()
		if valid:
			self.thisRound.append(self.savedDice)
			self.thisScore += self.getScore()
		else:
			#invalid... fix it?
			#player action perhaps
			#self.player.reselectSaveDice()
			asdf = 0
		self.player.notifySaveDice(self.thisRound)
		self.savedDice = []
		self.rollNum = len(roll)-len(saveIndecies)
		if self.rollNum == 0:
			self.rollAgain()
		
	def validateSave(self):
		"""Method validates that give dice selected to be saved are valid. I.e. no single 2 etc."""
		count = [0,0,0,0,0,0]
		retVal = False
		for i in range(len(self.savedDice)):
			count[self.savedDice[i]-1] += 1
		
		#saving a 1 or a 5 is always okay.
		if count[0] != 0 or count[4] != 0:
			retVal = True
		
		#accounts for three of a kinds
		rest = [1,2,3,5]
		for i in rest:
			if count[i] >= 3:
				retVal = True
			elif count[i] != 0:
				retVal = False
		
		#validates a straight.
		i = 0 #account for straights.
		for i in range(6):
			if count[i] != 1:
				break
		if i == 6:
			retVal = True
		
		#check for three pair.
		pairs = 0
		for i in range(6):
			if count[i] == 2:
				pairs += 1
		if pairs == 3:
			retVal = True
			
		return retVal
			
			
		
	def bank(self,farkle=False):
		"""Moves to the next round, and banks your points so you cannot lose them from a farkle."""
		#clear all the previous stuff, and start a new round... saving score.
		self.savedDice = [];
		self.thisRound = []
		self.totScore += self.thisScore
		self.thisScore = 0
		self.rollNum = 6
		self.roundCount += 1
		if not farkle:
			self.farkleCount = 0

	def rollAgain(self):
		"""Accounts for the case where you exhaust your dice without farkling. This allows you to have another set of 6 dice."""
		#restart the dice roll, and clear the saved dice. DO NOT MODIFY SCORE
		self.savedDice = []
		self.thisRound = []
		self.rollNum = 6;
		
	def getScore(self): 
		"""This method calculates the scrore for a given dice round. This method is called everytime you save the dice
		   to accumulate the score incrementally. Similar to the facebook game."""
		tempScore = 0;
		count = [0,0,0,0,0,0]
		for k in range(len(self.savedDice)):
			count[self.savedDice[k]-1] += 1
		pairs = 0
		straight = 0
		for j in range(6):
			if count[j] >= 3:
				temp = ((j+1)*100)*(count[j]-2)
				if j == 0: #multiple ones get you thousands instead of hundreds.
					temp *= 10
				tempScore += temp
			elif count[j] == 2:
				pairs += 1
				if j == 0:
					tempScore += 200
				elif j == 4:
					tempScore += 100
			elif count[j] == 1:
				straight += 1
				if j == 0:
					tempScore += 100
				elif j == 4:
					tempScore += 50
			else: #we have < 3
				if j == 0:
					tempScore += count[j]*100
				elif j == 4:
					tempScore += count[j]*50
		if pairs == 3:
			tempScore += 750
			if count[0] == 2:
				tempScore -= 200
			if count[4] == 2:
				tempScore -= 100
		elif straight == 6:
			tempScore += 1500 - 150 #150 was already added because of the single 1, and 5
		return tempScore
		
	def getTotScore(self):
		"""Method to return the total score that is immutable by farkles."""
		return self.totScore
	
	def getCurRoundScore(self):
		"""gets the score for a given round, can dissappear on farkle"""
		return self.thisScore
		
		
	def play(self, player):
		"""This method runs through playing of a game.  With the human player outlined below this is fairly interactive, 
			but with a bot this will go much quicker. Notice that this method doesn't handle any output to the screen.
			This is all done from within the player class if you so desire."""
		self.player = player
		while 1:
			if self.roundCount > 9:
				break;
			player.giveTotalPoints(self.getTotScore())
			player.giveRound(self.roundCount)
			player.giveCurScore(self.getCurRoundScore())
			theRoll = self.roll()
			player.giveRoll(theRoll)
			farkle = self.isFarkle(theRoll)
			if not farkle:
				self.saveDice(theRoll, player.getSaveDice())
				if self.thisScore >= 300:
					if player.getBank(self.getCurRoundScore(), self.getTotScore()):
						self.bank()
			else:
				player.getFarkleAction(self.farkleCount)
				self.updateFarkleCount()
		player.endGame(self.getTotScore())
		return 0;
		
###################################################################
##This class will layout the framework for a generic player class. 
## To make a bot, just make a class that implements the following 
## functions
###################################################################
class Player:
	"""This is an abstract parent class to outline the framework for a player."""
	def __init__(self):
		self.playerType = "none"
	def giveRoll(self, roll):
		return 0
	def getSaveDice(self):
		return [1]
	def getBank(self, curScore, totScore):
		return False
	def getFarkleAction(self, farkleCount):
		print "DRAT!!"
	def giveTotScore(self, score):
		print score
	def giveRound(self, roundNum):
		print roundNum
	def giveCurScore(self, curScore):
		print curScore
	def endGame(self):
		print "GAME OVER"
	def notifySaveDice(self, roundDice):
		print roundDice
	
	
#####################################################################
##This is a human instance of the player class. this will output text
## to the screen, and allow for human input, and human force quitting
## It stores state information merely to show an example of what could 
## be stored by a bot.
#####################################################################	
class Human(Player):
	"""This is the extension of the player class that implements a human player. That way I can actually test the game by hand."""
	def __init__(self):
		Player.__init__(self)
		self.palyerType = "human"
		self.curRoll = []
		self.totScore = 0
		self.roundNum = 0
		self.curScore = 0
		
	def giveRoll(self, roll):
		self.curRoll = roll
		print self.curRoll
	def getSaveDice(self):
		try:
			x = ""
			while(x == ""):
				x = raw_input("Select Which? (comma seperated list)")
			x = x.split(",")
			saved = []
			for i in range(len(x)):
				saved.append(int(x[i]))
		except KeyboardInterrupt:
			sys.exit(0) #bail... the user wants out.
		return saved
	def getBank(self, curScore, totScore):
		x = "a"
		print "Total: ", totScore, " This Round: ", curScore
		while x != "y" and x != "n":
			x = raw_input("Bank?(y/n)")
			x = x.lower()
		if(x == "y"):
			return True
		else:
			return False
		
	def getFarkleAction(self, farkleCount):
		print "!! FARKLE !!",
		if farkleCount == 3:
			print " -500 Points"
		else:
			print " COUNT: ", farkleCount
		try:
			x = raw_input("(press any key to continue)")
		except KeyboardInterrupt:
			sys.exit(0)
		
	def giveTotalPoints(self, score):
		self.totScore = score
		print "Total Points: ", score
	
	def giveRound(self, roundNum):
		self.roundNum = roundNum
		print "Round: ", self.roundNum+1
	
	def giveCurScore(self, curScore):
		self.curScore = curScore
		print "Cur Round Score: ", self.curScore
	
	def endGame(self, totScore):
		print "Final Score: ", totScore
		print "Thanks for playing!"
		
	def notifySaveDice(self, roundDice):
		print "Saved: "
		for i in range(len(roundDice)):
			print i+1, ". ", roundDice[i]
#the main function... this will actually play the game.
def main():
	game = Farkle()
	#this will be changed to a bot when I get that made.
	player = Human()
	game.play(player);

if __name__ == "__main__":
	main()