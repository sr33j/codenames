from random import sample, shuffle
from gensim.models import KeyedVectors
from scipy.spatial.distance import cosine

def cost(candidate,my_words,ur_words,neutral_words,bomb):
	avg_my_dist = 0
	if my_words:
		for word in my_words:
			avg_my_dist += cosine(candidate, word)**2
		avg_my_dist /= len(my_words)

	avg_ur_dist = 0
	if ur_words:
		for word in ur_words:
			avg_ur_dist += cosine(candidate, word)**2
		avg_ur_dist /= len(ur_words)

	avg_nu_dist = 0
	if neutral_words:
		for word in neutral_words:
			avg_nu_dist += cosine(candidate, word)**2
		avg_nu_dist /= len(neutral_words)

	bomb_dist = cosine(candidate, bomb)**2

	return 6*avg_my_dist -1*avg_nu_dist -2*avg_ur_dist -3*bomb_dist

def update(board,x,color):
	for i in range(len(board)):
		for j in range(len(board)):
			if board[i][j].strip() == x:
				board[i][j] = color
				return

def print_board(board):
	size = len(board)

	#each word will get 13 spaces
	space = 15
	line = '_'*space

	#two of which will be taken by '|'
	print(line*size)
	for row in board:
		for elem in row:
			left = (space-(len(elem)+2))//2
			right = (space-(len(elem)+2)) - left
			left_pad = " "*left
			right_pad = " "*right
			card = '|'+left_pad+elem+right_pad+'|'
			print(card,end="")
		print("\n"+line*size)
	print("\n")

print(".:.:.:.:. LOADING GAME .:.:.:.:.",end="\n")

N = 5
n_red = 9
n_blue = 8
n_other = N*N - n_red - n_blue - 1
#there is one bomb

bank = open("wordbank.txt").read().split("\n")
selected = sample(bank, N*N)

board = []
for i in range(N):
	board.append([])
	for j in range(N):
		board[i].append(selected[i*N+j])

shuffle(selected)

reds = {}
blues = {}
others = {}
for i in range(n_red):
	reds[selected[i]] = i
for i in range(n_red, n_red+n_blue):
	blues[selected[i]] = i
for i in range(n_red+n_blue,n_red+n_blue+n_other):
	others[selected[i]] = i

bomb = selected[-1];

illegal_clues = set()
for word in bank:
	illegal_clues.add(word)

print_board(board)

print(".:.:.:.:. POWERING UP BOT .:.:.:.:.",end="\n")


google_model = KeyedVectors.load_word2vec_format("GoogleNews-vectors-negative300.bin", binary=True)


clues = open("dict.txt").read().split("\n")
scores = []


points = 0
while reds:
	red_vecs = []
	for red in reds:
		if red in google_model:
			red_vecs.append(google_model[red])
	blue_vecs = []
	for blue in blues:
		if blue in google_model:
			blue_vecs.append(google_model[blue])
	other_vecs = []
	for other in others:
		if other in google_model:
			other_vecs.append(google_model[other])

	bomb_vec = google_model["bomb"]
	if bomb in google_model:
		bomb_vec = google_model[bomb]

		for clue in clues:
			if clue in google_model:
				score = cost(google_model[clue], red_vecs, blue_vecs, other_vecs, bomb_vec)
				scores.append((clue, score))

	top_scores = sorted(scores,key=lambda x: x[1])
	top_clue = "PLACEHOLDER"

	for score in top_scores:
		if not score[0] in illegal_clues:
			top_clue = score[0]
			break
	illegal_clues.add(top_clue)
	print("CLUE: " + top_clue)
	while True:
		if not reds:
			break
		x = input("GUESS:").strip()
		if x in reds:
			update(board,x,'R')
			del reds[x]
			points+=1
			print("POINTS: " + str(points))
		elif x in blues:
			print("WRONG")
			update(board,x,'B')
			del blues[x]
			points-=1
			break
		elif x in others:
			print("WRONG")
			del others[x]
			update(board,x,'O')
			break
		elif x == bomb:
			print("WRONG")
			update(board,x,'XXX')
			points = -1000000
			break
		else:
			print("WHAT")

	print("POINTS: " + str(points))
	print_board(board)


print("done")