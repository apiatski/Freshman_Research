# These are the stim files that set the box sizes. GUI input prompt will ask for Matrix ID. Type in digit: 1,2,3, etc. Currently using 2.
# Can shorten the lengths of these, but max array size is 18.
one=[1,2,3,3,2,1,2,1,3,2,3,1]
two=[.02,.04,.08,.04,.08,.02,.08,.02,.04,.04,.02,.08,.02,.04,.02,.04,.02,.08,.02,.02,.04]
three=[3,2,1,4,3,2,3,4,3,2]
def matrix_controller(matrix_id):
	print('in matrix_controller')
	if matrix_id=='1':
		print('in first tree')
		return one
	elif matrix_id=='2':
		return two
	elif matrix_id=='3':
		return three

