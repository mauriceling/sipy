# Start script file: D:\Dropbox\MyProjects\sipy\example_scripts\script_04.sipy
# begin script_04

# Start script file: D:\Dropbox\MyProjects\sipy\example_scripts\script_02.sipy
# begin script_02

let y be list 10,8,47,37,3,71,74,51,68,80,54,79,43,11,90,73,19,28,46,58,10,44,26,34,62,59
let x1 be list 15,12,48,42,6,76,75,55,72,81,55,83,46,11,95,78,19,33,46,61,12,47,29,37,62,64
let x2 be list 15,15,48,43,7,77,80,60,74,85,58,84,46,11,96,82,21,36,49,61,13,52,32,39,62,67
let x3 be list 9,5,42,37,1,74,80,60,68,85,48,81,37,10,89,82,12,26,45,57,6,45,30,32,60,66
let x4 be list 4,4,42,28,-6,66,77,53,60,76,47,76,28,3,84,72,12,19,45,56,4,40,21,25,55,58

variance levene list y x1 x2 x3 x4

# end script_02
# End script file: D:\Dropbox\MyProjects\sipy\example_scripts\script_02.sipy
# Start script file: D:\Dropbox\MyProjects\sipy\example_scripts\script_03.sipy
# begin script_03

let x5 be list 80,63,100,20,27,45,90,55,26,27,56,79,78,45,69,69,81,80,28,36,38,62,88,57,90,7
let x6 be list 83,67,104,23,30,50,92,59,26,29,59,81,78,48,69,71,81,80,28,36,40,66,92,57,92,7
let x7 be list 86,69,104,23,32,55,94,62,27,33,64,81,82,52,74,75,86,82,32,41,41,66,93,62,94,11
let x8 be list 81,59,94,13,28,47,90,61,20,30,61,76,74,42,72,66,86,82,22,32,39,62,83,53,90,3
let x9 be list 78,50,91,9,28,37,80,55,20,24,57,73,69,33,67,59,85,78,20,28,38,62,80,43,87,3

# Start script file: D:\Dropbox\MyProjects\sipy\example_scripts\script_01.sipy
# begin script_01

show environment
show history
show data

# end script_01
# End script file: D:\Dropbox\MyProjects\sipy\example_scripts\script_01.sipy

# end script_03
# End script file: D:\Dropbox\MyProjects\sipy\example_scripts\script_03.sipy

regress linear y x1 x3 x5 x7 x9

# end script_04
# End script file: D:\Dropbox\MyProjects\sipy\example_scripts\script_04.sipy
